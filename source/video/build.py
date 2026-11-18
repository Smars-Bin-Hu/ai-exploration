#!/usr/bin/env python3
"""Build a tutorial video's audio, frames, Final Cut Pro timeline and rough mp4 from its scenes file.

    .venv/bin/python source/video/build.py basic-01
    .venv/bin/python source/video/build.py basic-01 --voice tts:qwen3 --ref .claude/loops/voice/ref/ref-13s.wav

Reads source/courses/<video>/scenes.md (or scenes-draft.md; --scenes FILE overrides), see source/video/FORMAT.md.
Writes .claude/loops/video-out/<video>/: audio/ (one wav per sentence), frames/ (one png per @ line), avatar-<hash>.mov
(the speaking avatar overlay, see avatar.py), <video>.fcpxml and <video>-rough.mp4. Audio (one clip per sentence), its word
times, frames and the mp4's pieces are cached by what made them, so a rerun makes only what changed. Timing rules: timing.py.
"""
import argparse, hashlib, json, math, os, re, shlex, subprocess, sys, tempfile, time, wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import render, fcpxml, subs, align, timing, avatar as speaker  # noqa: E402

RATE = 48000
DEFAULT_SAY_VOICE = 'Samantha'
WHISPER_PY = ROOT / '.claude/loops/tts/whisper/venv/bin/python'
TRIM_VERSION = 't1'   # bump when trim_and_pad changes, so every clip is cut again
SEG_VERSION = 's1'    # bump when the rough mp4's segments change


def die(msg):
    sys.exit(f'build.py: {msg}')


def h(*parts):
    return hashlib.sha1('\x1f'.join(str(p) for p in parts).encode()).hexdigest()[:16]


# ---------- scenes file ----------

def parse(path):
    """-> title, scenes: [dict(title, items: [('pic', spec) | ('say', text)])]"""
    title, scenes = None, []
    for no, raw in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('//'):
            continue
        if line.startswith('## '):
            scenes.append(dict(title=line[3:].strip(), items=[])); continue
        if line.startswith('# '):
            title = line[2:].strip(); continue
        if not scenes:
            scenes.append(dict(title='', items=[]))
        if line.startswith('@'):
            scenes[-1]['items'].append(('pic', pic_spec(line, no, scenes[-1]['title'])))
        else:
            text = re.sub(r'\s*\[>\]\s*', ' ', line).strip()
            if text:
                scenes[-1]['items'].append(('say', dict(text=text, line=no)))
    return title or Path(path).parent.name, scenes


def pic_spec(line, no, scene_title):
    try:
        toks = shlex.split(line[1:].strip())
    except ValueError as e:
        die(f'line {no}: cannot read the @ line ({e}): {line}')
    if not toks:
        die(f'line {no}: an @ line needs a picture id, a template or fig: {line}')
    spec = dict(line=no, raw=line, id=toks[0], kind='image', args=[], opts={}, box=None, crop=None, text='', kicker=None)
    rest = toks[1:]
    if spec['id'] in render.OPTIONS:  # a template drawn in code, or a figure
        kind = spec['kind'] = spec['id']
        allowed = render.OPTIONS[kind]
        for t in rest:
            k, eq, v = t.partition('=')
            if eq and k in allowed:
                spec['opts'][k] = v
            elif eq and re.fullmatch(r'[a-z]+', k):
                die(f'line {no}: {kind} does not take {k}= (it takes {", ".join(sorted(allowed)) or "no options"}): {line}')
            else:
                spec['args'].append(t)
        if kind == 'card':
            if not spec['args']:
                die(f'line {no}: card needs its words in quotes: {line}')
            spec['text'] = ' '.join(spec['args'])
            spec['kicker'] = spec['opts'].get('kicker', kicker_from(scene_title))
        elif kind == 'fig':
            if len(spec['args']) != 1:
                die(f'line {no}: fig wants one name (the file figs/<name>.html) and maybe step=N: {line}')
        else:
            why = render.check(spec)
            if why:
                die(f'line {no}: {why}: {line}')
        return spec
    for t in rest:
        if t.startswith(('box=', 'crop=')):
            name, _, val = t.partition('=')
            try:
                b = [float(x) for x in val.split(',')]
                assert len(b) == 4 and all(0 <= x <= 1 for x in b) and b[2] > 0 and b[3] > 0
                assert b[0] + b[2] <= 1.0001 and b[1] + b[3] <= 1.0001
            except (ValueError, AssertionError):
                die(f'line {no}: {name}= wants four numbers 0-1 (x,y,w,h) inside the image: {line}')
            spec[name] = b
        elif t.startswith('text='):
            spec['text'] = t[5:]
        else:
            die(f'line {no}: unknown part "{t}" (expected box=x,y,w,h, crop=x,y,w,h or text="..."): {line}')
    return spec


def figs_dir(scenes_path):
    """Hand-made figures: <scenes file's folder>/<scenes name>-figs/ if it exists (e.g. samples-figs/), else .../figs/."""
    own = scenes_path.parent / f'{scenes_path.stem}-figs'
    return own if own.is_dir() else scenes_path.parent / 'figs'


def kicker_from(scene_title):
    m = re.match(r'(\d+)\s+(.*)', scene_title)
    return m.group(2) if m else scene_title


