#!/usr/bin/env python3
"""Build a tutorial video's audio, frames, Final Cut Pro timeline and rough mp4 from its scenes file.

    .venv/bin/python source/video/build.py basic-01                           # Qwen3-TTS cloning the author's talk-a.wav
    .venv/bin/python source/video/build.py basic-01 --ref .claude/loops/voice/ref/talk-b.wav   # another reference
    .venv/bin/python source/video/build.py basic-01 --voice rec               # the author's own takes, see below
    .venv/bin/python source/video/build.py basic-01 --rec-status              # which sentences are recorded
    .venv/bin/python source/video/build.py basic-01 --list-sentences          # the sentences as JSON, for the recorder
    .venv/bin/python source/video/build.py basic-01 --check-take <id>         # one take checked, JSON
    .venv/bin/python source/video/build.py basic-01 --list-paragraphs         # paragraphs and points as JSON, for the recorder
    .venv/bin/python source/video/build.py basic-01 --check-scene <sid>       # a talked scene take checked, JSON
    .venv/bin/python source/video/build.py basic-01 --check-para <id>         # a paragraph punch-in checked, JSON
    .venv/bin/python source/video/build.py basic-01 --polish-preview <sid>    # a scene take (or punch-in) polished, to listen to
    .venv/bin/python source/video/build.py basic-01 --edit-draft <sid>        # the take before any cut, to write edit/<sid>.json
    .venv/bin/python source/video/build.py basic-01 --subs-draft <sid>        # heard vs script, to write subs-fix/<sid>.json

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

Talk (--voice rec, as soon as there is any scene/<sid>.wav or para/<id>.wav in the take folder): the author talks each
scene in their own words; talk.py cuts fillers, stutters and restarts and finds where each point (script line) was said;
the take is cut into paragraphs at the pauses between them, pictures land on their points, subtitles are what was said,
and spoken.md (next to the scenes file) gets the cleaned transcript. A paragraph take newer than its scene take replaces
that paragraph. --polish-preview <sid|id> polishes one scene take (or punch-in) only, for the author to hear and approve
before any build: preview/<sid>-raw.mp3, -polished.mp3 and -polish.md in the take folder. See FORMAT.md, Recorded voice,
Talk.
"""
import argparse, array, hashlib, json, math, os, re, shlex, subprocess, sys, tempfile, time, wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import render, fcpxml, subs, align, timing, rec, talk, avatar as speaker  # noqa: E402

RATE = 48000
DEFAULT_SAY_VOICE = 'Samantha'
DEFAULT_VOICE = 'tts:qwen3'   # Kokoro + Seed-VC rejected by the author (2026-11-18: too distorted) and removed
# the chosen voice (2026-11-18): Qwen3-TTS 1.7B cloning 12 s cut from the author's own natural talk (not read aloud),
# with the script written in the author's style (source/courses/basic-01/style/author-style.md); see tts/README.md
DEFAULT_REF = ROOT / '.claude/loops/voice/ref/talk-a.wav'
WHISPER_PY = ROOT / '.claude/loops/tts/whisper/venv/bin/python'
TRIM_VERSION = 't3'   # bump when trim_and_pad changes, so every clip is cut again
# room tone: no inserted pause, padding or gap is digital silence (the room under the voice would vanish and come back,
# an audible stop); each is the clip's own room tone, crossfaded in and out over EDGE, and every clip edge is faded
SILENT_DB = -90.0     # a 10 ms frame quieter than this is digital silence, not room tone
EDGE = RATE // 50     # 20 ms: the fade at every clip edge, and the crossfade into and out of room tone
ROOM_TONE = ROOT / '.claude/loops/voice/ref/room-tone.wav'  # the author's room tone (2 s of a polished take), set to a
# clip's floor, for a clip with too little room tone of its own
BED_EASE = RATE // 8  # 125 ms: the room tone between clips eases from a clip edge's level to its own over this
TONE_VERSION = 'rt3'  # bump when the room tone or the edge fades change, so every clip edge and the timeline's bed are made again
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
# de-plosive: a short low-frequency burst (a 'p' or 'b' hitting the mic) is pulled down by up to 12 dB; voice above 300 Hz unchanged
DEPLOSIVE = ('adynamicequalizer=dfrequency=120:dftype=lowpass:tfrequency=150:tftype=lowshelf:mode=cutabove:attack=1:'
             'release=80:ratio=4:range=12:auto=adaptive')
# DEPLOSIVE is off: on the author's first real take its adaptive threshold took ~8 dB off everything under 200 Hz (the
# voice itself got thin), and a fixed threshold did nothing. The 80 Hz high-pass and the compressor handle the rest.
REC_DYN = ('highpass=f=80,'
           'volume={gain}dB,acompressor=threshold=-18dB:ratio=2:attack=15:release=200:knee=6,'
           'deesser=i=0.4')
REC_HEAD, REC_TAIL = 0.08, 0.15   # seconds kept before and after the voice of each take
REC_VERSION = 'r3'    # bump when the polish changes (here or in rec.py), so every take is polished again


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
            text, pauses = split_pauses(re.sub(r'\s*\[>\]\s*', ' ', line).strip())
            if text:
                scenes[-1]['items'].append(('say', dict(text=text, line=no, brk=blank, pauses=pauses)))
                blank = False
    return title or Path(path).parent.name, scenes


PAUSE_RX = re.compile(r'\[(\d*\.\d+|\d+(?:\.\d+)?)\]')  # a pause mark in a spoken line: [.3], [0.3], [1], seconds
PAUSE_VERSION = 'p3'  # bump when put_pauses changes, so every clip with a pause mark is made again (from the same voice)


def split_pauses(line):
    """'So, [.3] number one is,' -> ('So, number one is,', [(1, 0.3)]): the line without its pause marks (they are never
    spoken or shown), and each mark as (how many of the line's words come before it, seconds)."""
    parts, pauses = [], []
    for k, part in enumerate(PAUSE_RX.split(line)):
        if k % 2:
            pauses.append((len(' '.join(parts).split()), float(part)))
        else:
            parts.append(part)
    return re.sub(r'\s+', ' ', ' '.join(parts)).strip(), pauses


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


# ---------- room tone (see SILENT_DB, EDGE) ----------

def _sat(x):
    return -32768 if x < -32768 else 32767 if x > 32767 else int(round(x))


def _rms_db(pcm):
    return 10 * math.log10(max(sum(x * x for x in pcm) / max(len(pcm), 1), 1)) - 90.309


