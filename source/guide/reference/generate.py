# Harness Guide, reference layer: writes the pages Code map, Test map and Version history from the harness repository at a tag.
# Run from anywhere:  python3 source/guide/reference/generate.py [--tag 1.8.3] [--no-fit] [--only code|test|versions ...]
# Reads the harness with `git show <tag>:<path>` and `git ls-tree` in ~/Developer/DE-agentic-harness (never checks anything out).
# Writes source/guide/pages/32-code-map.md, 33-test-map.md, 34-version-history.md in the format of RULES.md, with a
# {src:path#Lx-Ly} citation for every entry. It then builds each page (build.py) and, while its PDF is over its page budget
# (BUDGET), writes it again with less text per entry (first sentence only, shorter lead-ins, fewer of them); --no-fit writes
# the fullest text and builds nothing. Then run build.py on the three pages as usual.
import argparse, ast, json, os, re, subprocess, sys

HARNESS = os.path.expanduser('~/Developer/DE-agentic-harness')
GUIDE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(GUIDE, 'pages')
BUDGET = {'32-code-map': 25, '33-test-map': 20, '34-version-history': 20}  # 20, not 22: at 20 the versions before 1.8.0 keep their level-6 text

# ---------- reading the harness at a tag ----------

def git(*args):
    r = subprocess.run(['git', '-C', HARNESS, *args], capture_output=True, text=True)
    if r.returncode: raise SystemExit(f'git {" ".join(args)} failed:\n{r.stderr}')
    return r.stdout

_shown = {}
def show(tag, path):
    if (tag, path) not in _shown: _shown[(tag, path)] = git('show', f'{tag}:{path}')
    return _shown[(tag, path)]

def ls(tag, prefix):
    return [p for p in git('ls-tree', '-r', '--name-only', tag, '--', prefix).splitlines() if p]

def docstring(tag, path):
    """(text, first line, last line) of a Python file's module docstring, or None."""
    try: tree = ast.parse(show(tag, path))
    except SyntaxError: return None
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(getattr(tree.body[0], 'value', None), ast.Constant) \
            and isinstance(tree.body[0].value.value, str):
        n = tree.body[0]
        return n.value.value, n.lineno, n.end_lineno
    return None

def comment_header(tag, path):
    """The comment lines at the top of a script, page or style file: (text, first line, last line), or None."""
    lines, start, out = show(tag, path).splitlines(), None, []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if i == 1 and s.startswith('#!'): continue
        if s.lower() in ('@echo off',): continue
        m = re.match(r'^(?://|#|rem\b|::)\s?(.*)$', s, re.I)
        if m and not s.startswith('#!'):
            start = start or i; out.append(m.group(1)); continue
        if s.startswith('/*') and not out:
            j = i; body = []
            while j <= len(lines):
                body.append(lines[j - 1].strip().lstrip('/*').rstrip('*/').strip('* ').strip())
                if '*/' in lines[j - 1]: break
                j += 1
            return ' '.join(b for b in body if b), i, j
        break
    return (' '.join(out), start, start + len(out) - 1) if out else None

def front_matter(tag, path):
    """Simple YAML front matter of a Markdown file: {key: (value, line)}."""
    lines = show(tag, path).splitlines()
    if not lines or lines[0].strip() != '---': return {}
    out, i = {}, 1
    while i < len(lines) and lines[i].strip() != '---':
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', lines[i])
        if m:
            key, val, at = m.group(1), m.group(2).strip(), i + 1
            if val in ('>', '|', '>-', '|-', '>+', '|+'):
                block = []
                while i + 1 < len(lines) and (lines[i + 1].startswith(' ') or not lines[i + 1].strip()):
                    i += 1; block.append(lines[i].strip())
                val = ' '.join(b for b in block if b)
            elif val[:1] in ('"', "'"):
                q = val[0]
                while not (len(val) > 1 and val.endswith(q)) and i + 1 < len(lines):
                    i += 1; val += ' ' + lines[i].strip()
                val = val[1:-1].replace("''", "'") if q == "'" else val[1:-1].replace('\\"', '"')
            out[key] = (val, at)
        i += 1
    return out

def first_paragraph_md(tag, path):
    """The first plain paragraph of a Markdown file (after front matter and headings): (text, first line, last line)."""
    lines = show(tag, path).splitlines()
    i = 0
    if lines and lines[0].strip() == '---':
        i = 1
        while i < len(lines) and lines[i].strip() != '---': i += 1
        i += 1
    while i < len(lines):
        s = lines[i].strip()
        if s and not s.startswith(('#', '>', '|', '```', '<!--', '-', '*', '![')): break
        i += 1
    if i >= len(lines): return None
    start, buf = i + 1, []
    while i < len(lines) and lines[i].strip():
        buf.append(lines[i].strip()); i += 1
    return ' '.join(buf), start, i

def h1(tag, path):
    for n, line in enumerate(show(tag, path).splitlines(), 1):
        if line.startswith('# '): return line[2:].strip(), n
    return None

def key_line(tag, path, key, after=1):
    """The line of `"key":` in a JSON file, at or after a line."""
    for n, line in enumerate(show(tag, path).splitlines(), 1):
        if n >= after and re.match(r'\s*"' + re.escape(key) + r'"\s*:', line): return n
    return None

# ---------- turning source text into safe, short Markdown ----------

