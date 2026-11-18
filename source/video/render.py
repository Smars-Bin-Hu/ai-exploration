# Draws one 1920x1080 PNG per `@` line of a scenes file. Every frame is an HTML page in one look (source/video/figs.css:
# dark grey, Source Serif 4, teal and orange from smarshu.com), shot by Chrome through shoot.cjs, one browser per batch.
# The templates below (card, picture, timeline, loop, formula, list, big, quote, logos) write their page here;
# a figure (`@ fig name`) is a page someone wrote by hand under figs/. The avatar is added to every frame by shoot.cjs.
import hashlib, html, json, math, subprocess, tempfile
from pathlib import Path

from PIL import Image

W, H = 1920, 1080
RENDER_VERSION = '2'  # bump when the look changes in code, so every frame is drawn again (figs.css is hashed by itself)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CSS = HERE / 'figs.css'
SHOOT = HERE / 'shoot.cjs'
ASSETS = ROOT / '.claude/loops/assets'
FONTS, LOGOS = ASSETS / 'fonts', ASSETS / 'logos'
ICONS = ASSETS / 'lucide/node_modules/lucide-static/icons'
AVATARS = [ROOT / '.claude/loops/voice/avatar.jpg', ROOT / '.claude/loops/voice/avatar.png',
           ROOT.parent / 'smarshu.com/public/portrait.jpg']
THEMES = {'dark': '', 'navy': 'theme-navy'}

# the stage (figs.css .stage): where pictures may go, inside margins that keep the subtitles and the avatar clear
STAGE_W, STAGE_H = W - 2 * 170, H - 100 - 180
CAPTION_H = 150

# what each template accepts after its quoted words; FORMAT.md describes them
OPTIONS = {
    'card': {'kicker', 'icon'},
    'timeline': {'now'},
    'loop': {'lit', 'centre'},
    'formula': {'lit'},
    'list': {'lit'},
    'big': {'icon'},
    'quote': {'by'},
    'logos': set(),
    'fig': {'step'},
}
LOGO_LABELS = {'github-copilot': 'GitHub Copilot', 'claude-code': 'Claude Code', 'codex': 'Codex', 'vscode': 'VS Code',
               'claude': 'Claude', 'openai': 'OpenAI', 'github': 'GitHub', 'cursor': 'Cursor', 'm365-copilot': 'M365 Copilot', 'sql-server': 'SQL Server'}


def default_avatar():
    return next((p for p in AVATARS if p.exists()), None)


def _sha(data):
    return hashlib.sha1(data).hexdigest()[:12]


def _listing(d):
    return ','.join(sorted(p.name for p in d.iterdir())) if d.exists() else ''


def inputs(spec, theme='dark', avatar=None):
    """Everything a frame depends on, as one string to hash: change any of it and the frame is drawn again."""
    parts = [RENDER_VERSION, spec['raw'], theme, _sha(CSS.read_bytes()), _sha(SHOOT.read_bytes()), _listing(FONTS)]
    if avatar:
        parts += [str(avatar), Path(avatar).stat().st_mtime]
    if spec.get('src'):
        parts += [str(spec['src']), Path(spec['src']).stat().st_mtime]
    if spec['kind'] == 'fig':
        parts.append(_sha(Path(spec['src']).read_bytes()))
    if spec['kind'] in ('logos', 'fig'):
        parts.append(_listing(LOGOS))
    return '\x1f'.join(str(p) for p in parts)


# ---------- pages ----------

e = html.escape


def _icon(name, cls=''):
    return f'<i data-icon="{e(name)}" class="{cls}"></i>' if name else ''


def _page(body, cls=''):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{CSS.as_uri()}"></head>'
            f'<body><main class="stage {cls}">{body}</main></body></html>')


def _title_size(text, sizes=((28, 116), (48, 100), (80, 88), (120, 76))):
    return next((s for n, s in sizes if len(text) <= n), 66)


def card(spec):
    title, kicker = spec['text'], spec.get('kicker') or ''
    body = _icon(spec['opts'].get('icon'), 'big-icon')
    if kicker:
        body += f'<div class="kicker">{e(kicker)}</div>'
    body += f'<h1 class="title" style="font-size:{_title_size(title)}px">{e(title)}</h1>'
    return _page(body, 't-card')


