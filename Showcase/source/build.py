# Showcase decks for Real Tasks: the template to copy for each task, and a sample filled with fake data.
# Run from the repo root: .venv/bin/python Showcase/source/build.py   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from deck import Deck, T, P, R, C, SERIF, SANS
import text as X

OUT = os.path.join(ROOT, 'Showcase', 'Real Tasks', '_template')
NOTE = ('Copy this file into a folder for the task, next to the task page saved from the board (Save as HTML). Take every picture from this one task, so its name shows in each. '
        'Replace every grey hint. To fill a dashed box, paste the screenshot and delete the box. Delete a box the task does not need.')

def slot(els, x, y, w, h, label, pic, where, need, caption, dark):
    lab_col = C['accent']
    els.append(T(x, y, w, 0.3, [[('lab', label)]], 9, lab_col, SANS))
    if pic:
        els.append(P(f'{H}/img/{pic}.png', x, y + 0.32, w, h, border=True))
    else:
        els.append(R(x, y + 0.32, w, h, line='9A9A96', dash=True))
        lines = [['Paste a screenshot here'], [('m', 'Where: ' + where)]] + ([[('m', 'Needed for: ' + need)]] if need else [])
        els.append(T(x + 0.25, y + 0.32 + h / 2 - 0.55, w - 0.5, 1.2, lines, 11, '9A9A96' if dark else C['muted'], SERIF, align='c', space=4))
    els.append(T(x, y + 0.4 + h, w, 0.6, [caption], 11, C['light'] if dark else C['ink'], SERIF))

def build(V):
    D = Deck(V['footer'])
    o = V['overview']
    els = Deck.head(V['kicker'], o['title'])
    els.append(T(0.75, 1.75, 5.55, 5.0, o['paras'], 13, C['ink'], SERIF, space=8))
    slot(els, 6.65, 1.7, 5.95, 3.9, *o['box'], dark=False)
    D.page(els, notes=NOTE)

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

    v = V['vertical']
    els = Deck.head(f"Vertical ability · {v['task']}", v['title'], dark=True)
    for i, b in enumerate(v['boxes']):
        slot(els, 0.75 + (i % 2) * 6.03, 1.7 + (i // 2) * 2.62, 5.8, 1.7, *b, dark=True)
    D.page(els, dark=True, notes=NOTE)

    z = V['horizontal']
    els = Deck.head(f"Horizontal ability · {z['task']}", z['title'], dark=True)
    for i, b in enumerate(z['boxes']):
        slot(els, 0.75 + (i % 2) * 6.03, 1.7 + (i // 2) * 2.62, 5.8, 1.7, *b, dark=True)
    D.page(els, dark=True, notes=NOTE)

    os.makedirs(OUT, exist_ok=True)
    name = V['file']
    D.save_pptx(f'{OUT}/{name}.pptx')
    D.save_pdf(H, f'{H}/_twin-{name.split()[0].lower()}.html', f'{OUT}/{name}.pdf', f'{H}/_pages/{name.split()[0].lower()}')
    print(name, len(D.pages), 'slides')

for V in (X.TEMPLATE, X.SAMPLE): build(V)
