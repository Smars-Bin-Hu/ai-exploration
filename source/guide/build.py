# Harness Guide: Markdown sources -> the knowledge files of the M365 Copilot agent, as text-based A4 PDF (PDF only: in the pilot a DOCX copy lost every link).
# Run from anywhere:  python3 source/guide/build.py [name ...]     (no names: every source file that is Guide knowledge)
# Needs pandoc, Google Chrome, and playwright-core from ~/Developer/smarshu.com.
# Input:  source/guide/pages/<name>.md (format: see RULES.md), pictures in source/guide/img/ and fig/.
# Output: AI Exploration/2 Ask the Harness Guide/Knowledge/pdf/<file>.pdf; previews in source/guide/_pages/<name>/.
# Not knowledge: the pages in NOT_KNOWLEDGE stay in source/guide/pages/ as a reference and are never built into Knowledge/.
# Exit 1 when a check fails (check.py).
import os, re, sys, json, glob, subprocess, html
import check

H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
KNOWLEDGE = os.path.join(ROOT, 'AI Exploration', '2 Ask the Harness Guide', 'Knowledge')
OUT = {'pdf': os.path.join(KNOWLEDGE, 'pdf')}
# How-to pages: the Guide answers "how do I" with the steps its concept and overview files give (RULES.md); it names no harness tutorial.
NOT_KNOWLEDGE = {'21-start-a-task'}
HARNESS_REPO = 'https://github.com/Smars-Bin-Hu/copilot-agentic-harness'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def parse(path):
    text = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m: raise SystemExit(f'{path}: no front matter')
    meta, courses = {}, []
    for line in m.group(1).splitlines():
        if line.startswith('course: '):  # course: <title> | <url>
            t, _, u = line[8:].partition('|'); courses.append((t.strip(), u.strip()))
        elif ':' in line:
            k, v = line.split(':', 1); meta[k.strip()] = v.strip()
    meta['courses'] = courses
    return meta, text[m.end():]

def gh(tag, ref):
    path, _, lines = ref.partition('#')
    return f'{HARNESS_REPO}/blob/{tag}/{path}' + (f'#{lines}' if lines else ''), path + (' ' + lines.replace('L', 'lines ', 1).replace('-L', '–') if lines else '')

def expand(meta, body):
    """{src:path#L1-L9} -> a visible, linked code location next to the claim; then the closing sections with full URLs written out,
    because an agent reading the text sees the words, not the link behind them."""
    tag, refs = meta['harness_tag'], []
    def one(m):
        ref = m.group(1).strip()
        if ref not in refs: refs.append(ref)
        url, label = gh(tag, ref)
        return f'(code: [{label}]({url}))'
    body = re.sub(r'\{src:([^}]+)\}', one, body)
    tail = [f'\n\n## {meta["subject"]}: code locations\n',
            f'All code locations are in the harness repository at version {tag} ({HARNESS_REPO}/tree/{tag}).\n']
    if meta['layer'] == 'reference':  # hundreds of locations: the URL pattern once in visible text, then the path and lines of each
        tail.append(f'Every location below is at `{HARNESS_REPO}/blob/{tag}/<path>#L<a>-L<b>`: the path, then its first and last line '
                    f'(a location with no lines is the whole file).\n')
        tail.append('; '.join(gh(tag, r)[1] for r in refs) + '.')
    else:
        for r in refs:
            url, label = gh(tag, r); tail.append(f'- {label}: {url}')
    if meta['courses']:
        tail.append(f'\n\n## {meta["subject"]}: courses to learn more\n')
        for t, u in meta['courses']: tail.append(f'- {t}: {u}')
    head = f'# {meta["title"]}\n\nHarness Guide · harness version {tag} · {meta["layer"]}\n\n'
    return head + body.strip() + '\n' + '\n'.join(tail) + '\n', refs

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode: raise SystemExit(f'{cmd[0]} failed:\n{r.stderr}')
    return r.stdout

