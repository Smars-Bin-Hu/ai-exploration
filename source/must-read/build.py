# AI Exploration/0 MUST READ.pdf: the one map of the folder. One A4 portrait page.
# One layout, two outputs: source/must-read/0 MUST READ.pptx (the master, edited by hand in PowerPoint: text boxes, pictures,
# colour bars) and an HTML twin printed to the PDF by Chrome. Once the PowerPoint is edited by hand it is the newer one:
# export its PDF from PowerPoint (File > Export > PDF) over AI Exploration/0 MUST READ.pdf and do not run this build over it.
# Run from anywhere:  .venv/bin/python source/must-read/build.py   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
# Pictures: source/must-read/img/ (made by thumbs.py). To change a picture in PowerPoint: right-click it > Change Picture.
# Checks, exit 1 on failure: one page; every text fits its box; every folder named under "AI Exploration/" exists.
import os, sys, json, html as H, subprocess
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(D))
TOP = os.path.join(ROOT, 'AI Exploration'); IMG = os.path.join(D, 'img'); BUILD = os.path.join(D, '_build')
PPTX = os.path.join(D, '0 MUST READ.pptx'); PDF = os.path.join(TOP, '0 MUST READ.pdf')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PW, PH = 8.27, 11.69  # A4, inches
SERIF, SANS, MONO = 'Georgia', 'Arial', 'Courier New'
INK, MUTED, BODY, RULE = '141414', '6B6B6B', '3C3C3A', 'D6D6D2'
GREEN, BLUE, GREY = '2F8A3E', '2A62B8', '9A9A96'
L, R = 0.8, 7.47  # left and right edge of the content

# ---- the page: a list of elements, in inches ----
# A text is a list of paragraphs; a paragraph is a list of runs; a run is a string or (string, flag).
# Flags: 'b' bold, 'f' a folder name (code font, bold, dark), 'g' a folder name in the grey group, 'q' an example question (blue italic),
# 'k' a command (code font).
def text(x, y, w, h, paras, size=12, color=BODY, font=SANS, bold=False, caps=False, spacing=0, after=0, align='l'):
    return dict(k='text', x=x, y=y, w=w, h=h, paras=paras, size=size, color=color, font=font, bold=bold, caps=caps, spacing=spacing, after=after, align=align)
def pic(name, x, y, w, h): return dict(k='pic', name=name, x=x, y=y, w=w, h=h)
def rect(x, y, w, h, fill): return dict(k='rect', x=x, y=y, w=w, h=h, fill=fill)

PATHS = ['3 Courses/Course list.pdf']  # every folder and file the page names, checked to exist under AI Exploration/

def item(x, y, w, folder, desc, flag, h=0.95):
    PATHS.append(folder.rstrip('/'))
    return text(x, y, w, h, [[(folder, flag)], desc if isinstance(desc, list) else [desc]], after=2)