def picture(spec, work):
    """A screenshot or page as a white card; box= in teal; crop= shows only that part, enlarged."""
    s = Image.open(spec['src'])
    src, box, crop = spec['src'], spec.get('box'), spec.get('crop')
    if crop:
        cx, cy, cw, ch = crop
        sw, sh = s.size
        s = s.convert('RGB').crop((round(cx * sw), round(cy * sh), round((cx + cw) * sw), round((cy + ch) * sh)))
        src = work / f'crop-{_sha(spec["raw"].encode())}.png'
        s.save(src)
        if box:  # the box is in source fractions: move it into the crop, cut to its edges, drop it if outside
            x0, y0 = max(box[0], cx), max(box[1], cy)
            x1, y1 = min(box[0] + box[2], cx + cw), min(box[1] + box[3], cy + ch)
            box = ((x0 - cx) / cw, (y0 - cy) / ch, (x1 - x0) / cw, (y1 - y0) / ch) if x1 > x0 and y1 > y0 else None
    iw, ih = s.size
    ah = STAGE_H - (CAPTION_H if spec.get('text') else 0)
    scale = min(STAGE_W / iw, ah / ih)
    dw, dh = round(iw * scale), round(ih * scale)
    hl = ''
    if box:
        pad = 8  # the line sits just outside the marked area
        bx, by, bw, bh = box
        hl = (f'<div class="hl" style="left:{bx * dw - pad:.1f}px;top:{by * dh - pad:.1f}px;'
              f'width:{bw * dw + 2 * pad:.1f}px;height:{bh * dh + 2 * pad:.1f}px"></div>')
    body = f'<figure class="shot" style="width:{dw}px;height:{dh}px;margin:0"><img src="{Path(src).as_uri()}">{hl}</figure>'
    if spec.get('text'):
        body += f'<div class="caption">{e(spec["text"])}</div>'
    return _page(body, 't-pic')


def timeline(spec):
    steps = [a.split('|', 1) if '|' in a else ['', a] for a in spec['args']]
    n = len(steps)
    now = _int(spec['opts'].get('now'))
    cols = []
    for i, (year, label) in enumerate(steps, 1):
        state = 'plain' if not now else 'past' if i < now else 'now' if i == now else 'future'
        tail = '<div class="tl-now">now</div>' if i == now else ''
        cols.append(f'<div class="tl-step {state}"><div class="tl-year">{e(year)}</div><div class="tl-dot"></div>'
                    f'<div class="tl-label">{e(label)}</div>{tail}</div>')
    c = lambda i: (i - 0.5) / n * 100  # centre of step i, % of the width
    lines = f'<div class="tl-line" style="left:{c(1)}%;width:{c(n) - c(1)}%"></div>'
    if now and now > 1:
        lines += f'<div class="tl-line reached" style="left:{c(1)}%;width:{c(now) - c(1)}%"></div>'
    return _page(f'<div class="tl">{lines}{"".join(cols)}</div>', 't-timeline')


def loop(spec):
    """Boxes around an ellipse, joined clockwise by arrows that run along it; lit= lights one box and the arrow into it."""
    items = spec['args']
    n, lit = len(items), _int(spec['opts'].get('lit'))
    bw, bh = 1460, 780
    cx, cy, rx, ry = bw / 2, bh / 2, 560, 290
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    pos = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in ang]
    size = [(0.5 * 42 * len(t.split('|')[0]) + 84 + (62 if '|' in t else 0), 104) for t in items]

    def inside(p, i, m=26):
        (x, y), (w, h) = pos[i], size[i]
        return abs(p[0] - x) < w / 2 + m and abs(p[1] - y) < h / 2 + m
    arcs = []
    for i in range(n):
        j = (i + 1) % n
        a0, a1 = ang[i], ang[i] + 2 * math.pi / n
        pts = [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in (a0 + (a1 - a0) * k / 400 for k in range(401))]
        pts = [p for p in pts if not inside(p, i) and not inside(p, j)]
        if len(pts) < 2:
            continue
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts[::4] + [pts[-1]])
        hot = lit and j + 1 == lit
        arcs.append(f'<path d="{d}" fill="none" stroke="{"#2dd4bf" if hot else "#5b6676"}" stroke-width="{4 if hot else 3}" '
                    f'stroke-linecap="round" marker-end="url(#{"ah-hot" if hot else "ah"})"/>')
    marker = lambda mid, col: (f'<marker id="{mid}" viewBox="0 0 12 12" refX="9" refY="6" markerWidth="5" markerHeight="5" '
                               f'orient="auto-start-reverse"><path d="M1,1 L11,6 L1,11 z" fill="{col}"/></marker>')
    svg = (f'<svg width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}"><defs>{marker("ah", "#5b6676")}{marker("ah-hot", "#2dd4bf")}'
           f'</defs>{"".join(arcs)}</svg>')
    boxes = ''
    for i, t in enumerate(items):
        label, _, icon = t.partition('|')
        boxes += (f'<div class="pill{" lit" if lit == i + 1 else ""}" style="left:{pos[i][0]:.1f}px;top:{pos[i][1]:.1f}px">'
                  f'{_icon(icon)}{e(label)}</div>')
    centre = spec['opts'].get('centre')
    centre = f'<div class="centre">{e(centre)}</div>' if centre else ''
    return _page(f'<div class="loop" style="width:{bw}px;height:{bh}px">{svg}{centre}{boxes}</div>', 't-loop')


