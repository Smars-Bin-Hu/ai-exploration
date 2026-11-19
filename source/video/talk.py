"""Talk: the author talks a scene (or one paragraph, a punch-in) in their own words instead of reading it.

Pure text work; build.py runs Whisper and the audio. What it does (FORMAT.md, Recorded voice, Talk):
  - plan(): which words of a take to cut: fillers (um, uh, er, hmm ...), stutters (a word or a fragment said twice: the
    first copy goes) and restarts (a false start, then the same words again: everything before the last attempt goes).
    "like", "so", "you know", "right", "I mean" stay. Flags a high density of "like" (it is not cut).
  - points(): where each spoken line of the script (a "point") was said in the transcript: a monotonic alignment of
    the script's content words to the transcript's (stems, numbers as digits, a few irregular verbs and close synonyms,
    fuzzy matches), then per line the densest run of its matched words. A point is said when half its weight is found;
    words of its key phrases (bold.json) weigh double. A point not found in order is looked for anywhere (order_ok).
  - paragraphs(): a scene's paragraphs over its transcript: which were said, and where to cut between them (the
    longest pause between the last word of one and the first word of the next).
"""
import difflib, math, re

import rec

TALK_VERSION = 'k2'
PROMPT_VERSION = 'kp1'
PAUSE_MAX, PAUSE_KEEP = 0.8, 0.4          # a pause longer than this is shortened to this (sentence takes: rec.py)
CUT_FILLERS = {'um', 'umm', 'uh', 'uhm', 'uhh', 'er', 'erm', 'ah', 'eh', 'hmm', 'hm', 'mm', 'mhm'}
COUNT_FILLERS = {'um', 'umm', 'uh', 'uhm', 'uhh', 'er', 'erm', 'hmm', 'hm'}
LIKE_DENSITY = 1 / 8                      # more "like" than one in 8 words is flagged
SAID = 0.5                                # a point is said when this share of its weight is found
ELSEWHERE = 0.6                           # ... and found out of order with this share, in a window anywhere
JOIN = {'but', 'and', 'so', 'then', 'or'}  # a point may start on one of these even with a comma after it
CLUSTER_GAP = 12                          # matched words of one point at most this many words apart

