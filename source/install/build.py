# Install the harness: a step-by-step guide for a colleague on a company Windows computer, one step per page.
# One layout, two outputs: source/install/Install the harness.pptx (the master, edited by hand) and an HTML twin printed to
# AI Exploration/4 Install the harness/Install the harness.pdf. Once the PowerPoint is edited by hand it is the newer one:
# export its PDF from PowerPoint and do not rebuild over it.
# Run from the repo root: .venv/bin/python source/install/build.py   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
import os, re, sys, html, json, subprocess
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(ROOT, 'source', 'tools'))
from pptx.dml.color import RGBColor
from deck import Deck, T, P, R, C, W, SERIF, SANS, LS
import text as X

MONO, GREY = 'Courier New', '9A9A96'
OUT = os.path.join(ROOT, 'AI Exploration', '4 Install the harness')
CROPS = os.path.join(H, '_crops')

class InstallDeck(Deck):
    """The shared engine, plus two run kinds: ('c', text) for what you type, ('mc', text) the same in a company placeholder."""
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
    """'**bold**' and '`code`' in a string, as runs. In a company placeholder every run is grey."""
    out = []
    for part in re.split(r'(\*\*.+?\*\*|`.+?`)', s):
        if not part: continue
        if part.startswith('**'):  # bold, which may hold `code`
            for r in runs(part[2:-2], grey):
                out.append(r if isinstance(r, tuple) else ('b', r))
        elif part.startswith('`'): out.append(('mc' if grey else 'c', part[1:-1]))
        else: out.append(('m', part) if grey else part)
    return out

# ---- the height of a text box: measured in Chrome, the same engine that prints the PDF (a first pass estimates) ----
MEAS, ASK = {}, {}
def text_h(paras, w, size, space, font=SERIF, bold=False):
    key = repr((paras, round(w, 3), size, space, font, bold))
    if key in MEAS: return MEAS[key]
    ASK[key] = T(0, 0, w, 1, paras, size, C['ink'], font, bold=bold, space=space)
    lines = sum(1 + len(''.join(r[1] if isinstance(r, tuple) else r for r in p)) * size * 0.47 // (w * 72) for p in paras)
    return lines * size * 1.2 * LS / 72 + (len(paras) - 1) * space / 72

def measure(deck):
    """Fill MEAS for every box asked for: one page with each box at its width and natural height."""
    keys = list(ASK)
    divs = []
    for k in keys:
        e = ASK[k]
        ps = ''.join(f'<p style="margin:0 0 {e["space"]}pt">' + ''.join(deck._run_html(r, e) for r in para) + '</p>' for para in e['paras'])
        divs.append(f'<div class="t" style="width:{e["w"]}in;font-family:{e["font"]};font-size:{e["size"]}pt;font-weight:{"bold" if e["bold"] else "normal"};line-height:{1.2 * e["ls"]:.3f}">{ps}</div>')
    page = f'{H}/_measure.html'
    open(page, 'w').write('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0} .t{position:relative} .t p:last-child{margin-bottom:0!important}</style></head><body>' + ''.join(divs) + '</body></html>')
    js = f'{H}/_measure.mjs'
    open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true }});
