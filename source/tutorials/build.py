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
    '2_stopped':   ('2', 'When the agent is stopped'),
    '3_checks':    ('3', 'Independent checks'),
    '4_outside':   ('4', 'Outside systems and connections'),
    '5_kb':        ('5', 'Knowledge base'),
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

def make(slug, X, imgs):
    num, title = DECKS[slug]
    title = getattr(X, 'TITLE', title)
    D = TutorialDeck(getattr(X, 'FOOTER', 'Harness tutorials · ' + title))
    warn = []

    cv = getattr(X, 'COVER', None)
    if cv is not None:
        how = [f'Harness version {VERSION}. One step per page.',
               '**Bold** is what you see on the screen. `Courier` is what you type.'] + list(cv.get('how', []))
        D.page([T(0.9, 1.9, 10, 0.4, [[cv.get('kicker', 'Harness tutorials' + (f' · {num}' if num else ''))]], 13, C['accent'], SANS, bold=True, caps=True, spacing=2),
                T(0.9, 2.4, 11.5, 1.2, [[cv.get('title', title)]], 54, C['ink'], SERIF, ls=1.0),
                T(0.9, 3.65, 10.5, 1.3, [runs(cv.get('sub', ''))], 20, C['muted'], SERIF),
                R(0.9, 5.15, 11.5, 0.06, fill=C['accent'], radius=False),
                T(0.9, 5.4, 11.5, 1.3, [runs(s) for s in how], 13, C['ink'], SERIF, space=5)], footer=False)

    pages = list(getattr(X, 'PAGES', []))
    cl = getattr(X, 'CLOSING', None)
    if cl is None and slug != 'sample':
        raise SystemExit(f'{slug}.py has no CLOSING: every deck ends with a closing page that points to {MUST_READ}.')
    if cl is not None:
        pages.append(dict(cl, kind='closing'))

    for n, pg in enumerate(pages, start=len(D.pages) + 1):
        kind = pg.get('kind') or ('pic' if 'pic' in pg else 'shot' if 'shot' in pg else 'text')
        text = list(pg.get('text', []))
        nw = count_words(text)
        if nw > WORD_LIMIT: warn.append(f'page {n} ({pg.get("title", "")!r}): {nw} words, more than ~{WORD_LIMIT}')
        if kind == 'closing':
            els = Deck.head(pg.get('kicker', 'What next'), pg.get('title', 'Where to go next'))
            a, y = column(text, TX, TOP, 9.5)
            els += a
            y = max(y + 0.15, 4.9)
            els += [R(TX, y, 11.83, 0.05, fill=C['accent'], radius=False),
                    T(TX, y + 0.25, 11.83, 0.9, [runs('Where to go next: open **0 MUST READ.pdf** at the top of the **AI Exploration** folder. '
                                                    'It says what each folder is for and which to read next.')], 16, C['ink'], SERIF)]
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
    if ASK:  # the first pass asked for the heights of its text boxes: measure them, then lay the pages out again
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
