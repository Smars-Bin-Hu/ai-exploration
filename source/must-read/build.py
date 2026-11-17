# AI Exploration/0 MUST READ.pdf: the one map of the folder. One A4 portrait page, printed from page.html with style.css.
# Run from anywhere:  python3 source/must-read/build.py
# Needs Google Chrome and playwright-core from ~/Developer/smarshu.com (as source/guide/build.py).
# Checks, exit 1 on failure: exactly one page; the text fits the printable area;
# every data-path and every <code> path that ends in / or .pdf exists (see check_paths).
# Preview: source/must-read/_pages/page.png, the built PDF rendered by qlmanage (macOS).
import os, re, sys, json, subprocess, html as H

D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(D))
TOP = os.path.join(ROOT, 'AI Exploration')
PDF = os.path.join(TOP, '0 MUST READ.pdf')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def check_paths(body):
    """Every data-path exists under AI Exploration/; every <code> path ending in / or .pdf exists, read from its item's
    data-path or from the top. Advanced/ is named as not added yet and is not checked."""
    bad = []
    for path in re.findall(r'data-path="([^"]+)"', body):
        if not os.path.exists(os.path.join(TOP, path)): bad.append(f'no "{path}"')
    for item in re.split(r'(?=<div class="item")|(?=<section)|(?=<p)', body):
        m = re.search(r'data-path="([^"]+)"', item)
        bases = [TOP] + ([os.path.join(TOP, m.group(1))] if m else []) + [os.path.join(TOP, '3 Courses')]
        for c in re.findall(r'<code>([^<]+)</code>', item):
            c = H.unescape(c)
            if not (c.endswith('/') or c.endswith('.pdf')) or c.startswith('Advanced'): continue
            if not any(os.path.exists(os.path.join(b, c)) for b in bases): bad.append(f'no "{c}"')
    return bad

def main():
    body = open(os.path.join(D, 'page.html'), encoding='utf-8').read()
    css = open(os.path.join(D, 'style.css'), encoding='utf-8').read()
    doc = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>0 MUST READ</title><style>' + css + '</style></head><body>'
           + body + '</body></html>')
    os.makedirs(os.path.join(D, '_build'), exist_ok=True); os.makedirs(os.path.join(D, '_pages'), exist_ok=True)
    html_path = os.path.join(D, '_build', 'page.html'); open(html_path, 'w', encoding='utf-8').write(doc)
    png = os.path.join(D, '_pages', 'page.png')
    js = os.path.join(D, '_build', 'print.mjs')
    open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: {json.dumps(CHROME)}, headless: true }});
const p = await b.newPage({{ viewport: {{ width: 643, height: 960 }}, deviceScaleFactor: 2 }});
await p.goto('file://' + {json.dumps(html_path)}); await p.evaluate(() => document.fonts.ready);
const h = await p.evaluate(() => Math.ceil(document.body.lastElementChild.getBoundingClientRect().bottom));
const buf = await p.pdf({{ path: {json.dumps(PDF)}, format: 'A4', printBackground: true, preferCSSPageSize: true,
  displayHeaderFooter: true, headerTemplate: '<span></span>',
  footerTemplate: '<div style="font:8px Arial;color:#9a9a96;width:100%;padding:0 20mm;display:flex;justify-content:space-between"><span>AI Exploration · 0 MUST READ</span><span>The one map of this folder</span></div>' }});
const pages = (buf.toString('latin1').match(/\\/Type\\s*\\/Page[^s]/g) || []).length;
console.log('REPORT ' + JSON.stringify({{ pages, height: h }}));
await b.close();''')
    r = subprocess.run(['node', js], capture_output=True, text=True)
    if r.returncode: raise SystemExit('node failed:\n' + r.stderr)
    rep = json.loads(r.stdout.split('REPORT ', 1)[1].splitlines()[0])
    # preview: the built PDF itself, rendered by macOS Quick Look at 1600 px (sips renders a PDF at only 595 px wide)
    subprocess.run(['qlmanage', '-t', '-s', '1600', '-o', os.path.join(D, '_build'), PDF], capture_output=True)
    os.replace(os.path.join(D, '_build', os.path.basename(PDF) + '.png'), png)
    bad = check_paths(body)
    if rep['pages'] != 1: bad.append(f'{rep["pages"]} pages, must be 1')
    if rep['height'] > 960: bad.append(f'content is {rep["height"]}px tall, the printable page is 960px')
    print(f'0 MUST READ.pdf: {rep["pages"]} page, content {rep["height"]}/960 px; preview {os.path.relpath(png, ROOT)}')
    if bad: print(f'FAIL: {len(bad)} problem(s)'); [print('  -', b) for b in bad]; sys.exit(1)
    print('All checks passed.')

if __name__ == '__main__':
    main()
