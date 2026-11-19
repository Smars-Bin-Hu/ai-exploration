"""Recorded voice: the author's own takes, one wav per sentence, made into pieces a paragraph clip is joined from.

Pure audio and text work on 48 kHz mono 16-bit PCM (array('h')); build.py runs the tools (ffmpeg, Whisper, DeepFilterNet)
and the cache. What happens to a take, in order (FORMAT.md, Recorded voice):
  1. heard: Whisper word times on the take as recorded, with a prompt that keeps fillers and repeats (verbatim()).
  2. plan(): the words against the sentence: cut fillers (um, uh, er ...), the first copy of a word or words said twice,
     and a false start (everything before the last complete attempt); flag missing, extra or wrong words.
  3. apply_cuts(): those cuts, at the quietest point near each word edge, joined with a 10 ms crossfade.
  4. (build.py) denoise, high-pass, level, gentle compression, de-ess.
  5. shorten_pauses(): a pause inside the sentence over PAUSE_MAX seconds is cut down to PAUSE_KEEP.
  6. voice_span() + trim: REC_HEAD before the voice, REC_TAIL after it.
  7. room_tone(): the take's quietest stretches, to fill the gaps between sentences instead of digital silence.
"""
import array, difflib, math, re

RATE = 48000
HOP = RATE // 100          # 10 ms
FILLERS = {'um', 'umm', 'uh', 'uhm', 'uhh', 'er', 'erm', 'ah', 'eh', 'hmm', 'hm', 'mm', 'mhm'}
PAUSE_MAX, PAUSE_KEEP = 0.5, 0.35
XFADE = HOP                # samples of crossfade at every cut
PROMPT_VERSION = 'v1'
# Whisper drops fillers, repeats and false starts when its prompt is the clean sentence; a prompt that is itself
# disfluent keeps them, and the sentence's words as a list keep the spelling close to the script (tried: say-made takes
# with an um, a repeated word and a restart; the plain sentence as prompt lost the restart, no words misheard it).
PROMPT = 'Umm, so, uh, I- I mean, the the thing is... Words: '


def norm(w):
    return re.sub(r'[^a-z0-9]', '', w.lower())


def verbatim(text):
    """The Whisper prompt for a take of this sentence."""
    return PROMPT + ', '.join(sorted({norm(w) for w in text.split() if norm(w)})) + '.'


# ---------- levels ----------

def db10(pcm):
    """array('h') -> loudness in dB of each 10 ms."""
    out = []
    for i in range(0, len(pcm), HOP):
        seg = pcm[i:i + HOP]
        e = sum(x * x for x in seg) / max(len(seg), 1)
        out.append(10 * math.log10(max(e, 1)) - 90.309)  # 20*log10(32768) = 90.309
    return out


def zcr10(pcm):
    """array('h') -> sign changes per sample in each 10 ms (voiced speech is low, breath and hiss are high)."""
    out = []
    for i in range(0, len(pcm), HOP):
        seg = pcm[i:i + HOP]
        out.append(sum(1 for x, y in zip(seg, seg[1:]) if (x < 0) != (y < 0)) / max(len(seg) - 1, 1))
    return out


def thresholds(db):
    """-> (peak, floor, hi, lo): the take's loud end (99th percentile, so a click does not set it), its room tone
    (10th percentile), the level of voiced speech (hi) and the level above the room tone (lo)."""
    srt = sorted(db)
    peak, floor = srt[int(0.99 * (len(srt) - 1))], srt[int(0.1 * (len(srt) - 1))]
    return peak, floor, max(peak - 25, floor + 15), max(peak - 45, floor + 8)