def resolve(pid):
    """catalog id -> image file (rules of source/video/catalog.md)."""
    parts = pid.split('/')
    if parts[0] == 'board' and len(parts) == 2:
        p = ROOT / 'source/tutorials/img/_board' / f'{parts[1]}.png'
    elif parts[0] == 'tutorials' and len(parts) == 3:
        p = ROOT / 'source/tutorials/img' / parts[1] / f'{parts[2]}.png'
    elif len(parts) == 2 and re.fullmatch(r'p\d+', parts[1]):
        p = ROOT / 'source/video/pages' / parts[0] / f'{parts[1]}.png'
    elif pid.endswith(('.png', '.jpg', '.jpeg')):
        p = Path(pid) if pid.startswith('/') else ROOT / pid
    else:
        return None, 'not a known id form (board/<name>, tutorials/<slug>/<name>, <course>/pNN, or a path to a .png)'
    return p, None


# ---------- audio ----------

class Voice:
    """say: macOS `say`, a few clips at once. tts:<model>: source/video/tts/say.py in batch mode, the model loaded once per run."""
    def __init__(self, args):
        self.spec = args.voice
        if args.voice == 'say' or args.voice.startswith('say:'):
            self.kind = 'say'
            self.name = args.voice[4:] if args.voice.startswith('say:') else DEFAULT_SAY_VOICE
            self.rate = args.rate
            self.settings = ('say', self.name, args.rate or '')
            self.jobs = args.jobs or 4
        elif args.voice.startswith('tts:'):
            self.kind = 'tts'
            self.model = args.voice[4:]
            self.script = HERE / 'tts' / 'say.py'
            if not self.script.exists():
                die(f'--voice tts:... needs {self.script.relative_to(ROOT)}, which does not exist yet')
            self.ref = Path(args.ref).resolve()
            if not self.ref.exists():
                die(f'reference voice not found: {self.ref} (give --ref)')
            ref_txt = self.ref.with_suffix('.txt')
            self.python = args.tts_python or sys.executable
            self.seed = args.seed
            self.settings = ('tts', self.model, hashlib.sha1(self.ref.read_bytes()).hexdigest()[:16],
                             ref_txt.read_text(encoding='utf-8').strip() if ref_txt.exists() else '', self.seed)
            sys.path.insert(0, str(self.script.parent))
            import say as tts_say
            # a checked model (vibevoice): say.py cleans and checks every take, and speaks a short line together with
            # the sentence before it (or after it, for the first) and cuts it out; that neighbour is part of the key
            base = tts_say.MODELS.get(self.model, (None, None, self.model))[2]
            self.checked = base in tts_say.CHECKED
            self.short_words = tts_say.SHORT_WORDS
            if self.checked:
                self.settings += ('checked', tts_say.CHECK_VERSION)
            # pronunciation fixes: only the text the model hears changes, the script and subtitles keep the original
            self.pron = []
            pf = self.script.parent / 'pronounce.tsv'
            if pf.exists():
                for line in pf.read_text(encoding='utf-8').splitlines():
                    if line.strip() and not line.startswith('#') and '\t' in line:
                        a, b = line.split('\t', 1)
                        self.pron.append((re.compile(r'(?<![\w-])' + re.escape(a.strip()) + r'(?![\w-])'), b.strip()))
                if self.pron:
                    self.settings += ('pron', hashlib.sha1(pf.read_bytes()).hexdigest()[:12])
        else:
            die(f'--voice must be say, say:<voice name> or tts:<model>, not {args.voice}')

    def around(self, sents, k):
        """-> (before, after): the neighbour a short sentence is spoken with (one of the two), or ('', '')."""
        if self.kind != 'tts' or not self.checked or len(sents[k]['text'].split()) >= self.short_words:
            return '', ''
        if k:
            return sents[k - 1]['text'], ''
        return '', sents[k + 1]['text'] if k + 1 < len(sents) else ''

    def spoken(self, text):
        for rx, rep in getattr(self, 'pron', []):
            text = rx.sub(rep, text)
        return text

    def key(self, text, around=('', '')):
        return h(text, *self.settings) if not any(around) else h(text, 'with', *around, *self.settings)

    def make_all(self, items):
        """items: [(text, out_wav[, (before, after)])] -> each out_wav a 48 kHz mono 16-bit wav."""
        with tempfile.TemporaryDirectory() as td:
            raws = [Path(td) / f'{i:04d}.{"aiff" if self.kind == "say" else "wav"}' for i in range(len(items))]
            if self.kind == 'say':
                def one(i):
                    txt = Path(td) / f'{i:04d}.txt'
                    txt.write_text(items[i][0], encoding='utf-8')
                    cmd = ['say', '-v', self.name] + (['-r', str(self.rate)] if self.rate else []) + ['-o', str(raws[i]), '-f', str(txt)]
                    r = subprocess.run(cmd, capture_output=True, text=True)
                    if r.returncode:
                        die(f'say failed for "{items[i][0][:60]}": {r.stderr.strip()[-400:]}')
                with ThreadPoolExecutor(self.jobs) as ex:
                    list(ex.map(one, range(len(items))))
            else:
                batch = Path(td) / 'lines.tsv'
                batch.write_text(''.join(f'{raws[i]}\t{self.spoken(it[0])}' + (f'\t{self.spoken(it[2][0])}\t{self.spoken(it[2][1])}' if len(it) > 2 and any(it[2]) else '')
                                         + '\n' for i, it in enumerate(items)), encoding='utf-8')
                r = subprocess.run([self.python, str(self.script), '--model', self.model, '--ref', str(self.ref),
                                    '--seed', str(self.seed), '--batch', str(batch)])
                if r.returncode:
                    die(f'tts/say.py failed (exit {r.returncode})')
            for raw, (text, out_wav, *_) in zip(raws, items):
                if not raw.exists():
                    die(f'the voice made no audio for "{text[:60]}"')
                tmp = Path(str(out_wav) + '.part.wav')
                ff = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-ar', str(RATE), '-ac', '1',
                                     '-c:a', 'pcm_s16le', str(tmp)], capture_output=True, text=True)
                if ff.returncode:
                    die(f'ffmpeg could not convert the voice output: {ff.stderr.strip()[-400:]}')
                tmp.replace(out_wav)