def build_page():
    els = [text(L, 0.8, 6, 0.25, [['AI Exploration']], size=9, color=MUTED, caps=True, spacing=2),
           text(L, 1.05, 7, 0.65, [['What to open here']], size=30, color=INK, font=SERIF)]

    y = 1.95  # READ
    els += [rect(L, y, 0.08, 3.62, GREEN), text(1.1, y, 4, 0.3, [['Read']], size=11, color=GREEN, bold=True, caps=True, spacing=2)]
    rows = [('1 Showcase/', 'Real tasks from my day, done with the AI harness. Picture books, with the task page as proof.', ('showcase-cover', 'showcase-task')),
            ('3 Courses/', ['Videos, one or two a week: how to use the harness, and the basics of AI engineering. We know you hate reading docs. ', ('Course list.pdf', 'b'), ' shows what is out and what is next.'], ('video-title', 'video-plan')),
            ('4 Install the harness/', 'Follow the steps and install it on your own computer.', ('install-cover', 'install-ready'))]
    iy = y + 0.42
    for (folder, desc, pics), h in zip(rows, (0.95, 1.15, 0.95)):
        els += [item(1.1, iy, 3.42, folder, desc, 'f', h), pic(pics[0], 4.67, iy, 1.35, 0.9), pic(pics[1], 6.12, iy, 1.35, 0.9)]
        iy += h + 0.07

    y = 5.87  # ASK M365 COPILOT
    els += [rect(L, y, 0.08, 2.2, BLUE), text(1.1, y, 5, 0.3, [['Ask M365 Copilot']], size=11, color=BLUE, bold=True, caps=True, spacing=2),
            text(1.1, y + 0.42, 4.2, 2.1, [
                ['For anyone who really wants to dive deep into this harness framework: its design, architecture, source code, features… Open the ',
                 ('Harness Guide', 'b'), ' agent and ask. This is not a tutorial for learning to use the harness.'],
                [('“What is this harness, and what problem does it solve?”', 'q')],
                [('“Why isn’t a rule in the prompt enough to keep the agent safe?”', 'q')]], color=INK, after=7),
            pic('ask-guide', 5.47, y + 0.65, 2.0, 1.13)]

    y = 8.42  # DO NOT OPEN
    els += [rect(L, y, 0.08, 1.85, GREY), text(1.1, y, 4, 0.3, [['Do not open']], size=11, color=GREY, bold=True, caps=True, spacing=2),
            item(1.1, y + 0.42, 6.3, '2 Ask the Harness Guide/Knowledge/',
                 'The files the Harness Guide agent reads. Written for the agent, not for people: ask the agent instead.', 'g'),
            item(1.1, y + 1.1, 6.3, '_Archive/',
                 'Earlier material kept for reference, such as the Deep Dive on how a Task works. Replaced by the Harness Guide and the Courses, and may be out of date.', 'g')]

    els += [rect(L, 10.62, R - L, 0.012, RULE),
            text(L, 10.7, R - L, 0.42, [['After installing, in VS Code Copilot chat: ', ('/harness-rookie-quick-start', 'k'), ' walks you through a first task; ',
                                         ('/harness-rookie-wondering', 'k'), ' teaches it all from the code (spends Copilot credits).']], size=9.5, color=MUTED),
            text(L, 11.28, 4, 0.2, [['AI Exploration · 0 MUST READ']], size=8, color=GREY),
            text(R - 3, 11.28, 3, 0.2, [['The one map of this folder']], size=8, color=GREY, align='r')]
    return els

def run_style(e, flag):
    f = dict(font=e['font'], bold=e['bold'], italic=False, color=e['color'])
    if flag == 'b': f['bold'] = True
    if flag in ('f', 'g'): f.update(font=MONO, bold=True, color=INK if flag == 'f' else MUTED)
    if flag == 'q': f.update(italic=True, color=BLUE)
    if flag == 'k': f.update(font=MONO, color=INK)
    return f

def runs(e):
    for para in e['paras']:
        yield [(r if isinstance(r, tuple) else (r, None)) for r in para]

# ---- PowerPoint ----
def cover_crop(path, bw, bh):
    """Crop fractions (left, right, top, bottom) that make the picture fill a bw x bh box, anchored left, centred vertically."""
    iw, ih = Image.open(path).size; s = max(bw / iw, bh / ih)
    cw, ch = bw / s, bh / s
    return 0, (iw - cw) / iw, (ih - ch) / 2 / ih, (ih - ch) / 2 / ih

