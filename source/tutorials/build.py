# The harness tutorials: picture-book slidedocs, one step per page, for a colleague who has the harness installed.
# Same engine and look as "Install the harness" (source/install/build.py, source/tools/deck.py): a .pptx master per deck,
# and an HTML twin printed to PDF by Chrome. The words of each deck live in source/tutorials/<slug>.py; README.md has the format.
#
# Run from the repo root:
#   .venv/bin/python source/tutorials/build.py <slug>     one deck, e.g. 1_day
#   .venv/bin/python source/tutorials/build.py all        every deck that has a text file (not the sample)
# Needs Chrome, and playwright-core from ~/Developer/smarshu.com.
#
# Screenshots are named by paths from the repo root. The build copies each one into the deck's own img/ folder, so a
# later build (and the PDF) never needs the folder it came from; when the source is gone, the copy is used.
# Once a .pptx is edited by hand it is the newer one: export its PDF from PowerPoint and do not rebuild over it.
import os, re, sys, html, json, shutil, filecmp, subprocess, importlib.util
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(ROOT, 'source', 'tools'))
from pptx.dml.color import RGBColor
from deck import Deck, T, P, R, C, W, SERIF, SANS, LS

VERSION = '1.7.45'
OUT = os.path.join(ROOT, 'AI Exploration', '3 Courses', 'Harness tutorials')
MUST_READ = 'AI Exploration/0 MUST READ.pdf'
MONO, GREY = 'Courier New', '9A9A96'
WORD_LIMIT = 60

# slug -> (number on the cover, title; the PDF is "<number> <title>.pdf")
DECKS = {
    '0_must_read': ('0', 'MUST READ'),
    '1_day':       ('1', 'A day with the harness'),
    '2_tour':      ('2', 'A tour of the harness'),
    '3_stopped':   ('3', 'When the agent is stopped'),
    '4_checks':    ('4', 'Independent checks'),
    '5_outside':   ('5', 'Outside systems and connections'),
    '6_kb':        ('6', 'Knowledge base'),
    'sample':      ('',  'Sample'),
}

class TutorialDeck(Deck):
    """The shared engine, plus two run kinds: ('c', text) for what you type, ('mc', text) the same in a company box."""
    def _runs(self, p, para, e):
        for r in para:
            kind = r[0] if isinstance(r, tuple) else None
            if kind in ('c', 'mc'):
                Deck._runs(self, p, [r[1]], e)
                f = p.runs[-1].font; f.name = MONO; f.bold = kind == 'c'
                if kind == 'mc': f.color.rgb = RGBColor.from_string(GREY)
            else:
                Deck._runs(self, p, [r], e)
    def _run_html(self, r, e):
        kind = r[0] if isinstance(r, tuple) else None
        if kind in ('c', 'mc'):
            return f'<span style="font-family:{MONO};font-weight:{"bold" if kind == "c" else "normal"}{";color:#" + GREY if kind == "mc" else ""}">{html.escape(r[1])}</span>'
        return Deck._run_html(self, r, e)

def runs(s, grey=False):
    """'**bold**' and '`code`' in a string, as runs. In a company box every run is grey."""
    out = []
    for part in re.split(r'(\*\*.+?\*\*|`.+?`)', s):
        if not part: continue
        if part.startswith('**'):
            for r in runs(part[2:-2], grey):
                out.append(r if isinstance(r, tuple) else ('b', r))
        elif part.startswith('`'): out.append(('mc' if grey else 'c', part[1:-1]))
        else: out.append(('m', part) if grey else part)
    return out

def words(s): return len(re.sub(r'\*\*|`', '', s).split())

