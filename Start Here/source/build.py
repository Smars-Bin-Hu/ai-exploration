# Start Here: one layout, two outputs. ../Start Here.pptx (editable text boxes) and an HTML twin printed to ../Start Here.pdf.
# Run from the repo root: .venv/bin/python "Start Here/source/build.py"   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
import os, html, subprocess, json
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
import slides as S

H = os.path.dirname(os.path.abspath(__file__)); TOP = os.path.dirname(H)
W, HT = 13.333, 7.5
SERIF, SANS = 'Georgia', 'Arial'
C = dict(ink='141414', paper='FFFFFF', dark='141414', muted='6B6B6B', light='D6D6D2', white='F2F2F0', accent='E8590C', wash='F2F1EC', faint='3A3A3A')
LS = 1.12  # PowerPoint line spacing (multiple); HTML uses 1.2x that

def img(name):
    for d in ('img', 'fig'):
        p = f'{H}/{d}/{name}.png'
        if os.path.exists(p): return p
    raise FileNotFoundError(name)

def fit(path, x, y, w, h, valign='middle'):
    iw, ih = Image.open(path).size
    s = min(w / iw, h / ih); dw, dh = iw * s, ih * s
    dy = y + (h - dh) / 2 if valign == 'middle' else y
    return x + (w - dw) / 2, dy, dw, dh

# ---- page model: a list of elements in inches ----
def T(x, y, w, h, paras, size, color, font=SERIF, bold=False, caps=False, space=6, align='l', spacing=0, ls=LS):
    return dict(k='text', x=x, y=y, w=w, h=h, paras=paras, size=size, color=color, font=font, bold=bold, caps=caps, space=space, align=align, spacing=spacing, ls=ls)
def P(path, x, y, w, h, border=False, valign='middle'):
    fx, fy, fw, fh = fit(path, x, y, w, h, valign); return dict(k='pic', path=path, x=fx, y=fy, w=fw, h=fh, border=border)
def R(x, y, w, h, fill=None, line=None, dash=False, radius=True):
    return dict(k='rect', x=x, y=y, w=w, h=h, fill=fill, line=line, dash=dash, radius=radius)

pages = []
def page(els, dark=False, footer=True):
    n = len(pages) + 1
    if footer:
        col = '9A9A96' if dark else C['muted']
        els = els + [T(0.75, 7.0, 6, 0.25, [['AI Exploration · Start Here']], 8.5, col, SANS, caps=True, spacing=1.2),
                     T(W - 0.75 - 4, 7.0, 4, 0.25, [[f'© 2026 Smars Hu · {n:02d}']], 8.5, col, SANS, align='r')]
    pages.append(dict(dark=dark, els=els))

def head(kicker, title, dark=False, title_w=11.8):
    return [T(0.75, 0.5, 11.8, 0.3, [[kicker]], 10, C['accent'], SANS, bold=True, caps=True, spacing=1.5),
            T(0.75, 0.82, title_w, 0.9, [[title]], 30, C['white'] if dark else C['ink'], SERIF, ls=1.0)]

# cover
page([T(0.9, 2.3, 10, 0.4, [[S.COVER['kicker']]], 13, C['accent'], SANS, bold=True, caps=True, spacing=2),
      T(0.9, 2.8, 11, 1.2, [[S.COVER['title']]], 60, C['ink'], SERIF, ls=1.0),
      T(0.9, 4.2, 8.6, 1.2, [[S.COVER['sub']]], 20, C['muted'], SERIF)], footer=False)