def voice_span(pcm, db=None):
    """Where the voice is in a take, robust to a click or a breath before or after it. -> (v0, v1) in samples, or None.
    The core is the voiced speech: 10 ms frames within 25 dB of the loud end with few sign changes (a vowel, not a
    breath or hiss), in runs of 50 ms or more (a click is shorter); a short run alone more than 0.7 s from the rest is
    dropped (a lip smack, a cough). From the core the span reaches out over quieter frames still above the room tone:
    up to 0.2 s before (an s or f the sentence starts with, but not a breath 40 ms or more before it), 0.3 s after (a
    last s, a word dying away, a last t or k up to 80 ms after its closure)."""
    db = db or db10(pcm)
    if not db:
        return None
    zc = zcr10(pcm)
    _, _, hi, lo = thresholds(db)

    def runs(ok):
        out = []
        for k, v in enumerate(ok):
            if v and out and k - out[-1][1] <= 3:  # gaps of 30 ms or less are one run
                out[-1][1] = k + 1
            elif v:
                out.append([k, k + 1])
        return [r for r in out if r[1] - r[0] >= 5]
    core = runs([d > hi and z < 0.06 for d, z in zip(db, zc)]) or runs([d > hi for d in db])
    if not core:
        return None
    while len(core) > 1 and core[0][1] - core[0][0] < 20 and core[1][0] - core[0][1] > 70:
        core.pop(0)
    while len(core) > 1 and core[-1][1] - core[-1][0] < 20 and core[-1][0] - core[-2][1] > 70:
        core.pop()
    a, b = core[0][0], core[-1][1]

    def reach(k, step, most, bridge):  # out from the core over frames above lo, across a dip of `bridge` frames at most
        end, j = k, k
        while 0 <= j + step < len(db) and abs(j + step - k) <= most:
            j += step
            if db[j] > lo:
                end = j
            elif abs(j - end) > bridge:
                break
        return end
    a = reach(a, -1, 20, 4)
    b = reach(b - 1, 1, 30, 8) + 1
    return a * HOP, min(b * HOP, len(pcm))


def fade(pcm, n_in, n_out):
    """Short fades at the ends of a cut (in place), so a cut in the room tone does not click."""
    for i in range(min(n_in, len(pcm))):
        pcm[i] = int(pcm[i] * i / n_in)
    for i in range(min(n_out, len(pcm))):
        pcm[-1 - i] = int(pcm[-1 - i] * i / n_out)


def splice(segs):
    """Pieces of audio -> one, each joined to the next with a XFADE crossfade."""
    out = array.array('h')
    for seg in segs:
        n = min(XFADE, len(out), len(seg))
        for i in range(n):
            r = (i + 1) / (n + 1)
            out[len(out) - n + i] = int(out[len(out) - n + i] * (1 - r) + seg[i] * r)
        out.extend(seg[n:])
    return out


# ---------- the words ----------

def compare(script, heard):
    """Two lists of normalised words -> difflib opcodes, where a replace whose letters are the same both sides
    ("along" heard for "a long") counts as equal."""
    ops = []
    for op in difflib.SequenceMatcher(None, script, heard, autojunk=False).get_opcodes():
        t, i1, i2, j1, j2 = op
        if t == 'replace' and ''.join(script[i1:i2]) == ''.join(heard[j1:j2]):
            t = 'equal'
        ops.append((t, i1, i2, j1, j2))
    return ops


def coverage(script, heard):
    return sum(i2 - i1 for t, i1, i2, _, _ in compare(script, heard) if t == 'equal') / max(len(script), 1)


def plan(text, words, db, length):
    """A take's words (Whisper, [[word, start, end]] in seconds) against its sentence -> dict(cuts: [(t0, t1, why)],
    heard, missing, extra, ok). db: the take's 10 ms levels; length: its seconds. Cuts are at the quietest point near
    the edges of the words cut, keeping the pause around them up to PAUSE_KEEP."""
    script = [norm(w) for w in text.split() if norm(w)]
    hyp = [(norm(w), s, e, w) for w, s, e in words if norm(w)]
    heard = ' '.join(w for w, _, _ in words)
    why = {}
    # a false start: everything before the last place a complete attempt (80% of the sentence's words) starts
    for p in range(len(hyp) - 1, 0, -1):
        if hyp[p][0] == script[0] and coverage(script, [x[0] for x in hyp[p:]]) >= 0.8:
            for k in range(p):
                why[k] = 'restart'
            break
    for k, x in enumerate(hyp):
        if k not in why and x[0] in FILLERS and x[0] not in script:
            why[k] = 'filler'
    for _ in range(4):  # a word or words said twice: the first copy goes (an unfinished last word still counts)
        keep = [k for k in range(len(hyp)) if k not in why]
        kw = [hyp[k][0] for k in keep]
        found = False
        for t, i1, i2, j1, j2 in compare(script, kw):
            if t not in ('insert', 'replace'):
                continue
            n = j2 - j1
            if t == 'replace' and coverage(script[i1:i2], kw[j1:j2]) > 0:
                continue

            def same(a, b):
                return len(a) == len(b) and all(x == y or (q == len(a) - 1 and y.startswith(x)) for q, (x, y) in enumerate(zip(a, b)))
            if same(kw[j1:j2], kw[j2:j2 + n]):
                cut = range(j1, j2)
            elif j1 >= n and same(kw[j1 - n:j1], kw[j1:j2]):
                cut = range(j1 - n, j1)
            else:
                continue
            for q in cut:
                why[keep[q]] = 'repeat'
            found = True
            break
        if not found:
            break
    keep = [k for k in range(len(hyp)) if k not in why]
    kw = [hyp[k][0] for k in keep]
    missing, extra = [], []
    for t, i1, i2, j1, j2 in compare(script, kw):
        if t in ('delete', 'replace'):
            missing += [w for w in text.split() if norm(w)][i1:i2]
        if t in ('insert', 'replace'):
            extra += [hyp[keep[q]][3] for q in range(j1, j2)]
    cuts = cut_ranges(hyp, why, keep, db, length)
    return dict(cuts=cuts, heard=heard, missing=missing, extra=extra, ok=not missing and not extra)