def clip_tone(pcm, most=1.0):
    """A clip's own room tone: its quietest stretches (50 ms or more within 6 dB of the 5th percentile of its 10 ms
    frames, digital silence left out), spliced, up to `most` seconds (a made voice is dense: 0.2 to 0.5 s, looped, at
    -66 to -77 dBFS). With under 0.2 s of its own: ROOM_TONE set to the level of what it has (or to its floor).
    -> array('h'), empty only if there is neither."""
    db = rec.db10(pcm)
    live = sorted(d for d in db if d > SILENT_DB)
    floor = live[len(live) // 20] if live else None
    if floor is not None:
        ok = lambda d: SILENT_DB < d <= floor + 6  # noqa: E731
        segs, k, got = [], 0, 0
        while k < len(db) and got < most * RATE:
            if not ok(db[k]):
                k += 1; continue
            j = k
            while j < len(db) and ok(db[j]):
                j += 1
            if j - k >= 5:
                segs.append(pcm[(k + 1) * rec.HOP:(j - 1) * rec.HOP]); got += len(segs[-1])
            k = j
        if got >= RATE // 5:
            return rec.splice(segs)
        if segs:
            floor = _rms_db(rec.splice(segs))
    if not ROOM_TONE.exists():
        return array.array('h')
    ref = read_pcm(ROOM_TONE)
    g = 10 ** (((floor if floor is not None else -70.0) - _rms_db(ref)) / 20)
    return array.array('h', (_sat(x * g) for x in ref))


def tone_loop(tone, n):
    """n samples of room tone, looped with a crossfade at each seam (digital silence if there is no tone)."""
    n = max(n, 0)
    if not len(tone):
        return array.array('h', bytes(2 * n))
    out = array.array('h')
    while len(out) < n:
        if out:
            xfade_append(out, tone, min(rec.XFADE, len(tone) // 4))
        else:
            out.extend(tone)
    return out[:n]


def tone_between(tone, n, before=(), after=()):
    """n samples of room tone to go between `before` and `after` (the sound either side): where that sound is louder
    than the tone, the tone starts (ends) at its level and eases to its own over BED_EASE (at most 12 dB up), so a
    word's tail or a made voice's own noise does not step down into the room."""
    fill = tone_loop(tone, n)
    t = _rms_db(tone) if len(tone) else -120.0
    w = RATE // 20
    lift = lambda seg: min(max(_rms_db(seg) - t, 0.0), 12.0) if len(seg) else 0.0  # noqa: E731
    up0, up1 = lift(before[-w:]), lift(after[:w])
    if up0 or up1:
        for q in range(len(fill)):
            up = max(up0 * max(0.0, 1 - q / BED_EASE), up1 * max(0.0, 1 - (len(fill) - 1 - q) / BED_EASE))
            if up:
                fill[q] = _sat(fill[q] * 10 ** (up / 20))
    return fill


def xfade_append(out, seg, n=EDGE):
    """Append seg to out (in place), its first n samples over out's last n: an equal-power crossfade (sin/cos), as for
    two unrelated noises (room tone, the quiet of a pause), so the level holds through it."""
    n = min(n, len(out), len(seg))
    o = len(out) - n
    for i in range(n):
        r = (i + 0.5) / n * math.pi / 2
        out[o + i] = _sat(out[o + i] * math.cos(r) + seg[i] * math.sin(r))
    out.extend(seg[n:])


def fill_silence(pcm, tone):
    """Every stretch of digital silence (two 10 ms frames or more under SILENT_DB) -> room tone, crossfaded over EDGE
    at both ends; the length is unchanged. -> (array('h'), seconds filled)."""
    db, hop, hh = rec.db10(pcm), rec.HOP, EDGE // 2
    runs, k = [], 0
    while k < len(db):
        if db[k] >= SILENT_DB:
            k += 1; continue
        j = k
        while j < len(db) and db[j] < SILENT_DB:
            j += 1
        if j - k >= 2:
            runs.append((k * hop, min(j * hop, len(pcm))))
        k = j
    if not runs or not len(tone):
        return pcm, 0.0
    out, last = array.array('h'), 0
    for a, b in runs:  # the run's room tone reaches hh into the sound either side, under its crossfades
        if a:
            xfade_append(out, pcm[last:a + hh])
        xfade_append(out, tone_between(tone, b - a + (hh if a else 0) + (hh if b < len(pcm) else 0),
                                       pcm[max(0, a - hh - RATE // 20):max(0, a - hh)], pcm[b + hh:b + hh + RATE // 20]))
        last = max(b - hh, 0) if b < len(pcm) else len(pcm)
    xfade_append(out, pcm[last:])
    return out[:len(pcm)], sum(b - a for a, b in runs) / RATE


def edge_faded(path):
    """A copy of a timeline clip with an EDGE fade (sin) at each end, which the room tone under it in the timeline
    (cos, room_bed) crossfades with, so no clip starts or stops with a hard edge; and the clip's room tone.
    -> (path of the copy, tone)."""
    dst = path.with_name(f'{path.stem}-{TONE_VERSION}.wav')
    tf = dst.with_name(dst.stem + '-tone.wav')
    if not (dst.exists() and tf.exists()):
        pcm = read_pcm(path)
        write_pcm(tf, clip_tone(pcm))
        n = min(EDGE, len(pcm) // 2)
        for i in range(n):
            g = math.sin((i + 0.5) / n * math.pi / 2)
            pcm[i] = _sat(pcm[i] * g); pcm[-1 - i] = _sat(pcm[-1 - i] * g)
        write_pcm(dst, pcm)
    return dst, read_pcm(tf)


def room_bed(clips, total, fps):
    """The room tone under the whole timeline: wherever no clip plays, the room tone of the clip before it (of the first
    clip, before that), faded in (cos) under each clip's fade-out and out under the next one's fade-in, so the sum holds
    the level and never drops to digital silence between clips, paragraphs or scenes. Where a clip's edge (the 50 ms
    inside its fade) is louder than its room tone, the tone starts at that level and eases down to its own over BED_EASE
    (at most 12 dB up): no step from a word's tail to the room. clips: [dict(path, start, dur, tone)], in frames, the
    clips' files faded by edge_faded. -> array('h'), total frames long."""
    spf = RATE // fps
    L = total * spf
    bed = array.array('h', bytes(2 * L))
    spans = []
    for c in sorted(clips, key=lambda c: c['start']):
        pcm, w = read_pcm(c['path']), RATE // 20
        t = _rms_db(c['tone']) if len(c['tone']) else -120.0
        lift = lambda seg: min(max(_rms_db(seg) - t, 0.0), 12.0) if len(seg) else 0.0  # noqa: E731
        spans.append((c['start'] * spf, (c['start'] + c['dur']) * spf, c['tone'],
                      lift(pcm[EDGE:EDGE + w]), lift(pcm[max(0, len(pcm) - EDGE - w):len(pcm) - EDGE])))
    if not spans:
        return bed
    n_of = lambda s: min(EDGE, (s[1] - s[0]) // 2)  # noqa: E731
    gaps = [(0, spans[0][0], spans[0][2], 0, n_of(spans[0]), 0.0, spans[0][3])]
    for s0, s1 in zip(spans, spans[1:]):
        gaps.append((s0[1], s1[0], s0[2], n_of(s0), n_of(s1), s0[4], s1[3]))
    gaps.append((spans[-1][1], L, spans[-1][2], n_of(spans[-1]), 0, spans[-1][4], 0.0))
    for e, a, tone, n_out, n_in, up_out, up_in in gaps:  # from a clip's end e to the next one's start a
        lo, hi = e - n_out, a + n_in
        if hi - lo <= 0 or a < e:  # clips that overlap: no bed between them
            continue
        fill = tone_loop(tone, hi - lo)
        F = len(fill)
        near_out, near_in = n_out + BED_EASE, n_in + BED_EASE
        idx = range(F) if F <= near_out + near_in else [*range(near_out), *range(F - near_in, F)]
        for q in idx:  # under a clip's fade (the clip sin, the bed cos), and easing from its edge's level
            i = F - 1 - q
            up = max(up_out * max(0.0, 1 - max(q - n_out, 0) / BED_EASE), up_in * max(0.0, 1 - max(i - n_in, 0) / BED_EASE))
            g = 10 ** (up / 20)
            if q < n_out:
                g *= math.sin((q + 0.5) / n_out * math.pi / 2)
            if i < n_in:
                g *= math.sin((i + 0.5) / n_in * math.pi / 2)
            fill[q] = _sat(fill[q] * g)
        if lo == 0 or hi == L:  # the very start and end of the video: a short fade, not a step
            fl = fill
            for i in range(min(EDGE, len(fl))):
                g = (i + 0.5) / EDGE
                if lo == 0:
                    fl[i] = _sat(fl[i] * g)
                if hi == L:
                    fl[-1 - i] = _sat(fl[-1 - i] * g)
        bed[lo:hi] = fill
    return bed


def trim_and_pad(src, dst, fps, head=0.06, tail=0.15):
    """Copy a 48 kHz mono wav cut to its voice (by loudness, keeping `head` and `tail` seconds of what is around it, so no
    word is cut), padded with its own room tone to a whole number of frames, so every time in the timeline is exact; any
    digital silence left in it (a voice that starts or ends on it) is room tone too (fill_silence).
    -> (frames, vs, ve, off): the clip's length, where the voice starts and ends in it, and where the clip starts in
    src (seconds)."""
    import audioop, warnings
    with wave.open(str(src)) as w:
        data, n = w.readframes(w.getnframes()), w.getnframes()
    tone = clip_tone(array.array('h', data))
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
    pcm, _ = fill_silence(array.array('h', data[2 * a:2 * b]), tone)
    m = b - a
    spf = RATE // fps
    frames = max(1, math.ceil(m / spf))
    if frames * spf > m:  # the padding: room tone, crossfaded in under the clip's last EDGE
        xfade_append(pcm, tone_between(tone, frames * spf - m + min(EDGE, m), pcm[:max(0, m - EDGE)]), min(EDGE, m))
    with wave.open(str(dst), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm[:frames * spf].tobytes())
    return frames, round((v0 - a) / RATE, 4), round((v1 - a) / RATE, 4), round(a / RATE, 4)


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
    return [dict(text=it['text'], line=it['line'], scene=si, brk=it['brk'], pauses=it.get('pauses', []))
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
    for s in ss:  # a talk take has its own prompt (talk.prompt) and is heard in windows
        tag = h(args.whisper_model, s.get('ptag', rec.PROMPT_VERSION))[:6]
        s['take_hash'] = s.get('take_hash') or hashlib.sha1(s['take'].read_bytes()).hexdigest()[:16]
        s['words_file'] = wdir / f'{s["take_hash"]}-{tag}.json'
    todo = [s for s in ss if not s['words_file'].exists()]
    if todo and not Path(args.whisper_python).exists():
        print(f'  note: no {args.whisper_python}; takes are not checked for fillers, repeats and restarts', file=sys.stderr)
    elif todo:
        wdir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            jobs = Path(td) / 'jobs.json'
            jobs.write_text(json.dumps([dict(wav=str(s['take']), text=s['text'], prompt=s.get('prompt') or rec.verbatim(s['text']),
                                             out=str(s['words_file']), window=s.get('window')) for s in todo]), encoding='utf-8')
            quiet_out = args.check_take or args.check_para or args.check_scene
            r = subprocess.run([args.whisper_python, str(HERE / 'align.py'), '--model', args.whisper_model, '--batch', str(jobs)],
                               stdout=subprocess.DEVNULL if quiet_out else None)
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


# ---------- talk: a scene (or a paragraph, punched in) said in the author's own words (talk.py has the text work) ----------

def paragraph_list(scenes, lines, bold):
    """The paragraphs of the video: [dict(id, sid, scene, para, lines: [global line indexes], text, beats, bold)].
    id: sentence_id of the paragraph's lines joined by spaces; sid: the same of its scene's lines; beats: the lines a
    picture changes at (an @ line before them)."""
    beat, g, pending = set(), 0, False
    for sc in scenes:
        for kind, it in sc['items']:
            if kind == 'pic':
                pending = True
            else:
                if pending:
                    beat.add(g)
                pending = False; g += 1
    out = []
    for g, ln in enumerate(lines):
        if not out or out[-1]['scene'] != ln['scene'] or ln['brk']:
            out.append(dict(scene=ln['scene'], para=len(out), lines=[]))
        out[-1]['lines'].append(g)
    for p in out:
        p['text'] = re.sub(r'\s+', ' ', ' '.join(lines[g]['text'] for g in p['lines'])).strip()
        p['id'] = sentence_id(p['text'])
        p['beats'] = [g in beat for g in p['lines']]
        p['bold'] = [bold.get(lines[g]['text'], []) for g in p['lines']]
        p['line'] = lines[p['lines'][0]]['line']
    for si in {p['scene'] for p in out}:
        sid = sentence_id(' '.join(lines[g]['text'] for p in out if p['scene'] == si for g in p['lines']))
        for p in out:
            if p['scene'] == si:
                p['sid'] = sid
    return out


def load_bold(scenes_path, video):
    """bold.json next to the scenes file, else in source/courses/<video>/: {line text: [key phrases]}."""
    for f in (scenes_path.parent / 'bold.json', ROOT / 'source/courses' / video / 'bold.json'):
        if f.exists():
            return json.loads(f.read_text(encoding='utf-8'))
    return {}


def current(folder, name):
    f = folder / f'{name}.wav'
    return f if f.exists() else None


def talk_mode(rdir):
    """Talk takes are used when the take folder has any scene or paragraph take."""
    return any(not re.search(r'\.take\d+$', f.stem) for d in ('scene', 'para') for f in (rdir / d).glob('*.wav'))


def punch_in_used(para_take, scene_item):
    """A paragraph take replaces its part of the scene take only while it is newer than the scene take (as the recording
    pane does): a scene recorded again after it wins."""
    return scene_item is None or para_take.stat().st_mtime > scene_item['take'].stat().st_mtime


def talk_item(take, text, kind, key):
    """A talk take to hear and polish (the dict take_words and polish_takes work on)."""
    return dict(take=take, text=text, talk=True, prompt=talk.prompt(text), ptag=talk.PROMPT_VERSION, window=25,
                kind=kind, key=key)


def talk_plan(s, raw):
    """A talk take's cuts (talk.plan) on its decoded samples, and what was heard."""
    words = s.get('words') or []
    p = talk.plan(words, rec.db10(raw), len(raw) / RATE, talk.PAUSE_KEEP, s['text'], s.get('edits') or ()) if words \
        else dict(cuts=[], keep=[])
    kept = []
    for n, k in enumerate(p['keep']):  # a word after a cut filler that Whisper capitalised as if a sentence began
        w = list(words[k])
        if n and p['keep'][n - 1] != k - 1 and w[0][:1].isupper() and w[0] != 'I' and talk.base(w[0]) in talk.STOP \
                and not re.search(r'[.?!]["\')]*$', words[p['keep'][n - 1]][0]):
            w[0] = w[0][:1].lower() + w[0][1:]
        kept.append(w)
    return dict(cuts=p['cuts'], kept=kept, heard=' '.join(w for w, _, _ in words) if words else None,
                missing=[], extra=[], ok=None, like=talk.like_flag(kept, s['text']), fillers=talk.fillers(words),
                why={str(k): v for k, v in p.get('why', {}).items()}, keep=p['keep'],
                auto={k: v for k, v in p.get('auto', {}).items()}, restored=p.get('restored', []))


def para_lines(p, lines):
    return [dict(text=lines[g]['text'], bold=b) for g, b in zip(p['lines'], p['bold'])]


def check_talk(args, paras, lines, rdir, adir):
    """--check-para / --check-scene: one talk take checked for the recording pane, JSON on stdout and in
    <id>.check.json next to the take (FORMAT.md, Recorded voice, Talk)."""
    scene = bool(args.check_scene)
    want = args.check_scene or args.check_para
    mine = [p for p in paras if (p['sid'] if scene else p['id']) == want]
    take = current(rdir / ('scene' if scene else 'para'), want)
    key = 'sid' if scene else 'id'
    if not mine or not take:
        print(json.dumps({key: want, 'ok': False, 'error': 'no such ' + ('scene' if scene else 'paragraph') + ' in this video'
                          if not mine else f'no take {rdir / ("scene" if scene else "para") / (want + ".wav")}'}))
        sys.exit(1)
    s = talk_item(take, ' '.join(p['text'] for p in mine), 'scene' if scene else 'para', want)
    take_words([s], adir / 'rec' / 'words', args)
    load_edits(s, getattr(args, 'edit_dir', None))
    with tempfile.TemporaryDirectory() as td:
        raw = decode(take, Path(td) / 'raw.wav')
    pl = talk_plan(s, raw)
    short, _ = rec.shorten_pauses(rec.apply_cuts(raw, pl['cuts']), most=talk.PAUSE_MAX, keep=talk.PAUSE_KEEP)
    span = rec.voice_span(short)
    seconds = round((span[1] - span[0]) / RATE, 2) if span else 0.0
    heard = pl['heard'] or ''
    if scene:
        per, found, spans, _ = talk.paragraphs([para_lines(p, lines) for p in mine], pl['kept'])
        out_p = []
        for p, pts, sp in zip(mine, per, spans):
            pj, order_ok, missing = talk.summary(pts)
            out_p.append(dict(id=p['id'], para=p['para'], t0=pl['kept'][sp[0]][1] if sp else None,
                              t1=pl['kept'][sp[1]][2] if sp else None, points=pj, order_ok=order_ok, missing=missing))
        res = dict(sid=want, ok=all(x['order_ok'] and not x['missing'] for x in out_p), heard=heard, paras=out_p,
                   fillers=pl['fillers'], seconds=seconds)
    else:
        pj, order_ok, missing = talk.summary(talk.points(para_lines(mine[0], lines), pl['kept']))
        res = dict(id=want, ok=order_ok and not missing, heard=heard, points=pj, order_ok=order_ok, missing=missing,
                   fillers=pl['fillers'], seconds=seconds)
    if s.get('words') is None:
        res['ok'] = None
    body = json.dumps(res, ensure_ascii=False)
    take.with_name(f'{want}.check.json').write_text(body + '\n', encoding='utf-8')
    print(body)


def talk_settings(args):
    """-> (denoiser, tag): what a polished talk take depends on besides the take itself (its file name has both)."""
    den, tag = rec_settings(args)
    return den, h(tag, talk.TALK_VERSION, talk.PAUSE_MAX, talk.PAUSE_KEEP, talk.PROMPT_VERSION)[:8]


def polish_talk(items, tdir, args, den, tag):
    """Talk takes (talk_item) -> each polished once into tdir (cached under the take's hash and the settings, what was
    cut and heard in tdir/takes.json); sets s['cut_take'] and s['rec']. -> the items polished now."""
    tdir.mkdir(parents=True, exist_ok=True)
    meta_path = tdir / 'takes.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    take_words(items, tdir / 'words', args)  # cached by the take's hash: the editorial pass is checked against them
    for s in items:
        load_edits(s, getattr(args, 'edit_dir', None))
        # the editorial pass is part of the name: new edits polish this take again, and nothing else
        s['cut_take'] = tdir / (f'{s["take_hash"]}-{tag}' + (f'-e{s["edit_tag"]}' if s['edit_tag'] else '') + '.wav')
    todo, seen = [], set()
    for s in items:
        if (s['cut_take'].name not in meta or not s['cut_take'].exists()) and s['cut_take'] not in seen:
            todo.append(s); seen.add(s['cut_take'])
    if todo:
        print(f'polishing {len(todo)} talk take(s) (denoise: {den}) ...', flush=True)
        made = polish_takes(todo, tdir, args, den)
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}  # another run may have added some
        meta.update(made)
        meta_path.write_text(json.dumps(meta, indent=0, sort_keys=True))
    for s in items:
        s['rec'] = meta[s['cut_take'].name]
    return todo


def plosives(pcm, td):
    """What the de-plosive (DEPLOSIVE, in REC_DYN) does to a take. -> (bursts, voice): bursts [(t, dB)] are the p and b
    pops: runs of 80 ms or less, starting sharply, where the sound is as loud as voiced speech and the band under 100 Hz
    carries most of it (within 4 dB of the whole band; in speech it is about 12 dB under), at their start in seconds, with the
    most the de-plosive took off the band under 200 Hz there; voice is the median dB it took off that band over the
    rest of the voice. Per 10 ms, the take with and without DEPLOSIVE, as given (not denoised: near enough, the
    denoiser takes at most 12 dB off, and off the room tone, not off a pop)."""
    src = td / 'plos-in.wav'
    write_pcm(src, pcm)
    out = []
    for name, af in (('a', 'highpass=f=80,lowpass=f=200'), ('b', f'highpass=f=80,{DEPLOSIVE},lowpass=f=200'),
                     ('v', 'lowpass=f=100')):
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', af, '-c:a', 'pcm_s16le',
                            str(td / f'plos-{name}.wav')], capture_output=True, text=True)
        if r.returncode:
            return [], None
        out.append(rec.db10(read_pcm(td / f'plos-{name}.wav')))
    a, b, v = out
    full = rec.db10(pcm)
    n = min(len(a), len(b), len(v), len(full))
    vfloor = rec.thresholds(v)[1]
    _, _, hi, lo = rec.thresholds(full)
    hits = [k for k in range(n) if v[k] > vfloor + 20 and v[k] >= full[k] - 4 and full[k] > hi]
    runs = []
    for k in hits:
        if runs and k - runs[-1][-1] <= 3:
            runs[-1].append(k)
        else:
            runs.append([k])
    # a pop starts sharply (6 dB up under 100 Hz within 30 ms); a word dying away, where the low band lasts longest, does not
    runs = [r for r in runs if r[-1] - r[0] < 8 and r[0] >= 3 and v[r[0]] - min(v[r[0] - 3:r[0]]) >= 6]
    burst = {q for r in runs for q in range(r[0] - 2, r[-1] + 3)}
    rest = sorted(a[k] - b[k] for k in range(n) if full[k] > lo and k not in burst)
    return ([(r[0] / 100, round(max(a[q] - b[q] for q in range(r[0], r[-1] + 2) if q < n), 1)) for r in runs],
            round(rest[len(rest) // 2], 1) if rest else None)


def mp3(src, dst):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-c:a', 'libmp3lame', '-q:a', '2', str(dst)],
                       capture_output=True, text=True)
    if r.returncode:
        die(f'ffmpeg could not write {dst}: {r.stderr.strip()[-300:]}')


def clock(t):
    return f'{int(t // 60)}:{t % 60:05.2f}'


def polish_preview(args, scenes, paras, lines, rdir, adir):
    """--polish-preview: one scene take (sid) or punch-in (paragraph id) polished as the build polishes it, before any
    picture or subtitle is made, for the author to listen to: rdir/preview/<sid>-raw.mp3, <sid>-polished.mp3 and
    <sid>-polish.md (what was cut or changed, at what time in the raw take; the transcript cleaned; the points missing
    or out of order; "like"; loudness). The polished take lands in the build's cache (audio/rec/), so the build that
    follows does not polish it again (FORMAT.md, Recorded voice, Talk)."""
    want = args.polish_preview
    mine = [p for p in paras if p['sid'] == want]
    kind, take = 'scene', current(rdir / 'scene', want) if mine else None
    if not take and any(p['id'] == want for p in paras):
        mine = [p for p in paras if p['id'] == want]
        kind, take = 'para', current(rdir / 'para', want)
    if not mine:
        die(f'{want} is no scene (sid) or paragraph (id) of this video; --list-paragraphs prints them')
    if not take:
        die(f'no take {rdir / kind / (want + ".wav")}')
    s = talk_item(take, ' '.join(p['text'] for p in mine), kind, want)
    tdir = adir / 'rec'
    take_words([s], tdir / 'words', args)
    den, tag = talk_settings(args)
    fresh = polish_talk([s], tdir, args, den, tag)
    m = s['rec']
    pdir = rdir / 'preview'
    pdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        raw = decode(take, td / 'raw.wav')
        pl = talk_plan(s, raw)
        loud_raw = ebur128(td / 'raw.wav')
        mp3(td / 'raw.wav', pdir / f'{want}-raw.mp3')
        loud = normalise(s['cut_take'], td / 'pol.wav', LOUDNESS)  # as the build sets every clip
        mp3(td / 'pol.wav', pdir / f'{want}-polished.mp3')
        pol = read_pcm(td / 'pol.wav')
        plos, plos_voice = plosives(rec.apply_cuts(raw, pl['cuts']), td)
    words = s.get('words') or []
    cuts = pl['cuts']
    rows = []  # (start, end, what, detail), seconds in the raw take
    for t0, t1, why in cuts:
        said = [w for w, a, b in words if t0 <= (a + b) / 2 <= t1]
        rows.append((t0, t1, why, '"' + ' '.join(said) + '"' if said else ''))
    runs = []  # the words the editorial pass kept against an automatic cut
    for k in pl.get('restored', []):
        if runs and runs[-1][-1] == k - 1:
            runs[-1].append(k)
        else:
            runs.append([k])
    for r in runs:
        rows.append((words[r[0]][1], words[r[-1]][2], 'edit: kept',
                     f'"{" ".join(words[k][0] for k in r)}" (was cut: {pl["auto"].get(r[0], "?")})'))
    for a, b in m.get('pauses') or []:
        rows.append((to_take_time(a, cuts), to_take_time(b, cuts), 'pause shortened',
                     f'{b - a + talk.PAUSE_KEEP:.2f} s → {talk.PAUSE_KEEP:.2f} s'))
    for t, db in plos:
        t = to_take_time(t, cuts)
        w = next((w for w, a, b in words if a - 0.05 <= t <= b + 0.05), '')
        rows.append((t, None, 'plosive', f'{db:.0f} dB off under 200 Hz' + (f', in "{w}"' if w else '')))
    rows.sort(key=lambda r: r[0])
    kept = pl['kept']
    # the points against the script
    issues, heard_parts, n_pts = [], [], 0
    if kind == 'scene':
        per, found, spans, pcuts = talk.paragraphs([para_lines(p, lines) for p in mine], kept)
        bounds = sorted(i for i, _ in pcuts.values())
        at = 0
        segs = []
        for i in bounds + [len(kept) - 1]:
            segs.append(kept[at:i + 1]); at = i + 1
        labels = [p for p, f in zip(mine, found) if f]
        heard_parts = list(zip(labels, segs)) if labels else [(None, kept)]
    else:
        per = [talk.points(para_lines(mine[0], lines), kept)]
        heard_parts = [(mine[0], kept)]
    for p, pts in zip(mine, per):
        _, order_ok, missing = talk.summary(pts)
        n_pts += len(pts)
        for q in pts:
            txt = lines[p['lines'][q['k']]]['text']
            if not q['said']:
                issues.append(f'- missing: paragraph {p["para"]}, point {q["k"] + 1}: "{txt}"')
            elif q['order'] is False:
                issues.append(f'- not found in order: paragraph {p["para"]}, point {q["k"] + 1}; nearest match out of order at '
                              f'{clock(q["t"])} (check it was said): "{txt}"')
        if order_ok is False and not any(q['order'] is False for q in pts if q['said']):
            issues.append(f'- out of order in time: paragraph {p["para"]} ("{p["text"][:50]}…")')
    n_like, dens, flagged = pl['like']
    likes = [clock(a) for w, a, b in kept if rec.norm(w) == 'like']
    pk_raw, f_raw = rec.thresholds(rec.db10(raw))[:2]
    pk_pol, f_pol = rec.thresholds(rec.db10(pol))[:2]
    title = scenes[mine[0]['scene']]['title']
    what = f'scene "{title}"' if kind == 'scene' else f'punch-in, paragraph {mine[0]["para"]} of "{title}"'
    counts = {}
    for r in rows:
        counts[r[2]] = counts.get(r[2], 0) + 1
    md = [f'# Polish preview: {what}', '',
          f'Take `{take}` ({len(raw) / RATE:.1f} s) → polished {m["dur"]:.1f} s. '
          f'Listen: `{want}-raw.mp3`, `{want}-polished.mp3` (next to this file).',
          f'Denoise: {den}. Polished {"now" if fresh else "earlier (from the build cache)"}: '
          f'`{s["cut_take"].relative_to(ROOT) if s["cut_take"].is_relative_to(ROOT) else s["cut_take"]}`; '
          f'the build uses it as is.',
          'Editorial pass: ' + (f'`{edit_report(s["edit_rep"], want)}`'.replace('\n          ', '`; `') if s.get('edit_rep')
                                else f'none (`{args.edit_dir.relative_to(ROOT) if args.edit_dir.is_relative_to(ROOT) else args.edit_dir}/{want}.json`; '
                                     f'--edit-draft {want} to write one).'), '']
    if s.get('words') is None:
        md += ['**No Whisper** (no venv at --whisper-python): nothing was cut, the points were not checked.', '']
    md += ['## Verdict', '',
           ('All ' + str(n_pts) + ' points said, in order.' if not issues else f'{len(issues)} of {n_pts} points need a look (below).')
           + ' Changes: ' + (', '.join(f'{v} {k}' for k, v in sorted(counts.items())) or 'none') + '.'
           + (f' "like" is dense ({n_like}, one in {1 / dens:.0f} words).' if flagged else ''), '',
           '## Cut or changed (times in the raw take)', '']
    if rows:
        md += ['| at | to | what | words / detail |', '| --- | --- | --- | --- |']
        md += [f'| {clock(a)} | {clock(b) if b is not None else ""} | {w} | {d} |' for a, b, w, d in rows]
    else:
        md += ['Nothing.']
    md += ['', 'filler: um, uh, er, hmm (cut). stutter: a word or fragment said twice, the first copy cut. restart: a '
           'false start, cut back to the last attempt. edit: the editorial pass (edit/<sid>.json) cut it, or kept words '
           'an automatic cut took. pause shortened: over '
           f'{talk.PAUSE_MAX} s, cut to {talk.PAUSE_KEEP} s. plosive: a p or b burst pulled down (nothing cut).'
           + (f' Away from bursts the de-plosive took a median {plos_voice:.0f} dB off the voice under 200 Hz.'
              if plos_voice is not None else ''),
           '', '## Points against the script', '']
    md += issues or [f'All {n_pts} points found, in order.']
    md += ['', '## "like"', '',
           f'{n_like} beyond the script\'s own, one in {1 / dens:.0f} words heard' if n_like else 'None beyond the script\'s own.']
    if n_like:
        md[-1] += (f': **flagged** (more than one in {round(1 / talk.LIKE_DENSITY)}).' if flagged else
                   f': fine (flagged above one in {round(1 / talk.LIKE_DENSITY)}).') + ' Every "like" heard: ' + ', '.join(likes) + '.'
    md += ['', f'Fillers (um, uh, er, hmm) heard: {pl["fillers"]}, all cut.', '',
           '## Loudness', '', '| | raw | polished |', '| --- | --- | --- |',
           f'| integrated | {loud_raw[0]:.1f} LUFS | {loud["lufs_out"]:.1f} LUFS |',
           f'| true peak | {loud_raw[1]:.1f} dBTP | {loud["peak_out"]:.1f} dBTP |',
           f'| voice above room tone | {pk_raw - f_raw:.0f} dB | {pk_pol - f_pol:.0f} dB |', '',
           f'Polished = what the build puts on the timeline: denoised, levelled, compressed, set to {LOUDNESS:.0f} LUFS '
           f'(peaks at most {PEAK} dBTP{", a few limited" if loud["limited"] else ""}).', '',
           '## Heard, cleaned', '']
    for p, seg in heard_parts:
        txt = ' '.join(w for w, _, _ in seg).strip()
        if p is not None and kind == 'scene':
            md += [f'**Paragraph {p["para"]}** ({clock(seg[0][1]) if seg else "-"}): {txt[:1].upper() + txt[1:]}', '']
        else:
            md += [txt[:1].upper() + txt[1:] if txt else '(nothing heard)', '']
    (pdir / f'{want}-polish.md').write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    print(f'{pdir / (want + "-raw.mp3")}\n{pdir / (want + "-polished.mp3")}\n{pdir / (want + "-polish.md")}')
    print(md[md.index('## Verdict') + 2])


# ---------- the editorial pass: what a human editor cuts or keeps in a talk take (FORMAT.md, Recorded voice, Talk) ----------

def edit_dir(scenes_path, video):
    """edit/ next to the scenes file if it is there, else source/courses/<video>/edit/."""
    near = scenes_path.parent / 'edit'
    return near if near.is_dir() else ROOT / 'source/courses' / video / 'edit'


def load_edits(s, edir):
    """A talk take's editorial pass, edir/<key>.json: {"take": <take hash>, "edits": [{"op": "cut"|"keep", "from": i,
    "to": j, "heard": "<words i..j>", "why": "..."}]}, on the word indexes of the take's transcript before any cut
    (s['words'], as --edit-draft shows them). Sets s['edits'] (the ones that apply, for talk.plan), s['edit_tag'] (a
    hash of them, part of the polished take's name: '' when none) and s['edit_rep'] (None without a file). An edit
    applies when its range is in the transcript, its "heard" words are the words there (case and punctuation aside;
    no "heard" is not checked) and it does not overlap an edit before it. A file for another take is not applied."""
    s['edits'], s['edit_tag'], s['edit_rep'] = [], '', None
    f = Path(edir) / f'{s["key"]}.json' if edir else None
    if f is None or not f.exists():
        return
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        die(f'{f}: {e}')
    edits = data.get('edits', [])
    rep = s['edit_rep'] = dict(file=f, take=data.get('take'), stale=data.get('take') != s['take_hash'], edits=[], applied=0)
    if rep['stale']:
        rep['edits'] = [(e, 'stale') for e in edits]
        return
    words = s.get('words') or []
    taken = set()
    for e in edits:
        op, a, b = e.get('op'), e.get('from'), e.get('to')
        if op not in ('cut', 'keep') or not isinstance(a, int) or not isinstance(b, int) or not 0 <= a <= b < len(words):
            rep['edits'].append((e, 'not applied: op must be cut or keep, from..to word indexes of the transcript')); continue
        want = [x for x in (talk.base(w) for w in str(e.get('heard', '')).split()) if x]
        got = [x for x in (talk.base(w[0]) for w in words[a:b + 1]) if x]
        if want and want != got:
            rep['edits'].append((e, f'not applied: the words at {a}..{b} are "{" ".join(w[0] for w in words[a:b + 1])}"'))
            continue
        if taken & set(range(a, b + 1)):
            rep['edits'].append((e, 'not applied: overlaps another edit')); continue
        taken |= set(range(a, b + 1))
        s['edits'].append({'op': op, 'from': a, 'to': b, 'why': str(e.get('why', ''))})
        rep['edits'].append((e, 'applied'))
    rep['applied'] = len(s['edits'])
    if s['edits']:
        s['edit_tag'] = h(talk.EDIT_VERSION, talk.EDIT_PAUSE, json.dumps([[e['op'], e['from'], e['to']] for e in s['edits']]))[:6]


def edit_report(rep, key):
    """One line for the build's report (and the previews) about a take's editorial pass."""
    rel = rep['file'].relative_to(ROOT) if rep['file'].is_relative_to(ROOT) else rep['file']
    if rep['stale']:
        return (f'{rel}: written for take {rep["take"]}, not this one (the take was recorded again): not applied; '
                f'--edit-draft {key} to edit the new take')
    bad = [(e, st) for e, st in rep['edits'] if st != 'applied']
    return (f'{rel}: {rep["applied"]} of {len(rep["edits"])} edit(s) applied'
            + ''.join(f'\n          {e.get("op")} {e.get("from")}..{e.get("to")} "{e.get("heard", "")}": {st}' for e, st in bad))


def talk_take(want, paras, rdir):
    """A scene sid or paragraph id -> (its paragraphs, 'scene' or 'para', its current take); dies when there is none."""
    mine = [p for p in paras if p['sid'] == want]
    kind, take = 'scene', current(rdir / 'scene', want) if mine else None
    if not take and any(p['id'] == want for p in paras):
        mine = [p for p in paras if p['id'] == want]
        kind, take = 'para', current(rdir / 'para', want)
    if not mine:
        die(f'{want} is no scene (sid) or paragraph (id) of this video; --list-paragraphs prints them')
    if not take:
        die(f'no take {rdir / kind / (want + ".wav")}')
    return mine, kind, take


def edit_draft(args, scenes, paras, lines, rdir, adir):
    """--edit-draft: a talk take's whole transcript before any cut, every word with its index and time, the automatic
    cuts marked (and the editorial pass, if there is one), by paragraph next to the script's lines, for whoever writes
    its editorial pass (edit/<key>.json). Writes <rec-dir>/preview/<key>-edit-draft.md. No audio is changed."""
    want = args.edit_draft
    mine, kind, take = talk_take(want, paras, rdir)
    s = talk_item(take, ' '.join(p['text'] for p in mine), kind, want)
    take_words([s], adir / 'rec' / 'words', args)
    words = s.get('words') or []
    if not words:
        die('no words heard (no Whisper?): nothing to edit')
    load_edits(s, args.edit_dir)
    with tempfile.TemporaryDirectory() as td:
        raw = decode(take, Path(td) / 'raw.wav')
    pl = talk_plan(s, raw)
    keep, auto, final = pl['keep'], pl['auto'], {int(k): v for k, v in pl['why'].items()}
    # the paragraphs over the words kept, their borders moved back to the transcript's indexes
    if kind == 'scene':
        _, found, _, pcuts = talk.paragraphs([para_lines(p, lines) for p in mine], pl['kept'])
        labels = [p for p, f in zip(mine, found) if f]
        starts = [0] + [keep[j] for _, j in sorted(pcuts.values())]
    else:
        labels, starts = mine, [0]
    if not labels:
        labels, starts = mine[:1], [0]
    edited = {}
    for e in s['edits']:
        for k in range(e['from'], e['to'] + 1):
            edited[k] = e
    title = scenes[mine[0]['scene']]['title']
    rel = lambda x: x.relative_to(ROOT) if x.is_relative_to(ROOT) else x
    efile = args.edit_dir / f'{want}.json'
    md = [f'# Edit draft: {"scene" if kind == "scene" else "punch-in, paragraph " + str(mine[0]["para"]) + " of"} "{title}"', '',
          f'Take `{rel(take)}`, hash `{s["take_hash"]}`, {len(raw) / RATE:.1f} s: its {len(words)} words as Whisper heard '
          'them, before any cut. `n` before a word is its index (count on from it), then its time in the take as recorded.',
          '', f'Editorial pass: `{rel(efile)}`: ' + ('none yet.' if s['edit_rep'] is None else
                                                     edit_report(s['edit_rep'], want).split(': ', 1)[1].replace('\n          ', '; ')),
          '', 'Marks: ~~words~~ ⟨why⟩ the polish cuts them (filler, stutter, restart: automatic; edit: the editorial pass); '
          '⟪words⟫ ⟨kept⟩ an automatic cut the editorial pass undoes; ‖1.4 s‖ a pause (0.5 s or more) before the next word.',
          '', 'Write the editorial pass as below: `cut` or `keep` the words `from`..`to` (indexes here, both included), '
          '`heard` the words there (checked), `why` one of repeat, slip, fragment, over-cut restored, splice. Keep the best '
          'take of an idea said twice (or splice its best halves), cut slips and fragments, restore what the automatic '
          'cuts took that was meant; keep the author\'s style (like, so) and pauses.', '', '```json',
          json.dumps(dict(take=s['take_hash'], sid=want, edits=[{'op': 'cut', 'from': 0, 'to': 0, 'heard': words[0][0],
                                                                    'why': 'fragment'}]), ensure_ascii=False), '```', '']

    def text(a, b):  # words a..b-1 as lines: a new line after a sentence end, a pause of 0.5 s or more, or 12 words
        out, cur, n = [], [], 0
        k = a
        while k < b:
            if not cur:
                cur.append(f'- `{k}` {clock(words[k][1])} ·'); n = 0
            tag = final.get(k)
            mark = lambda q: (final.get(q), q in pl['restored'], id(edited.get(q)))
            j = k
            if tag or k in pl['restored']:  # a run of words with the same mark, up to a pause
                while j + 1 < b and mark(j + 1) == mark(k) and words[j + 1][1] - words[j][2] < 0.5:
                    j += 1
            run = ' '.join(words[q][0].replace('|', '\\|') for q in range(k, j + 1))
            if tag:
                cur.append(f'~~{run}~~ ⟨{tag}⟩')
            elif k in pl['restored']:
                cur.append(f'⟪{run}⟫ ⟨kept: was {auto.get(k, "cut")}⟩')
            else:
                cur.append(run)
            n += j - k + 1
            gap = words[j + 1][1] - words[j][2] if j + 1 < len(words) else 0
            if gap >= 0.5:
                cur.append(f'‖{gap:.1f} s‖')
            if j + 1 >= b or gap >= 0.5 or n >= 12 or re.search(r'[.?!]["\')]*$', words[j][0]):
                out.append(' '.join(cur)); cur = []
            k = j + 1
        if cur:
            out.append(' '.join(cur))
        return out
    for p, a, b in zip(labels, starts, starts[1:] + [len(words)]):
        md += [f'## Paragraph {p["para"]} ({clock(words[a][1])} to {clock(words[b - 1][2])})', '', 'Script:', '']
        md += [f'> {k + 1}. {lines[g]["text"]}' for k, g in enumerate(p['lines'])]
        md += ['', 'Heard:', ''] + text(a, b) + ['']
    missing = [p for p in mine if p not in labels]
    if missing:
        md += ['Not found in the take (their words, if said, are in the paragraphs above): '
               + ', '.join(str(p['para']) for p in missing) + '.', '']
    dst = rdir / 'preview' / f'{want}-edit-draft.md'
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    print(dst)
    if s['edit_rep']:
        print(edit_report(s['edit_rep'], want))


# ---------- subtitle proofreading: corrections to what Whisper heard, per take (FORMAT.md, Recorded voice, Talk) ----------

FIX_NEAR = 8   # an edit whose words are not at its "at" is looked for this many words either side (the take's words moved)


def fix_dir(scenes_path, video):
    """subs-fix/ next to the scenes file if it is there, else source/courses/<video>/subs-fix/."""
    near = scenes_path.parent / 'subs-fix'
    return near if near.is_dir() else ROOT / 'source/courses' / video / 'subs-fix'


def subs_fix(words, key, take_hash, fdir, keep=None):
    """A talk take's words as kept (s['rec']['words']: [[word, t0, t1]]) -> (words corrected, report or None).
    fdir/<key>.json (key: the scene's sid, or a punch-in's paragraph id) is {"take": <take hash>, "edits": [{"at": <index
    of the first heard word>, "from": "<heard words>", "to": "<corrected words>"}]}; indexes are into the words as kept,
    before any edit. An edit applies where its "from" words are (compared without case and punctuation), at "at" or up to
    FIX_NEAR words from it; "to" "" removes them, "from" "" inserts before word "at". The new words share the time of the
    words they replace by letter count, so cues stay in sync. A file for another take (its "take" is not this one) is
    not applied. An edit may also carry "raw": the index of its first word in the take's transcript before any cut (as
    --edit-draft shows it); with keep (the raw index of each word kept, s['rec']['keep']) it is looked for there first,
    so it stays in place when the editorial pass changes which words are kept.
    report: dict(file, take, stale, edits: [(edit, index or None, status)], applied)."""
    f = fdir / f'{key}.json'
    if not f.exists():
        return words, None
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        die(f'{f}: {e}')
    edits = data.get('edits', [])
    rep = dict(file=f, take=data.get('take'), stale=data.get('take') != take_hash, edits=[], applied=0)
    if rep['stale']:
        rep['edits'] = [(e, None, 'stale') for e in edits]
        return words, rep
    out = [list(w) for w in words]
    keys = [talk.base(w[0]) for w in out]
    taken, todo = set(), []
    for e in edits:
        frm = [talk.base(x) for x in str(e.get('from', '')).split()]
        n, at = len(frm), int(e.get('at', 0))
        if keep and isinstance(e.get('raw'), int):
            at = next((q for q, r in enumerate(keep) if r >= e['raw']), at)
        i = next((at + d for d in sorted(range(-FIX_NEAR, FIX_NEAR + 1), key=abs)
                  if 0 <= at + d and at + d + n <= len(out) and keys[at + d:at + d + n] == frm), None)
        if n == 0:
            i = at if 0 <= at <= len(out) else None
        if i is None:
            rep['edits'].append((e, None, 'not found')); continue
        span = set(range(i, i + n)) if n else {i - 0.5}
        if span & taken:
            rep['edits'].append((e, i, 'overlaps another edit')); continue
        taken |= span
        todo.append((i, n, e))
        rep['edits'].append((e, i, 'applied'))
    for i, n, e in sorted(todo, key=lambda x: -x[0]):
        new = str(e.get('to', '')).split()
        if n:
            t0, t1 = out[i][1], out[i + n - 1][2]
        else:
            t0 = t1 = out[i][1] if i < len(out) else (out[-1][2] if out else 0.0)
        tot, acc, rows = sum(len(x) + 1 for x in new), 0, []
        for x in new:
            a = t0 + (t1 - t0) * acc / max(tot, 1)
            acc += len(x) + 1
            rows.append([x, round(a, 3), round(t0 + (t1 - t0) * acc / max(tot, 1), 3)])
        out[i:i + n] = rows
    rep['applied'] = len(todo)
    return out, rep


def fix_report(rep, key):
    """One line for the build's report about a take's corrections file."""
    rel = rep['file'].relative_to(ROOT) if rep['file'].is_relative_to(ROOT) else rep['file']
    if rep['stale']:
        return (f'{rel}: written for take {rep["take"]}, not this one (the take was recorded again): not applied; '
                f'--subs-draft {key} to proofread the new take')
    bad = [(e, st) for e, _, st in rep['edits'] if st != 'applied']
    return (f'{rel}: {rep["applied"]} of {len(rep["edits"])} correction(s) applied'
            + ''.join(f'\n          {st}: at {e.get("at")} "{e.get("from", "")}" -> "{e.get("to", "")}"' for e, st in bad))


def subs_draft(args, scenes, paras, lines, rdir, adir, fdir):
    """--subs-draft: one scene take (sid) or punch-in (id) as heard and kept (the words the subtitles are made of, with
    their indexes) next to the script, line by line, for whoever writes its corrections file (FORMAT.md, Recorded
    voice, Talk). Polishes the take if the build's cache does not have it yet. Writes <rec-dir>/preview/<key>-subs-draft.md."""
    want = args.subs_draft
    mine = [p for p in paras if p['sid'] == want]
    kind, take = 'scene', current(rdir / 'scene', want) if mine else None
    if not take and any(p['id'] == want for p in paras):
        mine = [p for p in paras if p['id'] == want]
        kind, take = 'para', current(rdir / 'para', want)
    if not mine:
        die(f'{want} is no scene (sid) or paragraph (id) of this video; --list-paragraphs prints them')
    if not take:
        die(f'no take {rdir / kind / (want + ".wav")}')
    s = talk_item(take, ' '.join(p['text'] for p in mine), kind, want)
    den, tag = talk_settings(args)
    polish_talk([s], adir / 'rec', args, den, tag)
    words = s['rec'].get('words') or []
    if not words:
        die('no words heard (no Whisper?): nothing to proofread')
    _, rep = subs_fix(words, want, s['take_hash'], fdir, s['rec'].get('keep'))
    # where each script line was said: its heard words run from its point's first word to the next found point's
    if kind == 'scene':
        per, _, _, _ = talk.paragraphs([para_lines(p, lines) for p in mine], words)
    else:
        per = [talk.points(para_lines(mine[0], lines), words)]
    flat = [(p, q) for p, pts in zip(mine, per) for q in pts]
    starts = sorted({q['w0'] for _, q in flat if q['said'] and q['order']} | {0})
    owner = {}  # first word index -> (paragraph, point) it opens
    for p, q in flat:
        if q['said'] and q['order']:
            owner.setdefault(q['w0'], (p['para'], q['k']))
    first_said = next(((p['para'], q['k']) for p, q in flat if q['said'] and q['order']), None)
    if first_said:
        owner[0] = first_said
    spans = {}
    for a, b in zip(starts, starts[1:] + [len(words)]):
        if a in owner:
            spans[owner[a]] = (a, b)

    keep = s['rec'].get('keep')

    def heard(a, b):  # the words a..b-1, an index before the first, after each clause end and every 6 words
        out, run = [], 0
        for i in range(a, b):
            if i == a or run >= 6 or re.search(r'[,;:.!?]["\')]*$|\.\.\.$', words[i - 1][0]):
                out.append(f'`{i}/{keep[i]}`' if keep else f'`{i}`'); run = 0
            out.append(words[i][0].replace('|', '\\|')); run += 1
        return ' '.join(out)
    title = scenes[mine[0]['scene']]['title']
    rel = lambda x: x.relative_to(ROOT) if x.is_relative_to(ROOT) else x
    md = [f'# Subtitle draft: {"scene" if kind == "scene" else "punch-in, paragraph " + str(mine[0]["para"]) + " of"} "{title}"', '',
          f'Take `{rel(take)}`, hash `{s["take_hash"]}`: {len(words)} words as kept after the polish (fillers, stutters, '
          'restarts cut). These words, with these indexes, are what the subtitles, spoken.md and the FCPXML captions are made of.',
          '', f'Corrections file: `{rel(fdir / (want + ".json"))}`: '
          + ('none yet.' if rep is None else fix_report(rep, want).split(': ', 1)[1].replace('\n          ', '; ')), '',
          'Write it as below. `at` is the index of the first heard word (the `n` before a word marks its index; count on '
          'from it); `raw` its index in the take\'s transcript before any cut (the `r` of `n/r`; count on from it, '
          'skipping the words cut: --edit-draft shows them); `from` the heard words exactly as shown (case and punctuation do not matter); `to` what the subtitle '
          'should say (`""` removes the words). Fix what Whisper misheard (the script says what was meant), names, '
          'fragments left by a cut restart, and light grammar; keep the author\'s own wording.', '', '```json',
          json.dumps(dict(take=s['take_hash'], sid=want, scene=title, edits=[dict(at=0, raw=keep[0] if keep else 0,
                                                                                 **{'from': words[0][0], 'to': words[0][0]})]),
                     ensure_ascii=False), '```', '']
    for p, pts in zip(mine, per):
        md += [f'## Paragraph {p["para"]}', '', '| | script | heard |', '| --- | --- | --- |']
        for q in pts:
            txt = lines[p['lines'][q['k']]]['text'].replace('|', '\\|')
            sp = spans.get((p['para'], q['k']))
            cell = heard(*sp) if sp else ('*(not found in order; its words, if said, are in the row before)*' if not q['said']
                                          else '*(found only out of order; in the row before)*')
            md.append(f'| {q["k"] + 1} | {txt} | {cell} |')
        md.append('')
    dst = rdir / 'preview' / f'{want}-subs-draft.md'
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    print(dst)
    if rep:
        print(fix_report(rep, want))


def talk_chunks(paras, units, lines, args, adir, rdir):
    """--voice rec with talk takes: the clips, one or more per scene. A scene take is polished as a whole, its points
    aligned over what was said, and it is cut into its paragraphs at the pause between them; a run of paragraphs from
    one scene take is one clip (back to back in the timeline, the author's own pauses between them). A paragraph take
    (a punch-in) replaces its paragraph; a paragraph in neither is spoken by the --rec-missing voice from the script.
    units[i] is paragraph i. -> (chunks, filled units, takes polished now, notes)."""
    tdir = adir / 'rec'
    den, tag = talk_settings(args)
    items, by_scene, by_para = [], {}, {}
    for si in sorted({p['scene'] for p in paras}):
        mine = [p for p in paras if p['scene'] == si]
        f = current(rdir / 'scene', mine[0]['sid'])
        if f:
            by_scene[si] = talk_item(f, ' '.join(p['text'] for p in mine), 'scene', mine[0]['sid'])
            items.append(by_scene[si])
    stale = []
    for p in paras:
        f = current(rdir / 'para', p['id'])
        if f and punch_in_used(f, by_scene.get(p['scene'])):
            by_para[p['para']] = talk_item(f, p['text'], 'para', p['id'])
            items.append(by_para[p['para']])
        elif f:
            stale.append(p)
    notes = [f'punch-in older than the scene take, unused: paragraph {p["para"]} ({p["id"]}): {p["text"][:50]}' for p in stale]
    todo = polish_talk(items, tdir, args, den, tag)
    # the take's proofread corrections (subs-fix/<sid|id>.json), before anything reads its words: paragraphs, pictures,
    # subtitles, spoken.md and the FCPXML captions all see the corrected words, on the same times
    args.fix_reports, args.edit_reports = [], []
    seen_fix = set()
    for s in items:
        if s['cut_take'].name + s['key'] in seen_fix:
            continue
        seen_fix.add(s['cut_take'].name + s['key'])
        fixed, rep = subs_fix(s['rec'].get('words') or [], s['key'], s['take_hash'], args.fix_dir, s['rec'].get('keep'))
        if rep:
            s['rec'] = dict(s['rec'], words=fixed)
            args.fix_reports.append((s['key'], rep))
        if s.get('edit_rep'):
            args.edit_reports.append((s['key'], s['edit_rep']))
    # where each paragraph comes from
    src = {}
    for si, s in by_scene.items():
        mine = [p for p in paras if p['scene'] == si]
        words = s['rec'].get('words') or []
        per, found, spans, cuts = talk.paragraphs([para_lines(p, lines) for p in mine], words)
        s['found'] = found
        s['cuts'] = cuts
        s['order'] = [p['para'] for p in mine]
        for p, pts, f in zip(mine, per, found):
            if f:
                src[p['para']] = ('scene', s, pts)
            elif p['para'] not in by_para:
                notes.append(f'not found in the scene take: {p["text"][:60]}')
    for pi, s in by_para.items():
        p = paras[pi]
        src[pi] = ('para', s, talk.points(para_lines(p, lines), s['rec'].get('words') or []))
    missing = [p for p in paras if p['para'] not in src]
    if missing and args.rec_missing == 'stop':
        die(f'{len(missing)} of {len(paras)} paragraphs have no take (no scene take with them in it, no paragraph take) in {rdir}:\n'
            + '\n'.join(f'  {p["scene"]}, paragraph {p["para"]} ({p["id"]}, scene {p["sid"]}): {p["text"][:70]}' for p in missing)
            + '\nrecord them, or add --rec-missing tts to speak them with the default voice for a preview')
    # the clips
    chunks = []

    def quiet_cut(s, i):  # the cut between word i and i+1 of a scene take's piece: the quietest point in the pause
        w = s['rec']['words']
        if 'db' not in s:
            s['db'] = rec.db10(read_pcm(s['cut_take']))
        a, b = w[i][2], w[i + 1][1]
        return rec.quiet(s['db'], a - 0.05, max(b, a) + 0.05, (a + max(a, b)) / 2)

    k = 0
    while k < len(paras):
        p = paras[k]
        kind = src[p['para']][0] if p['para'] in src else 'fill'
        if kind == 'scene':  # a run of paragraphs from one scene take, in the take's order
            s = src[p['para']][1]
            run = [p]
            while k + len(run) < len(paras):
                q = paras[k + len(run)]
                if q['scene'] != p['scene'] or src.get(q['para'], (None,))[0] != 'scene':
                    break
                run.append(q)
            found_order = [pi for pi, f in zip(s['order'], s['found']) if f]
            w = s['rec']['words']
            first, last = found_order.index(run[0]['para']), found_order.index(run[-1]['para'])
            b0 = 0.0 if first == 0 else quiet_cut(s, s['cuts'][(s['order'].index(found_order[first - 1]),
                                                                 s['order'].index(run[0]['para']))][0])
            b1 = s['rec']['dur'] if last == len(found_order) - 1 else quiet_cut(
                s, s['cuts'][(s['order'].index(run[-1]['para']), s['order'].index(found_order[last + 1]))][0])
            bounds = []
            for a_, b_ in zip(run, run[1:]):
                i, j = s['cuts'][(s['order'].index(a_['para']), s['order'].index(b_['para']))]
                bounds.append((w[i][2] - b0, w[j][1] - b0))
            cw = [[x, round(t0 - b0, 3), round(t1 - b0, 3)] for x, t0, t1 in w if b0 <= (t0 + t1) / 2 < b1]
            pts = [[dict(q, t=None if q['t'] is None else round(q['t'] - b0, 3)) for q in src[r['para']][2]] for r in run]
            key = 'talk-' + h('scene', s['cut_take'].name, b0, b1)
            c = dict(key=key, raw=adir / f'{key}.wav', talk=True, take=s, words=cw, bounds=bounds, pts=pts,
                     paras=[r['para'] for r in run], cut=(b0, b1))
            k += len(run)
        elif kind == 'para':
            s = src[p['para']][1]
            key = 'talk-' + h('para', s['cut_take'].name)
            c = dict(key=key, raw=adir / f'{key}.wav', talk=True, take=s, words=s['rec'].get('words') or [], bounds=[],
                     pts=[src[p['para']][2]], paras=[p['para']], cut=(0.0, s['rec']['dur']))
            k += 1
        else:
            c = dict(fill=True, paras=[p['para']], text=p['text'])
            k += 1
        c['sents'] = c['paras']
        c['scene'], c['para'], c['line'] = p['scene'], p['para'], p['line']
        c['text'] = ' '.join(paras[i]['text'] for i in c['paras'])
        c['around'] = ('', '')
        for i in c['paras']:
            units[i]['chunk'] = len(chunks)
        chunks.append(c)
    made = []
    for c in chunks:
        if c.get('talk'):
            c['wav'] = adir / f'{c["key"]}-{args.fps}p.wav'
            if not c['raw'].exists():
                pcm = read_pcm(c['take']['cut_take'])
                piece = pcm[round(c['cut'][0] * RATE):round(c['cut'][1] * RATE)]
                rec.fade(piece, rec.XFADE, rec.XFADE)
                write_pcm(c['raw'], piece)
                made.append(c)
    filled = [c for c in chunks if c.get('fill')]
    if filled:  # missing paragraphs, spoken from the script by a voice, cut to their voice and set to the takes' level
        fargs = argparse.Namespace(**vars(args))
        fargs.voice = DEFAULT_VOICE if args.rec_missing == 'tts' else args.rec_missing
        fv = Voice(fargs)
        items_f, seen = [], set()
        for c in filled:
            c['fill_key'] = fv.key(c['text'])
            c['fill_raw'] = adir / f'{c["fill_key"]}.wav'
            if not c['fill_raw'].exists() and c['fill_key'] not in seen:
                items_f.append((c['text'], c['fill_raw'])); seen.add(c['fill_key'])
        if items_f:
            print(f'speaking {len(items_f)} missing paragraph(s) with {fv.spec} ...', flush=True)
            fv.make_all(items_f)
        args.fill_spec = fv.spec
        for c in filled:
            c['key'] = f'fill-{c["fill_key"]}-{tag}'
            c['raw'] = tdir / f'{c["key"]}.wav'
            c['wav'] = adir / f'{c["key"]}-{args.fps}p.wav'
            if not c['raw'].exists():
                pcm = read_pcm(c['fill_raw'])
                span = rec.voice_span(pcm) or (0, len(pcm))
                a, b = max(0, span[0] - round(REC_HEAD * RATE)), min(len(pcm), span[1] + round(REC_TAIL * RATE))
                piece = pcm[a:b]
                rec.fade(piece, rec.XFADE, rec.XFADE)
                write_pcm(tdir / f'{c["key"]}-cut.wav', piece)
                normalise(tdir / f'{c["key"]}-cut.wav', c['raw'], REC_LEVEL)
                made.append(c)
    return chunks, [units[c['paras'][0]] for c in filled], todo, notes, made


def talk_starts(s, pts, t0, texts):
    """A talked paragraph's line starts (seconds in its piece) from where its points were said (pts, t in the clip),
    t0: where the piece starts in the clip. A point not said in order is placed by letter count between the points
    either side of it. -> (starts, placed: the k of the points placed so)."""
    n = len(texts)
    known = {}
    for q in pts:
        if q['said'] and q.get('order', True) and q['t'] is not None:
            known[q['k']] = min(max(q['t'] - t0, s['vs']), s['ve'])
    known[0] = s['vs']
    pos, p_ = [], 0
    for tx in texts:
        pos.append(p_); p_ += len(tx) + 1
    anchors = sorted((pos[k], t) for k, t in known.items()) + [(p_, s['ve'])]
    starts, placed = [], []
    for k in range(n):
        if k in known:
            t = known[k]
        else:
            placed.append(k)
            lo = max((a for a in anchors if a[0] <= pos[k]), key=lambda a: a[0])
            hi = min((a for a in anchors if a[0] > pos[k]), key=lambda a: a[0])
            t = lo[1] + (hi[1] - lo[1]) * (pos[k] - lo[0]) / max(hi[0] - lo[0], 1)
        starts.append(t)
    for k in range(1, n):  # never backwards
        starts[k] = min(max(starts[k], starts[k - 1] + 0.1), max(s['ve'], starts[k - 1] + 0.1))
    return starts, placed


def write_spoken(path, title, scenes, paras, units, chunks):
    """spoken.md: per scene and paragraph what was said (the words kept, as the subtitles show them); a paragraph not
    recorded yet is the script's, under a // line."""
    out = [f'# {title}', '', '// What was said, from the takes (build.py writes this on every build with talk takes).', '']
    for si, sc in enumerate(scenes):
        mine = [p for p in paras if p['scene'] == si]
        if not mine:
            continue
        out += [f'## {sc["title"]}', '']
        for p in mine:
            u = units[p['para']]
            if chunks[u['chunk']].get('talk'):
                said = ' '.join(w for w, _, _ in (u.get('words') or [])).strip()
                out += [said[:1].upper() + said[1:] if said else '// (nothing heard)', '']
            else:
                out += ['// not recorded yet: the script', p['text'], '']
    body = '\n'.join(out).rstrip() + '\n'
    if not path.exists() or path.read_text(encoding='utf-8') != body:
        path.write_text(body, encoding='utf-8')
        return True
    return False


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
            s['plan'] = talk_plan(s, raw) if s.get('talk') else take_plan(s, raw)
            s['raw_len'] = len(raw) / RATE
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
            dyn = read_pcm(td / f'{i}-dyn.wav')
            if s.get('talk'):
                pcm, pauses = rec.shorten_pauses(dyn, most=talk.PAUSE_MAX, keep=talk.PAUSE_KEEP)
            else:
                pcm, pauses = rec.shorten_pauses(dyn)
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
            out[s['cut_take'].name] = m = dict(dur=round((b - a) / RATE, 4), vs=round((v0 - a) / RATE, 4), ve=round((v1 - a) / RATE, 4),
                                               lufs=ebur128(s['cut_take'])[0], gain=round(gain, 2), tone=round(len(tone) / RATE, 2),
                                               cuts=p['cuts'], pauses=pauses, ok=p['ok'], missing=p['missing'], extra=p['extra'],
                                               heard=p['heard'])
            if s.get('talk'):  # the words kept, moved to the piece's time: through the cuts, the pauses shortened, the trim
                f1, f2 = rec.time_map(p['cuts'], s['raw_len']), rec.time_map(pauses, len(dyn) / RATE)
                at = lambda t: round(min(max(f2(f1(t)) - a / RATE, 0.0), (b - a) / RATE), 3)
                m.update(words=[[w, at(t0), at(t1)] for w, t0, t1 in p['kept']], like=p['like'], fillers=p['fillers'],
                         keep=p['keep'])
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
    if c.get('talk'):  # a talked clip: what was said, its paragraphs cut at the pauses talk.py chose (c['bounds'])
        words = c['words_c']
    elif c['align'].exists():
        words = json.loads(c['align'].read_text(encoding='utf-8')).get('words')
    with wave.open(str(c['norm'])) as w:
        data = w.readframes(w.getnframes())
    spf = RATE // fps
    n_frames = len(data) // 2 // spf
    db = _db10(data)
    thr = max(max(db, default=-90) - 40, -55)
    hyp = [] if c.get('talk') else [(align.norm(wd), a, b) for wd, a, b in (words or []) if align.norm(wd)]
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
        if c.get('talk'):
            lo, hi, how = c['bounds_c'][j - 1][0] - 0.04, max(c['bounds_c'][j - 1]) + 0.04, 'talk'
        elif matched >= 0.5 and before and after and after[0] > before[-1] - 0.05:
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
        s['clip_t0'] = t0
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


def chunk_pauses(c, sents, lines):
    """The pause marks of a clip's lines -> [(how many of the clip's words come before it, seconds)]. A mark before the
    clip's first word or after its last is left out: the timeline sets the time between clips (--para-gap, --gap)."""
    out, n = [], 0
    for i in c['sents']:
        for g in sents[i]['lines']:
            out += [(n + k, sec) for k, sec in lines[g].get('pauses', [])]
            n += len(lines[g]['text'].split())
    return [(k, sec) for k, sec in out if 0 < k < n]


def put_pauses(todo, adir, args):
    """Pause marks -> pauses in the made voice, filled with its own room tone (clip_tone), never digital silence. Each clip in todo has src (the voice as made from its text, marks left
    out, so the voice says the paragraph in one go), text, pauses [(words before, seconds)] and raw (where the clip with
    its pauses goes). The words' times come from mlx-whisper on src (cached like align_all); a mark between word k-1 and
    word k tops the pause there up to its length: the quiet already between the two words counts (the voice's own comma
    or sentence pause), and room tone is put in at the quietest 10 ms of it. Without word times, where the letters say.
    -> dict(marks, added (seconds), already (marks the voice's own pause already covered), letters (placed by letters))."""
    import difflib
    rep = dict(marks=0, added=0.0, already=0, letters=0)
    jobs = [dict(wav=c['src'], text=c['text']) for c in todo]
    align_all(jobs, adir, args)
    for c, job in zip(todo, jobs):
        with wave.open(str(c['src'])) as w:
            data = w.readframes(w.getnframes())
        db = _db10(data)
        thr = max(max(db, default=-90) - 40, -60)
        quiet = [d < thr for d in db]
        voiced = [k for k, q in enumerate(quiet) if not q]
        vs, ve = (voiced[0] / 100, (voiced[-1] + 1) / 100) if voiced else (0, len(db) / 100)
        words = c['text'].split()
        hyp = []
        if job['align'].exists():
            hyp = [(align.norm(wd), a, b) for wd, a, b in json.loads(job['align'].read_text(encoding='utf-8')).get('words', [])
                   if align.norm(wd)]
        toks = [(align.norm(wd), i) for i, wd in enumerate(words) if align.norm(wd)]
        at = {}  # word index -> (start, end) in src
        if toks and hyp:
            sm = difflib.SequenceMatcher(None, [t[0] for t in toks], [x[0] for x in hyp], autojunk=False)
            for a, b, n in sm.get_matching_blocks():
                for q in range(n):
                    at[toks[a + q][1]] = hyp[b + q][1:]
        use_words = len(at) >= 0.5 * max(len(toks), 1)
        chars = [0]
        for wd in words:
            chars.append(chars[-1] + len(wd) + 1)
        inserts = []  # (10 ms frame where the pause goes in, its seconds)
        for k, sec in c['pauses']:
            rep['marks'] += 1
            before = [at[i][1] for i in range(k - 1, -1, -1) if i in at][:1]
            after = [at[i][0] for i in range(k, len(words)) if i in at][:1]
            if use_words and before and after:
                lo, hi = min(before[0], after[0]) - 0.1, max(before[0], after[0]) + 0.1
            else:  # where the letters say, with room either side
                mid = vs + (ve - vs) * chars[k] / max(chars[-1], 1)
                lo, hi = mid - 0.4, mid + 0.4
                rep['letters'] += 1
            f0, f1 = max(0, int(lo * 100)), min(len(db), int(hi * 100) + 1)
            best, run, start = (0, None), 0, f0  # the longest quiet run in the window: the pause the voice made
            for f in range(f0, f1):
                if quiet[f]:
                    run += 1
                    if run > best[0]:
                        best = (run, f - run + 1)
                else:
                    run = 0
            if best[1] is not None:
                have = best[0] / 100
                at_f = min(range(best[1], best[1] + best[0]), key=lambda f: (db[f], abs(f - (best[1] + best[0] / 2))))
            else:
                have = 0.0
                at_f = min(range(f0, max(f1, f0 + 1)), key=lambda f: db[f] if f < len(db) else 0)
            if sec - have < 0.01:
                rep['already'] += 1
                continue
            inserts.append((at_f, round(sec - have, 3)))
            rep['added'] += sec - have
        pcm = array.array('h', data)
        tone = clip_tone(pcm)  # the pause is the clip's own room tone, not digital silence
        out, last = array.array('h'), 0
        hop, hh = RATE // 100, EDGE // 2  # 10 ms frames; the voice crossfades into the room tone over EDGE, centred on the cut
        for f, sec in sorted(inserts):
            cut = min(max(f * hop + hop // 2, hh), len(pcm) - hh)  # the middle of the quietest 10 ms
            xfade_append(out, pcm[last:cut + hh])
            xfade_append(out, tone_between(tone, round(sec * RATE) + EDGE, pcm[max(0, cut - hh - RATE // 20):cut - hh],
                                           pcm[cut + hh:cut + hh + RATE // 20]))  # adds exactly sec: EDGE of it under the crossfades
            last = cut - hh
        xfade_append(out, pcm[last:])
        tmp = Path(str(c['raw']) + '.part.wav')
        with wave.open(str(tmp), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(out.tobytes())
        tmp.replace(c['raw'])
    return rep


# ---------- build ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', help='folder name under source/courses/, e.g. basic-01')
    ap.add_argument('--scenes', help='scenes file to read instead of source/courses/<video>/scenes.md')
    ap.add_argument('--voice', default=DEFAULT_VOICE, help='say (macOS, Samantha), say:<voice>, tts:<model> '
                    '(source/video/tts/say.py), or rec: the author\'s own takes, one per sentence (see --rec-dir)')
    ap.add_argument('--list-sentences', action='store_true', help='print the sentences as JSON and stop: [{"id", "scene", '
                    '"para", "n", "text"}]; id = first 12 hex of sha1(text), para and n count from 0 over the whole video')
    ap.add_argument('--list-paragraphs', action='store_true', help='print the paragraphs as JSON and stop: [{"id", "sid", '
                    '"scene", "para", "text", "lines": [{"k", "text", "beat", "bold"}]}]; id / sid = first 12 hex of sha1 of '
                    'the paragraph\'s / scene\'s spoken lines joined by spaces')
    ap.add_argument('--check-para', metavar='ID', help='rec: check a paragraph take (a punch-in), JSON: {"id", "ok", "heard", '
                    '"points": [{"k", "said", "t"}], "order_ok", "missing", "fillers", "seconds"}; also <id>.check.json')
    ap.add_argument('--check-scene', metavar='SID', help='rec: check a scene take, JSON: {"sid", "ok", "heard", "paras": '
                    '[{"id", "para", "t0", "t1", "points", "order_ok", "missing"}], "fillers", "seconds"}; also <sid>.check.json')
    ap.add_argument('--polish-preview', metavar='SID|ID', help='rec: polish one scene take (sid) or punch-in (paragraph '
                    'id) as the build would, and stop, before any picture or subtitle: <rec-dir>/preview/<sid>-raw.mp3, '
                    '<sid>-polished.mp3 and <sid>-polish.md (what was cut or changed, at what time in the raw take; the '
                    'transcript cleaned; points missing or out of order; "like"; loudness before and after). The polished '
                    'take goes into the build\'s cache, so the build after it does not polish it again')
    ap.add_argument('--edit-draft', metavar='SID|ID', help='rec, talk: write <rec-dir>/preview/<sid>-edit-draft.md, the '
                    'take\'s whole transcript before any cut (word indexes and times, the automatic cuts marked) next to '
                    'the script, by paragraph, to write its editorial pass from: source/courses/<video>/edit/<sid>.json '
                    '(cut or keep word ranges), applied by the polish')
    ap.add_argument('--subs-draft', metavar='SID|ID', help='rec, talk: write <rec-dir>/preview/<sid>-subs-draft.md, the '
                    'take\'s words as kept (with their indexes) next to the script, line by line, to write its subtitle '
                    'corrections from: source/courses/<video>/subs-fix/<sid>.json, applied by every build')
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
    ap.add_argument('--ref', default=str(DEFAULT_REF),
                    help='tts only: reference voice wav; its words in the .txt next to it (default: 12 s of the author\'s '
                    'own natural talk)')
    ap.add_argument('--seed', type=int, default=1, help='tts only: seed passed to tts/say.py')
    ap.add_argument('--tts-python', help='tts only: python that runs tts/say.py (default: this one)')
    ap.add_argument('--jobs', type=int, help='say only: clips made at once (default 4)')
    R = timing.Rules()
    ap.add_argument('--gap', type=float, default=R.gap, help='seconds of room tone between two clips of one long paragraph '
                    '(inside a clip the voice keeps its own pauses)')
    ap.add_argument('--para-gap', type=float, default=R.para_gap, help='seconds of room tone between paragraphs on the same picture')
    ap.add_argument('--para-max', type=float, default=20.0, help='a paragraph longer than this many seconds of speech (at '
                    f'{CPS:.0f} letters a second) is spoken in runs of whole sentences of about equal length')
    ap.add_argument('--dwell', type=float, default=R.dwell, help='when the picture changes between paragraphs: seconds the '
                    'outgoing picture stays after the words end, before the next one fades in')
    ap.add_argument('--busy', type=float, default=R.busy, help='seconds added to --dwell when the outgoing picture is busy '
                    '(a screenshot, a list of 4+ items, a figure with many words)')
    ap.add_argument('--scene-gap', type=float, default=R.scene_gap, help='seconds of room tone between scenes (at least dwell + lead)')
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
    args.out = str(Path(args.out).resolve())  # ffmpeg's concat list is read from a temp folder: relative paths break it
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
    paras = paragraph_list(scenes, lines, load_bold(scenes_path, args.video))
    if args.list_paragraphs:
        print('[' + ',\n'.join(json.dumps(dict(id=p['id'], sid=p['sid'], scene=scenes[p['scene']]['title'], para=p['para'],
                                               text=p['text'], lines=[dict(k=k, text=lines[g]['text'], beat=b, bold=bd)
                                                                      for k, (g, b, bd) in enumerate(zip(p['lines'], p['beats'], p['bold']))]),
                                          ensure_ascii=False) for p in paras) + ']')
        return
    rdir = Path(args.rec_dir).resolve() if args.rec_dir else REC_DIR / args.video
    args.edit_dir = edit_dir(scenes_path, args.video)
    if args.edit_draft:
        (Path(args.out) / args.video / 'audio').mkdir(parents=True, exist_ok=True)
        edit_draft(args, scenes, paras, lines, rdir, Path(args.out) / args.video / 'audio')
        return
    if args.polish_preview:
        (Path(args.out) / args.video / 'audio').mkdir(parents=True, exist_ok=True)
        polish_preview(args, scenes, paras, lines, rdir, Path(args.out) / args.video / 'audio')
        return
    args.fix_dir = fix_dir(scenes_path, args.video)
    if args.subs_draft:
        (Path(args.out) / args.video / 'audio').mkdir(parents=True, exist_ok=True)
        subs_draft(args, scenes, paras, lines, rdir, Path(args.out) / args.video / 'audio', args.fix_dir)
        return
    if args.check_para or args.check_scene:
        (Path(args.out) / args.video / 'audio').mkdir(parents=True, exist_ok=True)
        check_talk(args, paras, lines, rdir, Path(args.out) / args.video / 'audio')
        return
    is_talk = args.voice == 'rec' and talk_mode(rdir) or (args.rec_status and talk_mode(rdir))
    if args.rec_status and is_talk:
        print(f'{rdir}  (talk: one take per scene, paragraph takes punched in)')
        n_sc = n_rec = 0
        for si, sc in enumerate(scenes):
            mine = [p for p in paras if p['scene'] == si]
            if not mine:
                continue
            n_sc += 1
            st = current(rdir / 'scene', mine[0]['sid'])
            n_rec += bool(st)
            print(f'{sc["title"][:40]:<40} {"recorded" if st else "missing ":<9} scene {mine[0]["sid"]}, {len(mine)} paragraphs')
            for p in mine:
                f = current(rdir / 'para', p['id'])
                if f:
                    used = punch_in_used(f, dict(take=st) if st else None)
                    print(f'    punch-in  paragraph {p["para"]:<3} {p["id"]}  '
                          + ('' if used else '(older than the scene take, unused) ') + p['text'][:50])
                elif not st:
                    print(f'    missing   paragraph {p["para"]:<3} {p["id"]}  {p["text"][:50]}')
        print(f'{"total":<40} {n_rec:>3} / {n_sc:<3} scenes recorded, '
              f'{sum(1 for p in paras if current(rdir / "para", p["id"]))} paragraph take(s)')
        return
    if (args.rec_status or args.voice == 'rec' or args.check_take) and not is_talk:
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
            print(f'(no scene or paragraph takes in {rdir / "scene"} or {rdir / "para"}: talk takes are used once there are)')
            return
        if args.check_take:
            (Path(args.out) / args.video / 'audio').mkdir(parents=True, exist_ok=True)
            check_take(sents, scenes, rdir, Path(args.out) / args.video / 'audio', args)
            return
        if missing_rec and args.rec_missing == 'stop' and not args.check_take:
            die(f'{len(missing_rec)} of {len(sents)} sentences have no take in {rdir}:\n'
                + '\n'.join(f'  {scenes[s["scene"]]["title"]}, sentence {sents.index(s)} ({s["id"]}): {s["text"][:70]}'
                            for s in missing_rec)
                + '\nrecord them, or add --rec-missing tts to speak them with the default voice for a preview')
    if args.voice == 'rec':
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
    filled, talk_notes = [], []
    if is_talk:  # the author talked each scene (and maybe punched in paragraphs): one unit per paragraph
        sents = [dict(scene=p['scene'], para=p['para'], lines=p['lines'], text=p['text'], line=p['line']) for p in paras]
        chunks, filled, polished, talk_notes, todo = talk_chunks(paras, sents, lines, args, adir, rdir)
        kept_old, failed_old = [], []
    elif is_rec:  # the author's takes: one clip per paragraph, however long (--para-max is for a made voice)
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
        # pause marks ([.3]): the voice speaks the paragraph without them (the clip above, shared with the same text
        # unmarked), then silence goes in at the marked word boundaries; the clip with its pauses has its own key
        todo_p, seen_p = [], set()
        for c in chunks:
            c['pauses'] = chunk_pauses(c, sents, lines)
            if c['pauses']:
                c['src'] = c['raw']
                c['key'] = h(c['key'], 'pauses', json.dumps(c['pauses']), PAUSE_VERSION)
                c['raw'] = adir / f'{c["key"]}.wav'
                c['wav'] = adir / f'{c["key"]}-{fps}p.wav'
                if not c['raw'].exists() and c['key'] not in seen_p:
                    todo_p.append(c); seen_p.add(c['key'])
        if todo_p:
            pr = put_pauses(todo_p, adir, args)
            print(f'pause marks: {pr["marks"]} in {len(todo_p)} clip(s), {pr["added"]:.1f} s of room tone put in; '
                  f'{pr["already"]} already as long in the voice'
                  + (f'; {pr["letters"]} placed by letter count (no word times)' if pr['letters'] else ''))
        todo += [c for c in todo_p if c not in todo]  # a clip made just now and given its pauses is listed once
    made_keys = {c['key'] for c in todo}

    meta_path = adir / 'durations.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for c in chunks:
        k = f'{c["key"]}-{fps}-{TRIM_VERSION}'
        if c['key'] in made_keys or k not in meta or len(meta[k]) < 4 or not c['wav'].exists():
            meta[k] = trim_and_pad(c['raw'], c['wav'], fps, head=REC_HEAD if is_rec else 0.06)
        c['frames'], c['vs'], c['ve'], c['off'] = meta[k]
        if c.get('talk'):  # what was said, in the trimmed clip's time
            o = c['off']
            c['words_c'] = [[w, round(a - o, 3), round(b - o, 3)] for w, a, b in c['words']]
            c['bounds_c'] = [(a - o, b - o) for a, b in c['bounds']]
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
    n_aligned = align_all([c for c in chunks if not c.get('talk')], adir, args)
    for c in chunks:
        cut_chunk(c, sents, lines, fps, adir)
    spoken_made = is_talk and write_spoken(scenes_path.parent / ('spoken.md' if scenes_path.name == 'scenes.md' else f'spoken-{scenes_path.stem.removeprefix("scenes-")}.md'), title, scenes, paras, sents, chunks)
    hows = {'aligned': 0, 'interpolated': 0, 'proportional': 0, 'talk': 0}
    inner = dict(word=0, interpolated=0, proportional=0)  # line starts inside sentences
    for s in sents:
        s['loud'] = chunks[s['chunk']]['loud']
        texts = [lines[g]['text'] for g in s['lines']]
        c = chunks[s['chunk']]
        if c.get('talk'):  # a talked paragraph: each line starts where its point was said (talk.points)
            pts = [dict(q, t=None if q['t'] is None else q['t'] - c['off']) for q in c['pts'][c['paras'].index(s['para'])]]
            s['starts'], s['placed'] = talk_starts(s, pts, s['clip_t0'], texts)
            s['points'], s['how'] = pts, 'talk'
            s['matched'] = sum(1 for q in pts if q['said']) / max(len(pts), 1)
            s['take'] = c['take']['take']
            hows['talk'] += 1
            for j in range(1, len(texts)):
                inner['interpolated' if j in s['placed'] else 'word'] += 1
            continue
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
    clips = []
    for i, s in enumerate(sents):  # each clip faded at its ends, over the room tone under the timeline (room_bed)
        path, tone = edge_faded(s['norm'])
        clips.append(dict(path=path, name=f'{i + 1:03d} {s["text"][:50]}', start=s['start'], dur=s['frames'], tone=tone))
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
        if lang == 'en' and is_talk:  # what was said, for a talked paragraph; the script's lines for one filled in
            cl = []
            for k, s in enumerate(sents):
                if chunks[s['chunk']].get('talk'):
                    nxt = sents[k + 1]['start'] + round(sents[k + 1]['vs'] * fps) if k + 1 < len(sents) else total
                    cl += subs.word_cues(s['words'] or [], s['start'], fps, end=nxt)
                else:
                    cl += subs.cues([lines[g]['text'] for g in s['lines']], [l_start[g] for g in s['lines']],
                                    [l_dur[g] for g in s['lines']])
            for a, b in zip(cl, cl[1:]):  # a cue never runs into the next paragraph's first
                if a[0] + a[1] > b[0]:
                    cl[cl.index(a)] = (a[0], max(1, b[0] - a[0]), a[2])
            captions.append((lang, cl))
            continue
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
                     [(str(f['path']), f['start'], f['dur'], f['xfade']) for f in frames], title, fps, total, TONE_VERSION])
    # the room tone under the whole timeline, a wav of its own (in Final Cut Pro too, on the lane under the voice)
    bed_path = out / f'room-tone-{h(tl)}.wav'
    if not bed_path.exists():
        for f in out.glob('room-tone-*.wav'):
            f.unlink()
        write_pcm(bed_path, room_bed(clips, total, fps))
    bed = read_pcm(bed_path)
    # the speaking avatar: one overlay video for the whole timeline, made again only when the audio, its times or the avatar change
    overlay, made_ov = None, []
    if avatar and not still_avatar:
        ok = h(speaker.STYLE, avatar, avatar.stat().st_mtime, fps, total, json.dumps([(str(c['path']), c['start']) for c in clips]))
        ov = out / f'avatar-{ok}.mov'
        if not ov.exists() or not speaker.preview_path(ov).exists():
            t1 = time.time()
            try:
                info = speaker.make(ov, track=mix(clips, total, fps, bed), rate=RATE, fps=fps, total=total,
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
                     overlay=overlay, bed=bed_path)
        state['fcpxml'] = sig; made_out.append(fx.name)
    made_segs = 0
    if not args.no_mp4 and (state.get('mp4') != sig_mp4 or not mp4.exists()):
        made_segs = rough(mp4, frames, clips, total, fps, out, burn, overlay, bed)
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
    if is_talk:
        print(f'\naudio:  {len(chunks)} clip(s) for {n_para} paragraphs (a run of paragraphs from one scene take is one '
              f'clip), {len(made_keys)} made, {n_audio - len(made_keys)} reused; cut into {len(sents)} paragraph pieces '
              f'({sum(1 for s in sents if s["cut"] == "talk")} at the pause between two talked paragraphs)')
    else:
        print(f'\naudio:  {len(chunks)} clip(s) for {n_para} paragraphs ({len(chunks) - n_para} split for length), '
              f'{len(made_keys)} made, {n_audio - len(made_keys)} reused; cut into {len(sents)} sentence pieces '
              f'({sum(1 for s in sents if s["cut"] == "words")} cuts between matched words, '
              f'{sum(1 for s in sents if s["cut"] == "letters")} by letter count)')
    if is_talk:
        tu = [s for s in sents if chunks[s['chunk']].get('talk')]
        takes = {c['take']['cut_take'].name: c['take'] for c in chunks if c.get('talk')}
        print(f'voice:  talked, {len(tu)} of {len(sents)} paragraphs from {sum(1 for t in takes.values() if t["kind"] == "scene")} '
              f'scene take(s) and {sum(1 for t in takes.values() if t["kind"] == "para")} punch-in(s) in {rdir}'
              + (f'; {len(filled)} filled in with {args.fill_spec} (not recorded yet):' if filled else ''))
        for s in filled:
            print(f'  filled  {scenes[s["scene"]]["title"][:24]}, paragraph {s["para"]}: {s["text"][:60]}')
        for n in talk_notes:
            print(f'  note    {n}')
        whys = {}
        for t in takes.values():
            for c in t['rec']['cuts']:
                whys[c[2]] = whys.get(c[2], 0) + 1
        print(f'polish: {len(polished)} take(s) polished now, {len(takes) - len(polished)} reused; cut '
              + (', '.join(f'{n} {w}' for w, n in sorted(whys.items())) or 'nothing')
              + f'; {sum(len(t["rec"]["pauses"]) for t in takes.values())} pause(s) over {talk.PAUSE_MAX} s shortened to '
              f'{talk.PAUSE_KEEP} s' if takes else 'polish: no takes')
        for t in takes.values():
            n, d, flag = t['rec']['like']
            if flag:
                print(f'  like    {t["kind"]} take {t["key"]}: "like" {n} times beyond the script, {d:.0%} of the words '
                      f'(over 1 in {round(1 / talk.LIKE_DENSITY)}); not cut')
        for s in tu:
            nf = [q['k'] for q in s['points'] if not q['said']]
            oo = [q['k'] for q in s['points'] if q['said'] and q.get('order') is False]
            if s['placed']:
                print(f'  points  paragraph {s["para"]}: line(s) {", ".join(str(k) for k in s["placed"])} placed between their '
                      f'neighbours' + (f' (not said: {nf})' if nf else '') + (f' (said out of order: {oo})' if oo else '')
                      + f': {s["text"][:50]}')
        for key, rep in getattr(args, 'edit_reports', []):
            print(f'  edit    {edit_report(rep, key)}')
        for key, rep in getattr(args, 'fix_reports', []):
            print(f'  subs    {fix_report(rep, key)}')
        print(f'spoken: {scenes_path.parent / "spoken.md"} {"written" if spoken_made else "unchanged"}')
    elif is_rec:
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
        if s['how'] not in ('aligned', 'talk') and len(s['lines']) > 1:
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


def mix(clips, total, fps, bed=None):
    """The whole timeline's audio: 16-bit mono PCM at RATE, each clip at its start, over the room tone `bed` (room_bed:
    it is there only between clips and under their faded ends, so where they meet the two add up)."""
    spf = RATE // fps
    track = array.array('h', bed) if bed is not None else array.array('h', bytes(2 * total * spf))
    for c in clips:
        data = read_pcm(c['path'])
        at = c['start'] * spf
        n = min(EDGE, len(data) // 2)
        for i in list(range(n)) + list(range(len(data) - n, len(data))):
            if at + i < len(track):
                data[i] = _sat(data[i] + track[at + i])
        track[at:at + len(data)] = data[:max(0, len(track) - at)]
    return track.tobytes()


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


def rough(mp4, frames, clips, total, fps, out, burn=None, overlay=None, bed=None):
    """Stills with cross-dissolves plus one audio track: a quick check that words and pictures line up.
    The picture track is made of small pieces (a still held, or a dissolve between two), each cached by what it shows
    and how long, then joined and laid under the avatar and the subtitles in one pass. -> pieces made."""
    track = mix(clips, total, fps, bed)
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