for st in S.STORY:
    els = head(st['kicker'], st['title'])
    if 'cards' in st:
        cw, ch, gx, gy = 5.8, 1.95, 0.23, 0.2
        for i, card in enumerate(st['cards']):
            x = 0.75 + (i % 2) * (cw + gx); y = 1.72 + (i // 2) * (ch + gy)
            els += [R(x, y, cw, ch, fill=C['wash']), R(x, y, 0.06, ch, fill=C['accent'], radius=False),
                    T(x + 0.28, y + 0.2, cw - 0.5, ch - 0.35, [card], 13, C['ink'], SERIF)]
        els.append(T(0.75, 6.0, 11.8, 0.9, st['closing'], 13, C['ink'], SERIF, space=4))
    elif st.get('wide'):
        els.append(T(0.75, 1.72, 11.8, 0.8, st['paras'], 14, C['ink'], SERIF))
        els.append(P(img(st['fig']), 0.75, 2.75, 11.8, 4.0))
    else:
        tw = st.get('textw', 5.55); fx = 0.75 + tw + 0.35
        els.append(T(0.75, 1.75, tw, 5.0, st['paras'], 14, C['ink'], SERIF, space=9))
        els.append(P(img(st['fig']), fx, 1.75, 12.6 - fx, 5.0))
    page(els)

for f in S.FEATURES:
    side, title, shot, texts = f[:4]; note = f[4] if len(f) > 4 else None
    els = head(f'{side} ability · In the harness', title, dark=True, title_w=11.8)
    paras = []
    for i, t in enumerate(texts):
        paras.append([('lab', S.L[i])]); paras.append([t])
    if shot and (shot in S.WIDE or (lambda wh: wh[0] / wh[1])(Image.open(img(shot)).size) > 3.5):
        # a very wide screenshot: text in two columns on top, the screenshot across the page below it
        half = len(paras) // 2
        sh = S.WIDE.get(shot, 1.85)  # height of the screenshot; the text gets the rest
        els.append(T(0.75, 1.72, 5.75, 5.0 - sh, paras[:half], 12, C['light'], SERIF, space=5))
        els.append(T(6.85, 1.72, 5.75, 5.0 - sh, paras[half:], 12, C['light'], SERIF, space=5))
        els.append(P(img(shot), 0.75, 6.85 - sh, 11.85, sh, border=True))
        page(els, dark=True); continue
    els.append(T(0.75, 1.72, 5.6, 5.15, paras, 12, C['light'], SERIF, space=5))
    if shot:
        els.append(P(img(shot), 6.7, 1.75, 5.9, 4.85 if note else 5.1, border=True))
        if note: els.append(T(6.7, 6.68, 5.9, 0.25, [[('i', note)]], 10, '9A9A96', SERIF, align='r'))
    else:
        els += [R(6.7, 1.75, 5.9, 5.0, line='9A9A96', dash=True),
                T(7.0, 3.85, 5.3, 0.9, [['Screenshot to add on the company computer:'], ['a test run on DEV, as the task records it']], 13, '9A9A96', SERIF, align='c')]
    page(els, dark=True)

for bh in S.BEHIND:
    # the 'Behind it' of a feature, when it needs a page of its own
    els = head(f"{bh['side']} ability · In the harness", bh['title'], dark=True)
    paras = [[('lab', S.L[4])]] + bh['paras']
    els.append(T(0.75, 1.72, 5.6, 5.15, paras, 12, C['light'], SERIF, space=7))
    els.append(P(img(bh['fig']), 6.7, 1.75, 5.9, 5.1, border=True))
    page(els, dark=True)

ix = S.INDEX
page(head(ix['kicker'], ix['title']) + [T(0.75, 1.75, 5.55, 5.0, ix['paras'], 14, C['ink'], SERIF, space=12), P(img(ix['fig']), 6.65, 1.75, 5.95, 5.0)])

# ---- PowerPoint ----
def rgb(h): return RGBColor.from_string(h)
def add_runs(p, para, e):
    for r in para:
        kind, text = (r if isinstance(r, tuple) else (None, r))
        run = p.add_run(); run.text = text.upper() if e['caps'] else text
        f = run.font; f.name = e['font']; f.size = Pt(e['size']); f.color.rgb = rgb(e['color']); f.bold = e['bold']
        if kind == 'b': f.bold = True
        if kind == 'i': f.italic = True
        if kind == 'a': f.color.rgb = rgb(C['accent']); f.bold = True
        if kind == 'lab':
            f.name = SANS; f.size = Pt(9); f.bold = True; f.color.rgb = rgb(C['accent']); run.text = text.upper()
        if e['spacing']:
            rPr = run._r.get_or_add_rPr(); rPr.set('spc', str(int(e['spacing'] * 100)))

prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(HT)
blank = prs.slide_layouts[6]
for pg in pages:
    s = prs.slides.add_slide(blank)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(C['dark'] if pg['dark'] else C['paper'])
    for e in pg['els']:
        if e['k'] == 'rect':
            sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if e['radius'] else MSO_SHAPE.RECTANGLE, Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h']))
            if e['radius']: sh.adjustments[0] = 0.04
            if e['fill']: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(e['fill'])
            else: sh.fill.background()
            if e['line']:
                sh.line.color.rgb = rgb(e['line']); sh.line.width = Pt(1.25)
                if e['dash']: sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
            else: sh.line.fill.background()
            sh.shadow.inherit = False
        elif e['k'] == 'pic':
            pic = s.shapes.add_picture(e['path'], Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h']))
            if e['border']: pic.line.color.rgb = rgb(C['faint']); pic.line.width = Pt(0.75)
        else:
            tb = s.shapes.add_textbox(Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h']))
            tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            for i, para in enumerate(e['paras']):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.line_spacing = e['ls']; p.space_after = Pt(e['space'] if not (para and isinstance(para[0], tuple) and para[0][0] == 'lab') else 2)
                p.alignment = {'l': PP_ALIGN.LEFT, 'r': PP_ALIGN.RIGHT, 'c': PP_ALIGN.CENTER}[e['align']]
                add_runs(p, para, e)
pptx_path = f'{TOP}/Start Here.pptx'
prs.save(pptx_path)

# ---- HTML twin, for the PDF and the page check ----
def run_html(r, e):
    kind, text = (r if isinstance(r, tuple) else (None, r))
    t = html.escape(text.upper() if e['caps'] else text)
    st = {'b': 'font-weight:bold', 'i': 'font-style:italic', 'a': f'color:#{C["accent"]};font-weight:bold',
          'lab': f'font-family:{SANS};font-size:9pt;font-weight:bold;color:#{C["accent"]};letter-spacing:.06em'}.get(kind, '')
    return f'<span style="{st}">{t.upper() if kind == "lab" else t}</span>' if st else t
out = []
for i, pg in enumerate(pages):
    els = []
    for e in pg['els']:
        box = f'left:{e["x"]}in;top:{e["y"]}in;width:{e["w"]}in;height:{e["h"]}in'
        if e['k'] == 'rect':
            els.append(f'<div class="r" style="{box};background:{"#" + e["fill"] if e["fill"] else "none"};border:{("1.25pt " + ("dashed" if e["dash"] else "solid") + " #" + e["line"]) if e["line"] else "0"};border-radius:{"0.08in" if e["radius"] else "0"}"></div>')
        elif e['k'] == 'pic':
            rel = os.path.relpath(e['path'], H)
            els.append(f'<img src="{rel}" style="{box};{"outline:0.75pt solid #" + C["faint"] if e["border"] else ""}">')
        else:
            ps = ''.join(f'<p style="margin:0 0 {2 if (para and isinstance(para[0], tuple) and para[0][0] == "lab") else e["space"]}pt">' + ''.join(run_html(r, e) for r in para) + '</p>' for para in e['paras'])
            els.append(f'<div class="t" style="{box};font-family:{e["font"]};font-size:{e["size"]}pt;color:#{e["color"]};font-weight:{"bold" if e["bold"] else "normal"};text-align:{dict(l="left", r="right", c="center")[e["align"]]};letter-spacing:{e["spacing"]}pt;line-height:{1.2 * e["ls"]:.3f}">{ps}</div>')
    out.append(f'<section style="background:#{C["dark"] if pg["dark"] else C["paper"]}">{"".join(els)}</section>')
doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>Start Here</title><style>
@page{{size:{W}in {HT}in;margin:0}} html,body{{margin:0}} section{{position:relative;width:{W}in;height:{HT}in;overflow:hidden;break-after:page}}
section>*{{position:absolute;box-sizing:border-box}} img{{object-fit:contain}}
</style></head><body>{"".join(out)}</body></html>'''
open(f'{H}/_twin.html', 'w').write(doc)
js = f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true }});
const p = await b.newPage({{ viewport: {{ width: 1280, height: 720 }}, deviceScaleFactor: 1.5 }});
await p.goto('file://{H}/_twin.html'); await p.evaluate(() => document.fonts.ready);
const over = await p.$$eval('section', ss => ss.flatMap((s, i) => [...s.querySelectorAll('.t')].filter(t => t.scrollHeight > t.clientHeight + 2).map(t => [i + 1, t.scrollHeight - t.clientHeight, t.textContent.slice(0, 40)])));
console.log('overflow', JSON.stringify(over));
const secs = await p.$$('section');
for (let i = 0; i < secs.length; i++) await secs[i].screenshot({{ path: '{H}/_pages/p' + String(i + 1).padStart(2, '0') + '.png' }});
await p.pdf({{ path: '{TOP}/Start Here.pdf', preferCSSPageSize: true, printBackground: true }});
await b.close();'''
os.makedirs(f'{H}/_pages', exist_ok=True)
open(f'{H}/_twin.mjs', 'w').write(js)
subprocess.run(['node', f'{H}/_twin.mjs'], check=True)
print(len(pages), 'slides ->', pptx_path)
