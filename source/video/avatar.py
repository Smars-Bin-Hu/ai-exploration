# The speaking avatar: the person's round picture bottom right, as its own small video with alpha, laid over the stills.
# Silent: the picture with its thin teal ring, still. Speaking: a soft teal glow whose brightness and width follow the
# narration's loudness frame by frame, and a faint ring that ripples outward at each sentence start and loudness peak.
# Drawn with Pillow only: every glow level and every ripple age is drawn once, then each frame is a few composites.
import audioop, math, subprocess, warnings
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

STYLE = 'a2'  # bump when the drawing below changes, so the overlay is made again

SIZE = 360                    # the overlay video is SIZE x SIZE, its centre on CENTRE of the 1920x1080 frame
CENTRE = (1920 - 72 - 66, 1080 - 64 - 66)  # matches .avatar in figs.css (right 72, bottom 64, 132 px)
R = 66                        # outer radius of the picture, ring included
RING = 3
TEAL = (45, 212, 191)
LEVELS = 48                   # glow levels drawn
ATTACK, RELEASE = 0.040, 0.250   # seconds, of the loudness envelope
RIPPLE_LIFE, RIPPLE_GAP = 0.8, 0.6
HOP = 0.010                   # seconds per loudness block


# ---------- loudness ----------

def _smooth(xs, attack, release, hop=HOP):
    a_up, a_down = 1 - math.exp(-hop / attack), 1 - math.exp(-hop / release)
    y, out = 0.0, []
    for x in xs:
        y += (a_up if x > y else a_down) * (x - y)
        out.append(y)
    return out


def loudness(track, rate, fps, total):
    """track: 16-bit mono PCM bytes of the whole timeline -> (level per video frame 0..1, fast envelope per block, blocks per frame).
    Normalised to the voice's own range: the quiet tenth of its speech is 0, the loudest few per cent are 1."""
    n = int(rate * HOP)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        db = [20 * math.log10(max(audioop.rms(track[i:i + 2 * n], 2), 1) / 32768) for i in range(0, len(track), 2 * n)]
    speech = sorted(d for d in db if d > -50)
    per = 1 / (HOP * fps)  # loudness blocks per video frame
    if not speech:
        return [0.0] * total, [], [], per
    lo, hi = speech[len(speech) // 10], speech[min(len(speech) - 1, int(len(speech) * 0.97))]
    norm = [0.0 if d <= -50 else min(1.0, max(0.0, (d - lo) / max(hi - lo, 1e-6))) for d in db]
    slow = _smooth(norm, ATTACK, RELEASE)
    fast = _smooth(norm, 0.010, 0.060)
    level = []
    for f in range(total):
        a, b = int(f * per), max(int(f * per) + 1, int((f + 1) * per))
        seg = slow[a:b] or [0.0]
        level.append(sum(seg) / len(seg))
    return level, fast, slow, per


def onsets(fast, slow, per, sentence_starts, total):
    """Video frames where a ripple starts: every sentence start, and loudness peaks, never closer than RIPPLE_GAP."""
    gap = RIPPLE_GAP / (HOP * per)
    peaks = []
    for i in range(1, len(fast) - 1):
        if fast[i] >= fast[i - 1] and fast[i] > fast[i + 1] and fast[i] > 0.6 and fast[i] - slow[i] > 0.22:
            peaks.append(i / per)
    marks = sorted(set(sentence_starts))
    for p in peaks:  # a peak counts only away from every ripple already kept
        if all(abs(p - m) >= gap for m in marks):
            marks.append(p); marks.sort()
    out, last = [], -1e9
    for m in marks:
        if m - last >= gap and m < total:
            out.append(int(round(m))); last = m
    return out


# ---------- drawing ----------

def _dist_q():
    """distance of each pixel centre from the middle, in quarter pixels"""
    c = SIZE / 2
    return [min(int(math.hypot(x + 0.5 - c, y + 0.5 - c) * 4), 4 * SIZE) for y in range(SIZE) for x in range(SIZE)]


def _teal_layer(dq, alpha_of):
    lut = bytes(max(0, min(255, round(255 * alpha_of(q / 4)))) for q in range(4 * SIZE + 1))
    a = Image.frombytes('L', (SIZE, SIZE), bytes(map(lut.__getitem__, dq)))
    img = Image.new('RGBA', (SIZE, SIZE), TEAL + (0,))
    img.putalpha(a)
    return img


def glow(level):
    """alpha at distance d for a glow level 0..1: brighter and wider as the voice gets louder"""
    peak, width = 0.07 + 0.27 * level, 4 + 15 * level
    return lambda d: peak * math.exp(-((d - R) / width) ** 2) if d > R - 1 else 0


def ripple(p):
    """alpha at distance d for a ripple of age p (0..1 of its life): eases out, fades to nothing"""
    rad, amp = R + 4 + 64 * (1 - (1 - p) ** 2), 0.30 * (1 - p) ** 1.6
    return lambda d: amp * max(0.0, 1 - abs(d - rad) / 1.4)


def layers(avatar_path, fps):
    s = 4  # supersampling for the round edges
    big = SIZE * s
    c0, c1 = big // 2 - R * s, big // 2 + R * s
    # shadow under the picture (as the CSS box-shadow 0 12px 30px rgba(0,0,0,.5))
    sh = Image.new('L', (SIZE, SIZE), 0)
    ImageDraw.Draw(sh).ellipse([SIZE / 2 - R, SIZE / 2 - R + 12, SIZE / 2 + R, SIZE / 2 + R + 12], fill=128)
    shadow = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(15)))
    # the picture in a circle, with the teal ring
    photo = Image.open(avatar_path).convert('RGB')
    w, h = photo.size
    side = min(w, h)
    photo = photo.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2)).resize((2 * R * s, 2 * R * s), Image.LANCZOS)
    face = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse([c0, c0, c1 - 1, c1 - 1], fill=255)
    face.paste(photo, (c0, c0))
    face.putalpha(mask)
    ImageDraw.Draw(face).ellipse([c0, c0, c1 - 1, c1 - 1], outline=TEAL + (255,), width=RING * s)
    face = face.resize((SIZE, SIZE), Image.LANCZOS)
    dq = _dist_q()
    glows = [None] + [_teal_layer(dq, glow(i / LEVELS)) for i in range(1, LEVELS + 1)]
    n_rip = max(1, round(RIPPLE_LIFE * fps))
    ripples = [_teal_layer(dq, ripple(i / n_rip)) for i in range(n_rip)]
    return shadow, face, glows, ripples