# ---- the height of a text box: measured in Chrome, the engine that prints the PDF (a first pass estimates) ----
MEAS, ASK = {}, {}
def text_h(paras, w, size, space, font=SERIF, bold=False):
    key = repr((paras, round(w, 3), size, space, font, bold))
    if key in MEAS: return MEAS[key]
    ASK[key] = T(0, 0, w, 1, paras, size, C['ink'], font, bold=bold, space=space)
    lines = sum(1 + len(''.join(r[1] if isinstance(r, tuple) else r for r in p)) * size * 0.47 // (w * 72) for p in paras)
    return lines * size * 1.2 * LS / 72 + (len(paras) - 1) * space / 72

def measure(deck, scratch):
    keys = list(ASK); divs = []
    for k in keys:
        e = ASK[k]
        ps = ''.join(f'<p style="margin:0 0 {e["space"]}pt">' + ''.join(deck._run_html(r, e) for r in para) + '</p>' for para in e['paras'])
        divs.append(f'<div class="t" style="width:{e["w"]}in;font-family:{e["font"]};font-size:{e["size"]}pt;font-weight:{"bold" if e["bold"] else "normal"};line-height:{1.2 * e["ls"]:.3f}">{ps}</div>')
    page = f'{scratch}/_measure.html'
    open(page, 'w').write('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0} .t{position:relative} .t p:last-child{margin-bottom:0!important}</style></head><body>' + ''.join(divs) + '</body></html>')
    js = f'{scratch}/_measure.mjs'
    open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true }});
