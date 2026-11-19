#!/usr/bin/env python3
"""Build a tutorial video's audio, frames, Final Cut Pro timeline and rough mp4 from its scenes file.

    .venv/bin/python source/video/build.py basic-01
    .venv/bin/python source/video/build.py basic-01 --voice tts:qwen3 --ref .claude/loops/voice/ref/ref-13s.wav
    .venv/bin/python source/video/build.py basic-01 --voice rec               # the author's own takes, see below
    .venv/bin/python source/video/build.py basic-01 --rec-status              # which sentences are recorded
    .venv/bin/python source/video/build.py basic-01 --list-sentences          # the sentences as JSON, for the recorder
    .venv/bin/python source/video/build.py basic-01 --check-take <id>         # one take checked, JSON

Reads source/courses/<video>/scenes.md (or scenes-draft.md; --scenes FILE overrides), see source/video/FORMAT.md.
Writes .claude/loops/video-out/<video>/: audio/ (one wav per paragraph, and its sentences cut out of it), frames/ (one png
per @ line), avatar-<hash>.mov (the speaking avatar overlay, see avatar.py), <video>.fcpxml and <video>-rough.mp4. Audio
(one clip per paragraph), its word times, frames and the mp4's pieces are cached by what made them, so a rerun makes only
what changed. Timing rules: timing.py.

Recorded voice (--voice rec): one take per sentence in .claude/loops/voice/rec/<video>/<id>.wav, id = the first 12 hex
of the sha1 of the sentence's text (as --list-sentences prints it). Each take is polished (rec.py: fillers, repeats and
a false start cut, DeepFilterNet denoise, high-pass, level, gentle compression, de-ess, long pauses shortened, cut to its
voice); a paragraph's takes are joined --rec-gap apart over their room tone and go on like a spoken paragraph clip
(loudness, word times, cut into sentences, timeline). A new take makes only its paragraph again. Missing takes stop the
build, unless --rec-missing tts. --check-take <id> checks one take for the recording pane (JSON). See FORMAT.md,
Recorded voice.
"""
import argparse, array, hashlib, json, math, os, re, shlex, subprocess, sys, tempfile, time, wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import render, fcpxml, subs, align, timing, rec, avatar as speaker  # noqa: E402

RATE = 48000
DEFAULT_SAY_VOICE = 'Samantha'
DEFAULT_VOICE = 'tts:kokoro-seedvc'
WHISPER_PY = ROOT / '.claude/loops/tts/whisper/venv/bin/python'
TRIM_VERSION = 't1'   # bump when trim_and_pad changes, so every clip is cut again
SEG_VERSION = 's1'    # bump when the rough mp4's segments change
LOUDNESS, PEAK = -18.0, -1.5   # every paragraph clip is set to this integrated loudness (LUFS), true peak at most PEAK dBTP
LOUD_VERSION = 'n1'   # bump when normalise changes, so every clip is normalised again (no voice made again)
CPS = 16.0            # letters per second the voice speaks (Kokoro am_fenrir: 16 to 17), to keep a clip under --para-max
# --voice rec: the author's own takes, one wav per sentence, in REC_DIR/<video>/<id>.wav (FORMAT.md, Recorded voice;
# rec.py has the steps)
REC_DIR = ROOT / '.claude/loops/voice/rec'
DF_PY = ROOT / '.claude/loops/tts/deepfilter/venv/bin/python'   # DeepFilterNet, see denoise.py
DF_ATTEN = 12         # dB DeepFilterNet takes off at most: gentle (the voice changed by 0.1 to 0.2 dB in each band)
# the fallback (--rec-denoise afftdn, or no DeepFilterNet): nr=8 takes 4-5 dB off a -65 dBFS room tone, the voice
# unchanged, the room tone left a steady hiss (nr=20 makes it warble)
AFFTDN = 'afftdn=nr=8:nf=-55:tn=1'
REC_LEVEL = -20.0     # each take is set to this loudness (LUFS) before compression, so takes made on other days match
# after the denoise: rumble off, the level, a gentle compressor (2:1 above -18 dB, 6 dB knee: only the loud words), and
# a de-esser to take back the s the compressor brings forward (measured on say-made takes, each band 80 Hz-16 kHz within
# -0.1 to +1.1 dB of the take; 2.5:1 above -24 dB lifted 3-16 kHz by 2.5 to 4.5 dB, which a de-esser at 0.3 did not undo)
REC_DYN = ('highpass=f=80,'
           # de-plosive: a short low-frequency burst (a 'p' or 'b' hitting the mic) is pulled down by up to 12 dB; voice above 300 Hz unchanged
           'adynamicequalizer=dfrequency=120:dftype=lowpass:tfrequency=150:tftype=lowshelf:mode=cutabove:attack=1:release=80:ratio=4:range=12:auto=adaptive,'
           'volume={gain}dB,acompressor=threshold=-18dB:ratio=2:attack=15:release=200:knee=6,'
           'deesser=i=0.4')
REC_HEAD, REC_TAIL = 0.08, 0.15   # seconds kept before and after the voice of each take
REC_VERSION = 'r2'    # bump when the polish changes (here or in rec.py), so every take is polished again


def die(msg):
    sys.exit(f'build.py: {msg}')


def h(*parts):
    return hashlib.sha1('\x1f'.join(str(p) for p in parts).encode()).hexdigest()[:16]


# ---------- scenes file ----------