def make(out, *, track, rate, fps, total, sentence_starts, avatar_path):
    """Writes the overlay for Final Cut Pro, `out` (.mov, HEVC with alpha, made by Apple's avconvert, so Apple's decoders
    read it), and `preview_path(out)` (H.264, colour left and alpha right) for ffmpeg, which cannot read HEVC alpha.
    The frames go once through ffmpeg into a temporary ProRes 4444 and the preview; avconvert then makes the HEVC."""
    level, fast, slow, per = loudness(track, rate, fps, total)
    starts = onsets(fast, slow, per, sentence_starts, total)
    shadow, face, glows, ripples = layers(avatar_path, fps)
    n_rip = len(ripples)
    out, prev = Path(out), preview_path(out)
    pro, prev_tmp = out.with_suffix('.prores.part.mov'), prev.with_suffix('.part.mp4')
    graph = '[0:v]split[a][b];[a]format=rgb24[c];[b]alphaextract,format=rgb24[al];[c][al]hstack,format=yuv420p[p]'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{SIZE}x{SIZE}',
                            '-r', str(fps), '-i', '-', '-filter_complex', graph,
                            '-map', '0:v', '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', str(pro),
                            '-map', '[p]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-tune', 'animation', str(prev_tmp)],
                           stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    cache, si = {}, 0
    active = []  # start frames of ripples still alive
    try:
        for f in range(total):
            while si < len(starts) and starts[si] <= f:
                active.append(starts[si]); si += 1
            active = [a for a in active if f - a < n_rip]
            q = min(LEVELS, round(level[f] * LEVELS)) if level[f] > 0.03 else 0
            key = (q, tuple(f - a for a in active))
            data = cache.get(key)
            if data is None:
                img = shadow.copy()
                if q:
                    img.alpha_composite(glows[q])
                for age in key[1]:
                    img.alpha_composite(ripples[age])
                img.alpha_composite(face)
                data = img.tobytes()
                if len(cache) < 4000:
                    cache[key] = data
            enc.stdin.write(data)
        enc.stdin.close()
    except BrokenPipeError:
        pass
    err = enc.stderr.read().decode()
    if enc.wait():
        raise RuntimeError(f'ffmpeg could not make the avatar overlay: {err.strip()[-600:]}')
    tmp = out.with_suffix('.part.mov')
    r = subprocess.run(['avconvert', '--preset', 'PresetHEVCHighestQualityWithAlpha', '--source', str(pro),
                        '--output', str(tmp), '--replace'], capture_output=True, text=True)
    pro.unlink(missing_ok=True)
    if r.returncode or not tmp.exists():
        raise RuntimeError(f'avconvert could not make the HEVC overlay: {(r.stdout + r.stderr).strip()[-600:]}')
    tmp.replace(out)
    prev_tmp.replace(prev)
    return dict(onsets=len(starts), speaking=sum(1 for x in level if x > 0.03))


def preview_path(out):
    return Path(out).with_suffix('.preview.mp4')
