# The checks every Deep Dive topic must pass (build.py runs them after printing).
# 1 words: text outside figures, per page        2 banned words (press-release style)
# 3 sources: every content page cites code; every cited path and line range exists at the pinned harness tag
# 4 reuse: no run of 8 words shared with the book, smarshu.com articles or the harness docs
# 5 layout: no text overflows its box, no missing image
import os, re, subprocess, glob

MAX_WORDS = 120
HARNESS = os.path.expanduser('~/Developer/DE-agentic-harness')
BANNED = ['seamless', 'seamlessly', 'powerful', 'revolutionary', 'revolutionize', 'game-changer', 'game changer', 'cutting-edge',
          'unlock', 'unlocks', 'supercharge', 'leverage', 'leverages', 'effortless', 'effortlessly', 'magic', 'magical',
          'state-of-the-art', 'best-in-class', 'next-generation', 'next-gen', 'empower', 'empowers', 'transformative',
          'incredible', 'amazing', 'world-class', 'blazing', 'ai-powered', 'smart', '10x', 'simply', 'just works',
          'out of the box', 'under the hood', 'secret sauce', 'single source of truth']
CORPUS_GLOBS = [os.path.expanduser('~/Developer/copilot-harness-engineering/book/src/*/en.md'),
                os.path.expanduser('~/Developer/smarshu.com/src/content/**/*.md*'),
                os.path.join(HARNESS, 'docs/*.md'), os.path.join(HARNESS, 'README.md'), os.path.join(HARNESS, '.harness/INDEX.md'),
                os.path.expanduser('~/Developer/ai-exploration/source/start-here/slides.py')]
N = 8

def words(s):
    s = re.sub(r'\{src:[^}]+\}', ' ', s)
    s = re.sub(r'`[^`]*`', ' x ', s)
    s = re.sub(r'[*_\[\]()]|https?://\S+', ' ', s)
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", s)

def page_text(pg):
    return ' '.join([pg.get('body', ''), pg.get('caption', '')])

_corpus = None
def corpus():
    global _corpus
    if _corpus is None:
        grams = set()
        for g in CORPUS_GLOBS:
            for f in glob.glob(g, recursive=True):
                w = [x.lower() for x in words(open(f, encoding='utf-8', errors='ignore').read())]
                grams.update(tuple(w[i:i + N]) for i in range(len(w) - N + 1))
        _corpus = grams
    return _corpus

def file_lines(tag, path):
    r = subprocess.run(['git', '-C', HARNESS, 'show', f'{tag}:{path}'], capture_output=True, text=True)
    return None if r.returncode else r.stdout.count('\n') + 1

def run(meta, pages, layout, tdir):
    probs, tag = [], meta['harness_tag']
    for i, pg in enumerate(pages, 1):
        where = f'page {i} ({pg.get("body", "")[:40]!r})'
        text = page_text(pg)
        n = len(words(text))
        if n > MAX_WORDS: probs.append(f'{where}: {n} words outside figures (max {MAX_WORDS})')
        low = ' ' + re.sub(r'\s+', ' ', text.lower()) + ' '
        if pg['layout'] not in ('split', 'figure', 'text'): probs.append(f'{where}: layout "{pg["layout"]}" does not exist (split, figure, text; no cover)')
        if pg.get('part') not in ('pattern', 'depth'): probs.append(f'{where}: needs "part: pattern" or "part: depth"')
        for k in ('title', 'kicker'):
            if pg.get(k): probs.append(f'{where}: "{k}:" is not used any more (no page titles); put the point in the first sentence')
        for b in BANNED:
            if re.search(r'(?<![a-z0-9-])' + re.escape(b) + r'(?![a-z0-9-])', low): probs.append(f'{where}: banned word "{b}"')
        if '```' in pg.get('body', ''): probs.append(f'{where}: code block (give the location, not the code)')
        if pg['layout'] != 'text' and not pg.get('_refs'): probs.append(f'{where}: no source location on a content page')
        for ref in pg.get('_refs', []):
            path, _, rng = ref.partition('#')
            total = file_lines(tag, path)
            if total is None: probs.append(f'{where}: {path} does not exist at {tag}'); continue
            if rng:
                m = re.fullmatch(r'L(\d+)(?:-L(\d+))?', rng)
                if not m: probs.append(f'{where}: bad line range "{rng}" (use #L10 or #L10-L40)')
                elif int(m.group(2) or m.group(1)) > total: probs.append(f'{where}: {path} has only {total} lines, cited {rng}')
        for fig in [pg.get('fig')] if pg.get('fig') else []:
            if not os.path.exists(os.path.join(tdir, fig)): probs.append(f'{where}: missing figure {fig}')
        w = [x.lower() for x in words(text)]
        hits = {' '.join(w[j:j + N]) for j in range(len(w) - N + 1) if tuple(w[j:j + N]) in corpus()}
        for h in sorted(hits)[:3]: probs.append(f'{where}: reuses existing text: "{h}"')
    parts = [pg.get('part') for pg in pages]
    if parts and (parts[0] != 'pattern' or 'pattern' in parts[parts.index('depth'):] if 'depth' in parts else False):
        probs.append('the pattern pages must come first, then the depth pages')
    for r in layout:
        if r['over']: probs.append(f'page {r["page"]}: text does not fit: {", ".join(r["over"])}')
        if r['broken']: probs.append(f'page {r["page"]}: image not loaded: {", ".join(r["broken"])}')
    return probs