CJK = re.compile(r'[　-鿿＀-￯]')
REPLACE = {'simply': '', 'leverage': 'use', 'leverages': 'uses', 'unlock': 'open', 'unlocks': 'opens', 'powerful': 'strong',
           'magic': 'marker', 'seamless': 'smooth', 'seamlessly': 'smoothly', 'effortless': 'easy', 'empower': 'let',
           'amazing': 'good', 'incredible': 'large', 'supercharge': 'speed up', 'magical': 'special'}

_ID = r'(?:[A-Z]{1,4}-?\d+[A-Za-z0-9-]*|[A-Z]{1,4}-[A-Z]+\d*[A-Za-z0-9-]*)'
ITEM_ID = re.compile(r'^' + _ID + r'(?:\s+(?:' + _ID + r'|\d+[A-Za-z0-9-]*|[A-Z]{1,4}|\.\.\.|…|to|and))*$')

def drop_ids(m):
    """In a parenthesis, drop the internal item numbers of the harness's own plans (M15-4, B71, C13 FR 17a); keep versions and words."""
    tokens = [t.strip() for t in m.group(1).split(',')]
    keep = [t for t in tokens if t and not ITEM_ID.match(t)]
    return '(' + ', '.join(keep) + ')' if keep else ''

def code_split(text):
    """Pieces of text, alternately outside and inside backtick spans (outside first)."""
    return re.split(r'(`[^`]*`)', text)