def cut_ranges(hyp, why, keep, db, length, keep_pause=PAUSE_KEEP):
    """Words to cut -> time ranges [(t0, t1, why)]. hyp: [(norm, start, end, word)]; why: {index: reason}; keep: the
    indexes kept. Each cut is at the quietest point near the edges of the words cut, keeping the pause around them up
    to keep_pause."""
    cuts, k = [], 0
    while k < len(hyp):
        if k not in why:
            k += 1; continue
        j = k
        while j + 1 < len(hyp) and j + 1 in why:
            j += 1
        prev = max((q for q in keep if q < k), default=None)
        nxt = min((q for q in keep if q > j), default=None)
        room = ((hyp[k][1] - hyp[prev][2]) if prev is not None else 0) + ((hyp[nxt][1] - hyp[j][2]) if nxt is not None else 0)
        p = min(keep_pause, max(0.0, room))
        # Whisper's word edges can be 0.1 to 0.3 s off: look for the quiet a little either side of them
        t0 = 0.0 if prev is None else quiet(db, hyp[prev][2] - 0.1, hyp[k][1] + 0.1, hyp[prev][2] + p / 2)
        t1 = length if nxt is None else quiet(db, hyp[j][2] - 0.1, hyp[nxt][1] + 0.1,
                                             hyp[nxt][1] - (0.1 if prev is None else p / 2))
        if t1 > t0:
            cuts.append((round(t0, 3), round(t1, 3), why[k] if all(why[q] == why[k] for q in range(k, j + 1)) else
                         '+'.join(sorted({why[q] for q in range(k, j + 1)}))))
        k = j + 1
    return cuts


def quiet(db, a, b, target):
    """The 10 ms frame edge between a and b seconds that is about the quietest (within 4 dB of the least), the one
    closest to target. -> seconds."""
    k0, k1 = max(0, int(a * 100)), min(len(db) - 1, int(math.ceil(b * 100)))
    if k1 < k0:
        return max(0.0, min(target, len(db) / 100))
    least = min(db[k0:k1 + 1])
    cand = [k for k in range(k0, k1 + 1) if db[k] <= least + 4]
    return min(cand, key=lambda k: abs(k / 100 - target)) / 100


def apply_cuts(pcm, cuts):
    """Cut the time ranges [(t0, t1, why)] out of a take, the pieces joined with a crossfade."""
    if not cuts:
        return pcm
    segs, at = [], 0
    for t0, t1, _ in sorted(cuts):
        a, b = round(t0 * RATE), round(t1 * RATE)
        if a > at:
            segs.append(pcm[at:a])
        at = max(at, b)
    segs.append(pcm[at:])
    return splice([s for s in segs if len(s)])


