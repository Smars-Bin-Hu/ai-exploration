# Start Here: one layout, two outputs. source/start-here/Start Here.pptx (editable text boxes) and an HTML twin printed to AI Exploration/1 Showcase/Start Here.pdf.
# Once the PowerPoint is edited by hand it is the newer one: do not rebuild over it; export its PDF from PowerPoint instead.
# Run from the repo root: .venv/bin/python source/start-here/build.py   (needs Chrome, and playwright-core from ~/Developer/smarshu.com)
import os, sys
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.path.join(ROOT, 'source', 'tools'))
from deck import Deck, T, P, R, C, W, SERIF, SANS
import slides as S

def img(name):
    for d in ('img', 'fig'):
        p = f'{H}/{d}/{name}.png'
        if os.path.exists(p): return p
    raise FileNotFoundError(name)

D = Deck('AI Exploration · Start Here')
page, head = D.page, Deck.head

# cover
page([T(0.9, 2.3, 10, 0.4, [[S.COVER['kicker']]], 13, C['accent'], SANS, bold=True, caps=True, spacing=2),
      T(0.9, 2.8, 11, 1.2, [[S.COVER['title']]], 60, C['ink'], SERIF, ls=1.0),
      T(0.9, 4.2, 8.6, 1.2, [[S.COVER['sub']]], 20, C['muted'], SERIF)], footer=False)

for st in S.STORY:
    els = head(st['kicker'], st['title'])
    if 'cards' in st:
        cw, ch, gx, gy = 5.8, 1.95, 0.23, 0.2
        for i, card in enumerate(st['cards']):
            x = 0.75 + (i % 2) * (cw + gx); y = 1.72 + (i // 2) * (ch + gy)
            els += [R(x, y, cw, ch, fill=C['wash']), R(x, y, 0.06, ch, fill=C['accent'], radius=False),
                    T(x + 0.28, y + 0.2, cw - 0.5, ch - 0.35, [card], 13, C['ink'], SERIF)]
        els.append(T(0.75, 6.0, 11.8, 0.9, st['closing'], 13, C['ink'], SERIF, space=4))
    elif st.get('wide'):
        els.append(T(0.75, 1.72, 11.8, 0.8, st['paras'], 14, C['ink'], SERIF))
        els.append(P(img(st['fig']), 0.75, 2.75, 11.8, 4.0))
    else:
        tw = st.get('textw', 5.55); fx = 0.75 + tw + 0.35
        els.append(T(0.75, 1.75, tw, 5.0, st['paras'], 14, C['ink'], SERIF, space=9))
        els.append(P(img(st['fig']), fx, 1.75, 12.6 - fx, 5.0))
    page(els)

for f in S.FEATURES:
    side, title, shot, texts = f[:4]; note = f[4] if len(f) > 4 else None
    els = head(f'{side} ability · In the harness', title, dark=True, title_w=11.8)
    paras = []
    for i, t in enumerate(texts):
        paras.append([('lab', S.L[i])]); paras.append([t])
    if shot and (shot in S.WIDE or (lambda wh: wh[0] / wh[1])(Image.open(img(shot)).size) > 3.5):
        # a very wide screenshot: text in two columns on top, the screenshot across the page below it
        half = len(paras) // 2
        sh = S.WIDE.get(shot, 1.85)  # height of the screenshot; the text gets the rest
        els.append(T(0.75, 1.72, 5.75, 5.0 - sh, paras[:half], 12, C['light'], SERIF, space=5))
        els.append(T(6.85, 1.72, 5.75, 5.0 - sh, paras[half:], 12, C['light'], SERIF, space=5))
        els.append(P(img(shot), 0.75, 6.85 - sh, 11.85, sh, border=True))
        page(els, dark=True); continue
    els.append(T(0.75, 1.72, 5.6, 5.15, paras, 12, C['light'], SERIF, space=5))
    if shot:
        els.append(P(img(shot), 6.7, 1.75, 5.9, 4.85 if note else 5.1, border=True))
        if note: els.append(T(6.7, 6.68, 5.9, 0.25, [[('i', note)]], 10, '9A9A96', SERIF, align='r'))
    else:
        els += [R(6.7, 1.75, 5.9, 5.0, line='9A9A96', dash=True),
                T(7.0, 3.85, 5.3, 0.9, [['Screenshot to add on the company computer:'], ['a test run on DEV, as the task records it']], 13, '9A9A96', SERIF, align='c')]
    page(els, dark=True)

for bh in S.BEHIND:
    # the 'Behind it' of a feature, when it needs a page of its own
    els = head(f"{bh['side']} ability · In the harness", bh['title'], dark=True)
    paras = [[('lab', S.L[4])]] + bh['paras']
    els.append(T(0.75, 1.72, 5.6, 5.15, paras, 12, C['light'], SERIF, space=7))
    els.append(P(img(bh['fig']), 6.7, 1.75, 5.9, 5.1, border=True))
    page(els, dark=True)

ix = S.INDEX
page(head(ix['kicker'], ix['title']) + [T(0.75, 1.75, 5.55, 5.0, ix['paras'], 14, C['ink'], SERIF, space=12), P(img(ix['fig']), 6.65, 1.75, 5.95, 5.0)])

pptx_path = f'{H}/Start Here.pptx'
D.save_pptx(pptx_path)
D.save_pdf(H, f'{H}/_twin.html', f'{ROOT}/AI Exploration/1 Showcase/Start Here.pdf', f'{H}/_pages')
print(len(D.pages), 'slides ->', pptx_path)