const p = await b.newPage(); await p.goto('file://{page}'); await p.evaluate(() => document.fonts.ready);
console.log(JSON.stringify(await p.$$eval('.t', ts => ts.map(t => t.getBoundingClientRect().height))));
await b.close();''')
    hs = json.loads(subprocess.run(['node', js], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
    for k, h in zip(keys, hs): MEAS[k] = h / 96
    ASK.clear()

def code_lines(text):
    return [[l] for l in text.split('\n')]

def column(blocks, x, y, w, size=13):
    """Stack the blocks of one column from y down. Returns (elements, bottom)."""
    els, buf = [], []
    def flush():
        nonlocal y
        if not buf: return
        h = text_h(list(buf), w, size, 7) + 0.06
        els.append(T(x, y, w, h, list(buf), size, C['ink'], SERIF, space=7)); y += h + 0.1; buf.clear()
    for b in blocks:
        if isinstance(b, str):
            buf.append(runs(b)); continue
        flush()
        kind, val = b
        if kind == 'code':  # one command per line; a long one gets a smaller font before it would wrap
            paras = code_lines(val)
            cs = max(10, min(11.5, (w - 0.45) * 72 / (0.6 * max(len(l) for l in val.split('\n')))))
            h = text_h(paras, w - 0.4, cs, 2, MONO, True) + 0.3
            els += [R(x, y, w, h, fill=C['wash']), T(x + 0.2, y + 0.14, w - 0.4, h - 0.2, paras, cs, C['ink'], MONO, bold=True, space=2)]
            y += h + 0.14
        elif kind == 'small':
            h = text_h([[val]], w, 10, 0) + 0.05
            els.append(T(x, y, w, h, [[('i', val)]], 10, GREY, SERIF)); y += h + 0.08
        elif kind == 'co':
            paras = []
            for item in val:
                if isinstance(item, tuple):  # ('mcode', text): a command inside the placeholder
                    paras += [[('mc', l)] for l in item[1].split('\n')]
                else:
                    paras.append(runs(item, grey=True))
            cs = 12
            h = text_h(paras, w - 0.4, cs, 5) + 0.34
            els += [R(x, y, w, h, line=GREY, dash=True), T(x + 0.2, y + 0.16, w - 0.4, h - 0.24, paras, cs, GREY, SERIF, space=5)]
            y += h + 0.14
    flush()
    return els, y

def crop(name, box):
    src = f'{H}/img/{name}.png'
    if not box: return src
    os.makedirs(CROPS, exist_ok=True)
    out = f'{CROPS}/{name}-{"-".join(map(str, box))}.png'
    Image.open(src).crop(box).save(out)
    return out

def shot_box(x, y, w, h, what):
    return [R(x, y, w, h, line=GREY, dash=True),
            T(x + 0.35, y + h / 2 - 0.45, w - 0.7, 0.9, [[('m', '[Company: screenshot]')], [('m', what)]], 12, GREY, SERIF, align='c', space=4)]

TOP, BOTTOM = 1.75, 6.85

def make():
    D = InstallDeck(X.FOOTER)

    # cover
    cv = X.COVER
    D.page([T(0.9, 1.9, 10, 0.4, [[cv['kicker']]], 13, C['accent'], SANS, bold=True, caps=True, spacing=2),
            T(0.9, 2.4, 11, 1.2, [[cv['title']]], 60, C['ink'], SERIF, ls=1.0),
            T(0.9, 3.75, 9.6, 1.1, [[cv['sub']]], 20, C['muted'], SERIF),
            R(0.9, 5.15, 11.5, 0.06, fill=C['accent'], radius=False),
            T(0.9, 5.4, 11.5, 1.3, [runs(s) for s in cv['how'][:2]] + [[('m', cv['how'][2])]], 13, C['ink'], SERIF, space=5)], footer=False)

    tall = []
    for n, pg in enumerate(X.PAGES, start=2):
        els = Deck.head(pg['kicker'], pg['title'])
        top = TOP
        if 'top' in pg:  # blocks across the whole page first
            a, top = column(pg['top'], 0.75, TOP, 11.83)
            els += a
        if pg.get('wide'):  # the text in two columns on top, the picture across the page under it
            half = (len(pg['left']) + 1) // 2
            a, ya = column(pg['left'][:half], 0.75, top, 5.75)
            b, yb = column(pg['left'][half:], 6.85, top, 5.75)
            els += a + b
            y = max(ya, yb) + 0.1
            pic = P(crop(*pg['pic']), 0.75, y, 11.85, BOTTOM - y, border=True, valign='top')
            els.append(pic)
            yb = pic['y'] + pic['h'] + 0.15
            if 'shot' in pg: els += shot_box(0.75, yb, 11.83, BOTTOM - yb, pg['shot'])
        elif 'right' in pg:  # two columns of text
            a, ya = column(pg['left'], 0.75, top, 5.75)
            b, yb = column(pg['right'], 6.85, top, 5.75)
            els += a + b; y = max(ya, yb)
            if 'shot' in pg: els += shot_box(6.85, yb + 0.05, 5.75, BOTTOM - yb - 0.05, pg['shot'])
        else:  # text on the left, the screenshot on the right
            a, y = column(pg['left'], 0.75, top, 5.9)
            els += a
            px, pw, py = 7.0, 5.6, top
            cap = pg.get('caption')
            if 'pic' in pg:
                path = crop(*pg['pic'])
                iw, ih = Image.open(path).size
                room = BOTTOM - py - (0.4 if cap else 0)
                if 'shot' in pg: room = min(room, pw * ih / iw)
                pic = P(path, px, py, pw, room, border=True, valign='top')
                els.append(pic)
                yb = pic['y'] + pic['h'] + 0.08
                if cap:
                    els.append(T(px, yb, pw, 0.35, [[('i', cap)]], 10, GREY, SERIF)); yb += 0.45
                if 'shot' in pg: els += shot_box(px, yb + 0.1, pw, BOTTOM - yb - 0.1, pg['shot'])
            else:
                els += shot_box(px, py, pw, BOTTOM - py, pg['shot'])
        if y > BOTTOM + 0.05: tall.append((n, round(y - BOTTOM, 2)))
        D.page(els, notes=pg.get('notes'))
    return D, tall

D, tall = make()
if ASK:  # the first pass asked for the heights of its text boxes: measure them, then lay the pages out again
    measure(D); D, tall = make()

os.makedirs(OUT, exist_ok=True)
pptx_path = f'{H}/Install the harness.pptx'
D.save_pptx(pptx_path)
D.save_pdf(H, f'{H}/_twin.html', f'{OUT}/Install the harness.pdf', f'{H}/_pages')
print('too tall (page, inches)', tall)
print(len(D.pages), 'slides ->', pptx_path)
