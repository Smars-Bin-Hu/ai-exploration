# Showcase deck for one real task: a summary page, then one dark page per screenshot (tall or wide), with a small heading
# and a conclusion. Builds the template to copy and a sample filled with fake data.
# Run from the repo root: .venv/bin/python Showcase/source/build.py   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from deck import Deck, T, P, R, C, SERIF, SANS
import text as X

OUT = os.path.join(ROOT, 'Showcase', 'Real Tasks', '_template')
NOTE = ('One deck for one task. Replace every grey hint. For each screenshot, copy the page with the right shape (tall or wide), '
        'paste the picture over the dashed box and delete the box. ') + X.SHOTS

def shot(els, pic, x, y, w, h, shape):
    if pic:
        els.append(P(f'{H}/img/{pic}.png', x, y, w, h, border=True))
    else:
        els.append(R(x, y, w, h, line='9A9A96', dash=True))
        els.append(T(x + 0.4, y + h / 2 - 0.4, w - 0.8, 0.9, [[f'Paste a {shape} screenshot here'], [('m', 'Crop it to the part that proves the point')]], 13, '9A9A96', SERIF, align='c', space=4))

def build(V):
    D = Deck(V['footer'])
    s = V['summary']
    els = Deck.head(f"{V['task_kicker']} · {s['kind']}", s['title'])
    els.append(T(0.75, 1.72, 11.8, 0.35, [s['facts']], 11, C['muted'], SANS))
    cw, ch = 5.8, 1.8
    for i, (lab, body) in enumerate(s['cards']):
        x = 0.75 + (i % 2) * (cw + 0.23); y = 2.2 + (i // 2) * (ch + 0.2)
        els += [R(x, y, cw, ch, fill=C['wash']), R(x, y, 0.06, ch, fill=C['accent'], radius=False),
                T(x + 0.28, y + 0.18, cw - 0.5, ch - 0.3, [[('lab', lab)], body], 12.5, C['ink'], SERIF, space=4)]
    els.append(T(0.75, 6.12, 11.8, 0.8, [[('b', 'Result: ')] + s['result'], [('b', 'Not so good: ')] + s['notgood']], 12, C['ink'], SERIF, space=3))
    D.page(els, notes=NOTE)

    for shape, pic, heading, paras in V['pages']:
        els = []
        if shape == 'tall':  # the picture on the left, as tall as the page allows; heading and conclusion on the right
            shot(els, pic, 0.75, 0.55, 6.6, 6.2, 'tall')
            els.append(T(7.75, 1.0, 4.85, 0.9, [heading], 22, C['white'], SERIF, ls=1.05))
            els.append(T(7.75, 2.05, 4.85, 4.6, paras, 14, C['light'], SERIF, space=10))
        else:  # the picture across the page; heading above, conclusion under it
            els.append(T(0.75, 0.5, 11.8, 0.55, [heading], 22, C['white'], SERIF, ls=1.05))
            shot(els, pic, 0.75, 1.25, 11.83, 4.4, 'wide')
            els.append(T(0.75, 5.9, 11.8, 0.95, paras, 14, C['light'], SERIF, space=6))
        D.page(els, dark=True, notes=NOTE)

    os.makedirs(OUT, exist_ok=True)
    name = V['file']; key = name.split()[0].lower()
    D.save_pptx(f'{OUT}/{name}.pptx')
    D.save_pdf(H, f'{H}/_twin-{key}.html', f'{OUT}/{name}.pdf', f'{H}/_pages/{key}')
    print(name, len(D.pages), 'slides')

for V in (X.TEMPLATE, X.SAMPLE): build(V)