def formula(spec):
    terms = spec['args']
    lit = _int(spec['opts'].get('lit')) or len(terms)
    chars = sum(len(t) for t in terms) + 3 * (len(terms) - 1)
    size = min(156, int(1500 / (0.5 * chars)))
    parts = []
    for i, t in enumerate(terms, 1):
        if i == 2:
            parts.append('<span class="op">=</span>')
        elif i > 2:
            parts.append('<span class="op">+</span>')
        parts.append(f'<span class="term{" lit" if i == lit else ""}">{e(t)}</span>')
    return _page(f'<div class="row" style="font-size:{size}px">{"".join(parts)}</div>', 't-formula')


def list_(spec):
    title, items = spec['args'][0], spec['args'][1:]
    lit = _int(spec['opts'].get('lit'))
    rows = math.ceil(len(items) / 2) if len(items) > 5 else len(items)
    lis = []
    for i, t in enumerate(items, 1):
        text, _, icon = t.partition('|')
        state = '' if not lit else 'done' if i < lit else 'lit' if i == lit else 'later'
        lis.append(f'<li class="{state}"><span class="n">{i}</span>{_icon(icon)}<span>{e(text)}</span></li>')
    size = 44 if len(items) <= 5 else 40
    cols = 2 if len(items) > 5 else 1
    return _page(f'<div class="rule"></div><h2 class="title">{e(title)}</h2>'
                 f'<ol style="grid-template-rows:repeat({rows},auto);grid-template-columns:repeat({cols},1fr);font-size:{size}px">'
                 f'{"".join(lis)}</ol>', 't-list')


def big(spec):
    num = spec['args'][0]
    line = ' '.join(spec['args'][1:])
    body = _icon(spec['opts'].get('icon'), 'big-icon') + f'<div class="num">{e(num)}</div>'
    if line:
        body += f'<div class="line">{e(line)}</div>'
    return _page(body, 't-big')


def quote(spec):
    text = ' '.join(spec['args'])
    by = spec['opts'].get('by')
    size = 68 if len(text) <= 140 else 56
    body = f'<div class="mark">&ldquo;</div><blockquote style="font-size:{size}px">{e(text)}</blockquote>'
    if by:
        body += f'<div class="by">{e(by)}</div>'
    return _page(body, 't-quote')


def logos(spec):
    tiles = []
    for t in spec['args']:
        name, _, label = t.partition('|')
        auto = not label
        label = label or LOGO_LABELS.get(name, name.replace('-', ' ').title())
        tiles.append(f'<div class="logo"><div class="tile"><img data-logo="{e(name)}"></div>'
                     f'<div class="label{" auto" if auto else ""}">{e(label)}</div></div>')
    return _page(f'<div class="row">{"".join(tiles)}</div>', 't-logos')


def _int(v):
    return int(v) if v not in (None, '') else None


TEMPLATES = {'card': card, 'timeline': timeline, 'loop': loop, 'formula': formula, 'list': list_, 'big': big,
             'quote': quote, 'logos': logos}


def check(spec):
    """-> an error message for a template's @ line, or None."""
    k, a, o = spec['kind'], spec['args'], spec['opts']
    for name in ('now', 'lit', 'step'):
        if name in o and not str(o[name]).isdigit():
            return f'{name}= wants a whole number'
    need = {'timeline': 2, 'loop': 2, 'formula': 2, 'list': 2, 'big': 1, 'quote': 1, 'logos': 1}.get(k, 0)
    if len(a) < need:
        return f'{k} needs at least {need} quoted part{"s" if need > 1 else ""}'
    return None


# ---------- shooting ----------

def render(jobs, theme='dark', avatar=None):
    """jobs: [(spec, out_png)]. Writes every page, then shoots them all in one browser."""
    if not jobs:
        return
    with tempfile.TemporaryDirectory(prefix='frames-') as td:
        work = Path(td)
        shots = []
        for i, (spec, out) in enumerate(jobs):
            if spec['kind'] == 'fig':
                url, step = Path(spec['src']).as_uri(), _int(spec['opts'].get('step'))
            else:
                page = picture(spec, work) if spec['kind'] == 'image' else TEMPLATES[spec['kind']](spec)
                p = work / f'{i:04d}.html'
                p.write_text(page, encoding='utf-8')
                url, step = p.as_uri(), None
            shots.append(dict(url=url, out=str(out), step=step, theme=THEMES[theme],
                              avatar=Path(avatar).as_uri() if avatar else None))
        jf = work / 'jobs.json'
        jf.write_text(json.dumps(dict(css=CSS.as_uri(), icons=str(ICONS), logos=str(LOGOS), jobs=shots)))
        r = subprocess.run(['node', str(SHOOT), str(jf)], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f'shoot.cjs failed: {r.stderr.strip()[-800:]}')
