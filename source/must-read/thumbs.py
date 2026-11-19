# Cover thumbnails for 0 MUST READ (source/must-read/img/). Run from the repository root:  .venv/bin/python source/must-read/thumbs.py
# Sources: the Showcase and Install page renders (source/*/_pages/, build scratch), two frames of the basic-01 video
# (.claude/loops/video-out/samples/, not in git), and the M365 Copilot logo (.claude/loops/assets/logos/, not in git).
# The video frames are cropped to x < 1700 so the presenter's avatar (bottom right) never goes into git.
from PIL import Image, ImageDraw, ImageFont
H = 220  # stored height in px; page.html shows them at about half

def save(im, name):
    im = im.convert('RGB'); im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
    im.save(f'source/must-read/img/{name}.png', optimize=True)

def crop(path, box): return Image.open(path).convert('RGB').crop(box)

V = '.claude/loops/video-out/samples/'
save(crop('source/start-here/_pages/p01.png', (60, 0, 1700, 1080)), 'showcase-cover')
save(crop('source/showcase/_pages/sample/p02.png', (0, 0, 1920, 1080)), 'showcase-task')
save(crop(V + '01-card-stop-using-ai-the-2024-way-kicker-b.png', (0, 0, 1700, 1080)), 'video-title')
save(crop(V + '02-board-one-11-plan-crop-0-021-0-335-0-958.png', (0, 0, 1700, 1080)), 'video-plan')
save(crop('source/install/_pages/p01.png', (0, 0, 1920, 1080)), 'install-cover')
save(crop('source/install/_pages/p06.png', (1006, 250, 1816, 640)), 'install-ready')

# the Harness Guide card: the M365 Copilot logo on a plain dark card (no recolour, no busy background), drawn by Chrome
import os, json, subprocess
ROOT = os.getcwd(); out = f'{ROOT}/source/must-read/img/ask-guide.png'
logo = f'{ROOT}/.claude/loops/assets/logos/m365-copilot.svg'; font = f'{ROOT}/.claude/loops/assets/fonts/SourceSerif4-Semibold.ttf'
html = f'''<style>@font-face{{font-family:S;src:url("file://{font}")}}body{{margin:0;width:780px;height:440px;background:#14161a;display:flex;
flex-direction:column;align-items:center;justify-content:center;gap:34px}}img{{width:150px}}b{{font:52px S;color:#f2f2ee;font-weight:normal}}</style>
<img src="file://{logo}"><b>Harness Guide</b>'''
os.makedirs(f'{ROOT}/source/must-read/_build', exist_ok=True); hp = f'{ROOT}/source/must-read/_build/card.html'; open(hp, 'w').write(html)
js = f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true }});
const p = await b.newPage({{ viewport: {{ width: 780, height: 440 }} }}); await p.goto('file://{hp}'); await p.evaluate(() => document.fonts.ready);
await p.screenshot({{ path: {json.dumps(out)} }}); await b.close();'''
jp = f'{ROOT}/source/must-read/_build/card.mjs'; open(jp, 'w').write(js)
subprocess.run(['node', jp], check=True)
im = Image.open(out); save(im, 'ask-guide')
