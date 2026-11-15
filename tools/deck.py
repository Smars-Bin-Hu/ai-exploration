# The slide engine shared by Start Here and the Showcase templates: one page model, two outputs.
# A .pptx with editable text boxes, and an HTML twin printed to PDF by Chrome (playwright-core from ~/Developer/smarshu.com),
# which also reports text that does not fit its box.
import os, html, subprocess
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE

W, HT = 13.333, 7.5
SERIF, SANS = 'Georgia', 'Arial'
C = dict(ink='141414', paper='FFFFFF', dark='141414', muted='6B6B6B', light='D6D6D2', white='F2F2F0', accent='E8590C', wash='F2F1EC', faint='3A3A3A')
LS = 1.12  # PowerPoint line spacing (multiple); HTML uses 1.2x that

def fit(path, x, y, w, h, valign='middle'):
    iw, ih = Image.open(path).size
    s = min(w / iw, h / ih); dw, dh = iw * s, ih * s
    dy = y + (h - dh) / 2 if valign == 'middle' else y
    return x + (w - dw) / 2, dy, dw, dh

def T(x, y, w, h, paras, size, color, font=SERIF, bold=False, caps=False, space=6, align='l', spacing=0, ls=LS):
    return dict(k='text', x=x, y=y, w=w, h=h, paras=paras, size=size, color=color, font=font, bold=bold, caps=caps, space=space, align=align, spacing=spacing, ls=ls)
def P(path, x, y, w, h, border=False, valign='middle'):
    fx, fy, fw, fh = fit(path, x, y, w, h, valign); return dict(k='pic', path=path, x=fx, y=fy, w=fw, h=fh, border=border)
def R(x, y, w, h, fill=None, line=None, dash=False, radius=True):
    return dict(k='rect', x=x, y=y, w=w, h=h, fill=fill, line=line, dash=dash, radius=radius)

def is_lab(para): return bool(para) and isinstance(para[0], tuple) and para[0][0] == 'lab'