STOP = set('''a an the and or but nor if then than so as of at by for from in into on onto off to up down out with
without within about over under after before again also too very just really actually basically like well okay ok yeah
oh um umm uh uhm er erm ah eh hmm hm mm mhm gonna wanna kinda sorta
is am are was were be been being do does did doing have has had having get gets got
i me my mine we us our ours you your yours he him his she her hers it its they them their theirs this that these those
there here what which who whom whose when where why how all any some each every both either neither such own same other
another more most much many few lot lots can could will would shall should may might must let lets s re ve ll d m t
one ones thing things way'''.split())
NUM = {w: str(i) for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen '
                                        'fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split())}
NUM.update({'thirty': '30', 'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70', 'eighty': '80', 'ninety': '90',
            'hundred': '100', 'thousand': '1000', 'thousands': '1000', 'hundreds': '100', 'first': '1', 'second': '2',
            'third': '3', 'fourth': '4', 'fifth': '5', 'sixth': '6', 'seventh': '7', 'eighth': '8', 'ninth': '9'})
IRREG = dict(paid='pay', built='build', went='go', gone='go', got='get', gotten='get', said='say', made='make',
             thought='think', done='do', did='do', saw='see', seen='see', ran='run', wrote='write', written='write',
             forgot='forget', forgotten='forget', found='find', gave='give', given='give', told='tell', took='take',
             taken='take', spent='spend', knew='know', known='know', held='hold', brought='bring', kept='keep',
             left='leave', meant='mean', people='person', children='child', men='man', better='good', best='good',
             worse='bad', worst='bad', bigger='big', biggest='big', felt='feel', heard='hear', sent='send', stuck='stick',
             dug='dig', hit='hit', put='put', set='set', began='begin', begun='begin', broke='break', broken='break',
             chose='choose', chosen='choose', led='lead', lost='lose', sat='sit', stood='stand', understood='understand')
# close synonyms a speaker swaps in when talking freely (each group counts as one word, a little less than an exact match)
SYNONYMS = '''company firm business organisation organization employer enterprise | lot many plenty loads tons bunch
| pay buy purchase subscribe spend | tool app product | big huge large massive giant enormous | old legacy ancient
| wrong mistake error bug broken incorrect | check verify review inspect test | start begin kick | finish done complete
end | look see watch view | say tell explain describe mention | hard difficult tough tricky | easy simple | fast quick
quickly faster | real actual | person human someone somebody everybody everyone individual | requirement request ask spec
| file document doc | code codebase | answer reply response respond | question ask query | forget lose | remember recall
| chat conversation chatbot | rule instruction guideline | stop quit halt | dangerous risky unsafe harmful | money cost
spend credit budget | time hour minute | show display present | build make create write | change modify edit update
| run execute | find search locate hunt dig | paste copy | team group squad | model llm | program script code
| agent assistant | safe secure | let allow permit | need require must | keep stay remain | sure confident certain
| right correct | work job task | idea point'''


def base(word):
    """A word as heard or written -> lower case letters and digits; n't -> not, 's 're 've 'll 'd 'm dropped."""
    w = word.lower().replace('’', "'")
    if w.endswith("n't"):
        return 'not'
    w = re.sub(r"'(s|re|ve|ll|d|m)$", '', w)
    return re.sub(r'[^a-z0-9]', '', w)


def stem(w):
    """A base word -> a rough stem: numbers as digits, a few irregular forms, then -ies/-ing/-ed/-es/-s/-ly off."""
    if not w or w.isdigit():
        return w
    if w in NUM:
        return NUM[w]
    if w in IRREG:
        return IRREG[w]
    for suf, rep in (('ies', 'y'), ('ied', 'y'), ('ing', ''), ('ed', ''), ('es', ''), ('s', ''), ('ly', '')):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[:-len(suf)] + rep
            break
    if len(w) > 3 and w[-1] == w[-2] and w[-1] not in 'lsz':
        w = w[:-1]
    if len(w) > 3 and w.endswith('e'):
        w = w[:-1]
    return w


SYN = {}
for _k, _grp in enumerate(SYNONYMS.split('|')):
    for _w in _grp.split():
        SYN.setdefault(stem(_w), _k)


def parts(word):
    """One written or heard word -> its base pieces ("CI-CD" -> ci, cd; "80%" -> 80, percent)."""
    w = word.replace('%', ' percent')
    return [b for b in (base(x) for x in re.split(r'[-/\s–—]+', w)) if b]


_sim_cache = {}


def sim(a, b):
    """Two stems -> 1 same, 0.9 close synonyms, 0.8 one a prefix of the other, 0.7 nearly the same letters, else 0."""
    if a == b:
        return 1.0
    k = (a, b)
    if k in _sim_cache:
        return _sim_cache[k]
    s = 0.0
    if a.isdigit() or b.isdigit():
        s = 0.0
    elif a in SYN and SYN[a] == SYN.get(b):
        s = 0.9
    elif min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a)):
        s = 0.8
    elif min(len(a), len(b)) >= 4 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8:
        s = 0.7
    _sim_cache[k] = s
    return s


def content(text, bold=()):
    """A script line -> its content tokens [(stem, weight)]: words that are not function words (all of them when none
    is left), a word of a key phrase weighs 2, else 1."""
    bold_words = {stem(p) for ph in bold for w in ph.split() for p in parts(w)}
    toks = [stem(p) for w in text.split() for p in parts(w)]
    keep = [t for t in toks if t not in STOP and not (len(t) == 1 and not t.isdigit())]
    if not keep:
        keep = [t for t in toks if t not in CUT_FILLERS]
    return [(t, 2.0 if t in bold_words else 1.0) for t in keep]


# ---------- the cuts ----------

