# The checks every Harness Guide file must pass (build.py runs them).
# sources: every cited path and line range exists at the pinned harness tag; every section that states how the harness works cites code
# self-contained: every "##" heading names the file's subject, so a passage found on its own still says what it is about
# pictures: every picture exists and has a caption that says what it shows; no picture failed to load
# links: every course link answers; no footnotes (a footnote is cut away from its claim when the text is split)
# words: no press-release words
# totals: at most 50 knowledge files (the M365 OneDrive limit) and 600 pages (M365 recommends 300; the person decided on 2026-11-19 to keep 577 pages for now; raised for the code-level internals files, to be checked against retrieval in the company test)
import os, re, subprocess, urllib.request

HARNESS = os.path.expanduser('~/Developer/DE-agentic-harness')
MAX_FILES, MAX_PAGES, MIN_CAPTION_WORDS = 50, 600, 5
BANNED = ['seamless', 'seamlessly', 'powerful', 'revolutionary', 'game-changer', 'cutting-edge', 'unlock', 'supercharge', 'leverage',
          'effortless', 'effortlessly', 'magic', 'magical', 'state-of-the-art', 'best-in-class', 'next-generation', 'empower',
          'transformative', 'incredible', 'amazing', 'world-class', 'ai-powered', '10x', 'simply', 'just works', 'under the hood']
LAYERS = ('overview', 'concept', 'how-to', 'reference', 'idea')
_lines = {}

def file_lines(tag, path):
    if (tag, path) not in _lines:
        r = subprocess.run(['git', '-C', HARNESS, 'show', f'{tag}:{path}'], capture_output=True, text=True)
        _lines[(tag, path)] = None if r.returncode else r.stdout.count('\n') + 1
    return _lines[(tag, path)]

_urls = {}
def reachable(url):
    if url not in _urls:
        try:
            req = urllib.request.Request(url, method='GET', headers={'User-Agent': 'guide-link-check'})
            _urls[url] = urllib.request.urlopen(req, timeout=15).status < 400
        except Exception:
            _urls[url] = False
    return _urls[url]

def sections(body):
    """(heading, text) for every '## ' section; the text before the first heading has heading None."""
    parts = re.split(r'^## (.+)$', body, flags=re.M)
    out = [(None, parts[0])]
    out += [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    return out

def run(name, meta, body, refs, layout, base):
    p = []
    for k in ('title', 'subject', 'layer', 'file', 'harness_tag'):
        if not meta.get(k): p.append(f'front matter: "{k}:" is missing')
    if meta.get('layer') and meta['layer'] not in LAYERS: p.append(f'front matter: layer must be one of {", ".join(LAYERS)}')
    tag, subject = meta.get('harness_tag', ''), meta.get('subject', '').lower()
    for ref in refs:
        path, _, rng = ref.partition('#')
        total = file_lines(tag, path)
        if total is None: p.append(f'{path} does not exist at {tag}'); continue
        if rng:
            m = re.fullmatch(r'L(\d+)(?:-L(\d+))?', rng)
            if not m: p.append(f'bad line range "{rng}" (use #L10 or #L10-L40)')
            elif int(m.group(2) or m.group(1)) > total: p.append(f'{path} has only {total} lines, cited {rng}')
    for head, text in sections(body):
        if head is None: continue
        if subject and subject not in head.lower(): p.append(f'section "{head}": the heading must name the subject "{meta["subject"]}"')
        if meta.get('layer') in ('overview', 'concept') and not re.search(r'\{src:', text) and not head.lower().endswith(('questions', 'terms')):
            p.append(f'section "{head}": no code location (every section on how the harness works cites code)')
    for alt, src in re.findall(r'!\[([^\]]*)\]\(([^)\s]+)', body):
        if not os.path.exists(os.path.join(base, src)): p.append(f'picture {src} does not exist')
        if len(alt.split()) < MIN_CAPTION_WORDS: p.append(f'picture {src}: the caption must say what it shows (at least {MIN_CAPTION_WORDS} words)')
    if layout['broken']: p.append(f'pictures not loaded: {", ".join(layout["broken"])}')
    if re.search(r'\[\^[^\]]+\]', body): p.append('footnotes are not allowed: put the code location next to the claim')
    for t, u in meta.get('courses', []):
        if not reachable(u): p.append(f'course link does not answer: {u}')
    low = ' ' + re.sub(r'\s+', ' ', re.sub(r'\{src:[^}]+\}|`[^`]*`', ' ', body).lower()) + ' '
    for b in BANNED:
        if re.search(r'(?<![a-z0-9-])' + re.escape(b) + r'(?![a-z0-9-])', low): p.append(f'banned word "{b}"')
    return p

def totals(files, pages):
    p = []
    if files > MAX_FILES: p.append(f'{files} knowledge files (max {MAX_FILES})')
    if pages is not None and pages > MAX_PAGES: p.append(f'{pages} pages in all (max {MAX_PAGES})')
    return p