def parse(path):
    """-> title, scenes: [dict(title, items: [('pic', spec) | ('say', dict(text, line, brk))])]; brk: a blank line comes
    between this spoken line and the one before it (a paragraph break; @ lines do not break, a scene heading does)."""
    title, scenes = None, []
    blank = False  # a blank line since the last spoken line: the next spoken line starts a paragraph
    for no, raw in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if not line:
            blank = True; continue
        if line.startswith('//'):
            continue
        if line.startswith('## '):
            scenes.append(dict(title=line[3:].strip(), items=[])); blank = False; continue
        if line.startswith('# '):
            title = line[2:].strip(); continue
        if not scenes:
            scenes.append(dict(title='', items=[]))
        if line.startswith('@'):
            scenes[-1]['items'].append(('pic', pic_spec(line, no, scenes[-1]['title'])))
        else:
            text = re.sub(r'\s*\[>\]\s*', ' ', line).strip()
            if text:
                scenes[-1]['items'].append(('say', dict(text=text, line=no, brk=blank)))
                blank = False
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
    return own.resolve() if own.is_dir() else scenes_path.parent / 'figs'  # resolved: a linked folder keeps its css links


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
            preset = tts_say.MODELS.get(self.model, (None, None, None, {}))[3]
            if preset:  # the preset's settings (kokoro-seedvc: voice, f0 model, question rise) are part of the key
                self.settings += ('preset', json.dumps(preset, sort_keys=True))
            # a checked model (vibevoice): say.py cleans and checks every take, and speaks a short line together with
            # the sentence before it (or after it, for the first) and cuts it out; that neighbour is part of the key
            base = tts_say.MODELS.get(self.model, (None, None, self.model))[2]
            self.checked = base in tts_say.CHECKED
            self.short_words = tts_say.SHORT_WORDS
            self.say = tts_say
            if self.checked:
                self.settings += ('checked', tts_say.CHECK_VERSION)
                self.version_at = len(self.settings) - 1
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
            die(f'--voice must be say, say:<voice name>, tts:<model> or rec, not {args.voice}')

    def around(self, sents, k, version=None):
        """-> (before, after): the neighbours a short sentence is spoken with, or ('', ''). Since check version c3 both
        (the short line in the middle); before it, the one before (the one after, for the first sentence)."""
        if self.kind != 'tts' or not self.checked:
            return '', ''
        short = 5 if version == 'c2' else self.short_words
        if len(sents[k]['text'].split()) >= short:
            return '', ''
        before = sents[k - 1]['text'] if k else ''
        after = sents[k + 1]['text'] if k + 1 < len(sents) else ''
        if version == 'c2':
            return (before, '') if k else ('', after)
        return before, after

    def spoken(self, text):
        for rx, rep in getattr(self, 'pron', []):
            text = rx.sub(rep, text)
        return text

    def key(self, text, around=('', ''), version=None):
        st = self.settings
        if version:  # the key the clip had under an older check version
            st = st[:self.version_at] + (version,) + st[self.version_at + 1:]
        return h(text, *st) if not any(around) else h(text, 'with', *around, *st)

    def reuse_old(self, sents, adir):
        """Clips made by an older check version (say.py OLD_VERSIONS) stay in use when they pass the voice gate, so a new
        check remakes only the clips it fails. The gate's measures are cached in audio/voice-gate.json.
        -> (kept, failed): sentences now using an old clip; (sentence, flags) of old clips that failed."""
        if self.kind != 'tts' or not self.checked:
            return [], []
        cand = {}
        for k, s in enumerate(sents):
            if s['raw'].exists():
                continue
            for v in self.say.OLD_VERSIONS:
                ok = self.key(s['text'], self.around(sents, k, v), v)
                if (adir / f'{ok}.wav').exists():
                    cand[k] = ok
                    break
        gate_path = adir / 'voice-gate.json'
        gate = json.loads(gate_path.read_text()) if gate_path.exists() else {}
        need = sorted({ok for ok in cand.values() if ok not in gate})
        if need:
            print(f'voice gate: measuring {len(need)} clip(s) made before it ...', flush=True)
            res = self.say.likeness([adir / f'{ok}.wav' for ok in need], self.ref)
            for ok in need:
                gate[ok] = res[str(adir / f'{ok}.wav')]
            gate_path.write_text(json.dumps(gate, indent=0, sort_keys=True))
        kept, failed = [], []
        for k, ok in cand.items():
            flags = self.say.voice_flags(gate[ok])
            if flags:
                failed.append((sents[k], flags))
            else:
                sents[k].update(key=ok, raw=adir / f'{ok}.wav', wav=adir / f'{ok}-{self.fps}p.wav', around=('', ''))
                kept.append(sents[k])
        return kept, failed

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
                report = ([] if not self.checked else
                          ['--report', str(Path(items[0][1]).parent / f'say-report-{time.strftime("%Y%m%d-%H%M%S")}.json')])
                r = subprocess.run([self.python, str(self.script), '--model', self.model, '--ref', str(self.ref),
                                    '--seed', str(self.seed), '--batch', str(batch)] + report)
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


def ebur128(path):
    """-> (integrated loudness in LUFS, true peak in dBTP) of an audio file, by ffmpeg's EBU R128 meter."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-filter_complex',
                        'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True)
    summ = r.stderr[r.stderr.rfind('Summary:'):]
    i = re.search(r'I:\s+(-?[\d.]+|-inf) LUFS', summ)
    p = re.search(r'True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS', summ)
    if not i or not p:
        die(f'ffmpeg could not measure the loudness of {path}: {r.stderr.strip()[-300:]}')
    return float(i.group(1)), float(p.group(1))


def normalise(src, dst, target=LOUDNESS):
    """Copy a clip at `target` LUFS integrated, its true peak at most PEAK dBTP: one gain, and a lookahead limiter on
    the few peaks a gain would push past PEAK (delay compensated, so the clip keeps its length and timing).
    -> dict(lufs, peak, gain, limited, lufs_out, peak_out)."""
    LOUDNESS = target  # noqa: N806 (the loop below sets the clip to this)
    lufs, peak = ebur128(src)
    gain, out = LOUDNESS - lufs, None
    if lufs < -60:  # no voice to measure: leave it as it is
        gain = 0.0
    for _ in range(3):  # the limiter takes a little loudness off; measure again and make it up
        limited = peak + gain > PEAK
        af = f'volume={gain:.2f}dB:precision=double'
        if limited:  # a sample-peak limiter, set 0.5 dB under the true-peak limit
            af += f',alimiter=limit={10 ** ((PEAK - 0.5) / 20):.4f}:attack=5:release=50:level=false:latency=true'
        tmp = Path(str(dst) + '.part.wav')
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', af, '-ar', str(RATE), '-ac', '1',
                            '-c:a', 'pcm_s16le', str(tmp)], capture_output=True, text=True)
        if r.returncode:
            die(f'ffmpeg could not normalise {src}: {r.stderr.strip()[-300:]}')
        out = ebur128(tmp)
        tmp.replace(dst)
        if gain == 0.0 or abs(out[0] - LOUDNESS) <= 0.2:
            break
        gain += LOUDNESS - out[0]
    return dict(lufs=lufs, peak=peak, gain=round(gain, 2), limited=limited, lufs_out=out[0], peak_out=out[1])


# ---------- recorded voice (--voice rec; the audio and text work is in rec.py) ----------

def sentence_id(text):
    """A sentence's recording id: the first 12 hex of the sha1 of its text (UTF-8, whitespace collapsed)."""
    return hashlib.sha1(re.sub(r'\s+', ' ', text).strip().encode('utf-8')).hexdigest()[:12]