def plan(words, db, length, keep_pause=PAUSE_KEEP, script='', edits=()):
    """A take's words (Whisper, fillers kept: [[word, start, end]] in seconds) -> dict(cuts: [(t0, t1, why)],
    keep: indexes of the words kept, why: {index: filler|stutter|restart|edit: <why>}, auto: the automatic why alone,
    restored: the indexes an edit kept against an automatic cut). db: the take's 10 ms levels.
    edits: the editorial pass (build.py load_edits), [dict(op=cut|keep, from=i, to=j, why=...)] on the word indexes,
    applied over the automatic cuts: "cut" cuts words i..j, "keep" keeps them (undoing an automatic cut).
    A restart is a false start of g words, then its first m words again (m >= 2, or the false start ends in a cut-off
    word). Not a restart: the script has those words so ("find the code, paste the code"), or the repeated words end
    in a comma or stop the first time (a list: "the code, paste the code"), unless the whole attempt is said again."""
    scr = ' ' + ' '.join(rec.norm(w) for w in script.split() if rec.norm(w)) + ' '
    hyp = [(rec.norm(w), s, e, w) for w, s, e in words]
    why = {}
    for k, x in enumerate(hyp):
        if not x[0] or x[0] in CUT_FILLERS:
            why[k] = 'filler'
    for _ in range(3):
        keep = [k for k in range(len(hyp)) if k not in why]
        kw = [hyp[k][0] for k in keep]
        i = 0
        while i < len(keep) - 1:
            raw, a, b = hyp[keep[i]][3], kw[i], kw[i + 1]
            frag = raw.rstrip().endswith(('-', '—', '–')) or (len(a) <= 3 and a not in STOP and a not in NUM)
            if a == b and a not in ('very', 'had', 'that', 'bye', 'no'):  # "the the": the first copy goes
                why[keep[i]] = 'stutter'; i += 1; continue
            if frag and b.startswith(a) and len(b) > len(a):  # "fi- find"
                why[keep[i]] = 'stutter'; i += 1; continue
            done = False
            for g in range(2, 7):  # a false start of g words, then the same words again: keep the last attempt
                if i + g + 1 >= len(kw) + 1:
                    break
                m = 0
                while i + g + m < len(kw) and m < g and kw[i + m] == kw[i + g + m]:
                    m += 1
                said_so = ' ' + ' '.join(kw[i:i + g + m]) + ' ' in scr
                listed = m < g and re.search(r'[,;:.!?]$', hyp[keep[i + m - 1]][3].strip())
                if (m >= 2 and not said_so and not listed) or (m == 1 and raw.rstrip().endswith('-')):
                    for q in range(i, i + g):
                        why[keep[q]] = 'restart'
                    i += g; done = True
                    break
            if not done:
                i += 1
    auto, restored = dict(why), set()
    for e in edits:
        for k in range(max(0, e['from']), min(len(hyp) - 1, e['to']) + 1):
            if e['op'] == 'cut':
                why[k] = 'edit: ' + (e.get('why') or 'cut').split()[0].rstrip(':;,')
            elif k in why:
                del why[k]
                restored.add(k)
    keep = [k for k in range(len(hyp)) if k not in why]
    cuts = rec.cut_ranges(hyp, why, keep, db, length, keep_pause)
    if edits:
        cuts = edit_joints(cuts, hyp, why, keep, db)
    return dict(cuts=cuts, keep=keep, why=why, auto=auto, restored=sorted(restored))


EDIT_VERSION = 'e4'        # bump when edit_joints changes: every edited take is polished again
EDIT_PAUSE = (0.25, 0.4)   # an editorial joint keeps at least / aims at this much of no voice across it (seconds)


def voice_runs(db, v):
    """10 ms levels -> the runs of voice [(k0, k1)] (frames k0..k1-1 at or above v, dips of 30 ms or less bridged, 50 ms
    or longer)."""
    runs, k, n = [], 0, len(db)
    while k < n:
        if db[k] < v:
            k += 1; continue
        j = k
        while j < n and (db[j] >= v or any(db[q] >= v for q in range(j + 1, min(n, j + 4)))):
            j += 1
        if j - k >= 5:
            runs.append((k, j))
        k = j
    return runs


