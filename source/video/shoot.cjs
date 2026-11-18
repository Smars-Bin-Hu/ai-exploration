// Screenshots HTML pages at 1920x1080 for render.py: one browser for a whole batch.
//   node source/video/shoot.cjs jobs.json
// jobs.json: {css, icons, logos, jobs: [{url, out, step, theme, avatar}]}
//   css: file:// url of figs.css, added when the page does not link it already
//   icons: folder of Lucide svgs; <i data-icon="name"> gets that svg inline (stroke = currentColor)
//   logos: folder of logos; <img data-logo="name"> gets the best file for a dark background, or a labelled placeholder
//   step: elements with data-step="k" become .later (k > step), .lit (k == step) or .done (k < step); <html> gets .at-1 ... .at-step
//   theme: a class on <html>, e.g. theme-navy; avatar: file:// url of the round picture bottom right, or null
// Playwright: playwright-core from smarshu.com (or `playwright` if installed); the browser is the installed Chrome,
// else Playwright's own headless shell.
const fs = require('fs');
const path = require('path');

function loadPlaywright() {
  for (const p of ['playwright', 'playwright-core', '/Users/smars/Developer/smarshu.com/node_modules/playwright-core']) {
    try { return require(p); } catch (e) { /* next */ }
  }
  throw new Error('no Playwright: needs playwright-core in /Users/smars/Developer/smarshu.com/node_modules');
}

async function launch(chromium) {
  try { return await chromium.launch({ channel: 'chrome' }); } catch (e) { /* fall through */ }
  const cache = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
  const shells = fs.existsSync(cache) ? fs.readdirSync(cache).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse() : [];
  for (const d of shells) {
    const exe = path.join(cache, d, 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell');
    if (fs.existsSync(exe)) return chromium.launch({ executablePath: exe });
  }
  return chromium.launch();
}

// best logo file for a dark background: the name itself, then light variants, then any file that starts with the name
function logoFile(dir, name) {
  if (!fs.existsSync(dir)) return null;
  const files = fs.readdirSync(dir);
  const exts = ['.svg', '.png'];
  const order = ['', '-white', '-ivory', '-lockup-white', '-icon-white', '-wordmark-white', '-mark-white', '-light'];
  for (const suf of order) for (const ext of exts) if (files.includes(name + suf + ext)) return path.join(dir, name + suf + ext);
  const any = files.filter(f => f.startsWith(name + '-') && exts.includes(path.extname(f)) && !/black|slate|dark/.test(f)).sort();
  return any.length ? path.join(dir, any[0]) : null;
}

(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const { chromium } = loadPlaywright();
  const browser = await launch(chromium);
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const iconCache = {};
  for (const job of spec.jobs) {
    await page.goto(job.url, { waitUntil: 'load' });
    // icons and logos the page asks for
    const iconNames = await page.$$eval('i[data-icon]', els => [...new Set(els.map(e => e.dataset.icon))]);
    const icons = {};
    for (const n of iconNames) {
      if (!(n in iconCache)) {
        const f = path.join(spec.icons, n + '.svg');
        iconCache[n] = fs.existsSync(f) ? fs.readFileSync(f, 'utf8') : null;
      }
      icons[n] = iconCache[n];
    }
    const logoNames = await page.$$eval('img[data-logo]', els => [...new Set(els.map(e => e.dataset.logo))]);
    const logos = {};
    for (const n of logoNames) { const f = logoFile(spec.logos, n); logos[n] = f ? 'file://' + f : null; }
    await page.evaluate(async ({ job, icons, logos, css }) => {
      const html = document.documentElement;
      if (job.theme) html.classList.add(job.theme);
      if (![...document.querySelectorAll('link[rel=stylesheet]')].some(l => l.href.endsWith('figs.css'))) {
        const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = css;
        const done = new Promise(r => { l.onload = r; l.onerror = r; });
        document.head.appendChild(l); await done;
      }
      document.querySelectorAll('i[data-icon]').forEach(i => {
        const svg = icons[i.dataset.icon];
        if (svg) i.innerHTML = svg; else { i.textContent = '?'; i.title = 'missing icon ' + i.dataset.icon; }
      });
      document.querySelectorAll('img[data-logo]').forEach(img => {
        const src = logos[img.dataset.logo];
        if (src) { img.src = src; return; }
        // a labelled placeholder: in a logos row the label moves into the tile, so every tile is the same size
        const logo = img.closest('.logo'), lab = logo && logo.querySelector('.label');
        const box = document.createElement('div'); box.className = 'logo-missing';
        box.innerHTML = '<div class="ph-name"></div><div class="ph-note">logo missing: ' + img.dataset.logo + '</div>';
        box.querySelector('.ph-name').textContent = lab ? lab.textContent : img.dataset.logo;
        if (lab) lab.remove();
        const tile = img.closest('.tile'); if (tile) tile.classList.add('missing');
        img.replaceWith(box);
      });
      if (job.step != null) {
        for (let k = 1; k <= job.step; k++) html.classList.add('at-' + k);
        html.dataset.step = job.step;
        document.querySelectorAll('[data-step]').forEach(el => {
          const k = Number(el.dataset.step);
          el.classList.add(k > job.step ? 'later' : k === job.step ? 'lit' : 'done');
        });
      }
      if (job.avatar) {
        const a = document.createElement('img'); a.className = 'avatar'; a.src = job.avatar; document.body.appendChild(a);
      }
      await Promise.all([...document.images].map(im => im.complete ? 0 : new Promise(r => { im.onload = r; im.onerror = r; })));
      // a wide logo (a wordmark) carries its own name: no label under it
      document.querySelectorAll('.tile img').forEach(im => {
        if (im.naturalWidth / Math.max(1, im.naturalHeight) > 2.2) {
          im.closest('.tile').classList.add('wide');
          const lab = im.closest('.logo') && im.closest('.logo').querySelector('.label.auto');
          if (lab) lab.remove();
        }
      });
      await document.fonts.ready;
    }, { job, icons, logos, css: spec.css });
    await page.screenshot({ path: job.out, type: 'png' });
    process.stdout.write('.');
  }
  await browser.close();
  process.stdout.write('\n');
})().catch(e => { console.error(e.message || e); process.exit(1); });
