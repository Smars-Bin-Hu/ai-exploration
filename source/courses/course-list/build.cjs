// The course list: one 16:9 PDF page and manifest.txt in "AI Exploration/3 Courses/", from courses.json.
//   node source/courses/course-list/build.cjs
// Fonts: Source Serif 4 from FONTS (a folder of .ttf files), else <main checkout>/.claude/loops/assets/fonts, else the installed font.
// Playwright: playwright, playwright-core, or ../smarshu.com/node_modules/playwright-core next to this repository.
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const here = __dirname;
const root = path.resolve(here, '../../..');
const out = path.join(root, 'AI Exploration/3 Courses');
const data = JSON.parse(fs.readFileSync(path.join(here, 'courses.json'), 'utf8'));

function loadPlaywright() {
  for (const p of ['playwright', 'playwright-core', path.resolve(root, '../smarshu.com/node_modules/playwright-core'),
                   path.resolve(root, '../ai-exploration/../smarshu.com/node_modules/playwright-core')]) {
    try { return require(p); } catch (e) { /* next */ }
  }
  throw new Error('no Playwright: needs playwright-core in ../smarshu.com/node_modules');
}

function fontsDir() {
  if (process.env.FONTS) return process.env.FONTS;
  try {
    const common = execSync('git rev-parse --path-format=absolute --git-common-dir', { cwd: root }).toString().trim();
    const d = path.join(path.dirname(common), '.claude/loops/assets/fonts');
    if (fs.existsSync(d)) return d;
  } catch (e) { /* none */ }
  return null;
}

const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function html() {
  const fd = fontsDir();
  const face = fd ? [['Regular', 400], ['Semibold', 600], ['Bold', 700]].map(([f, w]) =>
    `@font-face{font-family:'Source Serif 4';font-weight:${w};src:url('file://${path.join(fd, 'SourceSerif4-' + f + '.ttf')}')}`).join('\n') : '';
  const row = (c, live) => `
    <div class="row ${live ? 'live' : ''}">
      <div class="tag">${c.series} ${c.n}</div>
      <div class="title">${esc(c.title)}</div>
      <div class="state">${live ? '&#9654; Video · ' + c.length : 'Planned'}</div>
    </div>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${face}
@page{size:1600px 900px;margin:0}
*{box-sizing:border-box;margin:0}
body{width:1600px;height:900px;background:#161616;color:#e8e6e1;font-family:'Source Serif 4',Georgia,serif;padding:56px 96px;position:relative}
h1{font-size:54px;font-weight:600;letter-spacing:-.5px}
.sub{font-size:22px;color:#9a978f;margin-top:8px}
.list{margin-top:30px;border-top:1px solid #2c2c2c}
.row{display:grid;grid-template-columns:170px 1fr 190px;align-items:baseline;padding:9px 0;border-bottom:1px solid #2c2c2c;font-size:23px;color:#7d7a73}
.row .tag{font-size:19px;letter-spacing:1px;text-transform:uppercase}
.row .state{text-align:right;font-size:20px}
.row.live{color:#e8e6e1}
.row.live .tag,.row.live .state{color:#2dd4bf;font-weight:600}
.row.live .title{font-weight:600}
.row.more{color:#7d7a73}
.note{position:absolute;left:96px;right:96px;bottom:44px;font-size:20px;color:#9a978f}
.note b{color:#e8590c;font-weight:600}
</style></head><body>
<h1>Courses</h1>
<div class="sub">One topic per video. The planned topics are a direction, not a promise: they may change.</div>
<div class="list">
${data.published.map(c => row(c, true)).join('')}
${data.planned.map(c => row(c, false)).join('')}
    <div class="row more"><div class="tag">&nbsp;</div><div class="title">&hellip; and more to come</div><div class="state"></div></div>
</div>
<div class="note"><b>Harness tutorials</b> &nbsp;How to use the harness, day to day: picture-book PDFs for now, each replaced when its video is ready.</div>
</body></html>`;
}

function manifest() {
  const pad = (s, n) => s + ' '.repeat(Math.max(1, n - s.length));
  const lines = ['Courses in this folder. The planned topics may change.', '', 'Published'];
  for (const c of data.published) lines.push(`  ${pad(c.series + ' ' + c.n, 13)}${pad(c.length, 9)}${c.file}`);
  lines.push('', 'Planned');
  for (const c of data.planned) lines.push(`  ${pad(c.series + ' ' + c.n, 13)}${c.title}`);
  lines.push('  ...          and more to come', '', 'Harness tutorials/: picture-book PDFs for now, each replaced when its video is ready.', '');
  return lines.join('\n');
}

(async () => {
  const { chromium } = loadPlaywright();
  let browser;
  try { browser = await chromium.launch({ channel: 'chrome' }); } catch (e) { browser = await chromium.launch(); }
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  const tmp = path.join(here, '_list.html');
  fs.writeFileSync(tmp, html());
  await page.goto('file://' + tmp);
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(out, 'Course list.pdf'), width: '1600px', height: '900px', printBackground: true });
  await page.screenshot({ path: path.join(here, '_preview.png') });
  await browser.close();
  fs.unlinkSync(tmp);
  fs.writeFileSync(path.join(out, 'manifest.txt'), manifest());
  console.log('wrote Course list.pdf and manifest.txt');
})();