def edit_joints(cuts, hyp, why, keep, db):
    """The joints of the editorial cuts (why "edit: ..."), set on the voice rather than on Whisper's word edges (they
    can be 0.3 s off), so the pause across the joint is about EDIT_PAUSE[1]. The kept voice before the joint ends at E,
    the kept voice after it starts at S (voice_runs at the take's level of voiced speech). After E, up to the first new
    onset, is quiet that may be kept (6 dB under voiced speech, or under it and not rising more than 3 dB in 10 ms:
    room tone, a breath, the voice dying away); before S the same, read backwards. A joint moves only through that
    quiet: it never keeps voice that was cut, nor cuts voice that was kept (a side where the cut does not sit in the
    quiet next to E or S keeps its own point). The pause is split over both sides, each cut at the quietest 10 ms
    near its aim."""
    if not db:
        return cuts
    _, _, v, _ = rec.thresholds(db)
    b = v - 6
    runs = voice_runs(db, v)
    n = len(db)
    loud = lambda k: 0 <= k < n and db[k] >= b
    # quiet that may be kept: under b, or a lone 10 ms tick, or under v and dying away (nb: the frame before it in the
    # direction of the scan)
    quiet_ok = lambda k, nb: (not loud(k) or not (loud(k - 1) or loud(k + 1))) and db[k] < v + 6 \
        or (db[k] < v and db[k] <= db[nb] + 3)

    def snap(lo, hi, target):  # the frame edge in lo..hi (seconds) whose 40 ms around is the quietest, nearest target
        ks = range(max(2, int(round(lo * 100))), min(n - 2, int(round(hi * 100))) + 1)
        if not ks:
            return target
        return min(ks, key=lambda k: (round(max(db[k - 2:k + 2]) / 3), abs(k / 100 - target))) / 100
    out = []
    for t0, t1, w in cuts:
        if not w.startswith('edit') and '+edit' not in w:
            out.append((t0, t1, w)); continue
        mid = [k for k in why if t0 - 0.05 <= (hyp[k][1] + hyp[k][2]) / 2 <= t1 + 0.05]
        prev = max((q for q in keep if mid and q < min(mid)), default=None)
        nxt = min((q for q in keep if mid and q > max(mid)), default=None)
        left = [r for r in runs if r[1] / 100 <= t0 + 0.03]
        right = [r for r in runs if r[0] / 100 >= t1 - 0.03]
        if prev is None or nxt is None or not left or not right:
            out.append((t0, t1, w)); continue
        E, S = left[-1][1], right[0][0]
        k = E
        while k < min(len(db), E + 100) and quiet_ok(k, k - 1):
            k += 1
        L1 = k                                   # E..L1-1: quiet after the kept voice
        k = S - 1
        while k > max(0, S - 100) and quiet_ok(k, k + 1):
            k -= 1
        R0 = k + 1                               # R0..S-1: quiet before the kept voice
        lfree = E / 100 - 0.03 <= t0 <= L1 / 100 + 0.03   # the cut sits in that quiet: it may move through it
        rfree = R0 / 100 - 0.03 <= t1 <= S / 100 + 0.03
        lmax, rmax = (L1 - E) / 100, (S - R0) / 100
        aim = EDIT_PAUSE[1]
        # a side that keeps its point: the quiet it already has (to the last / first frame at the level of voiced speech)
        lp = t0 - (max((q for q in range(E, int(t0 * 100)) if db[q] >= v), default=E - 1) + 1) / 100 if not lfree else None
        rp = min((q for q in range(int(math.ceil(t1 * 100)), S) if db[q] >= v), default=S) / 100 - t1 if not rfree else None
        if lfree and rfree:
            lp = min(lmax, aim / 2)
            rp = min(rmax, aim - lp)
            lp = min(lmax, aim - rp)
        elif lfree:
            lp = min(lmax, max(aim - rp, 0.05))
        elif rfree:
            rp = min(rmax, max(aim - lp, 0.03))
        n0 = snap(E / 100 + max(0.0, lp - 0.03), E / 100 + min(lmax, lp + 0.03), E / 100 + lp) if lfree else t0
        n1 = snap(S / 100 - min(rmax, rp + 0.03), S / 100 - max(0.0, rp - 0.03), S / 100 - rp) if rfree else t1
        out.append((round(n0, 3), round(n1, 3), w) if n1 > n0 else (t0, t1, w))
    return out