def spoken_lines(scenes):
    """The spoken lines of a parsed scenes file, in order: [dict(text, line, scene, brk)]."""
    return [dict(text=it['text'], line=it['line'], scene=si, brk=it['brk'])
            for si, sc in enumerate(scenes) for kind, it in sc['items'] if kind == 'say']


def rec_paths(sents, rdir):
    """Sets on each sentence its id and take (the current take's path, or None). -> the sentences with no take."""
    for s in sents:
        s['id'] = sentence_id(s['text'])
        f = rdir / f'{s["id"]}.wav'
        s['take'] = f if f.exists() else None
    return [s for s in sents if s['take'] is None]


def rec_settings(args):
    """What a cleaned take depends on, besides the take itself (its key), and the denoiser to use."""
    den = args.rec_denoise
    if den == 'df' and not DF_PY.exists():
        print(f'  note: no {DF_PY.relative_to(ROOT)}; denoising with ffmpeg afftdn instead (DeepFilterNet: see source/video/denoise.py)')
        den = 'afftdn'
    den_key = {'df': f'df3-{DF_ATTEN}', 'afftdn': AFFTDN, 'none': 'none'}[den]
    return den, h(REC_VERSION, den_key, REC_LEVEL, REC_DYN, REC_HEAD, REC_TAIL, rec.PAUSE_MAX, rec.PAUSE_KEEP,
                  rec.PROMPT_VERSION, args.whisper_model)[:8]


def decode(src, dst):
    """Any audio file -> 48 kHz mono 16-bit wav. -> its samples."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', 'aformat=sample_rates=48000:channel_layouts=mono',
                        '-c:a', 'pcm_s16le', str(dst)], capture_output=True, text=True)
    if r.returncode:
        die(f'ffmpeg could not read {src}: {r.stderr.strip()[-300:]}')
    return read_pcm(dst)


def read_pcm(path):
    with wave.open(str(path)) as w:
        return array.array('h', w.readframes(w.getnframes()))


def write_pcm(path, pcm):
    tmp = Path(str(path) + '.part.wav')
    with wave.open(str(tmp), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm.tobytes())
    tmp.replace(path)


def take_words(ss, wdir, args):
    """Whisper word times of each take, fillers and repeats kept (rec.verbatim), cached under the take's hash in wdir.
    Sets s['words'] ([[word, start, end]] in the take's seconds, or None when there is no Whisper)."""
    tag = h(args.whisper_model, rec.PROMPT_VERSION)[:6]
    for s in ss:
        s['take_hash'] = s.get('take_hash') or hashlib.sha1(s['take'].read_bytes()).hexdigest()[:16]
        s['words_file'] = wdir / f'{s["take_hash"]}-{tag}.json'
    todo = [s for s in ss if not s['words_file'].exists()]
    if todo and not Path(args.whisper_python).exists():
        print(f'  note: no {args.whisper_python}; takes are not checked for fillers, repeats and restarts', file=sys.stderr)
    elif todo:
        wdir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            jobs = Path(td) / 'jobs.json'
            jobs.write_text(json.dumps([dict(wav=str(s['take']), text=s['text'], prompt=rec.verbatim(s['text']),
                                             out=str(s['words_file'])) for s in todo]), encoding='utf-8')
            r = subprocess.run([args.whisper_python, str(HERE / 'align.py'), '--model', args.whisper_model, '--batch', str(jobs)],
                               stdout=subprocess.DEVNULL if args.check_take else None)
            if r.returncode:
                print(f'  note: align.py failed (exit {r.returncode}); those takes are not checked', file=sys.stderr)
    for s in ss:
        s['words'] = json.loads(s['words_file'].read_text())['words'] if s['words_file'].exists() else None


def take_plan(s, raw):
    """A take's cuts and check (rec.plan), on its decoded samples."""
    if not s.get('words'):
        return dict(cuts=[], heard=None, missing=[], extra=[], ok=None)
    return rec.plan(s['text'], s['words'], rec.db10(raw), len(raw) / RATE)


def to_take_time(t, cuts):
    """A time in a take after cuts -> the same moment in the take as recorded."""
    for t0, t1, _ in sorted(cuts):
        if t >= t0:
            t += t1 - t0
    return t


def check_take(sents, scenes, rdir, adir, args):
    """--check-take: one take checked as the recording pane needs it, JSON on stdout (see FORMAT.md, Recorded voice)."""
    s = next((s for s in sents if s['id'] == args.check_take), None)
    if s is None or not s['take']:
        print(json.dumps(dict(id=args.check_take, ok=False, error='no such sentence in this video' if s is None
                              else f'no take {rdir / (args.check_take + ".wav")}')))
        sys.exit(1)
    take_words([s], adir / 'rec' / 'words', args)
    with tempfile.TemporaryDirectory() as td:
        raw = decode(s['take'], Path(td) / 'raw.wav')
    p = take_plan(s, raw)
    cut = rec.apply_cuts(raw, p['cuts'])
    short, pauses = rec.shorten_pauses(cut)
    span = rec.voice_span(short)
    cuts = [dict(start=t0, end=t1, why=w) for t0, t1, w in p['cuts']]
    cuts += [dict(start=round(to_take_time(a, p['cuts']), 3), end=round(to_take_time(b, p['cuts']), 3), why='pause')
             for a, b in pauses]
    print(json.dumps(dict(id=s['id'], ok=p['ok'], heard=p['heard'], missing=p['missing'], extra=p['extra'],
                          cut=sorted(cuts, key=lambda c: c['start']),
                          seconds=round((span[1] - span[0]) / RATE, 2) if span else 0.0), ensure_ascii=False))


def polish_takes(ss, rdir, args, den):
    """Each take -> its piece (s['cut_take']) and room tone (…-tone.wav), as rec.py's header says: cuts (fillers,
    repeats, a false start), denoise, high-pass, level, compression, de-ess, long pauses shortened, cut to the voice.
    -> {piece name: meta}."""
    out = {}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        def first(i):
            s = ss[i]
            raw = decode(s['take'], td / f'{i}-raw.wav')
            s['plan'] = take_plan(s, raw)
            write_pcm(td / f'{i}-cut.wav', rec.apply_cuts(raw, s['plan']['cuts']))
        with ThreadPoolExecutor(6) as ex:
            list(ex.map(first, range(len(ss))))
        if den == 'df':
            jobs = td / 'df.json'
            jobs.write_text(json.dumps([dict(**{'in': str(td / f'{i}-cut.wav')}, out=str(td / f'{i}-dn.wav')) for i in range(len(ss))]))
            r = subprocess.run([str(DF_PY), str(HERE / 'denoise.py'), '--atten', str(DF_ATTEN), '--batch', str(jobs)],
                               capture_output=True, text=True)
            if r.returncode:
                die(f'denoise.py (DeepFilterNet) failed: {r.stderr.strip()[-500:]}\n(or --rec-denoise afftdn)')

        def second(i):
            s = ss[i]
            src = td / f'{i}-{"dn" if den == "df" else "cut"}.wav'
            pre = {'afftdn': f'apad=pad_dur=0.1,{AFFTDN},', 'df': '', 'none': ''}[den]  # afftdn drops its last 25 ms
            lufs = ebur128(src)[0]
            gain = 0.0 if lufs < -60 else REC_LEVEL - lufs
            r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', pre + REC_DYN.format(gain=f'{gain:.2f}'),
                                '-ar', str(RATE), '-ac', '1', '-c:a', 'pcm_s16le', str(td / f'{i}-dyn.wav')],
                               capture_output=True, text=True)
            if r.returncode:
                die(f'ffmpeg could not clean the take {s["take"]}: {r.stderr.strip()[-300:]}')
            pcm, pauses = rec.shorten_pauses(read_pcm(td / f'{i}-dyn.wav'))
            db = rec.db10(pcm)
            span = rec.voice_span(pcm, db)
            if span is None:
                die(f'no voice in the take {s["take"]} ({s["text"][:50]})')
            tone = rec.room_tone(pcm, db)
            v0, v1 = span
            a, b = max(0, v0 - round(REC_HEAD * RATE)), min(len(pcm), v1 + round(REC_TAIL * RATE))
            piece = pcm[a:b]
            rec.fade(piece, rec.XFADE, rec.XFADE)
            write_pcm(s['cut_take'], piece)
            write_pcm(tone_of(s['cut_take']), tone)
            p = s['plan']
            out[s['cut_take'].name] = dict(dur=round((b - a) / RATE, 4), vs=round((v0 - a) / RATE, 4), ve=round((v1 - a) / RATE, 4),
                                           lufs=ebur128(s['cut_take'])[0], gain=round(gain, 2), tone=round(len(tone) / RATE, 2),
                                           cuts=p['cuts'], pauses=pauses, ok=p['ok'], missing=p['missing'], extra=p['extra'],
                                           heard=p['heard'])
        with ThreadPoolExecutor(6) as ex:
            list(ex.map(second, range(len(ss))))
    return out