def to_pdf(name, html_path, pdf_path, pages_dir):
    os.makedirs(pages_dir, exist_ok=True)
    for f in os.listdir(pages_dir): os.remove(os.path.join(pages_dir, f))
    js = os.path.join(H, '_build', name + '.mjs')
    open(js, 'w').write(f'''import {{ createRequire }} from 'node:module';
const {{ chromium }} = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const b = await chromium.launch({{ executablePath: {json.dumps(CHROME)}, headless: true }});
const p = await b.newPage({{ viewport: {{ width: 900, height: 1200 }}, deviceScaleFactor: 1.5 }});
await p.goto('file://' + {json.dumps(html_path)}); await p.evaluate(() => document.fonts.ready);
await p.waitForFunction(() => [...document.images].every(i => i.complete));
const broken = await p.$$eval('img', ims => ims.filter(i => !i.naturalWidth).map(i => i.getAttribute('src')));
const buf = await p.pdf({{ path: {json.dumps(pdf_path)}, format: 'A4', printBackground: true, margin: {{ top: '18mm', bottom: '18mm', left: '18mm', right: '18mm' }},
  displayHeaderFooter: true, headerTemplate: '<span></span>',
  footerTemplate: '<div style="font:8px Arial;color:#9a9a96;width:100%;padding:0 18mm;display:flex;justify-content:space-between"><span>Harness Guide</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' }});
const pages = (buf.toString('latin1').match(/\\/Type\\s*\\/Page[^s]/g) || []).length;
await p.screenshot({{ path: {json.dumps(pages_dir)} + '/full.png', fullPage: true }});
console.log('REPORT ' + JSON.stringify({{ broken, pages }}));
await b.close();''')
    out = run(['node', js])
    return json.loads(out.split('REPORT ', 1)[1].splitlines()[0])

def build(name):
    src = os.path.join(H, 'pages', name + '.md')
    meta, body = parse(src)
    md, refs = expand(meta, body)
    os.makedirs(os.path.join(H, '_build'), exist_ok=True)
    mdx = os.path.join(H, '_build', name + '.md'); open(mdx, 'w', encoding='utf-8').write(md)
    html_path = os.path.join(H, '_build', name + '.html')
    run(['pandoc', mdx, '-f', 'markdown', '-t', 'html5', '-s', '--css', os.path.join(H, 'style.css'), '--embed-resources',
         '--resource-path', H, '--metadata', f'title={meta["title"]}', '--metadata', 'pagetitle=' + meta['title'], '-o', html_path,
         '--variable', 'title='])  # the title is written as the first heading by expand()
    for d in OUT.values(): os.makedirs(d, exist_ok=True)
    pdf = os.path.join(OUT['pdf'], meta['file'] + '.pdf')
    layout = to_pdf(name, html_path, pdf, os.path.join(H, '_pages', name))
    problems = check.run(name, meta, body, refs, layout, H)
    return meta, layout, problems

def main(names):
    if set(names) & NOT_KNOWLEDGE:
        raise SystemExit(f'not Guide knowledge (kept as a reference): {", ".join(sorted(set(names) & NOT_KNOWLEDGE))}')
    names = names or sorted(n for n in (os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(H, 'pages', '*.md'))) if n not in NOT_KNOWLEDGE)
    total_pages, bad = 0, []
    for n in names:
        meta, layout, probs = build(n)
        total_pages += layout['pages']
        print(f'{n}: {layout["pages"]} pages -> {meta["file"]}.pdf' + ('' if not probs else f'  FAIL ({len(probs)})'))
        bad += [f'{n}: {p}' for p in probs]
    files = len(glob.glob(os.path.join(OUT['pdf'], '*.pdf')))
    bad += check.totals(files, total_pages if len(names) == files else None)
    if bad:
        print(f'\nFAIL: {len(bad)} problem(s)'); [print('  -', p) for p in bad]; sys.exit(1)
    print(f'All checks passed. {files} knowledge files.')

if __name__ == '__main__':
    main(sys.argv[1:])
