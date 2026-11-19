# The timeline: where each sentence piece starts and when each picture fades in, in frames.
#
# The voice speaks a paragraph in one go (one clip; a long one in runs of whole sentences), and the clip is cut into one
# piece per sentence. Inside a clip the pieces are put back to back, so the voice keeps its own pauses and nothing is
# inserted; a picture that changes there fades in `lead` before the word its line starts with, with no dwell. Between
# two clips of one paragraph: `gap`. Between paragraphs on the same picture: `para_gap`. When the picture changes at
# a paragraph break, the outgoing picture stays `dwell` after the words end (+`busy` for a busy picture), then the new
# one fades in, `lead` before its first word; between scenes the silence is at least `scene_gap`. A picture holds at
# least `min_hold` from its fade-in to the next one's; a shorter beat is merged (see merge()). Transitions are centred
# on the edit point: the fade starts at the fade-in time, so the edit point is `d/2` after it.
from dataclasses import dataclass


@dataclass
class Rules:
    fps: int = 25
    gap: float = 0.3          # silence between two clips of one long paragraph
    para_gap: float = 0.5     # silence between paragraphs on the same picture
    dwell: float = 0.8        # at a paragraph break: the outgoing picture stays this long after the words end
    busy: float = 0.4         # added to dwell for a busy picture
    scene_gap: float = 1.4    # silence between scenes (at least dwell + lead)
    lead: float = 0.3         # a new picture starts fading in this long before its first word
    min_hold: float = 2.2     # a picture stays at least this long (fade-in to next fade-in) before a different picture
    step_min_hold: float = 1.0  # a step of a figure or list stays at least this long before its next step
    head: float = 0.6         # the first word starts this long after the video starts
    tail: float = 1.2         # the last picture stays this long after the last word
    xfade: float = 0.5        # cross-dissolve between different pictures
    step_xfade: float = 0.35  # between steps of one figure or one list


def _even(seconds, fps):
    return max(2, 2 * round(seconds * fps / 2))


def compute(sents, pics, r):
    """sents: [dict(frames, vs, ve, starts, scene, para, chunk, lines)] (vs, ve, starts in seconds within the piece;
    para: the paragraph, chunk: the clip it was cut from; lines: the global indexes of the spoken lines it is made of).
    pics: [dict(at, busy, group, scene)] in order, at = global line index, pics[0].at == 0. -> dict(T: clip starts, F: fade-in starts, hold, total), all in frames."""
    fps = r.fps
    where = {}  # global line -> (sentence, line within it)
    for k, s in enumerate(sents):
        for j, g in enumerate(s['lines']):
            where[g] = (k, j)
    pic_at = {p['at']: i for i, p in enumerate(pics)}
    shown_at = []  # global line -> index of the picture on screen while it is spoken
    cur = 0
    for g in range(len(where)):
        cur = pic_at.get(g, cur)
        shown_at.append(cur)
    T = []
    for k, s in enumerate(sents):
        if not k:
            T.append(max(0, round((r.head - s['vs']) * fps))); continue
        p = sents[k - 1]
        if s.get('chunk') is not None and s.get('chunk') == p.get('chunk'):  # cut from one clip: back to back
            T.append(T[-1] + p['frames']); continue
        out = pics[shown_at[p['lines'][-1]]]
        dwell = r.dwell + (r.busy if out['busy'] else 0)
        if s['scene'] != p['scene']:
            g = max(r.scene_gap, dwell + r.lead)
        elif s.get('para') is not None and s.get('para') == p.get('para'):
            g = max(r.gap, r.lead) if s['lines'][0] in pic_at else r.gap
        elif s['lines'][0] in pic_at:
            g = dwell + r.lead
        else:
            g = r.para_gap
        t = round((T[-1] / fps + p['ve'] + g - s['vs']) * fps)
        T.append(max(t, T[-1] + p['frames']))
    F = []
    for i, pc in enumerate(pics):
        k, j = where[pc['at']]
        f = 0 if not i else round((T[k] / fps + sents[k]['starts'][j] - r.lead) * fps)
        F.append(max(f, F[-1] + 1) if F else f)
    last = sents[-1]
    total = max(T[-1] + last['frames'], round((T[-1] / fps + last['ve'] + r.tail) * fps))
    hold = [(F[i + 1] if i + 1 < len(F) else total) - F[i] for i in range(len(F))]
    return dict(T=T, F=F, hold=hold, total=total)


def merge(sents, pics, r):
    """Merges beats that are too short, shortest first, until none is left (or none can be merged). Too short: under
    min_hold before a different picture; under step_min_hold before the next step of the same figure, list, loop,
    timeline or formula (a step dissolve is gentle, so a step may go by quickly and stay on its own words).
    A short picture is skipped when the picture before it is in the same scene (the one before stays longer, and a
    later step never shows early); else the next one (same scene) shows from its start. Words are never moved or cut.
    -> (pics, layout, merges: [(dropped pic, kept pic, hold seconds, how)], short: pics that stay short)"""
    pics = [dict(p) for p in pics]
    merges, stuck = [], set()
    while True:
        lay = compute(sents, pics, r)
        def need(i):
            nx = pics[i + 1] if i + 1 < len(pics) else None
            step = nx is not None and pics[i]['group'] and nx['group'] == pics[i]['group'] and nx['scene'] == pics[i]['scene']
            return round((r.step_min_hold if step else r.min_hold) * r.fps)
        short = [i for i, hd in enumerate(lay['hold']) if hd < need(i) and id(pics[i]) not in stuck]
        if not short:
            break
        i = min(short, key=lambda x: lay['hold'][x])
        p, nxt, prv = pics[i], pics[i + 1] if i + 1 < len(pics) else None, pics[i - 1] if i else None
        same_next = nxt is not None and nxt['scene'] == p['scene']
        same_prev = prv is not None and prv['scene'] == p['scene']
        secs = lay['hold'][i] / r.fps
        if same_prev:
            how, kept = 'skipped, the picture before stays', prv
        elif same_next:
            how, kept = 'next picture shown from its start', nxt
        else:
            stuck.add(id(p)); continue
        if kept is nxt:
            nxt['at'] = p['at']
        merges.append((p, kept, secs, how))
        del pics[i]
    short = [(p, hd / r.fps) for p, hd in zip(pics, lay['hold']) if id(p) in stuck]
    return pics, lay, merges, short


def transitions(pics, lay, r):
    """-> per picture i >= 1: (duration frames, kind), and the edit points E (frames; E[0] = 0)."""
    tr, E = [None], [0]
    for i in range(1, len(pics)):
        step = pics[i]['group'] is not None and pics[i]['group'] == pics[i - 1]['group']
        d = _even(r.step_xfade if step else r.xfade, r.fps)
        d = min(d, 2 * (min(lay['hold'][i - 1], lay['hold'][i]) // 4))  # never longer than half a hold
        d = max(d, 0)
        tr.append((d, 'step' if step else 'dissolve'))
        E.append(lay['F'][i] + d // 2)
    return tr, E
