#!/usr/bin/env python3
"""Build a tutorial video's audio, frames, Final Cut Pro timeline and rough mp4 from its scenes file.

    .venv/bin/python source/video/build.py basic-01
    .venv/bin/python source/video/build.py basic-01 --voice tts:qwen3 --ref .claude/loops/voice/ref/ref-13s.wav

Reads source/courses/<video>/scenes.md (or scenes-draft.md; --scenes FILE overrides), see source/video/FORMAT.md.
Writes .claude/loops/video-out/<video>/: audio/ (one wav per sentence), frames/ (one png per @ line),
<video>.fcpxml and <video>-rough.mp4. Audio and frames are cached by what made them, so a rerun makes only what changed.
"""
import argparse, hashlib, json, math, os, re, shlex, subprocess, sys, tempfile, time, wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import render, fcpxml  # noqa: E402

RATE = 48000
DEFAULT_SAY_VOICE = 'Samantha'


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
        die(f'line {no}: an @ line needs a picture id or card "...": {line}')
    spec = dict(line=no, raw=line, id=toks[0], box=None, crop=None, text='', kicker=None)
    rest = toks[1:]
    if spec['id'] == 'card':
        words = [t for t in rest if not t.startswith('kicker=')]
        if not words:
            die(f'line {no}: card needs its words in quotes: {line}')
        spec['text'] = ' '.join(words)
        k = [t for t in rest if t.startswith('kicker=')]
        spec['kicker'] = k[0][7:] if k else kicker_from(scene_title)
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
        else:
            die(f'--voice must be say, say:<voice name> or tts:<model>, not {args.voice}')

    def key(self, text):
        return h(text, *self.settings)

    def make_all(self, items):
        """items: [(text, out_wav)] -> each out_wav a 48 kHz mono 16-bit wav."""
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
                batch.write_text(''.join(f'{raws[i]}\t{t}\n' for i, (t, _) in enumerate(items)), encoding='utf-8')
                r = subprocess.run([self.python, str(self.script), '--model', self.model, '--ref', str(self.ref),
                                    '--seed', str(self.seed), '--batch', str(batch)])
                if r.returncode:
                    die(f'tts/say.py failed (exit {r.returncode})')
            for raw, (text, out_wav) in zip(raws, items):
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