def probe_seconds(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def trim_and_pad(src, dst, fps, head=0.06, tail=0.15):
    """Copy a 48 kHz mono wav cut to its voice (by loudness, keeping `head` and `tail` seconds of what is around it, so no
    word is cut), padded with silence to a whole number of frames, so every time in the timeline is exact.
    -> (frames, vs, ve): the clip's length, and where the voice starts and ends in it (seconds)."""
    import audioop, warnings
    with wave.open(str(src)) as w:
        data, n = w.readframes(w.getnframes()), w.getnframes()
    hop = RATE // 100  # 10 ms
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        db = [20 * math.log10(max(audioop.rms(data[i:i + 2 * hop], 2), 1) / 32768) for i in range(0, len(data), 2 * hop)]
    thr = max(max(db, default=-90) - 40, -55)
    loud = [i for i, d in enumerate(db) if d > thr]
    if loud:
        v0, v1 = loud[0] * hop, min(n, (loud[-1] + 1) * hop)
    else:
        v0, v1 = 0, n
    a, b = max(0, v0 - round(head * RATE)), min(n, v1 + round(tail * RATE))
    data = data[2 * a:2 * b]
    m = b - a
    spf = RATE // fps
    frames = max(1, math.ceil(m / spf))
    data += b'\0\0' * (frames * spf - m)
    with wave.open(str(dst), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(data)
    return frames, round((v0 - a) / RATE, 4), round((v1 - a) / RATE, 4)


def join_sentences(lines):
    """Spoken lines -> sentences: consecutive lines of one scene, joined until a line ends with . ? or ! (or the scene ends).
    Each sentence is one audio clip; its lines still say where the pictures change."""
    out = []
    for g, ln in enumerate(lines):
        if not out or out[-1]['closed'] or out[-1]['scene'] != ln['scene']:
            out.append(dict(scene=ln['scene'], lines=[], closed=False))
        out[-1]['lines'].append(g)
        out[-1]['closed'] = bool(re.search(r'[.?!]["\'”’)\]]*$', ln['text']))
    for s in out:
        s['text'] = ' '.join(lines[g]['text'] for g in s['lines'])
        s['line'] = lines[s['lines'][0]]['line']
    return out


def busy(spec):
    """A picture that takes longer to look at: a screenshot or page, a list showing 4+ items, a quote, or a figure that
    shows 30 or more words at its step."""
    k = spec.get('kind')
    if k == 'image':
        return True
    if k == 'quote':
        return True
    if k == 'list':
        lit = spec['opts'].get('lit')
        return (int(lit) if lit and lit.isdigit() else len(spec['args']) - 1) >= 4
    if k == 'fig' and spec.get('src') and Path(spec['src']).exists():
        return fig_words(Path(spec['src']).read_text(encoding='utf-8'), spec['opts'].get('step')) >= 30
    return False


def fig_words(page, step):
    """Words a figure page shows at a step: text outside <style>/<script> and outside elements with data-step > step."""
    from html.parser import HTMLParser
    n = int(step) if step and str(step).isdigit() else None
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr',
            'path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'ellipse', 'use', 'stop'}

    class P(HTMLParser):
        def __init__(self):
            super().__init__(); self.stack, self.words = [], 0

        def handle_starttag(self, tag, attrs):
            if tag in void:
                return
            a = dict(attrs)
            hide = tag in ('style', 'script', 'head') or (n is not None and (a.get('data-step') or '').isdigit()
                                                         and int(a['data-step']) > n)
            self.stack.append((tag, hide))

        def handle_startendtag(self, tag, attrs):
            pass

        def handle_endtag(self, tag):
            if tag in void:
                return
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]; break

        def handle_data(self, d):
            if not any(h for _, h in self.stack):
                self.words += len(re.findall(r'[A-Za-z0-9]+', d))
    p = P(); p.feed(page)
    return p.words


def group_of(spec):
    """Pictures in one group are steps of one build: the same figure at another step=, or the same list, loop, timeline
    or formula with another lit= / now=."""
    k = spec.get('kind')
    if k == 'fig':
        return ('fig', spec['args'][0])
    if k in ('list', 'loop', 'timeline', 'formula'):
        return (k,) + tuple(spec['args'])
    return None


def align_all(sents, adir, args):
    """Word times for each sentence clip, cached under the clip's own hash (and the model). -> how many were made."""
    tag = h(args.whisper_model)[:6]
    for s in sents:
        s['align'] = adir / 'align' / f'{hashlib.sha1(s["wav"].read_bytes()).hexdigest()[:16]}-{tag}.json'
    todo = {str(s['align']): s for s in sents if not s['align'].exists()}
    if todo and not Path(args.whisper_python).exists():
        print(f'  note: no {args.whisper_python}; pictures inside a sentence are placed by character count '
              f'(install: python3 -m venv .claude/loops/tts/whisper/venv && .claude/loops/tts/whisper/venv/bin/pip install mlx-whisper)')
        return 0
    if todo:
        (adir / 'align').mkdir(exist_ok=True)
        print(f'aligning {len(todo)} clip(s) with {args.whisper_model} ...', flush=True)
        with tempfile.TemporaryDirectory() as td:
            jobs = Path(td) / 'jobs.json'
            jobs.write_text(json.dumps([dict(wav=str(s['wav']), text=s['text'], out=o) for o, s in todo.items()]), encoding='utf-8')
            r = subprocess.run([args.whisper_python, str(HERE / 'align.py'), '--model', args.whisper_model, '--batch', str(jobs)])
            if r.returncode:
                print(f'  note: align.py failed (exit {r.returncode}); the clips it did not do are placed by character count')
    return len(todo)


# ---------- build ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', help='folder name under source/courses/, e.g. basic-01')
    ap.add_argument('--scenes', help='scenes file to read instead of source/courses/<video>/scenes.md')
    ap.add_argument('--voice', default='tts:vibevoice', help='say (macOS, Samantha), say:<voice>, or tts:<model> (source/video/tts/say.py)')
    ap.add_argument('--rate', type=int, help='say only: words per minute')
    ap.add_argument('--ref', default=str(ROOT / '.claude/loops/voice/ref/ref-13s.wav'),
                    help='tts only: reference voice wav; its words in the .txt next to it')
    ap.add_argument('--seed', type=int, default=1, help='tts only: seed passed to tts/say.py')
    ap.add_argument('--tts-python', help='tts only: python that runs tts/say.py (default: this one)')
    ap.add_argument('--jobs', type=int, help='say only: clips made at once (default 4)')
    R = timing.Rules()
    ap.add_argument('--gap', type=float, default=R.gap, help='seconds of silence between sentences on the same picture')
    ap.add_argument('--dwell', type=float, default=R.dwell, help='when the picture changes between sentences: seconds the '
                    'outgoing picture stays after the words end, before the next one fades in')
    ap.add_argument('--busy', type=float, default=R.busy, help='seconds added to --dwell when the outgoing picture is busy '
                    '(a screenshot, a list of 4+ items, a figure with many words)')
    ap.add_argument('--scene-gap', type=float, default=R.scene_gap, help='seconds of silence between scenes (at least dwell + lead)')
    ap.add_argument('--lead', type=float, default=R.lead, help='a new picture starts fading in this many seconds before its first word')
    ap.add_argument('--min-hold', type=float, default=R.min_hold, help='a picture stays at least this many seconds; shorter beats are merged')
    ap.add_argument('--xfade', type=float, default=R.xfade, help='cross-dissolve seconds between different pictures (0: cut)')
    ap.add_argument('--step-xfade', type=float, default=R.step_xfade, help='cross-dissolve seconds between steps of one figure or list')
    ap.add_argument('--head', type=float, default=R.head, help='seconds before the first word')
    ap.add_argument('--tail', type=float, default=R.tail, help='seconds the last picture stays after the last word')
    ap.add_argument('--whisper-python', default=str(WHISPER_PY), help='python of the venv with mlx-whisper (word times); '
                    'if it is missing, pictures inside a sentence are placed by character count')
    ap.add_argument('--whisper-model', default=align.DEFAULT_MODEL, help='mlx-whisper model (Hugging Face id or folder)')
    ap.add_argument('--fps', type=int, default=25, choices=[25, 30, 50, 60])
    ap.add_argument('--fcpxml-version', default='1.10', choices=['1.10', '1.11'])
    ap.add_argument('--no-mp4', action='store_true', help='skip the rough mp4')
    ap.add_argument('--subs', default='en', help='subtitle languages, comma-separated, e.g. en,zh. en is the spoken text; '
                    'another language <xx> reads source/courses/<video>/subs.<xx>.txt, one line per spoken line. '
                    'The first is burned into the mp4. Empty: no subtitles')
    ap.add_argument('--no-burn', action='store_true', help='do not burn subtitles into the rough mp4')
    ap.add_argument('--frames-only', action='store_true', help='draw the pictures only (every @ line, no audio, no timeline) '
                    'and copy them in order to <out>/<video>/NN-<line>.png, to look at a new look or template')
    ap.add_argument('--theme', default='dark', choices=sorted(render.THEMES), help='background: dark (grey) or navy (smarshu.com)')
    ap.add_argument('--avatar', help='round picture bottom right (default .claude/loops/voice/avatar.jpg or .png, '
                    'else the smarshu.com portrait); none: no avatar. It is a speaking overlay video over the stills '
                    '(glow follows the voice), except with --avatar-static or --frames-only, where it is drawn into each still')
    ap.add_argument('--avatar-static', action='store_true', help='draw the avatar into each still, no speaking overlay')
    ap.add_argument('--timing-json', help='also write the timeline (sentences, pictures, merges) to this file, to check it')
    ap.add_argument('--out', default=str(ROOT / '.claude/loops/video-out'), help='output root')
    args = ap.parse_args()
    t0 = time.time()

    if args.scenes:
        scenes_path = Path(args.scenes).resolve()
    else:
        d = ROOT / 'source/courses' / args.video
        scenes_path = next((p for p in (d / 'scenes.md', d / 'scenes-draft.md') if p.exists()), None)
        if not scenes_path:
            die(f'no scenes.md or scenes-draft.md in {d.relative_to(ROOT)} (or give --scenes FILE)')
    if not scenes_path.exists():
        die(f'scenes file not found: {scenes_path}')
    title, scenes = parse(scenes_path)

    out = Path(args.out) / args.video
    adir, fdir = out / 'audio', out / 'frames'
    fdir.mkdir(parents=True, exist_ok=True)
    if not args.frames_only:
        adir.mkdir(parents=True, exist_ok=True)
    fps = args.fps

    # 1. pictures: resolve every id first, so a missing image fails before anything is made
    missing = []
    pics = []  # every @ line in order, with its scene index and the index of the sentence it starts at
    n_sent = 0
    sentences = []
    for si, sc in enumerate(scenes):
        for kind, it in sc['items']:
            if kind == 'pic':
                if it['kind'] == 'fig':
                    src = figs_dir(scenes_path) / f'{it["args"][0]}.html'
                    if not src.exists():
                        missing.append(f'  line {it["line"]}: fig {it["args"][0]} -> {src.relative_to(ROOT) if src.is_relative_to(ROOT) else src} is missing')
                    it['src'] = src
                elif it['kind'] == 'image':
                    src, why = resolve(it['id'])
                    if why:
                        missing.append(f'  line {it["line"]}: {it["id"]}: {why}')
                    elif not src.exists():
                        missing.append(f'  line {it["line"]}: {it["id"]} -> {src.relative_to(ROOT) if src.is_relative_to(ROOT) else src} is missing')
                    it['src'] = src
                pics.append(dict(spec=it, scene=si, at=n_sent))
            else:
                sentences.append(dict(text=it['text'], line=it['line'], scene=si))
                n_sent += 1
    if missing:
        die('pictures not found:\n' + '\n'.join(missing))
    if not sentences and not args.frames_only:
        die('the scenes file has no sentences')

    # a picture shows from the sentence after it; two @ lines with no sentence between: the earlier one never shows
    by_start = {}
    for p in pics:
        if p['at'] >= len(sentences):
            print(f'  note: line {p["spec"]["line"]}: the @ line has no sentence after it, so it never shows')
            continue
        if p['at'] in by_start:
            print(f'  note: line {by_start[p["at"]]["spec"]["line"]}: replaced by the @ on line {p["spec"]["line"]} before any sentence')
        by_start[p['at']] = p
    if 0 not in by_start:  # sentences before the first @: show the video's title
        by_start[0] = dict(spec=dict(id='card', text=title, kicker='', raw=f'@ card "{title}"', line=0), scene=0, at=0)
    shown = [by_start[k] for k in sorted(by_start)]

    made_f, reused_f = [], []
    avatar = None if args.avatar == 'none' else Path(args.avatar).resolve() if args.avatar else render.default_avatar()
    if avatar and not avatar.exists():
        die(f'--avatar {avatar} does not exist')
    still_avatar = avatar if (args.avatar_static or args.frames_only) else None  # else the overlay video carries it
    todo_f = []
    for p in (pics if args.frames_only else shown):
        s = p['spec']
        s.setdefault('kind', 'card')  # the title card made above
        s.setdefault('args', [s.get('text', '')]); s.setdefault('opts', {})
        p['frame'] = fdir / f'{h(render.inputs(s, args.theme, still_avatar))}.png'
        p['name'] = (s['id'] if s['kind'] != 'card' else 'card ' + s['text'])[:60]
        if p['frame'].exists() or any(q['frame'] == p['frame'] for q in todo_f):  # drawn before, or twice in this file
            reused_f.append(p); continue
        todo_f.append(p)
    try:  # one browser for all of them
        render.render([(p['spec'], p['frame'].with_suffix('.part.png')) for p in todo_f], theme=args.theme, avatar=still_avatar)
    except RuntimeError as e:
        die(str(e))
    for p in todo_f:
        p['frame'].with_suffix('.part.png').replace(p['frame'])
        made_f.append(p)
    if args.frames_only:  # every @ line once, in order, under readable names next to frames/
        for f in out.glob('[0-9][0-9]-*.png'):
            f.unlink()
        for i, p in enumerate(pics, 1):
            slug = re.sub(r'[^a-z0-9]+', '-', p['spec']['raw'][1:].lower()).strip('-')[:40]
            (out / f'{i:02d}-{slug}.png').write_bytes(p['frame'].read_bytes())
        print(f'frames: {len(made_f)} made, {len(reused_f)} reused; {len(pics)} pictures in {out}')
        return

    # 2. audio: one clip per sentence (spoken lines joined until . ? !), cached by (sentence text, voice settings)
    lines = sentences  # the spoken lines of the scenes file; they say where pictures change
    sents = join_sentences(lines)
    voice = Voice(args)
    for k, s in enumerate(sents):
        s['around'] = voice.around(sents, k)
        s['key'] = voice.key(s['text'], s['around'])
        s['raw'] = adir / f'{s["key"]}.wav'
        s['wav'] = adir / f'{s["key"]}-{fps}p.wav'
    todo, seen = [], set()
    for s in sents:
        if not s['raw'].exists() and s['key'] not in seen:
            todo.append(s); seen.add(s['key'])
    if todo:
        print(f'making {len(todo)} audio clip(s) with {voice.spec} ...', flush=True)
        voice.make_all([(s['text'], s['raw'], s['around']) for s in todo])
    made_keys = {s['key'] for s in todo}

    meta_path = adir / 'durations.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for s in sents:
        k = f'{s["key"]}-{fps}-{TRIM_VERSION}'
        if s['key'] in made_keys or k not in meta or not s['wav'].exists():
            meta[k] = trim_and_pad(s['raw'], s['wav'], fps)
        s['frames'], s['vs'], s['ve'] = meta[k]
    meta_path.write_text(json.dumps(meta, indent=0, sort_keys=True))

    # word times: where each line of a sentence starts in its clip
    n_aligned = align_all(sents, adir, args)
    hows = {'aligned': 0, 'interpolated': 0, 'proportional': 0}
    inner = dict(word=0, interpolated=0, proportional=0)  # line starts inside sentences
    for s in sents:
        words = None
        if s['align'].exists():
            words = json.loads(s['align'].read_text(encoding='utf-8')).get('words')
        texts = [lines[g]['text'] for g in s['lines']]
        s['starts'], s['how'], s['matched'] = align.line_times(texts, words, s['vs'], s['ve'])
        hows[s['how']] += 1
        if len(texts) > 1:
            key = 'proportional' if s['how'] == 'proportional' else None
            for j in range(1, len(texts)):
                inner[key or ('word' if s['how'] == 'aligned' else 'interpolated')] += 1
    # (interpolated counts every inner line of a sentence with at least one interpolated start; good enough to report)

    # 3. timeline, in frames: the timing rules are in timing.py
    rules = timing.Rules(fps=fps, gap=args.gap, dwell=args.dwell, busy=args.busy, scene_gap=args.scene_gap, lead=args.lead,
                         min_hold=args.min_hold, head=args.head, tail=args.tail, xfade=args.xfade, step_xfade=args.step_xfade)
    for p in shown:
        p['busy'] = busy(p['spec'])
        p['group'] = group_of(p['spec'])
        p['scene'] = lines[p['at']]['scene']
    shown, lay, merges, still_short = timing.merge(sents, shown, rules)
    trans, E = timing.transitions(shown, lay, rules)
    total = lay['total']
    for k, s in enumerate(sents):
        s['start'] = lay['T'][k]
    for j, p in enumerate(shown):
        p['start'] = E[j]
        p['dur'] = (E[j + 1] if j + 1 < len(shown) else total) - E[j]
        p['xfade'] = trans[j][0] if j else 0

    # 4. outputs, only when the timeline changed
    clips = [dict(path=s['wav'], name=f'{i + 1:03d} {s["text"][:50]}', start=s['start'], dur=s['frames'])
             for i, s in enumerate(sents)]
    frames = [dict(path=p['frame'], name=p['name'], start=p['start'], dur=p['dur'], xfade=p['xfade']) for p in shown]
    # subtitles: one cue per spoken line, from the word its line starts with to the next line's (the last one of a
    # sentence: to a moment after the words end); long lines split into cues in a row
    l_start, l_dur = [0] * len(lines), [0] * len(lines)
    for k, s in enumerate(sents):
        nxt = sents[k + 1]['start'] + round(sents[k + 1]['vs'] * fps) if k + 1 < len(sents) else total
        st = [s['start'] + round(x * fps) for x in s['starts']]
        end_last = min(s['start'] + round((s['ve'] + 0.4) * fps), nxt)
        for j, g in enumerate(s['lines']):
            l_start[g] = st[j]
            l_dur[g] = max(1, (st[j + 1] if j + 1 < len(st) else end_last) - st[j])
    captions = []
    for lang in [x.strip() for x in args.subs.split(',') if x.strip()]:
        if lang == 'en':
            texts = [s['text'] for s in lines]
        else:
            src = (scenes_path.parent if args.scenes else ROOT / 'source/courses' / args.video) / f'subs.{lang}.txt'
            if not src.exists():
                die(f'--subs {lang} needs {src} (one line per spoken line, {len(lines)} lines)')
            texts = [x.strip() for x in src.read_text(encoding='utf-8').splitlines() if x.strip()]
            if len(texts) != len(lines):
                die(f'{src.name} has {len(texts)} lines, but the scenes file has {len(lines)} spoken lines')
        captions.append((lang, subs.cues(texts, l_start, l_dur)))
    made_subs = []
    for lang, cl in captions:
        f = out / f'{args.video}.{lang}.srt'
        body = subs.srt(cl, fps)
        if not f.exists() or f.read_text(encoding='utf-8') != body:
            f.write_text(body, encoding='utf-8'); made_subs.append(f.name)
    burn = captions[0][1] if captions and not args.no_burn else None

    tl = json.dumps([[(str(c['path']), c['start'], c['dur']) for c in clips],
                     [(str(f['path']), f['start'], f['dur'], f['xfade']) for f in frames], title, fps, total])
    # the speaking avatar: one overlay video for the whole timeline, made again only when the audio, its times or the avatar change
    overlay, made_ov = None, []
    if avatar and not still_avatar:
        ok = h(speaker.STYLE, avatar, avatar.stat().st_mtime, fps, total, json.dumps([(str(c['path']), c['start']) for c in clips]))
        ov = out / f'avatar-{ok}.mov'
        if not ov.exists() or not speaker.preview_path(ov).exists():
            t1 = time.time()
            try:
                info = speaker.make(ov, track=mix(clips, total, fps), rate=RATE, fps=fps, total=total,
                                    sentence_starts=[c['start'] + round(s['vs'] * fps) for c, s in zip(clips, sents)],
                                    avatar_path=avatar)
            except RuntimeError as e:
                die(str(e))
            made_ov.append(f'{ov.name} ({info["onsets"]} ripples, {ov.stat().st_size / 1e6:.1f} MB, {time.time() - t1:.1f} s)')
        overlay = dict(path=ov, size=speaker.SIZE, centre=speaker.CENTRE)
    sig = h(tl, args.fcpxml_version, json.dumps(captions), overlay and str(overlay['path']), fcpxml.VERSION)
    sig_mp4 = h(tl, json.dumps(burn), subs.ass([], fps, render.W, render.H), overlay and str(overlay['path']), SEG_VERSION)
    fx, mp4 = out / f'{args.video}.fcpxml', out / f'{args.video}-rough.mp4'
    state_path = out / 'build-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    made_out = made_subs[:] + made_ov
    if state.get('fcpxml') != sig or not fx.exists():
        fcpxml.write(fx, title=title, event=f'{args.video} (video pipeline)', fps=fps, width=render.W, height=render.H,
                     pictures=frames, clips=clips, total=total, version=args.fcpxml_version, captions=captions,
                     overlay=overlay)
        state['fcpxml'] = sig; made_out.append(fx.name)
    made_segs = 0
    if not args.no_mp4 and (state.get('mp4') != sig_mp4 or not mp4.exists()):
        made_segs = rough(mp4, frames, clips, total, fps, out, burn, overlay)
        state['mp4'] = sig_mp4; made_out.append(f'{mp4.name} ({made_segs} segments made)')
    state_path.write_text(json.dumps(state, indent=1))

    # 5. report
    sec = lambda f: f / fps
    print(f'\n{title}  ({scenes_path.relative_to(ROOT) if scenes_path.is_relative_to(ROOT) else scenes_path})')
    print(f'{"scene":<40} {"lines":>5} {"sentences":>9} {"start":>7} {"seconds":>8}')
    for si, sc in enumerate(scenes):
        ss = [s for s in sents if s['scene'] == si]
        if not ss:
            continue
        nxt = next((s['start'] for s in sents if s['scene'] > si), total)
        print(f'{sc["title"][:40]:<40} {sum(len(s["lines"]) for s in ss):>5} {len(ss):>9} {sec(ss[0]["start"]):>7.1f} '
              f'{sec(nxt - ss[0]["start"]):>8.1f}')
    print(f'{"total":<40} {len(lines):>5} {len(sents):>9} {"":>7} {sec(total):>8.1f}')
    n_audio = len({s['key'] for s in sents})
    print(f'\naudio:  {len(made_keys)} sentence clip(s) made, {n_audio - len(made_keys)} reused')
    for s in todo[:10]:
        print(f'  made  line {s["line"]}: {s["text"][:70]}')
    if len(todo) > 10:
        print(f'  ... and {len(todo) - 10} more')
    multi = sum(1 for s in sents if len(s['lines']) > 1)
    print(f'words:  {n_aligned} clip(s) aligned now; {multi} sentences have a picture or cue change inside: '
          f'{inner["word"]} line starts on a matched word, {inner["interpolated"]} in sentences with some interpolated '
          f'starts, {inner["proportional"]} by character count ({hows["proportional"]} sentence(s) fell back)')
    for s in sents:
        if s['how'] != 'aligned' and len(s['lines']) > 1:
            print(f'  {s["how"]:<12} line {s["line"]} ({s["matched"]:.0%} of words matched): {s["text"][:70]}')
    holds = lay['hold']
    print(f'pictures: {len(shown)} shown, shortest hold {sec(min(holds)):.2f} s (min {args.min_hold} s), '
          f'{sum(1 for t in trans[1:] if t[1] == "dissolve")} dissolves, {sum(1 for t in trans[1:] if t[1] == "step")} step dissolves')
    for p, kept, secs, how in merges:
        print(f'  merged line {p["spec"]["line"]} ({p["spec"]["raw"][2:50]}, {secs:.2f} s): {how} (line {kept["spec"]["line"]})')
    for p, secs in still_short:
        print(f'  short  line {p["spec"]["line"]} ({p["spec"]["raw"][2:50]}): {secs:.2f} s, nothing in its scene to merge with')
    print(f'frames: {len(made_f)} made, {len(reused_f)} reused')
    for p in made_f[:10]:
        print(f'  made  line {p["spec"]["line"]}: {p["spec"]["raw"][:70]}')
    if len(made_f) > 10:
        print(f'  ... and {len(made_f) - 10} more')
    print(f'timeline: {"rebuilt " + ", ".join(made_out) if made_out else "unchanged, srt, fcpxml and mp4 reused"}')
    print(f'out: {out}')
    print(f'done in {time.time() - t0:.1f} s')
    if args.timing_json:
        Path(args.timing_json).write_text(json.dumps(dict(
            fps=fps, total=total,
            sentences=[dict(line=s['line'], text=s['text'], start=s['start'], frames=s['frames'], vs=s['vs'], ve=s['ve'],
                            starts=s['starts'], how=s['how'], lines=[lines[g]['line'] for g in s['lines']]) for s in sents],
            pictures=[dict(line=p['spec']['line'], raw=p['spec']['raw'], fade_in=lay['F'][j], start=p['start'], dur=p['dur'],
                           hold=lay['hold'][j], xfade=p['xfade'], busy=p['busy']) for j, p in enumerate(shown)],
            merges=[dict(line=p['spec']['line'], into=kept['spec']['line'], seconds=secs, how=how) for p, kept, secs, how in merges],
        ), indent=1), encoding='utf-8')


def mix(clips, total, fps):
    """The whole timeline's audio: 16-bit mono PCM at RATE, each clip at its start."""
    spf = RATE // fps
    track = bytearray(total * spf * 2)
    for c in clips:
        with wave.open(str(c['path'])) as w:
            data = w.readframes(w.getnframes())
        at = c['start'] * spf * 2
        track[at:at + len(data)] = data
    return bytes(track)


def segments(frames, total):
    """The picture track as pieces: [('hold', png, n) | ('fade', png_from, png_to, n)], n frames each, in order.
    A dissolve of d frames is centred on its edit point."""
    out, t = [], 0
    for j, f in enumerate(frames):
        d_in = f['xfade'] if j else 0
        nxt = frames[j + 1] if j + 1 < len(frames) else None
        d_out = nxt['xfade'] if nxt else 0
        if d_in:
            out.append(('fade', str(frames[j - 1]['path']), str(f['path']), d_in)); t += d_in
        end = (nxt['start'] - d_out // 2) if nxt else total
        if end > t:
            out.append(('hold', str(f['path']), end - t)); t = end
    assert t == total, (t, total)
    return out


def segment(seg, dst, fps):
    """One piece of the picture track as a small H.264 file (no B-frames, so the pieces join exactly)."""
    enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-tune', 'stillimage', '-bf', '0', '-pix_fmt', 'yuv420p',
           '-r', str(fps), '-video_track_timescale', str(fps * 1000)]
    if seg[0] == 'hold':
        _, a, n = seg
        cmd = ['-loop', '1', '-framerate', str(fps), '-i', a, '-vf', 'format=yuv420p', '-frames:v', str(n)]
    else:
        _, a, b, n = seg
        d = n / fps
        cmd = ['-loop', '1', '-framerate', str(fps), '-t', f'{d + 1:.3f}', '-i', a,
               '-loop', '1', '-framerate', str(fps), '-t', f'{d + 1:.3f}', '-i', b,
               '-filter_complex', f'[0:v]format=yuv444p,settb=1/{fps}[a];[1:v]format=yuv444p,settb=1/{fps}[b];'
                                  f'[a][b]xfade=transition=fade:duration={d:.4f}:offset=0,format=yuv420p[v]',
               '-map', '[v]', '-frames:v', str(n)]
    tmp = dst.with_suffix('.part.mp4')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *cmd, *enc, str(tmp)], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f'ffmpeg could not make a segment of the rough mp4: {r.stderr.strip()[-600:]}')
    tmp.replace(dst)


