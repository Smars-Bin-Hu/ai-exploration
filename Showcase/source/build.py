# Showcase deck for one real task: a white summary page, then one dark page per screenshot (tall or wide); the screenshot
# is the page and a few sentences explain it, with no headings. Builds the template to copy and a sample filled with fake data.
# Run from the repo root: .venv/bin/python Showcase/source/build.py   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from deck import Deck, T, P, R, C, SERIF, SANS
import text as X

OUT = os.path.join(ROOT, 'Showcase', 'Real Tasks', '_template')
NOTE = ('One deck for one task. Replace every grey hint. For each screenshot, copy the page with the right shape (tall or wide), '
        'paste the picture over the dashed box and delete the box. The text explains the picture: what it shows and why it matters. ') + X.SHOTS

def shot(els, pic, x, y, w, h, shape):
    if pic:
        els.append(P(f'{H}/img/{pic}.png', x, y, w, h, border=True))
    else:
        els.append(R(x, y, w, h, line='9A9A96', dash=True))
        els.append(T(x + 0.4, y + h / 2 - 0.4, w - 0.8, 0.9, [[f'Paste a {shape} screenshot here'], [('m', 'Crop it to the part that proves the point')]], 13, '9A9A96', SERIF, align='c', space=4))

def build(V):
    D = Deck(V['footer'])
    s = V['summary']
    # page 1, white: the task in one line, then what happened, in a few paragraphs
    els = Deck.head(V['task_kicker'], s['title'])
    els.append(T(0.75, 1.75, 11.8, 0.35, [s['facts']], 11, C['muted'], SANS))
    els.append(T(0.75, 2.35, 11.8, 4.4, s['body'], 15, C['ink'], SERIF, space=12))
    D.page(els, notes=NOTE)

    # then one dark page per screenshot: the picture is the page, the text explains it; no headings
    for shape, pic, paras in V['pages']:
        els = []
        if shape == 'tall':  # the picture on the left, as tall as the page allows; the text on the right
            shot(els, pic, 0.75, 0.55, 7.4, 6.2, 'tall')
            els.append(T(8.5, 0.75, 4.1, 5.9, paras, 14, C['light'], SERIF, space=10))
        else:  # the picture across the page; the text under it
            shot(els, pic, 0.75, 0.55, 11.83, 5.1, 'wide')
            els.append(T(0.75, 5.85, 11.8, 1.0, paras, 14, C['light'], SERIF, space=6))
        D.page(els, dark=True, notes=NOTE)

    os.makedirs(OUT, exist_ok=True)
    name = V['file']; key = name.split()[0].lower()
    D.save_pptx(f'{OUT}/{name}.pptx')
    D.save_pdf(H, f'{H}/_twin-{key}.html', f'{OUT}/{name}.pdf', f'{H}/_pages/{key}')
    print(name, len(D.pages), 'slides')

for V in (X.TEMPLATE, X.SAMPLE): build(V)