class Deck:
    def __init__(self, footer_left):
        self.pages = []; self.footer_left = footer_left
    def page(self, els, dark=False, footer=True, notes=None):
        n = len(self.pages) + 1
        if footer:
            col = '9A9A96' if dark else C['muted']
            els = els + [T(0.75, 7.0, 6, 0.25, [[self.footer_left]], 8.5, col, SANS, caps=True, spacing=1.2),
                         T(W - 0.75 - 4, 7.0, 4, 0.25, [[f'© 2026 Smars Hu · {n:02d}']], 8.5, col, SANS, align='r')]
        self.pages.append(dict(dark=dark, els=els, notes=notes))
    @staticmethod
    def head(kicker, title, dark=False, title_w=11.8):
        return [T(0.75, 0.5, 11.8, 0.3, [[kicker]], 10, C['accent'], SANS, bold=True, caps=True, spacing=1.5),
                T(0.75, 0.82, title_w, 0.9, [[title]], 30, C['white'] if dark else C['ink'], SERIF, ls=1.0)]

    # ---- PowerPoint ----
    def _runs(self, p, para, e):
        for r in para:
            kind, text = (r if isinstance(r, tuple) else (None, r))
            run = p.add_run(); run.text = text.upper() if e['caps'] else text
            f = run.font; f.name = e['font']; f.size = Pt(e['size']); f.color.rgb = RGBColor.from_string(e['color']); f.bold = e['bold']
            if kind == 'b': f.bold = True
            if kind == 'i': f.italic = True
            if kind == 'a': f.color.rgb = RGBColor.from_string(C['accent']); f.bold = True
            if kind == 'm': f.italic = True; f.color.rgb = RGBColor.from_string('9A9A96')
            if kind == 'lab':
                f.name = SANS; f.size = Pt(9); f.bold = True; f.color.rgb = RGBColor.from_string(C['accent']); run.text = text.upper()
            if e['spacing']:
                run._r.get_or_add_rPr().set('spc', str(int(e['spacing'] * 100)))

    def save_pptx(self, path):
        rgb = RGBColor.from_string
        prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(HT)
        blank = prs.slide_layouts[6]
        for pg in self.pages:
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
                        p.line_spacing = e['ls']; p.space_after = Pt(2 if is_lab(para) else e['space'])
                        p.alignment = {'l': PP_ALIGN.LEFT, 'r': PP_ALIGN.RIGHT, 'c': PP_ALIGN.CENTER}[e['align']]
                        self._runs(p, para, e)
            if pg['notes']: s.notes_slide.notes_text_frame.text = pg['notes']
        prs.save(path)

    # ---- HTML twin, printed to PDF ----
    def _run_html(self, r, e):
        kind, text = (r if isinstance(r, tuple) else (None, r))
        t = html.escape(text.upper() if e['caps'] else text)
        st = {'b': 'font-weight:bold', 'i': 'font-style:italic', 'a': f'color:#{C["accent"]};font-weight:bold', 'm': 'font-style:italic;color:#9A9A96',
              'lab': f'font-family:{SANS};font-size:9pt;font-weight:bold;color:#{C["accent"]};letter-spacing:.06em'}.get(kind, '')
        return f'<span style="{st}">{t.upper() if kind == "lab" else t}</span>' if st else t

    def save_pdf(self, base, html_path, pdf_path, pages_dir):
        out = []
        for pg in self.pages:
            els = []
            for e in pg['els']:
                box = f'left:{e["x"]}in;top:{e["y"]}in;width:{e["w"]}in;height:{e["h"]}in'
                if e['k'] == 'rect':
                    els.append(f'<div class="r" style="{box};background:{"#" + e["fill"] if e["fill"] else "none"};border:{("1.25pt " + ("dashed" if e["dash"] else "solid") + " #" + e["line"]) if e["line"] else "0"};border-radius:{"0.08in" if e["radius"] else "0"}"></div>')
                elif e['k'] == 'pic':
                    els.append(f'<img src="{os.path.relpath(e["path"], base)}" style="{box};{"outline:0.75pt solid #" + C["faint"] if e["border"] else ""}">')
                else:
                    ps = ''.join(f'<p style="margin:0 0 {2 if is_lab(para) else e["space"]}pt">' + ''.join(self._run_html(r, e) for r in para) + '</p>' for para in e['paras'])
                    els.append(f'<div class="t" style="{box};font-family:{e["font"]};font-size:{e["size"]}pt;color:#{e["color"]};font-weight:{"bold" if e["bold"] else "normal"};text-align:{dict(l="left", r="right", c="center")[e["align"]]};letter-spacing:{e["spacing"]}pt;line-height:{1.2 * e["ls"]:.3f}">{ps}</div>')
            out.append(f'<section style="background:#{C["dark"] if pg["dark"] else C["paper"]}">{"".join(els)}</section>')
        doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>deck</title><style>
@page{{size:{W}in {HT}in;margin:0}} html,body{{margin:0}} section{{position:relative;width:{W}in;height:{HT}in;overflow:hidden;break-after:page}}
section>*{{position:absolute;box-sizing:border-box}} img{{object-fit:contain}}
</style></head><body>{"".join(out)}</body></html>'''
        open(html_path, 'w').write(doc)
        os.makedirs(pages_dir, exist_ok=True)
        js = html_path[:-5] + '.mjs'
        open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true }});
const p = await b.newPage({{ viewport: {{ width: 1280, height: 720 }}, deviceScaleFactor: 1.5 }});
await p.goto('file://{html_path}'); await p.evaluate(() => document.fonts.ready);
const over = await p.$$eval('section', ss => ss.flatMap((s, i) => [...s.querySelectorAll('.t')].filter(t => t.scrollHeight > t.clientHeight + 2).map(t => [i + 1, t.scrollHeight - t.clientHeight, t.textContent.slice(0, 40)])));
console.log('overflow', JSON.stringify(over));
const secs = await p.$$('section');
for (let i = 0; i < secs.length; i++) await secs[i].screenshot({{ path: '{pages_dir}/p' + String(i + 1).padStart(2, '0') + '.png' }});
await p.pdf({{ path: '{pdf_path}', preferCSSPageSize: true, printBackground: true }});
await b.close();''')
        subprocess.run(['node', js], check=True)
