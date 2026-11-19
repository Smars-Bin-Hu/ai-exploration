# Subtitles: each spoken line is one cue, timed as its audio clip. A line too long for two rows of ~42 characters
# becomes several cues in a row, split at a clause break, its time shared by character count. All times are in frames.
import re
from pathlib import Path

FONTS = Path(__file__).resolve().parent.parent.parent / '.claude/loops/assets/fonts'

WIDTH, ROWS = 42, 2


def wrap(text, width=WIDTH):
    rows, row = [], ''
    for word in text.split():
        trial = f'{row} {word}'.strip()
        if len(trial) <= width or not row:
            row = trial
        else:
            rows.append(row); row = word
    if row:
        rows.append(row)
    if len(rows) == 2:  # balance two rows, so the second is not a lone word
        words = text.split()
        best = min(range(1, len(words)), key=lambda i: max(len(' '.join(words[:i])), len(' '.join(words[i:]))))
        a, b = ' '.join(words[:best]), ' '.join(words[best:])
        if max(len(a), len(b)) <= width:
            rows = [a, b]
    return rows


def fits(text):
    return len(wrap(text)) <= ROWS


def chunks(text):
    """Split a line into pieces that each fit two rows: at clause breaks first, then at word boundaries."""
    if fits(text):
        return [text]
    parts = [p for p in re.split(r'(?<=[,;:.!?—–])\s+', text) if p]  # clause pieces, punctuation kept
    out, cur = [], ''
    for p in parts:
        trial = f'{cur} {p}'.strip()
        if fits(trial):
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = p
            while not fits(cur):  # one clause longer than two rows: cut at the last word that fits
                words, head = cur.split(), ''
                for i, w in enumerate(words):
                    if not fits(f'{head} {w}'.strip()):
                        out.append(head); cur = ' '.join(words[i:]); break
                    head = f'{head} {w}'.strip()
    if cur:
        out.append(cur)
    return out


def cues(lines, starts, durs):
    """lines[i] is spoken from starts[i] for durs[i] frames -> [(start, dur, [rows])]."""
    out = []
    for text, start, dur in zip(lines, starts, durs):
        pieces = chunks(text)
        total = sum(len(p) for p in pieces)
        t, used = start, 0
        for j, p in enumerate(pieces):
            used += len(p)
            end = start + dur if j == len(pieces) - 1 else start + round(dur * used / total)
            if end > t:
                out.append((t, end - t, wrap(p)))
            t = end
    return out


def word_cues(words, start, fps, end=None):
    """What was said, with word times -> cues: a talked paragraph's subtitles. words: [[word, t0, t1]] in seconds from
    `start` (a frame); end: the frame the last cue must end by. Cut at clause breaks (and pauses over 0.6 s), clauses
    packed into cues of two rows at most, a new cue after a sentence end once a cue has 25 letters; a clause too long
    for two rows is cut at the last word that fits. Each cue shows from its first word to its last word's end + 0.5 s
    (at least 0.8 s), never into the next cue; the first cue starts with a capital. -> [(start, dur, [rows])] in frames."""
    words = [w for w in words if w[0].strip()]
    clauses, cur = [], []
    for k, w in enumerate(words):
        cur.append(w)
        nxt = words[k + 1] if k + 1 < len(words) else None
        if nxt is None or re.search(r'[,;:.!?\u2014\u2013]["\'\u201d\u2019)]*$', w[0]) or nxt[1] - w[2] > 0.6:
            clauses.append(cur); cur = []
    txt = lambda ws: ' '.join(x[0] for x in ws)
    groups, cur = [], []
    for c in clauses:
        if cur and (not fits(txt(cur + c)) or (re.search(r'[.!?]["\'\u201d\u2019)]*$', cur[-1][0]) and len(txt(cur)) >= 25)):
            groups.append(cur); cur = []
        for w in c:
            if cur and not fits(txt(cur + [w])):
                groups.append(cur); cur = []
            cur.append(w)
    if cur:
        groups.append(cur)
    out = []
    for k, g in enumerate(groups):
        s = start + round(g[0][1] * fps)
        nxt = start + round(groups[k + 1][0][1] * fps) if k + 1 < len(groups) else end
        e = max(start + round((g[-1][2] + 0.5) * fps), s + round(0.8 * fps))
        if nxt is not None:
            e = min(e, nxt)
        if out and s < out[-1][0] + out[-1][1]:
            s = out[-1][0] + out[-1][1]
        if e > s:
            text = txt(g)
            out.append((s, e - s, wrap(text[:1].upper() + text[1:] if not k else text)))
    return out


def _ts(frames, fps, sep):
    ms = round(frames * 1000 / fps)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}'


def srt(cue_list, fps):
    return ''.join(f'{i}\n{_ts(s, fps, ",")} --> {_ts(s + d, fps, ",")}\n' + '\n'.join(rows) + '\n\n'
                   for i, (s, d, rows) in enumerate(cue_list, 1))


def ass(cue_list, fps, width, height):
    """An ASS file for burning in: white serif text on a dark translucent box, bottom centre, sized for 1080p.
    The side margins keep it clear of the avatar (bottom right). Source Serif 4 comes from the fonts folder that build.py
    hands to ffmpeg (fontsdir); without it, Georgia."""
    def t(f):
        cs = round(f * 100 / fps)
        return f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'
    esc = lambda s: s.replace('\\', '\\\\').replace('{', '(').replace('}', ')')
    font = 'Source Serif 4' if (FONTS / 'SourceSerif4-Regular.ttf').exists() else 'Georgia'
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},52,&H00F3EDE6,&H00F3EDE6,&HFF000000,&H48101010,0,0,0,0,100,100,0,0,4,16,0,2,300,300,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return head + ''.join(f'Dialogue: 0,{t(s)},{t(s + d)},Default,,0,0,0,,' + r'\N'.join(esc(r) for r in rows) + '\n'
                          for s, d, rows in cue_list)