def time_map(cuts, length):
    """The cuts [(t0, t1, ...)] apply_cuts makes in a take of `length` seconds -> f(t): where a moment of the take is
    after them (a moment inside a cut goes to its join), counting the crossfade at each join."""
    segs, at = [], 0
    for t0, t1, *_ in sorted(cuts):
        a, b = round(t0 * RATE), round(t1 * RATE)
        if a > at:
            segs.append((at, a))
        at = max(at, b)
    segs.append((at, round(length * RATE)))
    segs = [s for s in segs if s[1] > s[0]]
    outs, pos = [], 0
    for k, (a, b) in enumerate(segs):
        pos -= min(XFADE, pos, b - a) if k else 0
        outs.append(pos)
        pos += b - a

    def f(t):
        x = t * RATE
        for (a, b), o in zip(segs, outs):
            if x < a:
                return o / RATE
            if x <= b:
                return (o + x - a) / RATE
        return pos / RATE
    return f


def shorten_pauses(pcm, db=None, most=PAUSE_MAX, keep=PAUSE_KEEP):
    """A pause inside the voice longer than `most` (PAUSE_MAX) is cut to `keep` (PAUSE_KEEP) (its middle goes). -> (pcm, [(t0, t1)]):
    the new take and the stretches cut, in the take's seconds before the cut."""
    db = db or db10(pcm)
    span = voice_span(pcm, db)
    if not span:
        return pcm, []
    _, _, _, lo = thresholds(db)
    k0, k1 = span[0] // HOP, span[1] // HOP
    cuts, k = [], k0
    while k < k1:
        if db[k] > lo:
            k += 1; continue
        j = k
        while j < k1 and db[j] <= lo:
            j += 1
        if (j - k) / 100 > most:
            half = keep / 2
            cuts.append((round(k / 100 + half, 3), round(j / 100 - half, 3), 'pause'))
        k = j
    return apply_cuts(pcm, cuts), [(a, b) for a, b, _ in cuts]


def room_tone(pcm, db=None, most=2.0):
    """The take's room tone: its stretches of 100 ms or more within 4 dB of its quietest tenth, spliced, up to `most`
    seconds. -> array('h') (empty if there is none)."""
    db = db or db10(pcm)
    if len(db) < 20:
        return array.array('h')
    _, floor, _, _ = thresholds(db)
    segs, k = [], 0
    while k < len(db) and sum(map(len, segs)) < most * RATE:
        if db[k] > floor + 4:
            k += 1; continue
        j = k
        while j < len(db) and db[j] <= floor + 4:
            j += 1
        if j - k >= 10:
            segs.append(pcm[(k + 1) * HOP:(j - 1) * HOP])  # a frame in from each end, clear of the voice
        k = j
    return splice(segs) if segs else array.array('h')


def tone_fill(tone, n):
    """n samples of room tone (looped with crossfades; silence if there is none), faded in and out over XFADE."""
    if not len(tone) or n <= 0:
        return array.array('h', [0] * max(n, 0))
    out = array.array('h')
    while len(out) < n + XFADE:
        out = splice([out, tone]) if len(out) else array.array('h', tone)
    out = out[:n]
    fade(out, min(XFADE, n // 2), min(XFADE, n // 2))
    return out


def join(pieces, gap):
    """Takes cut to their voice -> one paragraph, `gap` seconds from the end of one's voice to the start of the next's;
    what their own head and tail do not cover is room tone. pieces: [(pcm, meta, tone)], meta with dur, vs, ve.
    The pieces' ends are faded, the room tone between them is faded in and out under those fades."""
    out = array.array('h')
    for k, (pcm, m, tone) in enumerate(pieces):
        if k:
            prev = pieces[k - 1][1]
            n = max(0, round((gap - (prev['dur'] - prev['ve']) - m['vs']) * RATE))
            fill = tone_fill(tone if len(tone) else pieces[k - 1][2], n + 2 * XFADE)
            o = max(0, len(out) - XFADE)  # the fill starts under the last piece's fade-out
            for i in range(min(XFADE, len(fill), len(out) - o)):
                out[o + i] = max(-32768, min(32767, out[o + i] + fill[i]))
            out.extend(fill[len(out) - o:len(fill) - XFADE] if len(fill) > XFADE else [])
            tail = fill[-XFADE:] if len(fill) > XFADE else array.array('h')
            head = array.array('h', pcm)
            for i in range(min(len(tail), len(head))):  # and ends under this piece's fade-in
                head[i] = max(-32768, min(32767, head[i] + tail[i]))
            out.extend(head)
        else:
            out.extend(pcm)
    return out