def make_pptx(els):
    prs = Presentation(); prs.slide_width = Inches(PW); prs.slide_height = Inches(PH)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    for e in els:
        if e['k'] == 'rect':
            sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h']))
            sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(e['fill']); sh.line.fill.background(); sh.shadow.inherit = False
        elif e['k'] == 'pic':
            path = os.path.join(IMG, e['name'] + '.png')
            p = s.shapes.add_picture(path, Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h']))
            p.crop_left, p.crop_right, p.crop_top, p.crop_bottom = cover_crop(path, e['w'], e['h'])
            p.line.color.rgb = RGBColor.from_string(RULE); p.line.width = Pt(0.75); p.name = e['name']
        else:
            tb = s.shapes.add_textbox(Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h'])); tf = tb.text_frame
            tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            for pi, para in enumerate(runs(e)):
                p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
                p.space_after = Pt(e['after'])
                if e['align'] == 'r': p.alignment = PP_ALIGN.RIGHT
                for t, flag in para:
                    st = run_style(e, flag); r = p.add_run(); r.text = t.upper() if e['caps'] else t
                    f = r.font; f.name = st['font']; f.size = Pt(e['size']); f.bold = st['bold']; f.italic = st['italic']
                    f.color.rgb = RGBColor.from_string(st['color'])
                    if e['spacing']: r._r.get_or_add_rPr().set('spc', str(int(e['spacing'] * 100)))
    prs.save(PPTX)

# ---- the HTML twin, printed to the PDF ----
def make_html(els):
    out = []
    for n, e in enumerate(els):
        pos = f'left:{e["x"]}in;top:{e["y"]}in;width:{e["w"]}in;height:{e["h"]}in'
        if e['k'] == 'rect': out.append(f'<div style="{pos};background:#{e["fill"]}"></div>')
        elif e['k'] == 'pic':
            out.append(f'<img src="file://{os.path.join(IMG, e["name"] + ".png")}" style="{pos};object-fit:cover;object-position:left center;'
                       f'outline:.75pt solid #{RULE};outline-offset:-.75pt">')
        else:
            ps = []
            for para in runs(e):
                rs = []
                for t, flag in para:
                    st = run_style(e, flag)
                    css = (f'font-family:{st["font"]};font-weight:{"bold" if st["bold"] else "normal"};'
                           f'font-style:{"italic" if st["italic"] else "normal"};color:#{st["color"]}')
                    rs.append(f'<span style="{css}">{H.escape(t.upper() if e["caps"] else t)}</span>')
                ps.append(f'<p style="margin:0 0 {e["after"]}pt">{"".join(rs)}</p>')
            sp = f';letter-spacing:{e["spacing"]}pt' if e['spacing'] else ''; al = ';text-align:right' if e['align'] == 'r' else ''
            out.append(f'<div class="t" style="{pos};font-size:{e["size"]}pt;line-height:normal{sp}{al}">{"".join(ps)}</div>')
    return ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>@page{size:' + f'{PW}in {PH}in' + ';margin:0}html,body{margin:0}'
            f'body{{width:{PW}in;height:{PH}in;position:relative;overflow:hidden;background:#fff}}body>*{{position:absolute;box-sizing:border-box}}'
            '</style></head><body>' + ''.join(out) + '</body></html>')

def main():
    els = build_page()
    make_pptx(els)
    os.makedirs(BUILD, exist_ok=True)
    hp = os.path.join(BUILD, 'page.html'); open(hp, 'w', encoding='utf-8').write(make_html(els))
    js = os.path.join(BUILD, 'print.mjs')
    open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: {json.dumps(CHROME)}, headless: true }});
const p = await b.newPage({{ viewport: {{ width: 794, height: 1123 }} }});
await p.goto('file://' + {json.dumps(hp)}); await p.evaluate(() => document.fonts.ready);
const over = await p.evaluate(() => [...document.querySelectorAll('.t')].filter(t => t.scrollHeight > t.clientHeight + 1).map(t => t.textContent.slice(0, 40)));
const buf = await p.pdf({{ path: {json.dumps(PDF)}, width: '{PW}in', height: '{PH}in', printBackground: true, preferCSSPageSize: true }});
const pages = (buf.toString('latin1').match(/\\/Type\\s*\\/Page[^s]/g) || []).length;
console.log('REPORT ' + JSON.stringify({{ pages, over }}));
await b.close();''')
    r = subprocess.run(['node', js], capture_output=True, text=True)
    if r.returncode: raise SystemExit('node failed:\n' + r.stderr)
    rep = json.loads(r.stdout.split('REPORT ', 1)[1].splitlines()[0])
    bad = [f'no "{p}"' for p in PATHS if not os.path.exists(os.path.join(TOP, p))]
    if rep['pages'] != 1: bad.append(f'{rep["pages"]} pages, must be 1')
    bad += [f'text does not fit its box: "{t}"' for t in rep['over']]
    subprocess.run(['qlmanage', '-t', '-s', '1600', '-o', BUILD, PDF], capture_output=True)
    prev = os.path.join(BUILD, 'page.png'); os.replace(os.path.join(BUILD, os.path.basename(PDF) + '.png'), prev)
    print(f'0 MUST READ: {rep["pages"]} page; {os.path.relpath(PPTX, ROOT)}; preview {os.path.relpath(prev, ROOT)}')
    if bad: print(f'FAIL: {len(bad)} problem(s)'); [print('  -', b) for b in bad]; sys.exit(1)
    print('All checks passed.')

if __name__ == '__main__':
    main()
