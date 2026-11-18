# Subtitles: each spoken line is one cue, timed as its audio clip. A line too long for two rows of ~42 characters
# becomes several cues in a row, split at a clause break, its time shared by character count. All times are in frames.
import re

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


def _ts(frames, fps, sep):
    ms = round(frames * 1000 / fps)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}'


def srt(cue_list, fps):
    return ''.join(f'{i}\n{_ts(s, fps, ",")} --> {_ts(s + d, fps, ",")}\n' + '\n'.join(rows) + '\n\n'
                   for i, (s, d, rows) in enumerate(cue_list, 1))


def ass(cue_list, fps, width, height):
    """An ASS file for burning in: white text on a dark translucent box, bottom centre, sized for 1080p."""
    def t(f):
        cs = round(f * 100 / fps)
        return f'{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'
    esc = lambda s: s.replace('\\', '\\\\').replace('{', '(').replace('}', ')')
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,50,&H00FFFFFF,&H00FFFFFF,&HFF000000,&H40141414,0,0,0,0,100,100,0,0,4,14,0,2,120,120,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return head + ''.join(f'Dialogue: 0,{t(s)},{t(s + d)},Default,,0,0,0,,' + r'\N'.join(esc(r) for r in rows) + '\n'
                          for s, d, rows in cue_list)