def like_flag(words, script):
    """-> (n, density, flagged): the "like"s heard beyond those the script has, per word heard."""
    n = sum(1 for w in words if rec.norm(w[0]) == 'like') - sum(1 for w in script.split() if rec.norm(w) == 'like')
    n = max(n, 0)
    d = n / max(len(words), 1)
    return n, round(d, 3), n >= 2 and d > LIKE_DENSITY


def fillers(words):
    return sum(1 for w in words if rec.norm(w[0]) in COUNT_FILLERS)


def prompt(text):
    """The Whisper prompt for a talk take of this text: the content words (names first), then a disfluent sample at the
    end, which Whisper keeps when it trims a long prompt from the front, so fillers, likes and restarts are written."""
    seen, names, rest = set(), [], []
    for w in text.split():
        b = re.sub(r"[^\w'-]", '', w)
        if not b or base(b) in STOP or base(b) in seen:
            continue
        seen.add(base(b))
        (names if b[0].isupper() or any(c.isdigit() for c in b) else rest).append(b)
    return 'Words: ' + ', '.join((names + rest)[:110]) + '. Umm, so, like, uh, I- I mean, the the thing is, you know...'


# ---------- where each point was said ----------

def points(lines, words):
    """lines: [dict(text, bold)] in script order; words: [[word, start, end]] heard (after cuts), in order.
    -> [dict(k, said, t, w0, w1, score, order)]: t the start of the point (seconds, or None), w0..w1 the word indexes of
    its matched run, order True when it was found in order, False when only out of order."""
    T = []  # transcript tokens: (stem, word index); function words too, for a point made only of them ("What do you do?")
    for wi, (w, _, _) in enumerate(words):
        for p in parts(w):
            st = stem(p)
            if st not in CUT_FILLERS:
                T.append((st, wi))
    S = []  # script tokens: (stem, weight, line)
    tot = []
    for k, ln in enumerate(lines):
        c = content(ln['text'], ln.get('bold', ()))
        tot.append(sum(w for _, w in c))
        S += [(t, w, k) for t, w in c]
    # tokens used by more than one line weigh less: they say little about where a point is
    used = {}
    for t, _, k in S:
        used.setdefault(t, set()).add(k)
    S = [(t, w * (0.6 if len(used[t]) > 1 else 1.0), k) for t, w, k in S]
    tot = [sum(w for _, w, kk in S if kk == k) for k in range(len(lines))]
    n, m = len(S), len(T)
    # monotonic weighted alignment (an LCS where a match scores weight x similarity)
    prev = [0.0] * (m + 1)
    back = []
    for i in range(1, n + 1):
        cur = [0.0] * (m + 1)
        bi = bytearray(m + 1)
        si, wi, _ = S[i - 1]
        for j in range(1, m + 1):
            best, how = prev[j], 0          # skip the script token
            if cur[j - 1] > best:
                best, how = cur[j - 1], 1   # skip the transcript token
            s = sim(si, T[j - 1][0])
            if s and prev[j - 1] + wi * s > best:
                best, how = prev[j - 1] + wi * s, 2
            cur[j], bi[j] = best, how
        back.append(bi)
        prev = cur
    match = {}  # script token -> (transcript token, score)
    i, j = n, m
    while i > 0 and j > 0:
        how = back[i - 1][j]
        if how == 2:
            match[i - 1] = (j - 1, S[i - 1][1] * sim(S[i - 1][0], T[j - 1][0])); i -= 1; j -= 1
        elif how == 1:
            j -= 1
        else:
            i -= 1
    out = []
    last_w = -1
    for k, ln in enumerate(lines):
        got = sorted((match[q][0], match[q][1]) for q in range(n) if S[q][2] == k and q in match)
        best, run = None, []
        for tj, sc in got:  # the densest run of matched tokens
            if run and tj - run[-1][0] > CLUSTER_GAP:
                if best is None or sum(x[1] for x in run) > sum(x[1] for x in best):
                    best = run
                run = []
            run.append((tj, sc))
        if run and (best is None or sum(x[1] for x in run) > sum(x[1] for x in best)):
            best = run
        score = sum(x[1] for x in best) / tot[k] if best and tot[k] else 0.0
        if best and score >= SAID:
            w0, w1 = T[best[0][0]][1], T[best[-1][0]][1]
            out.append(dict(k=k, said=True, order=True, w0=w0, w1=w1, score=round(score, 2)))
            last_w = w1
        else:
            out.append(dict(k=k, said=False, order=None, w0=None, w1=None, score=round(score, 2)))
    # a point the alignment did not find in order: look for it anywhere (a window of about its length)
    for p in out:
        if p['said']:
            continue
        c = content(lines[p['k']]['text'], lines[p['k']].get('bold', ()))
        if not c or not T:
            continue
        L = 3 * len(c) + 6
        tw = sum(w for _, w in c)
        bestsc, at = 0.0, None
        for a in range(0, max(1, m - L + 1)):
            win = T[a:a + L]
            sc = sum(w * max((sim(t, x[0]) for x in win), default=0) for t, w in c) / tw
            if sc > bestsc:
                bestsc, at = sc, a
        if bestsc >= ELSEWHERE and len(c) >= 2:
            win = [x for x in T[at:at + L] if any(sim(t, x[0]) for t, _ in c)]
            p.update(said=True, order=False, w0=win[0][1], w1=win[-1][1], score=round(bestsc, 2))
    # start time: the run's first word, back over up to 3 function words before it (not into the point before, not
    # over a comma or stop, but over a joining word with one: "but, what we see")
    prev_end = -1
    for p in out:
        if not p['said']:
            p['t'] = None; continue
        w0 = p['w0']
        lo = prev_end + 1 if p['order'] else 0
        q = w0
        while q - 1 >= max(lo, w0 - 3) and all(stem(x) in STOP for x in parts(words[q - 1][0]) or ['']) \
                and (not re.search(r'[.?!:;,]$', words[q - 1][0]) or base(words[q - 1][0]) in JOIN):
            q -= 1
        p['w0'] = q
        p['t'] = round(words[q][1], 3)
        if p['order']:
            prev_end = p['w1']
    return out