def tone_of(piece):
    return piece.with_name(piece.stem + '-tone.wav')


def rec_chunks(chunks, sents, args, adir):
    """--voice rec: each chunk (a whole paragraph) joined from its sentences' polished takes, --rec-gap apart, room tone
    between them; a sentence with no take is spoken by the --rec-missing voice (when it is not 'stop'), set to the
    takes' level. Sets c['key'] (from the takes' hashes, so a new take makes only its paragraph again) and c['raw'].
    -> (chunks made now, sentences filled in, takes polished now)."""
    rdir = adir / 'rec'
    rdir.mkdir(exist_ok=True)
    meta_path = rdir / 'takes.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    den, tag = rec_settings(args)
    takes = [s for s in sents if s['take']]
    for s in takes:
        s['take_hash'] = hashlib.sha1(s['take'].read_bytes()).hexdigest()[:16]
        s['cut_take'] = rdir / f'{s["take_hash"]}-{tag}.wav'
    todo, seen = [], set()
    for s in takes:
        if (s['cut_take'].name not in meta or not s['cut_take'].exists()) and s['cut_take'] not in seen:
            todo.append(s); seen.add(s['cut_take'])
    if todo:
        take_words(todo, rdir / 'words', args)
        print(f'polishing {len(todo)} take(s) (denoise: {den}) ...', flush=True)
        meta.update(polish_takes(todo, rdir, args, den))
        meta_path.write_text(json.dumps(meta, indent=0, sort_keys=True))
    for s in takes:
        s['rec'] = meta[s['cut_take'].name]
    filled = [s for s in sents if not s['take']]
    if filled:  # missing takes, spoken by a voice, cut to their voice and set to the takes' level (no other polish)
        fargs = argparse.Namespace(**vars(args))
        fargs.voice = DEFAULT_VOICE if args.rec_missing == 'tts' else args.rec_missing
        fv = Voice(fargs)
        items, seen = [], set()
        for s in filled:
            k = sents.index(s)
            s['fill_key'] = fv.key(s['text'], fv.around(sents, k))
            s['fill_raw'] = adir / f'{s["fill_key"]}.wav'
            if not s['fill_raw'].exists() and s['fill_key'] not in seen:
                items.append((s['text'], s['fill_raw'], fv.around(sents, k))); seen.add(s['fill_key'])
        if items:
            print(f'speaking {len(items)} missing sentence(s) with {fv.spec} ...', flush=True)
            fv.make_all(items)
        args.fill_spec = fv.spec
        for s in filled:
            name = f'fill-{s["fill_key"]}-{tag}.wav'
            f = rdir / name
            if name not in meta or not f.exists():
                pcm = read_pcm(s['fill_raw'])
                span = rec.voice_span(pcm) or (0, len(pcm))
                a, b = max(0, span[0] - round(REC_HEAD * RATE)), min(len(pcm), span[1] + round(REC_TAIL * RATE))
                piece = pcm[a:b]
                rec.fade(piece, rec.XFADE, rec.XFADE)
                write_pcm(rdir / f'fill-{s["fill_key"]}-cut.wav', piece)
                normalise(rdir / f'fill-{s["fill_key"]}-cut.wav', f, REC_LEVEL)
                meta[name] = dict(dur=round((b - a) / RATE, 4), vs=round((span[0] - a) / RATE, 4),
                                  ve=round((span[1] - a) / RATE, 4), lufs=ebur128(f)[0])
                meta_path.write_text(json.dumps(meta, indent=0, sort_keys=True))
            s['cut_take'], s['rec'] = f, meta[name]
    made = []
    for c in chunks:
        ss = [sents[i] for i in c['sents']]
        c['key'] = 'rec-' + h('rec', tag, args.rec_gap, *[s['cut_take'].name for s in ss])
        c['raw'] = adir / f'{c["key"]}.wav'
        c['wav'] = adir / f'{c["key"]}-{args.fps}p.wav'
        c['around'] = ('', '')
        if not c['raw'].exists():
            pieces = [(read_pcm(s['cut_take']), s['rec'],
                       read_pcm(tone_of(s['cut_take'])) if tone_of(s['cut_take']).exists() else array.array('h')) for s in ss]
            write_pcm(c['raw'], rec.join(pieces, args.rec_gap))
            made.append(c)
    return made, filled, todo


