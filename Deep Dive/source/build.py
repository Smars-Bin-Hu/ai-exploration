# Deep Dive: one topic folder -> one 16:9 PDF, then the checks.
# Run from anywhere:  python3 "Deep Dive/source/build.py" 04-task      (needs Google Chrome, and playwright-core from ~/Developer/smarshu.com)
# Input:  source/topics/<id>/pages.md and its fig/ and img/ folders (format: see RULES.md).
# Output: Deep Dive/<file>.pdf, previews in source/topics/<id>/_pages/, and the check report. Exit 1 when a check fails.
import os, re, sys, html, json, subprocess
import check

H = os.path.dirname(os.path.abspath(__file__)); TOP = os.path.dirname(H)
HARNESS_REPO = 'https://github.com/Smars-Bin-Hu/copilot-agentic-harness'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# ---------- parse ----------
def parse(path):
    text = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    meta = dict(l.split(':', 1) for l in m.group(1).splitlines() if ':' in l)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    pages = []
    for chunk in re.split(r'^=== ', text[m.end():], flags=re.M)[1:]:
        head, _, rest = chunk.partition('\n')
        pg = {'layout': head.strip(), 'body': ''}
        lines = rest.split('\n'); i = 0
        while i < len(lines) and re.match(r'^[a-z]+: ', lines[i]):
            k, v = lines[i].split(': ', 1); pg[k] = v.strip(); i += 1
        pg['body'] = '\n'.join(lines[i:]).strip()
        pages.append(pg)
    return meta, pages

# ---------- inline markdown ----------
def inline(s, refs, tag):
    out = []
    for part in re.split(r'(\{src:[^}]+\}|`[^`]+`)', s):
        if part.startswith('{src:'):
            ref = part[5:-1].strip()
            if ref not in refs: refs.append(ref)
            out.append(f'<sup class="ref">{refs.index(ref) + 1}</sup>')
        elif part.startswith('`'):
            out.append(f'<code>{html.escape(part[1:-1])}</code>')
        else:
            t = html.escape(part)
            t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
            t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
            t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
            out.append(t)
    return ''.join(out)

def block(md, refs, tag):
    out, items = [], []
    def flush():
        if items: out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'); items.clear()
    for para in re.split(r'\n\s*\n', md.strip()):
        for line in para.split('\n'):
            if line.startswith('- '): items.append(inline(line[2:], refs, tag))
            elif items and line.startswith('  '): items[-1] += ' ' + inline(line.strip(), refs, tag)
        if not para.startswith('- '):
            flush(); out.append(f'<p>{inline(" ".join(l.strip() for l in para.split(chr(10))), refs, tag)}</p>')
        else: flush()
    flush()
    return ''.join(out)

def ref_link(ref, tag):
    path, _, lines = ref.partition('#')
    url = f'{HARNESS_REPO}/blob/{tag}/{path}' + (f'#{lines}' if lines else '')
    return f'<a href="{html.escape(url)}">{html.escape(path)}{(":" + lines.replace("L", "").replace("-", "–")) if lines else ""}</a>'

# ---------- render ----------
def render(meta, pages, base):
    tag = meta['harness_tag']; n = meta['number']; total = len(pages)
    secs = []
    for i, pg in enumerate(pages, 1):
        refs = []
        lay = pg['layout']
        fig = ''
        if pg.get('fig'):
            cap = f'<figcaption>{inline(pg["caption"], refs, tag)}</figcaption>' if pg.get('caption') else ''
            cls = 'shot' if pg['fig'].startswith('img/') else 'diagram'
            fig = f'<figure class="{cls}"><img src="{html.escape(pg["fig"])}">{cap}</figure>'
        body = f'<div class="body">{block(pg["body"], refs, tag)}</div>' if pg['body'] else ''
        # no cover, no page titles: the figure and a few sentences are the page; the first sentence states the point
        inner = f'<div class="main {lay}">{body}{fig}</div>'
        src = ''
        if refs:
            src = '<div class="sources">' + ''.join(f'<span><sup>{k}</sup> {ref_link(r, tag)}</span>' for k, r in enumerate(refs, 1)) + '</div>'
        pin = f' · <a href="{HARNESS_REPO}/tree/{tag}">harness @ {tag}</a>' if i == 1 else ''
        part = {'pattern': ' · The pattern', 'depth': ' · In depth'}.get(pg.get('part', ''), '')
        foot = f'<footer><span>{html.escape(meta["series"])} · {n} · {html.escape(meta["short"])}{part}{pin}</span><span>© 2026 Smars Hu · {i} / {total}</span></footer>'
        secs.append(f'<section class="{lay}" data-page="{i}">{inner}{src}{foot}</section>')
        pg['_refs'] = refs
    css = open(os.path.join(H, 'style.css'), encoding='utf-8').read()
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(meta["title"])}</title><style>{css}</style></head><body>{"".join(secs)}</body></html>'

def print_pdf(html_path, pdf_path, pages_dir):
    os.makedirs(pages_dir, exist_ok=True)
    for f in os.listdir(pages_dir): os.remove(os.path.join(pages_dir, f))
    js = html_path[:-5] + '.mjs'
    open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: {json.dumps(CHROME)}, headless: true }});
const p = await b.newPage({{ viewport: {{ width: 1280, height: 720 }}, deviceScaleFactor: 1.5 }});
await p.goto('file://' + {json.dumps(html_path)}); await p.evaluate(() => document.fonts.ready);
await p.waitForFunction(() => [...document.images].every(i => i.complete));
const report = await p.$$eval('section', ss => ss.map((s, i) => {{
  const over = [...s.querySelectorAll('.body, figure, h2, .sources')].filter(e => e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2).map(e => e.className || e.tagName);
  const broken = [...s.querySelectorAll('img')].filter(im => !im.naturalWidth).map(im => im.getAttribute('src'));
  return {{ page: i + 1, over, broken }};
}}));
console.log('REPORT ' + JSON.stringify(report));
const secs = await p.$$('section');
for (let i = 0; i < secs.length; i++) await secs[i].screenshot({{ path: {json.dumps(pages_dir)} + '/p' + String(i + 1).padStart(2, '0') + '.png' }});
await p.pdf({{ path: {json.dumps(pdf_path)}, preferCSSPageSize: true, printBackground: true }});
await b.close();''')
    out = subprocess.run(['node', js], check=True, capture_output=True, text=True).stdout
    return json.loads(out.split('REPORT ', 1)[1].splitlines()[0])

def main(topic):
    tdir = os.path.join(H, 'topics', topic)
    meta, pages = parse(os.path.join(tdir, 'pages.md'))
    doc = render(meta, pages, tdir)
    html_path = os.path.join(tdir, '_twin.html'); open(html_path, 'w', encoding='utf-8').write(doc)
    pdf = os.path.join(TOP, meta['file'] + '.pdf') if not meta.get('draft') else os.path.join(tdir, '_draft.pdf')
    layout = print_pdf(html_path, pdf, os.path.join(tdir, '_pages'))
    problems = check.run(meta, pages, layout, tdir)
    print(f'{len(pages)} pages -> {pdf}')
    if problems:
        print(f'\nFAIL: {len(problems)} problem(s)'); [print('  -', p) for p in problems]; sys.exit(1)
    print('All checks passed.')

if __name__ == '__main__':
    main(sys.argv[1])