def clean(text):
    """One line; no Chinese (internal file names of test rounds); no press-release words; Markdown escaped outside code."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s*\([^()]*' + CJK.pattern + r'[^()]*\)', '', text)       # a parenthesis that names a Chinese file
    text = re.sub(r'\(([^()`]*)\)', drop_ids, text)                              # internal item numbers (M15-4, B71, C13 FR 17a)
    parts = code_split(text)
    out = []
    for k, part in enumerate(parts):
        if k % 2:  # code span
            if CJK.search(part): continue
            out.append(part.replace('[^', '[ ^')); continue
        part = CJK.sub('', part)
        for w, r in REPLACE.items():
            part = re.sub(r'(?i)(?<![a-z0-9-])' + w + r'(?![a-z0-9-])', r, part)
        part = re.sub(r'(?i)under the hood', 'inside', part)
        part = re.sub(r'([\\*_<>$~^\[\]#|])', r'\\\1', part)
        out.append(part)
    text = ''.join(out)
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\s+([,.;:)])(?=\s|$)', r'\1', text)
    return re.sub(r'\s{2,}', ' ', text).strip()

def sentences(text):
    """Split at '. ', '? ', '! ' (outside code spans) before a capital letter, a digit or a backtick."""
    parts, cur = [], ''
    for k, piece in enumerate(code_split(text)):
        if k % 2: cur += piece; continue
        bits = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9`"(])', piece)
        for j, b in enumerate(bits):
            if j: parts.append(cur.strip()); cur = ''
            cur += b
    if cur.strip(): parts.append(cur.strip())
    return parts

def shorten(text, max_sentences, max_chars):
    """The first sentences of a text, at most max_chars long (cut at a word, never inside a code span)."""
    ss = sentences(text) or [text]
    out = ' '.join(ss[:max_sentences])
    k = max_sentences
    while k < len(ss) and len(out) < 80 and len(out) + 1 + len(ss[k]) <= max_chars:  # a very short first sentence takes the next one
        out += ' ' + ss[k]; k += 1
    if len(out) > max_chars:
        cuts, code = [], False
        for i, ch in enumerate(out[:max_chars + 1]):
            if ch == '`': code = not code
            elif ch == ' ' and not code: cuts.append(i)
        out = out[:cuts[-1] if cuts else max_chars].rstrip(' ,;:(') + ' …'
    if out.count('`') % 2: out += '`'
    return re.sub(r' {2,}', ' ', out)

def doc_summary(text, max_sentences, max_chars):
    """The first paragraph of a docstring, without its indented tables, cleaned and shortened."""
    para = []
    for line in text.strip().splitlines():
        if not line.strip():
            if para: break
            continue
        if line.startswith('  ') and para: break
        para.append(line.strip())
    return shorten(clean(' '.join(para)), max_sentences, max_chars)

def phrase(camel):
    """WaitingForAPersonIsNotToolTimeTests -> 'waiting for a person is not tool time'."""
    name = re.sub(r'Tests?$', '', camel)
    words = re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+', name)
    return ' '.join(w if (w.isupper() and len(w) > 1) else w.lower() for w in words)

def table_cell(text):
    """Text for one cell of a pipe table: a '|' inside a code span would end the cell."""
    parts = code_split(text)
    return ''.join(p.replace('|', '\\|') if k % 2 else p for k, p in enumerate(parts))

def cite(path, a=None, b=None):
    if a is None: return '{src:' + path + '}'
    return '{src:' + path + f'#L{a}' + (f'-L{b}' if b and b != a else '') + '}'

def front(title, subject, file, tag, courses=()):
    return f'---\ntitle: {title}\nsubject: {subject}\nlayer: reference\nfile: {file}\nharness_tag: {tag}\n' + ''.join(f'course: {c}\n' for c in courses) + '---\n'

def node_lines(tag, path, name):
    """(first line, last line) of the class or function `name` in a Python file (the first one found)."""
    for node in ast.walk(ast.parse(show(tag, path))):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node.lineno, node.end_lineno
    raise SystemExit(f'{name} not found in {path} at {tag}')

# ---------- 32 Code map ----------

PY_AREAS = [  # (heading after "Code map: ", regex on the path), first match wins
    ('entry points (hook, launcher, CLI, doctor, integrity)', r'^\.harness/engine/[^/]+\.py$'),
    ('adapters (Copilot payloads in and out)', r'^\.harness/engine/adapters/'),
    ('engine core: knowledge base', r'^\.harness/engine/core/kb[^/]*\.py$'),
    ('engine core', r'^\.harness/engine/core/'),
    ('gate module', r'^\.harness/engine/modules/gate/'),
    ('task module: autorun', r'^\.harness/engine/modules/task/autorun'),
    ('task module: super agent', r'^\.harness/engine/modules/task/super'),
    ('task module: link to VS Code chats', r'^\.harness/engine/modules/task/(chat|vslink|vsrestart|tasksub)'),
    ('task module: board server and pages', r'^\.harness/engine/modules/task/(board|taskboard|taskdesk|taskhtml|[a-z]*view|wallpaper|mdtree|health|ready|setupjob|skillsend|tasksize|taskfiles|taskfileedit|taskinbox|taskrun|taskinsight|tasktrace|rewind)'),
    ('task module: checks, records and reports', r'^\.harness/engine/modules/task/(taskreview|reviewcheck|gatereview|task_report|perf|evidence|runrecord|testrecord|testdefects)'),
    ('task module: task life, commands and write-back', r'^\.harness/engine/modules/task/'),
    ('observe module (logs and statistics)', r'^\.harness/engine/modules/observe/'),
    ('evalcheck module (fixed scenarios)', r'^\.harness/engine/modules/evalcheck/'),
    ('modules package', r'^\.harness/engine/modules/'),
]

def code_map(tag, lv):
    S, C = lv['sentences'], lv['chars']
    files = ls(tag, '.harness/engine')
    py = [f for f in files if f.endswith('.py')]
    groups = {a: [] for a, _ in PY_AREAS}
    missing = []
    for f in py:
        area = next(a for a, rx in PY_AREAS if re.search(rx, f))
        d = docstring(tag, f)
        if d and d[0].strip():
            groups[area].append(f'- {cite(f, d[1], d[2])} {doc_summary(d[0], S, C)}')
        else:
            missing.append(f); groups[area].append(f'- `{f}` (no module docstring)')
    out = [front('Code map', 'Code map', '32 Code map', tag)]
    out.append('## Code map: what this file holds\n')
    out.append(f'The code map lists every file of the harness engine at version {tag}, and the hook configuration, the policies, the contracts, the agents, the skills and the text rules, '
               f'each with one or two sentences taken from the file itself (a Python module\'s docstring, a policy\'s `description`, a skill\'s `description`) and its code location. '
               f'It answers "where in the code is X" and "what does file Y do". The engine has {len(py)} Python files under `.harness/engine/`; '
               f'{len(missing)} of them have no module docstring and are listed by path only. Each entry starts with the file\'s code location (its path and the lines of its docstring), then what the file says it does. '
               f'The engine\'s own index of its parts is `.harness/INDEX.md` {cite(".harness/INDEX.md", next((n for n, l in enumerate(show(tag, ".harness/INDEX.md").splitlines(), 1) if l.startswith("| `.harness/engine/` |")), None))}.\n')
    out.append(f'## Code map: how the parts fit\n')
    out.append(f'Every hook event of a Copilot chat runs one command, `launch.py`, which loads and runs `hook.py` {cite(".harness/engine/launch.py", *docstring(tag, ".harness/engine/launch.py")[1:])}: the adapter turns the event into the harness\'s own form, the modules listed in `registry.json` for that event decide, '
               f'and the answers are merged (deny over ask over allow) {cite(".harness/engine/hook.py", *docstring(tag, ".harness/engine/hook.py")[1:])}. '
               f'The gate module guards writes; the task module keeps tasks, the board and autorun; the observe module writes the log; the evalcheck module judges fixed scenarios. '
               f'A person and the agent reach the same code through the `harness` command (`cli.py`) {cite(".harness/engine/cli.py", *docstring(tag, ".harness/engine/cli.py")[1:])}. '
               f'The policies in `.harness/policies/` hold the settings and lists the code reads; an override goes in the `.override.json` file of the same name '
               f'{cite(".harness/INDEX.md", next((n for n, l in enumerate(show(tag, ".harness/INDEX.md").splitlines(), 1) if l.startswith("| `.harness/policies/` |")), None))}.\n')
    for area, _ in PY_AREAS:
        if not groups[area]: continue
        out.append(f'## Code map: {area}\n')
        out.extend(groups[area]); out.append('')
        if area.startswith('engine core') and area == 'engine core':
            data = [f for f in files if f.startswith('.harness/engine/core/') and not f.endswith('.py')]
            if data:
                out.append('Data files of the engine core: ' + ', '.join(f'`{f.rsplit("/", 1)[1]}` {cite(f)}' for f in data) +
                           '. `messages.en.json` and `messages.zh.json` hold every sentence the hooks and the CLI say, in English and Chinese.\n')
        if area.startswith('adapters'):
            data = [f for f in files if f.startswith('.harness/engine/adapters/') and not f.endswith('.py')]
            if data: out.append('Data file of the adapters: ' + ', '.join(f'`{f.rsplit("/", 1)[1]}` {cite(f)}' for f in data) + '.\n')
    # board pages
    web = [f for f in files if '/modules/task/web/' in f]
    out.append('## Code map: board pages (`modules/task/web/`)\n')
    bs = '.harness/engine/modules/task/boardserve.py'
    out.append(f'The board\'s pages are served by `task board --serve` (`modules/task/boardserve.py`) on 127.0.0.1 only {cite(bs, *docstring(tag, bs)[1:])}. '
               f'The scripts and pages, each with the first sentence of its own header comment:\n')
    plain, pages, scripts = [], [], []
    for f in web:
        name = f.rsplit('/', 1)[1]
        if not f.endswith(('.js', '.html')): plain.append(name); continue
        c = comment_header(tag, f)
        item = f'`{name}`: {shorten(clean(c[0]), 1, min(C, 160)).rstrip(".")} {cite(f, c[1], c[2])}' if c and c[0].strip() else f'`{name}` {cite(f)}'
        (pages if name.endswith('.html') else scripts).append(item)
    # one paragraph each, not one bullet per file: the board has some forty small files
    if pages: out.append('Pages: ' + '; '.join(pages) + '.\n')
    if scripts: out.append('Scripts: ' + '; '.join(scripts) + '.\n')
    out.append(f'Style sheets and pictures of the board: {", ".join(f"`{p}`" for p in plain)}.\n')
    # hooks and registry
    hj = '.github/hooks/harness.json'
    events = list(json.loads(show(tag, hj))['hooks'])
    cmds = sorted({h['command'] for v in json.loads(show(tag, hj))['hooks'].values() for h in v})
    wins = sorted({h.get('windows', '') for v in json.loads(show(tag, hj))['hooks'].values() for h in v})
    out.append('## Code map: hooks and the module registry\n')
    out.append(f'The hook configuration `{hj}` subscribes the harness to {len(events)} events of a Copilot chat, '
               + (f'and every one runs the same command, `{cmds[0]}`' + (f' (`{wins[0]}` on Windows)' if len(wins) == 1 and wins[0] else '') if len(cmds) == 1 else 'with these commands: ' + ', '.join(f'`{c}`' for c in cmds))
               + ': ' + ', '.join(f'`{e}` {cite(hj, key_line(tag, hj, e))}' for e in events) + '.\n')
    reg = '.harness/registry.json'
    mods = json.loads(show(tag, reg))['modules']
    mline = key_line(tag, reg, 'modules')
    for name, m in mods.items():
        ln = key_line(tag, reg, name, mline)
        ev = ', '.join(f'`{e}`' for e in m.get('events', [])) or 'no hook event (command line only)'
        out.append(f'- Module `{name}` ({m.get("status")}, {"on" if m.get("enabled") else "off"}): hook events {ev}; '
                   f'{len(m.get("files", []))} files and folders belong to it {cite(reg, ln)}.')
    out.append(f'\nThe registry also lists the files of the engine itself, which an upgrade replaces as a whole {cite(reg, key_line(tag, reg, "engine"))}.\n')
    # the harness command and start files
    out.append('## Code map: the `harness` command and the start files\n')
    for f in ['.harness/bin/harness', '.harness/bin/harness.cmd', 'Start Harness.command', 'Start Harness.cmd']:
        if f not in set(ls(tag, f)): continue
        c = comment_header(tag, f)
        out.append(f'- `{f}`: ' + (f'{shorten(clean(c[0]), 2, C)} {cite(f, c[1], c[2])}' if c else cite(f)))
    out.append('')
    # policies
    out.append('## Code map: policies (`.harness/policies/`)\n')
    out.append('Each policy is a JSON file the engine reads; its `description` says what it holds. An override goes in the `.override.json` file of the same name.\n')
    for f in ls(tag, '.harness/policies'):
        if not f.endswith('.json'): continue
        try: d = json.loads(show(tag, f)).get('description', '')
        except ValueError: d = ''
        out.append(f'- `{f.rsplit("/", 1)[1]}`: ' + (f'{shorten(clean(d), S, C)} {cite(f, key_line(tag, f, "description"))}' if d else cite(f)))
    out.append('')
    # contracts
    out.append('## Code map: contracts (`.harness/contracts/`)\n')
    out.append('Contracts are the fixed forms other files must follow: the knowledge base standard, the tool pack protocol and the task templates.\n')
    tmpl = {}
    for f in ls(tag, '.harness/contracts'):
        m = re.match(r'^\.harness/contracts/templates/task/(\w+)/(.+)$', f)
        if m: tmpl.setdefault(m.group(1), []).append((m.group(2), f)); continue
        if f.endswith('.md') and '/templates/' not in f:
            p = first_paragraph_md(tag, f); t = h1(tag, f)
            head = clean(t[0]) + ': ' if t else ''
            out.append(f'- `{f.replace(".harness/contracts/", "")}`: {head}' + (f'{shorten(clean(p[0]), 1, C)} {cite(f, p[1], p[2])}' if p else cite(f)))
        else:
            out.append(f'- `{f.replace(".harness/contracts/", "")}` {cite(f)}')
    for lang, items in tmpl.items():
        out.append(f'- Task templates in `templates/task/{lang}/`: ' + ', '.join(f'`{n}` {cite(f)}' for n, f in items) + '.')
    out.append('')
    # agents
    out.append('## Code map: agents (`.github/agents/`)\n')
    out.append('An agent file sets a Copilot agent\'s role, tools and models in its front matter; each entry gives the first sentences of its `description` and its tools.\n')
    for f in ls(tag, '.github/agents'):
        fm = front_matter(tag, f)
        if 'description' in fm:
            d, ln = fm['description']
            tools = fm.get('tools', ('', 0))[0]
            out.append(f'- `{f.rsplit("/", 1)[1]}`: {shorten(clean(d), S, C)}' + (f' Tools: `{tools}`.' if tools else '') + f' {cite(f, ln, fm.get("tools", (None, ln))[1])}')
        else:
            out.append(f'- `{f.rsplit("/", 1)[1]}` {cite(f)}')
    out.append('')
    # skills
    skills = [f for f in ls(tag, '.github/skills') if re.match(r'^\.github/skills/[^/]+/SKILL\.md$', f)]
    for prefix, label in (('harness-', 'harness skills'), ('generic-', 'generic skills')):
        group = [f for f in skills if f.split('/')[2].startswith(prefix)]
        if not group: continue
        out.append(f'## Code map: {label} (`.github/skills/{prefix}*`)\n')
        out.append(f'One line per skill: the first sentence of the `description` in its `SKILL.md`.\n')
        for f in group:
            fm = front_matter(tag, f)
            d, ln = fm.get('description', ('', None))
            out.append(f'- `{f.split("/")[2]}`: ' + (f'{shorten(clean(d), 1, C)} {cite(f, ln)}' if d else cite(f)))
        out.append('')
    other = [f for f in skills if not f.split('/')[2].startswith(('harness-', 'generic-'))]
    if other:
        out.append('## Code map: other skills\n')
        for f in other:
            fm = front_matter(tag, f); d, ln = fm.get('description', ('', None))
            out.append(f'- `{f.split("/")[2]}`: ' + (f'{shorten(clean(d), 1, C)} {cite(f, ln)}' if d else cite(f)))
        out.append('')
    # text rules
    out.append('## Code map: text rules (instructions the model reads)\n')
    out.append('These files are text the model is asked to follow; no code enforces them by itself.\n')
    for f in ['AGENTS.md', '.github/copilot-instructions.md'] + ls(tag, '.github/instructions') + ls(tag, '.harness/standards') + ['.harness/INDEX.md']:
        if not ls(tag, f): continue
        fm = front_matter(tag, f)
        if 'description' in fm:
            d, ln = fm['description']; ap = fm.get('applyTo', ('', None))[0]
            out.append(f'- `{f}`: {shorten(clean(d), 1, C)}' + (f' Applies to `{ap}`.' if ap else '') + f' {cite(f, ln)}')
        else:
            p = first_paragraph_md(tag, f)
            out.append(f'- `{f}`: ' + (f'{shorten(clean(p[0]), 1, C)} {cite(f, p[1], p[2])}' if p else cite(f)))
    out.append('')
    return '\n'.join(out), {'python files': len(py), 'no docstring': missing}

# ---------- 33 Test map ----------

TEST_AREAS = [
    ('shared helpers (not tests)', r'^(support|taskcase|evalsynth)\.py$'),
    ('fixes from the 1.7.38 test rounds (C12, C13)', r'^test_c1[23]_'),
    ('autorun', r'^test_autorun'),
    ('super agent', r'^test_(super|gate_super)'),
    ('gate and guardrails', r'^test_(gate|admin|wait|outbox|breaker)'),
    ('hook entry, adapters and engine core', r'^test_(core|adapters|copilot_sdk|replay|old_python|winretry|language|reply|render|statements|ahp|pinpython)'),
    ('outside systems, connections and tool packs', r'^test_(connection|connlayers|open_connection|toolpacks|reach|computer_recipe|launchenv|readyitems)'),
    ('knowledge base and company content', r'^test_(kb|company|domainskills|standards|skillboard)'),
    ('target repositories and write-back', r'^test_(targets|promote|basesync|refs|writeback)'),
    ('board and link to VS Code chats', r'^test_(board|chat|vslink|vsrestart|cmdview|outview|health|gatereview|fusion|starticon|skillsend|approval_wake|taskboard|taskdesk|taskfiles|taskinbox|taskrun|tasksize|rewind)'),
    ('observe, reports and evals', r'^test_(observe|perfreview|evalcheck|evalrecord|evidence)'),
    ('setup, doctor, docs and upgrade', r'^test_(setup|doctor|docs|reinstall|skillcheck)'),
    ('tasks: life, stages, approvals and checks', r'^test_'),
]

def test_classes(src):
    try: tree = ast.parse(src)
    except SyntaxError: return [], 0
    names, count = [], 0
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            tests = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test')]
            count += len(tests)
            if tests: names.append(node.name)
        elif isinstance(node, ast.FunctionDef) and node.name.startswith('test'):
            count += 1; names.append(node.name)
    return names, count

TEST_COURSES = ('The book · 4.4 Build the enforcement layer like software | https://smarshu.com/book/read/4-4-enforcement-design.html',
                'The book · 6.3 Fixed tasks, scored by a script | https://smarshu.com/book/read/6-3-eval-tasks.html')

def guards(tag):
    """The hand-written section on the tests that guard the harness as a whole; every location is found at the tag."""
    T = '.harness/tests/'
    def c(f, name=None):
        if name is None:
            d = docstring(tag, T + f); return cite(T + f, d[1], d[2])
        return cite(T + f, *node_lines(tag, T + f, name))
    rows = len(re.findall(r'^    \(f?["\']', show(tag, T + 'test_gate_redteam.py'), re.M))
    out = ['## Test map: the tests that guard the whole\n',
           'Most test files check one part of the harness. A few check the harness as a whole: every document, every shipped Python file, every engine import, '
           'every spelling of a dangerous call, every command only a person may run. A change anywhere can break them, so they are what stops a change in one place '
           'from quietly breaking a promise made in another. They are listed here, each with what it guarantees, and again under their area below.\n',
           f'- `test_docs.py`: the README and `docs/` agree with the code. Every relative link has a target, every command a document shows runs, every policy field the reference names exists '
           f'and every top-level policy field is documented, every hook event and task template is listed, and the launcher scripts work {c("test_docs.py")} '
           f'{c("test_docs.py", "test_every_command_a_document_shows_runs")}.',
           f'- `test_old_python.py`: every Python file the repository ships, tool pack scripts included, loads on Python 3.9. It refuses the f-string forms only Python 3.12 reads, '
           f'after one such form in 1.7.38 kept the harness from starting on a work computer {c("test_old_python.py")} {c("test_old_python.py", "test_every_shipped_python_file_loads_on_python_3_9")}.',
           f'- `test_doctor.py`, three tests on the engine as a whole: the engine imports only the Python standard library and its own packages, so nothing has to be installed '
           f'{c("test_doctor.py", "test_engine_code_uses_only_the_standard_library")}; a module imports only `core/` and itself, never another module or the adapters '
           f'{c("test_doctor.py", "test_modules_import_only_core")}; every file under `.github/` and `.harness/` that git tracks is on a list of `registry.json`, so no file escapes `harness doctor` '
           f'{c("test_doctor.py", "test_every_shipped_file_belongs_to_a_registry_list")}.',
           f'- `test_gate_redteam.py`: the red team of the gate. {rows} ways of writing a call to the SQL Server sample type (case, comments, brackets, included script files, batch separators and more), '
           f'each with the answer the gate must give: pass, ask or refuse. Every row must get its answer, the test requires at least 80 rows with all three answers, '
           f'and a sample of the rows goes through the real hook with the same result {c("test_gate_redteam.py")} {c("test_gate_redteam.py", "RedTeamTests")}.',
           f'- `test_task.py`, `test_only_a_person_at_a_terminal_approves`: approving the plan and confirming the requirement are refused when the command is not typed by a person in a terminal, '
           f'and `confirm-req`, `approve-plan`, `approve-promote` and `recover` in a terminal call of the agent are denied by the hook {c("test_task.py", "test_only_a_person_at_a_terminal_approves")}.',
           f'- `test_c13_f2.py`, the commands only a person may run: every spelling of `harness task close` (quotes, a variable, `bash -c`, `python3 -m cli`, a here-document) is denied and names `harness task deliver` instead; '
           f'a harness call the gate cannot read (`xargs`, `$(...)`, a one-line interpreter) is denied; `approve-plan`, `confirm-req`, `approve-promote`, `approve-action`, `admin on`, `allow` and `review set` are read the same way; '
           f'and the harness commands an agent runs stay free {c("test_c13_f2.py", "HarnessCloseTests")}.',
           '']
    return out

def test_map(tag, lv):
    S, C, K = lv['sentences'], lv['chars'], lv['classes']
    files = [f for f in ls(tag, '.harness/tests') if f.endswith('.py')]
    groups = {a: [] for a, _ in TEST_AREAS}
    total_tests, missing = 0, []
    for f in files:
        name = f.rsplit('/', 1)[1]
        area = next(a for a, rx in TEST_AREAS if re.search(rx, name))
        src = show(tag, f)
        classes, n = test_classes(src)
        total_tests += n
        d = docstring(tag, f)
        ph = [phrase(c) if not c.startswith('test') else c[5:].replace('_', ' ') for c in classes]
        if d and d[0].strip():
            line = f'- `{name}`' + (f' ({n} tests)' if n else '') + f': {doc_summary(d[0], S, C)} {cite(f, d[1], d[2])}'
            k = max(K, 10) if area.startswith('fixes from') else K  # these docstrings mostly name internal items: the classes say what is checked
            if k and ph:
                more = len(ph) - k
                line += ' Checks: ' + '; '.join(clean(p) for p in ph[:k]) + (f'; and {more} more' if more > 0 else '') + '.'
        else:
            missing.append(f)
            line = f'- `{name}`' + (f' ({n} tests)' if n else '') + ': checks ' + '; '.join(clean(p) for p in ph[:max(K, 6)]) + f'. {cite(f)}'
        groups[area].append(line)
    out = [front('Test map', 'Test map', '33 Test map', tag, TEST_COURSES)]
    out.append('## Test map: what this file holds\n')
    out.append(f'The test map lists every test file of the harness at version {tag}: what each one checks, in the words of its own module docstring, '
               f'the number of tests in it, and the names of its test classes turned into plain phrases. '
               f'It answers "is X tested" and "where is the test for Y". There are {len([f for f in files if f.rsplit("/", 1)[1].startswith("test_")])} test files with {total_tests} test methods under `.harness/tests/`, '
               f'and fixed scenarios with recorded hook input under `.harness/eval/`. '
               f'A docstring often starts with the version (like 1.7.38) or the internal item (like B71 or M15-4) that added the tests.\n')
    out.extend(guards(tag))
    # how the tests are run
    out.append('## Test map: how the tests are run\n')
    idx = '.harness/INDEX.md'
    ln = next((n for n, l in enumerate(show(tag, idx).splitlines(), 1) if 'unittest discover' in l), None)
    internals = '.github/skills/harness-rookie-wondering/references/14-internals.md'
    il = next((n for n, l in enumerate(show(tag, internals).splitlines(), 1) if 'unittest discover' in l), None) if ls(tag, internals) else None
    admin = '.github/skills/harness-admin/SKILL.md'
    al = next((n for n, l in enumerate(show(tag, admin).splitlines(), 1) if 'unittest discover' in l), None) if ls(tag, admin) else None
    sup = docstring(tag, '.harness/tests/support.py')
    out.append(f'The harness tests are plain Python `unittest`, standard library only: `python3 -m unittest discover -s .harness/tests` on macOS and Linux, `python -m unittest discover -s .harness/tests` on Windows '
               + (cite(idx, ln) if ln else '') + (' ' + cite(internals, il) if il else '') + '. '
               f'The tests run `hook.py` and `cli.py` as real subprocesses with `HARNESS_ROOT` pointing at a temporary folder, so a test goes through the real hook entry point '
               + (cite('.harness/tests/support.py', sup[1], sup[2]) if sup else '') + '. '
               f'They use recorded hook input from real Copilot sessions as samples, and run in Chinese by default; `test_language.py` checks that English works end to end' + (' ' + cite(internals, il) if il else '') + '. '
               + (f'An admin who changes `.harness/engine/`, a policy or the hook configuration is told to run `harness doctor` and the tests after each change, and to add a test for a change of behaviour {cite(admin, al)}. ' if al else '')
               + '\n')
    out.append(f'The eval scenarios are different: `harness eval show` gives a prompt that a person runs once in a real Copilot chat, and `harness eval check` judges from the log and the files left behind whether it went right, with no model giving the score '
               f'{cite("docs/02-features.md", next((n for n, l in enumerate(show(tag, "docs/02-features.md").splitlines(), 1) if "eval check" in l), None))}.\n')
    for area, _ in TEST_AREAS:
        if not groups[area]: continue
        out.append(f'## Test map: {area}\n')
        out.extend(groups[area]); out.append('')
    # eval
    out.append('## Test map: eval scenarios and recorded hook input (`.harness/eval/`)\n')
    out.append('Each scenario is a prompt to run once in Copilot (`scenario.md`) and what the log and the files must show afterwards (`expect.json`), judged by `harness eval check`.\n')
    for f in ls(tag, '.harness/eval/scenarios'):
        if not f.endswith('scenario.md'): continue
        t = h1(tag, f)
        out.append(f'- `{f.split("/")[3]}`: ' + (f'{clean(t[0])} {cite(f, t[1])}' if t else cite(f)) + f' {cite(f.replace("scenario.md", "expect.json"))}')
    fx = [f for f in ls(tag, '.harness/eval/fixtures') if f.endswith('README.md')]
    for f in fx:
        p = first_paragraph_md(tag, f)
        n = len([x for x in ls(tag, f.rsplit('/', 1)[0]) if not x.endswith('README.md')])
        out.append(f'- `{f.rsplit("/", 1)[0].replace(".harness/eval/", "")}/` ({n} recorded files): ' + (f'{shorten(clean(p[0]), S, C)} {cite(f, p[1], p[2])}' if p else cite(f)))
    out.append('')
    return '\n'.join(out), {'test files': len(files), 'tests': total_tests, 'no docstring': missing}

# ---------- 34 Version history ----------

def releases(tag):
    path = 'docs/07-release-notes.md'
    lines = show(tag, path).splitlines()
    # a version is a "## 1.8.3 (date)" heading, or a "### 1.6.85 (date)" heading folded inside another version's section
    heads = [(n, m.group(1), m.group(2)) for n, l in enumerate(lines, 1) for m in [re.match(r'^#{2,3} (\d+\.\d+\.\d+)\s*\(([^)]*)\)', l)] if m]
    out = []
    for k, (n, ver, date) in enumerate(heads):
        end = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(lines)
        while end > n and not lines[end - 1].strip(): end -= 1
        summary, part, parts = None, None, []
        for i in range(n, end):
            l = lines[i]
            if re.match(r'^#{3,4} ', l): part = l.lstrip('#').strip(); parts.append([part, [], []]); continue
            if summary is None and l.strip() and part is None and not l.startswith(('-', '**', '<')): summary = l.strip(); continue
            m = re.match(r'^(?:- )?\*\*(.+?)\*\*', l)
            if m:
                if not parts: parts.append([None, [], []])
                parts[-1][1].append(m.group(1).strip())
            elif l.startswith('- ') and l[2:].strip().rstrip('.').lower() != 'nothing':
                if not parts: parts.append([None, [], []])
                parts[-1][2].append(l[2:].strip())
        out.append({'version': ver, 'date': date, 'start': n, 'end': end, 'summary': summary, 'parts': parts})
    return path, out

FULL = '1.8.'  # versions whose every bold lead-in is listed, whatever the level

def version_history(tag, lv):
    path, rels = releases(tag)
    out = [front('Version history', 'Version history', '34 Version history', tag)]
    out.append('## Version history: what this file holds\n')
    out.append(f'The version history lists every version of the harness from {rels[-1]["version"]} ({rels[-1]["date"]}) to {rels[0]["version"]} ({rels[0]["date"]}), newest first, '
               f'{len(rels)} versions in all, from the release notes `{path}`. Each version has its date, the one-line summary of the release notes, and the bold lead-in of each item '
               f'grouped by Added, Changed, Fixed and Retired: ' + (f'for {FULL}x every lead-in, for older versions the first {lv["bullets"]} and the number of the others ("and 3 more"); ' if lv['bullets'] else '') + f'the full text of an item is in the release notes at the code location given. '
               f'It answers "when did X come in" and "what changed in version Y". The dates are the release notes\' own {cite(path, 1, 11)}.\n')
    by_minor = {}
    for r in rels: by_minor.setdefault('.'.join(r['version'].split('.')[:2]), []).append(r)
    for minor, rs in by_minor.items():
        out.append(f'## Version history: {minor}.x ({rs[-1]["date"]} to {rs[0]["date"]}, {len(rs)} versions)\n')
        # one paragraph per release day, each version in it starting with its number in bold: no half-empty last line and
        # no gap per version, so some 280 versions fit the page budget
        day, para = None, []
        for r in rs + [None]:
            if r is None or r['date'] != day:
                if para: out.append(' '.join(para) + '\n')
                if r is None: break
                day, para = r['date'], []
            txt = f'**{r["version"]}** ({r["date"]}).'
            if r['summary']: txt += ' ' + shorten(clean(r['summary']), lv['summary'], lv['summary_chars'])
            for part, bold, plain in r['parts']:
                heads = bold or [shorten(clean(b), 1, 10**6) for b in plain]  # an item with no bold lead-in: its first sentence
                if not heads: continue
                full = r['version'].startswith(FULL)  # the newest versions: every lead-in, never "and N more"
                keep = heads if lv['bullets'] is None or full else heads[:lv['bullets']]
                hc = max(lv['head_chars'], 80) if full else lv['head_chars']
                items = [shorten(h if not bold else clean(h), 1, hc).rstrip('.:; ') for h in keep]
                more = len(heads) - len(keep)
                txt += (f' {part}: ' if part else ' ') + '; '.join(items) + (f'; and {more} more' if more > 0 else '') + '.'
            para.append(txt + ' ' + cite(path, r['start'], r['end']))
    return '\n'.join(out), {'versions': len(rels), 'no lead-ins': [r['version'] for r in rels if not any(b for _, b, _ in r['parts'])]}

# ---------- writing and fitting ----------

LEVELS = {
    '32-code-map': (code_map, [dict(sentences=2, chars=320), dict(sentences=1, chars=240), dict(sentences=1, chars=170), dict(sentences=1, chars=140), dict(sentences=1, chars=110)]),
    '33-test-map': (test_map, [dict(sentences=2, chars=320, classes=8), dict(sentences=1, chars=240, classes=6), dict(sentences=1, chars=200, classes=3),
                               dict(sentences=1, chars=160, classes=0)]),
    '34-version-history': (version_history, [dict(summary=2, summary_chars=400, bullets=None, head_chars=200),
                                             dict(summary=1, summary_chars=300, bullets=None, head_chars=120),
                                             dict(summary=1, summary_chars=220, bullets=None, head_chars=80),
                                             dict(summary=1, summary_chars=200, bullets=6, head_chars=80),
                                             dict(summary=1, summary_chars=160, bullets=4, head_chars=70),
                                             dict(summary=1, summary_chars=140, bullets=3, head_chars=60),
                                             dict(summary=1, summary_chars=120, bullets=3, head_chars=50),
                                             dict(summary=1, summary_chars=110, bullets=2, head_chars=50),
                                             dict(summary=1, summary_chars=100, bullets=2, head_chars=45),
                                             dict(summary=1, summary_chars=90, bullets=1, head_chars=45),
                                             dict(summary=1, summary_chars=80, bullets=1, head_chars=40)]),
}

def write(name, text):
    p = os.path.join(PAGES, name + '.md')
    open(p, 'w', encoding='utf-8').write(text.rstrip() + '\n')
    return p

def main():
    ap = argparse.ArgumentParser(description='Write the reference pages of the Harness Guide from the harness at a tag.')
    ap.add_argument('--tag', default='1.8.3')
    ap.add_argument('--no-fit', dest='fit', action='store_false', help='write the fullest text only; do not build and shorten to the page budget')
    ap.add_argument('--level', type=int, default=0, help='start at this level of shortening (0: fullest)')
    ap.add_argument('--only', nargs='*', choices=['code', 'test', 'versions'])
    a = ap.parse_args()
    pick = {'code': '32-code-map', 'test': '33-test-map', 'versions': '34-version-history'}
    names = [pick[o] for o in a.only] if a.only else list(LEVELS)
    git('rev-parse', '--verify', a.tag + '^{commit}')
    if a.fit:
        sys.path.insert(0, GUIDE); import build
    for name in names:
        fn, levels = LEVELS[name]
        for k in range(a.level, len(levels)):
            text, info = fn(a.tag, levels[k])
            write(name, text)
            if not a.fit:
                print(f'{name}: written (level {k}) {json.dumps({x: (len(v) if isinstance(v, list) else v) for x, v in info.items()})}'); break
            meta, layout, probs = build.build(name)
            print(f'{name}: level {k}, {layout["pages"]} pages (budget {BUDGET[name]})' + (f', {len(probs)} check problem(s)' if probs else ''))
            if layout['pages'] <= BUDGET[name]: break
        else:
            print(f'{name}: still over its budget at the shortest level')
        if info.get('no docstring'): print(f'  without a module docstring ({len(info["no docstring"])}): ' + ', '.join(info['no docstring']))
        if info.get('no lead-ins'): print(f'  versions with no bold lead-in: ' + ', '.join(info['no lead-ins']))

if __name__ == '__main__':
    main()