def join_sentences(lines):
    """Spoken lines -> sentences: consecutive lines of one scene, joined until a line ends with . ? or ! (or the scene or
    the paragraph ends). Each sentence knows its paragraph (para): a scene's lines with no blank line between them."""
    out, para = [], -1
    for g, ln in enumerate(lines):
        new_para = not out or out[-1]['scene'] != ln['scene'] or ln.get('brk')
        if new_para:
            para += 1
        if new_para or out[-1]['closed']:
            out.append(dict(scene=ln['scene'], para=para, lines=[], closed=False))
        out[-1]['lines'].append(g)
        out[-1]['closed'] = bool(re.search(r'[.?!]["\'”’)\]]*$', ln['text']))
    for s in out:
        s['text'] = ' '.join(lines[g]['text'] for g in s['lines'])
        s['line'] = lines[s['lines'][0]]['line']
    return out


def _split_even(size, n):
    """Cut a list of sizes into n contiguous runs, the largest run as small as it can be. -> [(start, end)]."""
    n = min(n, len(size))
    pre = [0]
    for x in size:
        pre.append(pre[-1] + x)
    best = {}  # (i, m): smallest max for size[i:] in m runs, and where the first run ends

    def go(i, m):
        if (i, m) in best:
            return best[i, m]
        if m == 1:
            r = (pre[-1] - pre[i], len(size))
        else:
            r = min(((max(pre[e] - pre[i], go(e, m - 1)[0]), e) for e in range(i + 1, len(size) - m + 2)))
        best[i, m] = r
        return r
    out, i = [], 0
    for m in range(n, 0, -1):
        e = go(i, m)[1]
        out.append((i, e)); i = e
    return out


def make_chunks(sents, max_s, cps):
    """Sentences -> the units the voice speaks in one call: a whole paragraph, or, when it would take longer than max_s
    seconds (cps letters per second), a run of whole sentences of it, the runs about equally long. Sets s['chunk'].
    -> [dict(text, sents: [sentence indexes], para, scene)]"""
    out, k = [], 0
    while k < len(sents):
        j = k
        while j < len(sents) and sents[j]['para'] == sents[k]['para']:
            j += 1
        para = list(range(k, j))
        size = [len(sents[i]['text']) + 1 for i in para]
        limit = max_s * cps
        n = max(1, math.ceil(sum(size) / limit))
        while True:  # the fewest runs that fit, split so the longest run is as short as it can be
            groups = _split_even(size, n)
            if n >= len(size) or max(sum(size[a:b]) for a, b in groups) <= limit:
                break
            n += 1
        out += [para[a:b] for a, b in groups]
        k = j
    chunks = []
    for ci, idx in enumerate(out):
        for i in idx:
            sents[i]['chunk'] = ci
        chunks.append(dict(text=' '.join(sents[i]['text'] for i in idx), sents=idx, para=sents[idx[0]]['para'],
                           scene=sents[idx[0]]['scene'], line=sents[idx[0]]['line']))
    return chunks


def _db10(data):
    """16-bit mono PCM -> loudness in dB of each 10 ms."""
    import audioop, warnings
    hop = RATE // 100
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        return [20 * math.log10(max(audioop.rms(data[i:i + 2 * hop], 2), 1) / 32768) for i in range(0, len(data), 2 * hop)]