def pad_to_frames(src, dst, fps):
    """Copy a 48 kHz mono wav, padded with silence to a whole number of frames, so every time in the timeline is exact."""
    with wave.open(str(src)) as w:
        data, n = w.readframes(w.getnframes()), w.getnframes()
    spf = RATE // fps
    frames = max(1, math.ceil(n / spf))
    data += b'\0\0' * (frames * spf - n)
    with wave.open(str(dst), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(data)
    return frames


# ---------- build ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', help='folder name under source/courses/, e.g. basic-01')
    ap.add_argument('--scenes', help='scenes file to read instead of source/courses/<video>/scenes.md')
    ap.add_argument('--voice', default='say', help='say (macOS, Samantha), say:<voice>, or tts:<model> (source/video/tts/say.py)')
    ap.add_argument('--rate', type=int, help='say only: words per minute')
    ap.add_argument('--ref', default=str(ROOT / '.claude/loops/voice/ref/ref-13s.wav'),
                    help='tts only: reference voice wav; its words in the .txt next to it')
    ap.add_argument('--seed', type=int, default=1, help='tts only: seed passed to tts/say.py')
    ap.add_argument('--tts-python', help='tts only: python that runs tts/say.py (default: this one)')
    ap.add_argument('--jobs', type=int, help='say only: clips made at once (default 4)')
    ap.add_argument('--gap', type=float, default=0.35, help='seconds between sentences')
    ap.add_argument('--scene-gap', type=float, default=0.8, help='seconds between scenes')
    ap.add_argument('--tail', type=float, default=1.0, help='seconds the last picture stays after the last sentence')
    ap.add_argument('--fps', type=int, default=25, choices=[25, 30, 50, 60])
    ap.add_argument('--fcpxml-version', default='1.10', choices=['1.10', '1.11'])
    ap.add_argument('--no-mp4', action='store_true', help='skip the rough mp4')
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
    adir.mkdir(parents=True, exist_ok=True); fdir.mkdir(parents=True, exist_ok=True)
    fps = args.fps

    # 1. pictures: resolve every id first, so a missing image fails before anything is made
    missing = []
    pics = []  # every @ line in order, with its scene index and the index of the sentence it starts at
    n_sent = 0
    sentences = []
    for si, sc in enumerate(scenes):
        for kind, it in sc['items']:
            if kind == 'pic':
                if it['id'] != 'card':
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
    if not sentences:
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
    for p in shown:
        s = p['spec']
        if s['id'] == 'card':
            key = h(render.RENDER_VERSION, 'card', s['text'], s['kicker'])
        else:
            key = h(render.RENDER_VERSION, s['raw'], s['src'], os.path.getmtime(s['src']))
        p['frame'] = fdir / f'{key}.png'
        p['name'] = (s['id'] if s['id'] != 'card' else 'card ' + s['text'])[:60]
        if p['frame'].exists():
            reused_f.append(p); continue
        tmp = p['frame'].with_suffix('.part.png')
        if s['id'] == 'card':
            render.card(tmp, s['text'], s['kicker'])
        else:
            full = s['src'].is_relative_to(ROOT / 'source/video/pages')
            render.picture(tmp, s['src'], s['box'], s['text'], full_bleed=full, crop=s['crop'])
        tmp.replace(p['frame'])
        made_f.append(p)

    # 2. audio: one clip per sentence, cached by (text, voice settings)
    voice = Voice(args)
    for s in sentences:
        s['key'] = voice.key(s['text'])
        s['raw'] = adir / f'{s["key"]}.wav'
        s['wav'] = adir / f'{s["key"]}-{fps}p.wav'
    todo, seen = [], set()
    for s in sentences:
        if not s['raw'].exists() and s['key'] not in seen:
            todo.append(s); seen.add(s['key'])
    if todo:
        print(f'making {len(todo)} audio clip(s) with {voice.spec} ...', flush=True)
        voice.make_all([(s['text'], s['raw']) for s in todo])
    made_keys = {s['key'] for s in todo}

    meta_path = adir / 'durations.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    for s in sentences:
        k = f'{s["key"]}-{fps}'
        if s['key'] in made_keys or k not in meta or not s['wav'].exists():
            meta[s['key']] = round(probe_seconds(s['raw']), 4)  # ffprobe: the clip's spoken length
            meta[k] = pad_to_frames(s['raw'], s['wav'], fps)
        s['seconds'], s['frames'] = meta[s['key']], meta[k]
    meta_path.write_text(json.dumps(meta, indent=0, sort_keys=True))

    # 3. timeline, in frames
    gap, scene_gap, tail = (round(x * fps) for x in (args.gap, args.scene_gap, args.tail))
    t = 0
    for i, s in enumerate(sentences):
        if i:
            t += scene_gap if s['scene'] != sentences[i - 1]['scene'] else gap
        s['start'] = t
        t += s['frames']
    total = t + tail
    for j, p in enumerate(shown):
        p['start'] = sentences[p['at']]['start'] if j else 0
    for j, p in enumerate(shown):
        p['dur'] = (shown[j + 1]['start'] if j + 1 < len(shown) else total) - p['start']

    # 4. outputs, only when the timeline changed
    clips = [dict(path=s['wav'], name=f'{i + 1:03d} {s["text"][:50]}', start=s['start'], dur=s['frames'])
             for i, s in enumerate(sentences)]
    frames = [dict(path=p['frame'], name=p['name'], start=p['start'], dur=p['dur']) for p in shown]
    tl = json.dumps([[(str(c['path']), c['start'], c['dur']) for c in clips],
                     [(str(f['path']), f['start'], f['dur']) for f in frames], title, fps, total])
    sig, sig_mp4 = h(tl, args.fcpxml_version), h(tl)
    fx, mp4 = out / f'{args.video}.fcpxml', out / f'{args.video}-rough.mp4'
    state_path = out / 'build-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    made_out = []
    if state.get('fcpxml') != sig or not fx.exists():
        fcpxml.write(fx, title=title, event=f'{args.video} (video pipeline)', fps=fps, width=render.W, height=render.H,
                     pictures=frames, clips=clips, total=total, version=args.fcpxml_version)
        state['fcpxml'] = sig; made_out.append(fx.name)
    if not args.no_mp4 and (state.get('mp4') != sig_mp4 or not mp4.exists()):
        rough(mp4, frames, clips, total, fps, out)
        state['mp4'] = sig_mp4; made_out.append(mp4.name)
    state_path.write_text(json.dumps(state, indent=1))

    # 5. report
    sec = lambda f: f / fps
    print(f'\n{title}  ({scenes_path.relative_to(ROOT) if scenes_path.is_relative_to(ROOT) else scenes_path})')
    print(f'{"scene":<40} {"sentences":>9} {"start":>7} {"seconds":>8}')
    for si, sc in enumerate(scenes):
        ss = [s for s in sentences if s['scene'] == si]
        if not ss:
            continue
        nxt = next((s['start'] for s in sentences if s['scene'] > si), total)
        print(f'{sc["title"][:40]:<40} {len(ss):>9} {sec(ss[0]["start"]):>7.1f} {sec(nxt - ss[0]["start"]):>8.1f}')
    print(f'{"total":<40} {len(sentences):>9} {"":>7} {sec(total):>8.1f}')
    n_audio = len({s['key'] for s in sentences})
    print(f'\naudio:  {len(made_keys)} made, {n_audio - len(made_keys)} reused')
    for s in todo[:10]:
        print(f'  made  line {s["line"]}: {s["text"][:70]}')
    if len(todo) > 10:
        print(f'  ... and {len(todo) - 10} more')
    print(f'frames: {len(made_f)} made, {len(reused_f)} reused')
    for p in made_f[:10]:
        print(f'  made  line {p["spec"]["line"]}: {p["spec"]["raw"][:70]}')
    if len(made_f) > 10:
        print(f'  ... and {len(made_f) - 10} more')
    print(f'timeline: {"rebuilt " + ", ".join(made_out) if made_out else "unchanged, fcpxml and mp4 reused"}')
    print(f'out: {out}')
    print(f'done in {time.time() - t0:.1f} s')


def rough(mp4, frames, clips, total, fps, out):
    """Stills plus one audio track, no transitions: a quick check that words and pictures line up."""
    spf = RATE // fps
    track = bytearray(total * spf * 2)
    for c in clips:
        with wave.open(str(c['path'])) as w:
            data = w.readframes(w.getnframes())
        at = c['start'] * spf * 2
        track[at:at + len(data)] = data
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / 'track.wav'
        with wave.open(str(wav), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(bytes(track))
        # each still is a looped input cut to its exact number of frames, then all are joined (frame-exact, unlike the concat demuxer)
        ins, graph = [], []
        for i, f in enumerate(frames):
            ins += ['-loop', '1', '-framerate', str(fps), '-i', str(f['path'])]
            graph.append(f'[{i}:v]trim=end_frame={f["dur"]},setpts=PTS-STARTPTS,format=yuv420p[v{i}]')
        graph.append(''.join(f'[v{i}]' for i in range(len(frames))) + f'concat=n={len(frames)}:v=1:a=0[v]')
        tmp = mp4.with_suffix('.part.mp4')
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-i', str(wav), '-filter_complex', ';'.join(graph),
                            '-map', '[v]', '-map', f'{len(frames)}:a', '-r', str(fps), '-c:v', 'libx264', '-preset', 'veryfast',
                            '-tune', 'stillimage', '-crf', '26', '-c:a', 'aac', '-b:a', '128k',
                            '-movflags', '+faststart', str(tmp)], capture_output=True, text=True)
        if r.returncode:
            die(f'ffmpeg could not make the rough mp4: {r.stderr.strip()[-600:]}')
        tmp.replace(mp4)


if __name__ == '__main__':
    main()