def summary(pts):
    """points() of one paragraph -> (points for JSON, order_ok, missing)."""
    said = [p for p in pts if p['said']]
    order_ok = all(p['order'] for p in said)
    if order_ok:  # also in time: each found point after the one before
        ts = [p['t'] for p in said]
        order_ok = all(b >= a for a, b in zip(ts, ts[1:]))
    return ([dict(k=p['k'], said=p['said'], t=p['t']) for p in pts], order_ok, [p['k'] for p in pts if not p['said']])


def paragraphs(paras, words):
    """A scene's paragraphs over its transcript. paras: [[dict(text, bold)] lines of each paragraph]; words: heard, in
    order. -> (pts per paragraph (points() with k within the paragraph), found per paragraph, cut: for each two found
    paragraphs in a row, (i, j) the word indexes either side of the pause to cut in)."""
    flat = [ln for p in paras for ln in p]
    pts = points(flat, words)
    per, at = [], 0
    for p in paras:
        mine = [dict(x, k=x['k'] - at) for x in pts[at:at + len(p)]]
        per.append(mine); at += len(p)
    found = [any(x['said'] and x['order'] for x in mine) for mine in per]
    span = [(min(x['w0'] for x in mine if x['said'] and x['order']), max(x['w1'] for x in mine if x['said'] and x['order']))
            if f else None for mine, f in zip(per, found)]
    cuts = {}
    idx = [q for q, f in enumerate(found) if f]
    for a, b in zip(idx, idx[1:]):
        lo, hi = span[a][1], span[b][0] - 1
        if hi < lo:
            lo = hi = max(span[b][0] - 1, 0)
        best = max(range(lo, hi + 1), key=lambda i: ((words[i + 1][1] - words[i][2]) if i + 1 < len(words) else 0)
                   + (0.3 if re.search(r'[.?!]$', words[i][0]) else 0) + i * 1e-6)
        cuts[(a, b)] = (best, best + 1)
    return per, found, span, cuts
