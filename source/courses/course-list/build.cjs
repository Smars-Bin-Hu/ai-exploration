// The course list (Basic, Advanced, Harness tutorials side by side): one 16:9 PDF page and manifest.txt in "AI Exploration/3 Courses/", from courses.json.
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
  const label = { video: c => '&#9654; Video · ' + c.length, pdf: () => 'PDF for now' };
  const row = c => `
      <div class="row ${c.state || 'planned'}">
        <div class="n">${c.n}</div>
        <div class="title">${esc(c.title)}<div class="state">${c.state ? label[c.state](c) : 'Planned'}</div></div>
      </div>`;
  const col = s => `
    <div class="col">
      <h2>${s.name}</h2><div class="about">${s.about}</div>
      <div class="list">${s.courses.map(row).join('')}
        <div class="row more"><div class="n">&hellip;</div><div class="title">and more to come</div></div>
      </div>
    </div>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${face}
@page{size:1600px 900px;margin:0}
*{box-sizing:border-box;margin:0}
body{width:1600px;height:900px;background:#161616;color:#e8e6e1;font-family:'Source Serif 4',Georgia,serif;padding:56px 80px}
h1{font-size:54px;font-weight:600;letter-spacing:-.5px}
.sub{font-size:21px;color:#9a978f;margin-top:6px}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:56px;margin-top:40px}
h2{font-size:30px;font-weight:600;color:#e8590c}
.about{font-size:18px;color:#9a978f;margin-top:2px}
.list{margin-top:16px;border-top:1px solid #2c2c2c}
.row{display:grid;grid-template-columns:40px 1fr;padding:9px 0;border-bottom:1px solid #2c2c2c;font-size:21px;line-height:1.25;color:#7d7a73}
.n{font-size:18px;padding-top:2px}
.state{font-size:15px;letter-spacing:.5px;margin-top:2px}
.row.video{color:#e8e6e1}
.row.video .title{font-weight:600}
.row.video .n,.row.video .state{color:#2dd4bf;font-weight:600}
.row.pdf{color:#c9c6bf}
.row.pdf .state{color:#9a978f}
.row.more .n{color:#7d7a73}
</style></head><body>
<h1>Courses</h1>
<div class="sub">${esc(data.note)}</div>
<div class="cols">${data.series.map(col).join('')}</div>
</body></html>`;
}

function manifest() {
  const lines = ['Courses in this folder. ' + data.note, ''];
  for (const s of data.series) {
    lines.push(`${s.folder}/  (${s.about})`);
    for (const c of s.courses) {
      const st = c.state === 'video' ? `video, ${c.length}` : c.state === 'pdf' ? 'PDF for now' : 'planned';
      lines.push(`  ${c.n.padEnd(4)}${st.padEnd(16)}${c.file || c.title}`);
    }
    lines.push('  ...                 and more to come', '');
  }
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