def cut_chunk(c, sents, lines, fps, adir):
    """One paragraph clip (normalised, whole frames) -> one piece per sentence, cut where the voice is quietest between
    the last word of one sentence and the first of the next (word times from mlx-whisper; without them, where the
    letters say, +-0.5 s), on a frame boundary so the pieces put back to back are the clip, sample for sample.
    Sets on each sentence: norm (its piece), frames, vs, ve (voice start and end in the piece, s), words (its word
    times, s within the piece), cut (how the cut before it was found)."""
    idx = c['sents']
    words = None
    if c['align'].exists():
        words = json.loads(c['align'].read_text(encoding='utf-8')).get('words')
    with wave.open(str(c['norm'])) as w:
        data = w.readframes(w.getnframes())
    spf = RATE // fps
    n_frames = len(data) // 2 // spf
    db = _db10(data)
    thr = max(max(db, default=-90) - 40, -55)
    hyp = [(align.norm(wd), a, b) for wd, a, b in (words or []) if align.norm(wd)]
    toks = []  # (normalised word, sentence position in chunk, char position in chunk text)
    pos = 0
    for j, i in enumerate(idx):
        for wd in sents[i]['text'].split():
            if align.norm(wd):
                toks.append((align.norm(wd), j, pos))
            pos += len(wd) + 1
    at = {}
    if toks and hyp:
        import difflib
        sm = difflib.SequenceMatcher(None, [t[0] for t in toks], [x[0] for x in hyp], autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for q in range(n):
                at[a + q] = hyp[b + q]
    matched = len(at) / max(len(toks), 1)
    cuts, hows = [0], []
    total_chars = max(pos - 1, 1)
    for j in range(1, len(idx)):
        before = [at[q][2] for q, t in enumerate(toks) if t[1] == j - 1 and q in at]
        after = [at[q][1] for q, t in enumerate(toks) if t[1] == j and q in at]
        if matched >= 0.5 and before and after and after[0] > before[-1] - 0.05:
            lo, hi, how = before[-1] - 0.04, after[0] + 0.04, 'words'
        else:  # where the letters say, with room either side
            first = next(t[2] for t in toks if t[1] == j) if any(t[1] == j for t in toks) else 0
            mid = c['vs'] + (c['ve'] - c['vs']) * first / total_chars
            lo, hi, how = mid - 0.5, mid + 0.5, 'letters'
        lo_f = max(cuts[-1] + 1, math.ceil(lo * fps))
        hi_f = min(n_frames - 1, math.floor(hi * fps))
        cand = list(range(lo_f, hi_f + 1)) or [min(max(cuts[-1] + 1, round((lo + hi) / 2 * fps)), n_frames - 1)]

        def quiet(f):  # loudness of the 20 ms around the frame boundary
            k = f * spf * 100 // RATE
            return max(db[max(k - 1, 0):k + 1] or [-90])
        cuts.append(min(cand, key=lambda f: (quiet(f), abs(f - (lo + hi) / 2 * fps))))
        hows.append(how)
    cuts.append(n_frames)
    for j, i in enumerate(idx):
        s = sents[i]
        f0, f1 = cuts[j], cuts[j + 1]
        if len(idx) == 1:
            s['norm'] = c['norm']
        else:
            s['norm'] = adir / f'{c["norm"].stem}-{f0}-{f1}.wav'
            if not s['norm'].exists():
                tmp = Path(str(s['norm']) + '.part.wav')
                with wave.open(str(tmp), 'wb') as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
                    w.writeframes(data[2 * f0 * spf:2 * f1 * spf])
                tmp.replace(s['norm'])
        t0, t1 = f0 / fps, f1 / fps
        loud = [k for k in range(int(t0 * 100), min(len(db), int(t1 * 100))) if db[k] > thr]
        s['frames'] = f1 - f0
        s['vs'] = round(loud[0] / 100 - t0, 4) if loud else 0.0
        s['ve'] = round(min((loud[-1] + 1) / 100, t1) - t0, 4) if loud else round(t1 - t0, 4)
        # the voice converter can leave a breath or a low noise in a pause, which loudness counts as voice: where the
        # sentence's first and last words were heard, they say where the voice starts and ends
        mine = [q for q, tk in enumerate(toks) if tk[1] == j]
        if matched >= 0.5 and mine and mine[0] in at and t0 <= at[mine[0]][1] < t1:
            k = int(max(t0 + s['vs'], at[mine[0]][1] - 0.03) * 100)  # Whisper often starts a word early, in the pause
            k0 = k
            while k < min(len(db), int(t1 * 100)) - 1 and k < k0 + 50 and db[k] < max(db, default=-90) - 30:
                k += 1
            s['vs'] = round(k / 100 - t0, 4) if k < k0 + 50 else round(k0 / 100 - t0, 4)
        if matched >= 0.5 and mine and mine[-1] in at and t0 < at[mine[-1]][2] <= t1:
            s['ve'] = round(max(min(s['ve'], at[mine[-1]][2] - t0 + 0.12), s['vs'] + 0.1), 4)
        s['words'] = None if words is None else [[wd, round(a - t0, 3), round(b - t0, 3)] for wd, a, b in words
                                                 if t0 <= (a + b) / 2 < t1]
        s['cut'] = hows[j - 1] if j else None
        s['matched_chunk'] = matched


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
    """Word times for each paragraph clip, cached under the clip's own hash (and the model). -> how many were made."""
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
    ap.add_argument('--voice', default=DEFAULT_VOICE, help='say (macOS, Samantha), say:<voice>, tts:<model> '
                    '(source/video/tts/say.py), or rec: the author\'s own takes, one per sentence (see --rec-dir)')
    ap.add_argument('--list-sentences', action='store_true', help='print the sentences as JSON and stop: [{"id", "scene", '
                    '"para", "n", "text"}]; id = first 12 hex of sha1(text), para and n count from 0 over the whole video')
    ap.add_argument('--rec-status', action='store_true', help='print per scene how many sentences have a take, and the '
                    'ones that do not, and stop')
    ap.add_argument('--rec-dir', help='rec: the folder of takes, <id>.wav each (default .claude/loops/voice/rec/<video>/; '
                    '<id>.take<N>.wav are older takes and are not used)')
    ap.add_argument('--rec-gap', type=float, default=0.35, help='rec: seconds from the end of one sentence\'s voice to '
                    'the start of the next one\'s, inside a paragraph')
    ap.add_argument('--check-take', metavar='ID', help='rec: check one take (sentence id) and print JSON: {"id", "ok", '
                    '"heard", "missing", "extra", "cut": [{"start", "end", "why"}], "seconds"}; one Whisper pass, no denoise')
    ap.add_argument('--rec-denoise', default='df', choices=['df', 'afftdn', 'none'], help='rec: denoiser, DeepFilterNet '
                    '(its venv .claude/loops/tts/deepfilter/venv; ffmpeg afftdn when it is missing), afftdn or none')
    ap.add_argument('--rec-missing', default='stop', help='rec: a sentence with no take: stop (list them and stop), tts '
                    f'(speak it with the default voice, {DEFAULT_VOICE}, to preview a partly recorded video), or any '
                    '--voice value but rec')
    ap.add_argument('--rate', type=int, help='say only: words per minute')
    ap.add_argument('--ref', default=str(ROOT / '.claude/loops/voice/ref/ref-13s.wav'),
                    help='tts only: reference voice wav; its words in the .txt next to it')
    ap.add_argument('--seed', type=int, default=1, help='tts only: seed passed to tts/say.py')
    ap.add_argument('--tts-python', help='tts only: python that runs tts/say.py (default: this one)')
    ap.add_argument('--jobs', type=int, help='say only: clips made at once (default 4)')
    R = timing.Rules()
    ap.add_argument('--gap', type=float, default=R.gap, help='seconds of silence between two clips of one long paragraph '
                    '(inside a clip the voice keeps its own pauses)')
    ap.add_argument('--para-gap', type=float, default=R.para_gap, help='seconds of silence between paragraphs on the same picture')
    ap.add_argument('--para-max', type=float, default=20.0, help='a paragraph longer than this many seconds of speech (at '
                    f'{CPS:.0f} letters a second) is spoken in runs of whole sentences of about equal length')
    ap.add_argument('--dwell', type=float, default=R.dwell, help='when the picture changes between paragraphs: seconds the '
                    'outgoing picture stays after the words end, before the next one fades in')
    ap.add_argument('--busy', type=float, default=R.busy, help='seconds added to --dwell when the outgoing picture is busy '
                    '(a screenshot, a list of 4+ items, a figure with many words)')
    ap.add_argument('--scene-gap', type=float, default=R.scene_gap, help='seconds of silence between scenes (at least dwell + lead)')
    ap.add_argument('--lead', type=float, default=R.lead, help='a new picture starts fading in this many seconds before its first word')
    ap.add_argument('--min-hold', type=float, default=R.min_hold, help='a picture stays at least this many seconds before a '
                    'different picture; shorter beats are merged')
    ap.add_argument('--step-min-hold', type=float, default=R.step_min_hold, help='a step of a figure or list stays at least '
                    'this many seconds before its next step')
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
    lines = spoken_lines(scenes)  # the spoken lines of the scenes file; they say where pictures change
    sents = join_sentences(lines)

    # the recorder's view: the sentences, and which have a take (nothing else on stdout, no audio work)
    if args.list_sentences:
        print('[' + ',\n'.join(json.dumps(dict(id=sentence_id(s['text']), scene=scenes[s['scene']]['title'], para=s['para'],
                                               n=n, text=re.sub(r'\s+', ' ', s['text']).strip()), ensure_ascii=False)
                                    for n, s in enumerate(sents)) + ']')
        return
    rdir = Path(args.rec_dir).resolve() if args.rec_dir else REC_DIR / args.video
    if args.rec_status or args.voice == 'rec' or args.check_take:
        missing_rec = rec_paths(sents, rdir)
        if args.rec_status:
            print(f'{rdir}')
            for si, sc in enumerate(scenes):
                ss = [s for s in sents if s['scene'] == si]
                if ss:
                    miss = [(n, s) for n, s in enumerate(sents) if s['scene'] == si and not s['take']]
                    print(f'{sc["title"][:40]:<40} {len(ss) - len(miss):>3} / {len(ss):<3} recorded')
                    for n, s in miss:
                        print(f'    missing  #{n:<3} {s["text"][:70]}')
            print(f'{"total":<40} {len(sents) - len(missing_rec):>3} / {len(sents):<3} recorded')
            return
        if args.check_take:
            (Path(args.out) / args.video / 'audio').mkdir(parents=True, exist_ok=True)
            check_take(sents, scenes, rdir, Path(args.out) / args.video / 'audio', args)
            return
        if missing_rec and args.rec_missing == 'stop':
            die(f'{len(missing_rec)} of {len(sents)} sentences have no take in {rdir}:\n'
                + '\n'.join(f'  {scenes[s["scene"]]["title"]}, sentence {sents.index(s)} ({s["id"]}): {s["text"][:70]}'
                            for s in missing_rec)
                + '\nrecord them, or add --rec-missing tts to speak them with the default voice for a preview')
        if args.rec_missing.startswith('rec') or not (args.rec_missing in ('stop', 'tts', 'say')
                                                      or args.rec_missing.startswith(('say:', 'tts:'))):
            die(f'--rec-missing takes stop, tts, say, say:<voice> or tts:<model>, not {args.rec_missing}')

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
                n_sent += 1
    if missing:
        die('pictures not found:\n' + '\n'.join(missing))
    if not lines and not args.frames_only:
        die('the scenes file has no sentences')

    # a picture shows from the sentence after it; two @ lines with no sentence between: the earlier one never shows
    by_start = {}
    for p in pics:
        if p['at'] >= len(lines):
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

    # 2. audio: one clip per paragraph (or per run of its sentences, when long), cached by (its text, voice settings);
    # then cut back into one piece per sentence at the quiet point between the words
    is_rec = args.voice == 'rec'
    filled = []
    if is_rec:  # the author's takes: one clip per paragraph, however long (--para-max is for a made voice)
        chunks = make_chunks(sents, math.inf, CPS)
        todo, filled, polished = rec_chunks(chunks, sents, args, adir)
        kept_old, failed_old = [], []
    else:
        chunks = make_chunks(sents, args.para_max, CPS)
        voice = Voice(args)
        for k, c in enumerate(chunks):
            c['around'] = voice.around(chunks, k)
            c['key'] = voice.key(c['text'], c['around'])
            c['raw'] = adir / f'{c["key"]}.wav'
            c['wav'] = adir / f'{c["key"]}-{fps}p.wav'
        voice.fps = fps
        kept_old, failed_old = voice.reuse_old(chunks, adir)
        todo, seen = [], set()
        for c in chunks:
            if not c['raw'].exists() and c['key'] not in seen:
                todo.append(c); seen.add(c['key'])
        if todo:
            print(f'making {len(todo)} paragraph clip(s) with {voice.spec} ...', flush=True)
            voice.make_all([(c['text'], c['raw'], c['around']) for c in todo])
    made_keys = {c['key'] for c in todo}

    meta_path = adir / 'durations.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for c in chunks:
        k = f'{c["key"]}-{fps}-{TRIM_VERSION}'
        if c['key'] in made_keys or k not in meta or not c['wav'].exists():
            meta[k] = trim_and_pad(c['raw'], c['wav'], fps, head=REC_HEAD if is_rec else 0.06)
        c['frames'], c['vs'], c['ve'] = meta[k]
    meta_path.write_text(json.dumps(meta, indent=0, sort_keys=True))

    # every clip at one loudness (LOUDNESS, PEAK), one gain for the whole paragraph clip
    loud_path = adir / 'loudness.json'
    loud = json.loads(loud_path.read_text()) if loud_path.exists() else {}
    todo_n = {}
    for c in chunks:
        c['lk'] = f'{c["key"]}-{fps}-{TRIM_VERSION}-{LOUD_VERSION}-{LOUDNESS}-{PEAK}'
        c['norm'] = adir / f'{c["key"]}-{fps}p-{h(c["lk"])[:6]}.wav'
        if c['key'] in made_keys or c['lk'] not in loud or not c['norm'].exists():
            todo_n[c['lk']] = c
    if todo_n:
        with ThreadPoolExecutor(8) as ex:
            for lk, r in zip(todo_n, ex.map(lambda c: normalise(c['wav'], c['norm']), todo_n.values())):
                loud[lk] = r
        loud_path.write_text(json.dumps(loud, indent=0, sort_keys=True))
    for c in chunks:
        c['loud'] = loud[c['lk']]

    # word times of each paragraph clip; they say where to cut it into sentences, and where each line starts
    n_aligned = align_all(chunks, adir, args)
    for c in chunks:
        cut_chunk(c, sents, lines, fps, adir)
    hows = {'aligned': 0, 'interpolated': 0, 'proportional': 0}
    inner = dict(word=0, interpolated=0, proportional=0)  # line starts inside sentences
    for s in sents:
        s['loud'] = chunks[s['chunk']]['loud']
        texts = [lines[g]['text'] for g in s['lines']]
        s['starts'], s['how'], s['matched'] = align.line_times(texts, s['words'], s['vs'], s['ve'])
        hows[s['how']] += 1
        if len(texts) > 1:
            key = 'proportional' if s['how'] == 'proportional' else None
            for j in range(1, len(texts)):
                inner[key or ('word' if s['how'] == 'aligned' else 'interpolated')] += 1
    # (interpolated counts every inner line of a sentence with at least one interpolated start; good enough to report)

    # 3. timeline, in frames: the timing rules are in timing.py
    rules = timing.Rules(fps=fps, gap=args.gap, dwell=args.dwell, busy=args.busy, scene_gap=args.scene_gap, lead=args.lead,
                         min_hold=args.min_hold, step_min_hold=args.step_min_hold, head=args.head, tail=args.tail, xfade=args.xfade, step_xfade=args.step_xfade,
                         para_gap=args.para_gap)
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
    clips = [dict(path=s['norm'], name=f'{i + 1:03d} {s["text"][:50]}', start=s['start'], dur=s['frames'])
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
    print(f'{"scene":<40} {"lines":>5} {"sentences":>9} {"paragraphs":>10} {"start":>7} {"seconds":>8}')
    for si, sc in enumerate(scenes):
        ss = [s for s in sents if s['scene'] == si]
        if not ss:
            continue
        nxt = next((s['start'] for s in sents if s['scene'] > si), total)
        print(f'{sc["title"][:40]:<40} {sum(len(s["lines"]) for s in ss):>5} {len(ss):>9} {len({s["para"] for s in ss}):>10} '
              f'{sec(ss[0]["start"]):>7.1f} '
              f'{sec(nxt - ss[0]["start"]):>8.1f}')
    print(f'{"total":<40} {len(lines):>5} {len(sents):>9} {len({s["para"] for s in sents}):>10} {"":>7} {sec(total):>8.1f}')
    n_audio = len({c['key'] for c in chunks})
    n_para = len({s['para'] for s in sents})
    print(f'\naudio:  {len(chunks)} clip(s) for {n_para} paragraphs ({len(chunks) - n_para} split for length), '
          f'{len(made_keys)} made, {n_audio - len(made_keys)} reused; cut into {len(sents)} sentence pieces '
          f'({sum(1 for s in sents if s["cut"] == "words")} cuts between matched words, '
          f'{sum(1 for s in sents if s["cut"] == "letters")} by letter count)')
    if is_rec:
        print(f'voice:  recorded, {len(sents) - len(filled)} of {len(sents)} sentences from takes in {rdir}'
              + (f'; {len(filled)} filled in with {args.fill_spec} (not recorded yet):' if filled else ''))
        for s in filled:
            print(f'  filled  {scenes[s["scene"]]["title"][:24]}, sentence {sents.index(s)}: {s["text"][:60]}')
        tk = [s for s in sents if s.get('take')]
        whys = {}
        for s in tk:
            for c in s['rec']['cuts']:
                whys[c[2]] = whys.get(c[2], 0) + 1
        print(f'polish: {len(polished)} take(s) polished now, {len(tk) - len(polished)} reused; cut '
              + (', '.join(f'{n} {w}' for w, n in sorted(whys.items())) or 'nothing')
              + f'; {sum(len(s["rec"]["pauses"]) for s in tk)} long pause(s) shortened; takes set to {REC_LEVEL} LUFS by '
              f'{min(s["rec"]["gain"] for s in tk):+.1f} to {max(s["rec"]["gain"] for s in tk):+.1f} dB, after polish '
              f'{min(s["rec"]["lufs"] for s in tk):.1f} to {max(s["rec"]["lufs"] for s in tk):.1f} LUFS'
              if tk else 'polish: no takes')
        for s in tk:
            r = s['rec']
            if r['ok'] is False:
                print(f'  check   sentence {sents.index(s)} ({s["id"]}): missing {r["missing"]}, extra {r["extra"]}; '
                      f'heard "{r["heard"][:70]}"')
        if tk and all(s['rec']['ok'] is None for s in tk):
            print('  (no Whisper: takes not checked)')
    if kept_old or failed_old:
        print(f'voice gate: {len(kept_old)} clip(s) of an older check kept, {len(failed_old)} failed it and were made again')
        for s, flags in failed_old:
            print(f'  failed line {s["line"]}: {"; ".join(flags)}: {s["text"][:60]}')
    for s in todo[:10]:
        print(f'  made  line {s["line"]}: {s["text"][:70]}')
    if len(todo) > 10:
        print(f'  ... and {len(todo) - 10} more')
    li = [c['loud']['lufs'] for c in chunks]; lo = [c['loud']['lufs_out'] for c in chunks]
    print(f'loudness: clips {min(li):.1f} to {max(li):.1f} LUFS as made, {min(lo):.1f} to {max(lo):.1f} after setting them to '
          f'{LOUDNESS} (peaks at most {max(c["loud"]["peak_out"] for c in chunks):.1f} dBTP; '
          f'{sum(1 for c in chunks if c["loud"]["limited"])} limited); {len(todo_n)} normalised now')
    multi = sum(1 for s in sents if len(s['lines']) > 1)
    print(f'words:  {n_aligned} clip(s) aligned now; {multi} sentences have a picture or cue change inside: '
          f'{inner["word"]} line starts on a matched word, {inner["interpolated"]} in sentences with some interpolated '
          f'starts, {inner["proportional"]} by character count ({hows["proportional"]} sentence(s) fell back)')
    for s in sents:
        if s['how'] != 'aligned' and len(s['lines']) > 1:
            print(f'  {s["how"]:<12} line {s["line"]} ({s["matched"]:.0%} of words matched): {s["text"][:70]}')
    holds = lay['hold']
    print(f'pictures: {len(shown)} shown, shortest hold {sec(min(holds)):.2f} s (min {args.min_hold} s, '
          f'{args.step_min_hold} s before a next step), '
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
            sentences=[dict(line=s['line'], text=s['text'], para=s['para'], chunk=s['chunk'], wav=str(s['norm']),
                            made=str(chunks[s['chunk']]['raw']), loudness=s['loud'], start=s['start'], frames=s['frames'],
                            vs=s['vs'], ve=s['ve'], cut=s['cut'], starts=s['starts'], how=s['how'],
                            take=(str(s['take']) if s.get('take') else 'filled' if is_rec else None),
                            polish=({k: v for k, v in s['rec'].items() if k != 'heard'} if s.get('rec') else None),
                            lines=[lines[g]['line'] for g in s['lines']]) for s in sents],
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
