# The phone review page for the Chinese draft: zh-Hans.md, with each 【图】/【截图】 shown as the real figure or screenshot,
# plus the cold-read record from review-notes.md. Run: python3 review_html.py <out.html>. Needs macOS sips (screenshots to JPEG).
import base64, html, os, re, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
ASSET = {2: 'fig/chain.svg', 4: 'fig/axes.svg', 5: 'fig/outside.svg', 6: 'fig/mapping.svg', 7: 'img/kb-overview.png', 8: 'img/reach.png',
         9: 'img/rca.png', 10: 'fig/envs.svg', 11: 'img/new-task.png', 12: 'img/approve-plan.png', 13: 'img/held-both.png',
         14: 'img/refusals.png', 15: 'img/task-review.png', 16: 'img/board-list.png', 17: 'img/report.png', 18: 'fig/tree.svg'}

def uri(rel):
    path = os.path.join(H, rel)
    if rel.endswith('.svg'):
        return 'data:image/svg+xml;base64,' + base64.b64encode(open(path, 'rb').read()).decode()
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, 'x.jpg')
        subprocess.run(['sips', '-Z', '1400', '-s', 'format', 'jpeg', '-s', 'formatOptions', '72', path, '--out', out], check=True, capture_output=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(open(out, 'rb').read()).decode()

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)

def render(md):
    out, page, lst, tbl = [], 0, None, []
    def close():
        nonlocal lst, tbl
        if lst: out.append(f'</{lst}>'); lst = None
        if tbl:
            out.append('<div class="tw"><table>' + ''.join('<tr>' + ''.join(f'<td>{inline(c.strip())}</td>' for c in r.strip('|').split('|')) + '</tr>' for r in tbl if not re.match(r'^\|[-| ]+\|$', r)) + '</table></div>'); tbl = []
    for line in md.splitlines():
        m = re.match(r'^## 第 (\d+) 页', line)
        if line.startswith('|'): tbl.append(line); continue
        if line.startswith('# '): close(); out.append(f'<h1>{inline(line[2:])}</h1>'); continue
        if line.startswith('## '):
            close(); page = int(m.group(1)) if m else 0; out.append(f'<h2>{inline(line[3:])}</h2>'); continue
        if line.strip() == '---': close(); out.append('<hr>'); continue
        if line.startswith('>'): close(); out.append(f'<p class="note">{inline(line.lstrip("> "))}</p>' if line.strip('> ') else ''); continue
        fig = re.match(r'^\s*【(图|截图)', line)
        if fig and page in ASSET:
            close(); out.append(f'<figure><div class="pic"><img src="{uri(ASSET[page])}" alt=""></div><figcaption>{inline(line.strip())}</figcaption></figure>'); continue
        li = re.match(r'^(\s*)(-|\d+\.) (.*)', line)
        if li:
            kind = 'ol' if li.group(2)[0].isdigit() else 'ul'
            if lst != kind: close(); out.append(f'<{kind}>'); lst = kind
            out.append(f'<li>{inline(li.group(3))}</li>'); continue
        if not line.strip(): close(); continue
        if lst and line.startswith('  '): out[-1] = out[-1][:-5] + '<br>' + inline(line.strip()) + '</li>'; continue
        close(); out.append(f'<p>{inline(line)}</p>')
    close(); return '\n'.join(out)

zh = open(os.path.join(H, 'zh-Hans.md')).read()
notes = open(os.path.join(H, 'review-notes.md')).read()
record = notes[notes.index('# 第 4 版（简中）的冷读记录'):] if '# 第 4 版（简中）的冷读记录' in notes else ''
page = open(os.path.join(H, 'review_html.css')).read() + '<main>\n' + render(zh) + ('\n<hr>\n' + render(record.replace('# ', '## ', 1)) if record else '') + '\n</main>\n'
open(sys.argv[1], 'w').write(page)
print(sys.argv[1], len(page) // 1024, 'KB')