const p = await b.newPage(); await p.goto('file://{page}'); await p.evaluate(() => document.fonts.ready);
console.log(JSON.stringify(await p.$$eval('.t', ts => ts.map(t => t.getBoundingClientRect().height))));
await b.close();''')
    hs = json.loads(subprocess.run(['node', js], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
    for k, h in zip(keys, hs): MEAS[k] = h / 96
    ASK.clear()

# ---- blocks of text, stacked in one column ----
SIZE = 15  # body text: bigger than Install, since a page holds at most ~60 words

def column(blocks, x, y, w, size=SIZE):
    """Stack the blocks of one column from y down. Returns (elements, bottom)."""
    els, buf = [], []
    def flush():
        nonlocal y
        if not buf: return
        h = text_h(list(buf), w, size, 8) + 0.06
        els.append(T(x, y, w, h, list(buf), size, C['ink'], SERIF, space=8)); y += h + 0.12; buf.clear()
    for b in blocks:
        if isinstance(b, str):
            buf.append(runs(b)); continue
        flush()
        kind, val = b
        if kind in ('list', 'steps'):
            paras = [([('a', f'{i}.  ')] if kind == 'steps' else [('a', '•  ')]) + runs(item) for i, item in enumerate(val, 1)]
            h = text_h(paras, w, size, 8) + 0.06
            els.append(T(x, y, w, h, paras, size, C['ink'], SERIF, space=8)); y += h + 0.12
        elif kind == 'code':
            paras = [[l] for l in val.split('\n')]
            cs = max(10, min(13, (w - 0.45) * 72 / (0.6 * max(len(l) for l in val.split('\n')))))
            h = text_h(paras, w - 0.4, cs, 2, MONO, True) + 0.3
            els += [R(x, y, w, h, fill=C['wash']), T(x + 0.2, y + 0.14, w - 0.4, h - 0.2, paras, cs, C['ink'], MONO, bold=True, space=2)]
            y += h + 0.16
        elif kind == 'small':
            h = text_h([[('i', val)]], w, 11, 0) + 0.05
            els.append(T(x, y, w, h, [[('i', val)]], 11, GREY, SERIF)); y += h + 0.1
        elif kind == 'co':
            paras = []
            for item in val:
                if isinstance(item, tuple): paras += [[('mc', l)] for l in item[1].split('\n')]
                else: paras.append(runs(item, grey=True))
            h = text_h(paras, w - 0.4, 12, 5) + 0.34
            els += [R(x, y, w, h, line=GREY, dash=True), T(x + 0.2, y + 0.16, w - 0.4, h - 0.24, paras, 12, GREY, SERIF, space=5)]
            y += h + 0.16
        else:
            raise SystemExit(f'unknown block kind {kind!r} (use a string, list, steps, code, small or co)')
    flush()
    return els, y

def count_words(blocks):
    n = 0
    for b in blocks:
        if isinstance(b, str): n += words(b)
        elif b[0] in ('list', 'steps'): n += sum(words(i) for i in b[1])
        elif b[0] == 'small': n += words(b[1])
    return n

# ---- screenshots: copied into the deck's img/ folder, cropped in scratch ----
class Images:
    def __init__(self, img_dir, scratch):
        self.dir, self.scratch, self.seen, self.missing = img_dir, scratch, {}, []
    def get(self, rel, box=None):
        name = os.path.basename(rel)
        if name in self.seen and self.seen[name] != rel:
            raise SystemExit(f'two screenshots named {name}: {self.seen[name]} and {rel}. Use one of them.')
        self.seen[name] = rel
        src, copy = os.path.join(ROOT, rel), os.path.join(self.dir, name)
        if os.path.exists(src):
            os.makedirs(self.dir, exist_ok=True)
            if not os.path.exists(copy) or not filecmp.cmp(src, copy, shallow=False): shutil.copyfile(src, copy)
        elif not os.path.exists(copy):
            self.missing.append(rel); return None
        if not box: return copy
        out = os.path.join(self.scratch, 'crops', f'{os.path.splitext(name)[0]}-{"-".join(map(str, box))}.png')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        Image.open(copy).crop(box).save(out)
        return out

def shot_box(x, y, w, h, what):
    return [R(x, y, w, h, line=GREY, dash=True),
            T(x + 0.35, y + h / 2 - 0.5, w - 0.7, 1.0, [[('m', '[Company: screenshot]')], [('m', what)]], 13, GREY, SERIF, align='c', space=4)]

TOP, BOTTOM = 1.75, 6.85
TX, TW = 0.75, 4.75           # the text column of a page with a picture
PX, PW = 5.85, W - 0.75 - 5.85  # the picture

# ---- a steps page: 1-4 numbered small steps, each a screenshot and one short line, laid out to make the pictures large ----
CAP, GAPX, GAPY = 14, 0.35, 0.28   # the size of a step's line; the gaps between cells
SX, SW, SBOT = 0.75, 11.83, 6.82   # the area of a steps page (the footer is at 7.0)
SHOT_ASPECT = 1.6                  # a placeholder's shape, width / height, unless the step gives one

def splits(n):
    """Every way to cut n items, in order, into consecutive groups."""
    if n == 0: yield []; return
    for k in range(1, n + 1):
        for rest in splits(n - k): yield [k] + rest

def place(mode, parts, asp, caps, top):
    """Cells (x, y, w, h of the picture) for one arrangement, or None. mode 'rows': each group a row, pictures in a row
    share a height; 'cols': each group a column, pictures in a column share a width. caps: the height of each step's line."""
    H_ = SBOT - top; cells = [None] * len(asp); i = 0; groups = []
    for k in parts: groups.append(list(range(i, i + k))); i += k
    if mode == 'rows':
        raw = [(SW - GAPX * (len(g) - 1)) / sum(asp[j] for j in g) for g in groups]
        capr = [max(caps[j] for j in g) for g in groups]
        room = H_ - sum(capr) - GAPY * (len(groups) - 1)
        if room <= 0: return None
        s = min(1, room / sum(raw)); y = top
        for g, h0, c in zip(groups, raw, capr):
            h = h0 * s; rw = sum(asp[j] * h for j in g) + GAPX * (len(g) - 1); x = SX + (SW - rw) / 2
            for j in g: cells[j] = (x, y, asp[j] * h, h); x += asp[j] * h + GAPX
            y += h + c + GAPY
    else:
        raw = []
        for g in groups:
            room = H_ - sum(caps[j] for j in g) - GAPY * (len(g) - 1)
            if room <= 0: return None
            raw.append(room / sum(1 / asp[j] for j in g))
        s = min(1, (SW - GAPX * (len(groups) - 1)) / sum(raw))
        x = SX + (SW - sum(raw) * s - GAPX * (len(groups) - 1)) / 2
        for g, w0 in zip(groups, raw):
            w = w0 * s; y = top
            for j in g: cells[j] = (x, y, w, w / asp[j]); y += w / asp[j] + caps[j] + GAPY
            x += w + GAPX
    return cells

def step_line(num, text): return [[('a', f'{num}  ')] + runs(text)]
def cap_h(num, text, w): return text_h(step_line(num, text), w, CAP, 0) + 0.1

def arrange(asp, lines, top):
    """The arrangement whose pictures are largest (by the product of their areas), the step lines measured at their widths."""
    import math
    best = None
    for mode in ('rows', 'cols'):
        for parts in splits(len(asp)):
            if mode == 'cols' and len(parts) == len(asp) and len(asp) > 1: continue  # the same as one row
            caps = [0.45] * len(asp)
            for _ in range(2):  # guess the line heights, then measure them at the widths they got
                cells = place(mode, parts, asp, caps, top)
                if not cells: break
                caps = [cap_h(n, t, c[2]) for (n, t), c in zip(lines, cells)]
            cells = cells and place(mode, parts, asp, caps, top)
            if not cells or min(c[2] for c in cells) < 1.2: continue
            score = sum(math.log(c[2] * c[3]) for c in cells)
            if not best or score > best[0]: best = (score, cells, caps)
    if not best: raise SystemExit('a steps page has no room for its pictures: use fewer steps or shorter lines')
    _, cells, caps = best
    dy = (SBOT - max(c[1] + c[3] + k for c, k in zip(cells, caps))) / 2  # centre the whole arrangement up and down
    return [(x, y + dy, w, h) for x, y, w, h in cells], caps

def group_label(text):
    return T(SX, 0.42, 8, 0.3, [[text]], 10, C['accent'], SANS, bold=True, caps=True, spacing=1.5)

def make(slug, X, imgs):
    num, title = DECKS[slug]
    title = getattr(X, 'TITLE', title)
    D = TutorialDeck(getattr(X, 'FOOTER', 'Harness tutorials · ' + title))
    warn = []

    pages = list(getattr(X, 'PAGES', []))
    cl = getattr(X, 'CLOSING', None)
    if cl is None and slug != 'sample':
        raise SystemExit(f'{slug}.py has no CLOSING: every deck ends with a closing page that points to {MUST_READ}.')
    if cl is not None:
        pages.append(dict(cl, kind='closing'))
    kinds = [pg.get('kind') or ('steps' if 'steps' in pg else 'pic' if 'pic' in pg else 'shot' if 'shot' in pg else 'text') for pg in pages]

    # before drawing: the page number of each page, the first step number of each steps page, the group of each page
    cv = getattr(X, 'COVER', None)
    contents = getattr(X, 'CONTENTS', None)
    first = 1 + (cv is not None) + bool(contents)
    starts, groups, step, group = [], [], 1, None
    for pg, kind in zip(pages, kinds):
        starts.append(step)
        if kind == 'steps':
            if not 1 <= len(pg['steps']) <= 4: raise SystemExit(f'a steps page has {len(pg["steps"])} steps; give 1 to 4')
            step += len(pg['steps'])
        if kind != 'closing': group = pg.get('group', group)
        groups.append(group if kind != 'closing' else None)

    if cv is not None:
        how = [f'Harness version {VERSION}.' + (' Follow the numbered steps in order.' if 'steps' in kinds else ' One step per page.'),
               '**Bold** is what you see on the screen. `Courier` is what you type.'] + list(cv.get('how', []))
        D.page([T(0.9, 1.9, 10, 0.4, [[cv.get('kicker', 'Harness tutorials' + (f' · {num}' if num else ''))]], 13, C['accent'], SANS, bold=True, caps=True, spacing=2),
                T(0.9, 2.4, 11.5, 1.2, [[cv.get('title', title)]], 54, C['ink'], SERIF, ls=1.0),
                T(0.9, 3.65, 10.5, 1.3, [runs(cv.get('sub', ''))], 20, C['muted'], SERIF),
                R(0.9, 5.15, 11.5, 0.06, fill=C['accent'], radius=False),
                T(0.9, 5.4, 11.5, 1.3, [runs(s) for s in how], 13, C['ink'], SERIF, space=5)], footer=False)

    if contents:  # one row per group: its name, its steps, the page it starts on
        rows = []
        for name in dict.fromkeys(g for g in groups if g):  # each group once, in order
            idx = [i for i, g in enumerate(groups) if g == name and kinds[i] == 'steps']
            a = starts[idx[0]] if idx else None
            b = starts[idx[-1]] + len(pages[idx[-1]]['steps']) - 1 if idx else None
            rows.append((name, a, b, first + groups.index(name)))
        if len(rows) > 7: warn.append(f'the contents has {len(rows)} groups; more than 7 do not fit')
        title = contents.get('title', 'Contents') if isinstance(contents, dict) else 'Contents'
        els = [group_label(title)]
        y, rh = 1.15, 0.72
        for name, a, b, p in rows:
            steps = '' if a is None else (f'Step {a}' if a == b else f'Steps {a}–{b}')
            els += [R(SX, y, SW, 0.012, fill=C['light'], radius=False),
                    T(SX, y + 0.14, 7.2, 0.5, [[name]], 24, C['ink'], SERIF, ls=1.0),
                    T(8.1, y + 0.24, 2.6, 0.35, [[steps]], 12, C['muted'], SANS, spacing=0.5),
                    T(SX + SW - 1.2, y + 0.14, 1.2, 0.5, [[f'{p:02d}']], 24, C['accent'], SERIF, align='r', ls=1.0)]
            y += rh
        els.append(R(SX, y, SW, 0.012, fill=C['light'], radius=False))
        D.page(els)

    for i, (pg, kind) in enumerate(zip(pages, kinds)):
        n = first + i
        if kind == 'steps':
            top = 0.88 if groups[i] else 0.55
            els = [group_label(groups[i])] if groups[i] else []
            asp, lines, srcs = [], [], []
            for k, st in enumerate(pg['steps']):
                lines.append((starts[i] + k, st.get('text', '')))
                if words(st.get('text', '')) > 20: warn.append(f'page {n}, step {starts[i] + k}: {words(st["text"])} words; keep it to one short line')
                if 'pic' in st:
                    path = imgs.get(*([st['pic']] if isinstance(st['pic'], str) else st['pic']))
                    srcs.append(path)
                    if path: iw, ih = Image.open(path).size; asp.append(iw / ih)
                    else: asp.append(SHOT_ASPECT)
                elif 'shot' in st:
                    srcs.append(None); asp.append(st.get('aspect', SHOT_ASPECT))
                else:
                    raise SystemExit(f'page {n}, step {starts[i] + k}: give pic (a screenshot) or shot (what to capture)')
            cells, caps = arrange(asp, lines, top)
            for st, (x, y, w, h), (num, t), c, path in zip(pg['steps'], cells, lines, caps, srcs):
                if 'pic' in st:
                    if path: els.append(P(path, x, y, w, h, border=True))
                else:
                    els += [R(x, y, w, h, line=GREY, dash=True),
                            T(x + 0.25, y + h / 2 - 0.45, w - 0.5, 0.9, [[('m', '[Company: screenshot]')], [('m', st['shot'])]],
                              12 if w > 4 else 10.5, GREY, SERIF, align='c', space=3)]
                els.append(T(x, y + h + 0.1, w, c - 0.1, step_line(num, t), CAP, C['ink'], SERIF))
            D.page(els, notes=pg.get('notes')); continue
        text = list(pg.get('text', []))
        nw = count_words(text)
        if nw > WORD_LIMIT: warn.append(f'page {n} ({pg.get("title", "")!r}): {nw} words, more than ~{WORD_LIMIT}')
        if kind == 'closing':
            els = Deck.head(pg.get('kicker', 'What next'), pg.get('title', 'Where to go next'))
            a, y = column(text, TX, TOP, 9.5)
            els += a
            y = max(y + 0.15, 4.9)
            pp = [runs('Where to go next: open **0 MUST READ.pdf** at the top of the **AI Exploration** folder. '
                       'It says what each folder is for and which to read next.')]
            for size, gap in ((16, 0.25), (13, 0.15)):  # smaller when the text above leaves little room
                ph = text_h(pp, 11.83, size, 0) + 0.05
                if y + gap + ph <= BOTTOM: break
            else:
                warn.append(f'page {n}: the closing text leaves no room for the pointer to {MUST_READ}')
            els += [R(TX, y, 11.83, 0.05, fill=C['accent'], radius=False),
                    T(TX, y + gap, 11.83, max(ph, 0.9) if size == 16 else ph, pp, size, C['ink'], SERIF)]
            D.page(els, notes=pg.get('notes')); continue
        els = Deck.head(pg['kicker'], pg['title'])
        if kind == 'text':
            a, y = column(text, TX, TOP, 9.5)
            els += a
        elif kind == 'shot':
            a, y = column(text, TX, TOP, TW)
            els += a + shot_box(PX, TOP, PW, BOTTOM - TOP, pg['shot'])
        elif kind == 'pic':
            path = imgs.get(*([pg['pic']] if isinstance(pg['pic'], str) else pg['pic']))
            cap = pg.get('caption')
            if pg.get('wide'):  # the text across the top, the picture across the page under it
                a, y = column(text, TX, TOP, 11.83)
                els += a; py, px, pw = y + 0.05, TX, 11.83
            else:
                a, y = column(text, TX, TOP, TW)
                els += a; py, px, pw = TOP, PX, PW
            if path:
                room = BOTTOM - py - (0.4 if cap else 0)
                pic = P(path, px, py, pw, room, border=True, valign='top')
                els.append(pic)
                if cap: els.append(T(pic['x'], pic['y'] + pic['h'] + 0.08, max(pic['w'], 4), 0.35, [[('i', cap)]], 11, GREY, SERIF))
                if room < 1.5: warn.append(f'page {n}: only {room:.1f} in left for the picture')
            if cap and words(cap) > 20: warn.append(f'page {n}: the caption has {words(cap)} words; keep it to one line')
        else:
            raise SystemExit(f'page {n}: unknown kind {kind!r}')
        if y > BOTTOM + 0.05: warn.append(f'page {n}: the text runs {y - BOTTOM:.2f} in below the bottom')
        D.page(els, notes=pg.get('notes'))
    return D, warn

def build(slug):
    if slug not in DECKS: raise SystemExit(f'unknown deck {slug!r}; one of: {", ".join(DECKS)}, all')
    src = os.path.join(H, f'{slug}.py')
    if not os.path.exists(src): raise SystemExit(f'no text file: {src}')
    spec = importlib.util.spec_from_file_location(f'tutorial_{slug}', src); X = importlib.util.module_from_spec(spec); spec.loader.exec_module(X)
    num, title = DECKS[slug]
    if slug == 'sample':
        out_dir = pptx_dir = os.path.join(H, '_sample'); img_dir = os.path.join(out_dir, 'img')
    else:
        out_dir, img_dir, pptx_dir = OUT, os.path.join(H, 'img', slug), H
    scratch = os.path.join(H, '_build', slug)
    os.makedirs(scratch, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
    MEAS.clear(); ASK.clear()
    imgs = Images(img_dir, scratch)
    D, warn = make(slug, X, imgs)
    if imgs.missing:
        raise SystemExit(f'{slug}: missing screenshots (no file, and no copy in {os.path.relpath(img_dir, ROOT)}):\n  ' + '\n  '.join(imgs.missing))
    for _ in range(4):  # a pass asked for the heights of its text boxes: measure them, then lay the pages out again
        if not ASK: break
        measure(D, scratch); D, warn = make(slug, X, imgs)
    pptx_path = os.path.join(pptx_dir, f'{slug}.pptx')
    pdf_path = os.path.join(out_dir, f'{num} {title}.pdf' if num else f'{title}.pdf')
    D.save_pptx(pptx_path)
    D.save_pdf(scratch, os.path.join(scratch, '_twin.html'), pdf_path, os.path.join(scratch, 'pages'))
    for w in warn: print('WARNING', slug, w)
    print(f'{slug}: {len(D.pages)} pages -> {os.path.relpath(pdf_path, ROOT)}, {os.path.relpath(pptx_path, ROOT)}; page images in {os.path.relpath(scratch, ROOT)}/pages')

if __name__ == '__main__':
    if len(sys.argv) != 2: raise SystemExit(__doc__ or 'usage: build.py <slug>|all')
    if sys.argv[1] == 'all':
        todo = [s for s in DECKS if s != 'sample' and os.path.exists(os.path.join(H, f'{s}.py'))]
        if not todo: print('no deck has a text file yet')
        for s in todo: build(s)
    else:
        build(sys.argv[1])