def rough(mp4, frames, clips, total, fps, out, burn=None, overlay=None):
    """Stills with cross-dissolves plus one audio track: a quick check that words and pictures line up.
    The picture track is made of small pieces (a still held, or a dissolve between two), each cached by what it shows
    and how long, then joined and laid under the avatar and the subtitles in one pass. -> pieces made."""
    track = mix(clips, total, fps)
    sdir = out / 'segments'
    sdir.mkdir(exist_ok=True)
    segs = segments(frames, total)
    files = [sdir / f'{h(SEG_VERSION, fps, *s)}.mp4' for s in segs]
    todo = {str(f): s for f, s in zip(files, segs) if not f.exists()}
    if todo:
        try:
            with ThreadPoolExecutor(6) as ex:
                list(ex.map(lambda kv: segment(kv[1], Path(kv[0]), fps), todo.items()))
        except RuntimeError as e:
            die(str(e))
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / 'track.wav'
        with wave.open(str(wav), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(bytes(track))
        lst = Path(td) / 'pieces.txt'
        lst.write_text(''.join(f"file '{f}'\n" for f in files), encoding='utf-8')
        ins = ['-f', 'concat', '-safe', '0', '-i', str(lst)]
        graph, n = [f'[0:v]setpts=N/({fps}*TB),format=yuv420p' + ('[s]' if overlay else '[c]' if burn else '[v]')], 1
        if overlay:  # the speaking avatar over the stills, its centre where the static one was (from its colour|alpha preview)
            ins += ['-i', str(speaker.preview_path(overlay['path']))]
            z = overlay['size']
            x, y = overlay['centre'][0] - z // 2, overlay['centre'][1] - z // 2
            graph.append(f'[{n}:v]split[o1][o2];[o1]crop={z}:{z}:0:0[oc];[o2]crop={z}:{z}:{z}:0,format=gray[oa];'
                         f'[oc][oa]alphamerge[ov];[s][ov]overlay=x={x}:y={y}:format=auto,format=yuv420p' + ('[c]' if burn else '[v]'))
            n += 1
        if burn:  # subtitles drawn by libass from an .ass file sized for 1080p
            ass = Path(td) / 'subs.ass'
            ass.write_text(subs.ass(burn, fps, render.W, render.H), encoding='utf-8')
            graph.append(f"[c]ass='{ass}':fontsdir='{render.FONTS}'[v]")
        tmp = mp4.with_suffix('.part.mp4')
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-i', str(wav), '-filter_complex', ';'.join(graph),
                            '-map', '[v]', '-map', f'{n}:a', '-r', str(fps), '-frames:v', str(total),
                            '-c:v', 'libx264', '-preset', 'veryfast',
                            '-tune', 'stillimage', '-crf', '26', '-c:a', 'aac', '-b:a', '128k',
                            '-movflags', '+faststart', str(tmp)], capture_output=True, text=True)
        if r.returncode:
            die(f'ffmpeg could not make the rough mp4: {r.stderr.strip()[-600:]}')
        tmp.replace(mp4)
    return len(todo)


if __name__ == '__main__':
    main()
