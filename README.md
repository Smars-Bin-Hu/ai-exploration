# AI Exploration

The source of the company OneDrive folder "AI Exploration". Pull it on the company computer, add the company-only files there, and copy the folder to OneDrive.

| Folder | What is in it | Where it comes from |
|---|---|---|
| `Start Here/` | `Start Here.pptx` (edit this one) and `Start Here.pdf` (preview) | built from `Start Here/source/` |
| `Harness Engineering 101/` | slidedoc PDFs: `Basic/`, `Advanced/`, `Mindset/` | exported from the smarshu.com repository (`npm run export:team`) |
| `Showcase/` | `Lessons/` (PDFs) and `Real Tasks/` | `Real Tasks/` is company only: added on the company computer, never committed |
| `Harness/` | the harness install package, the knowledge base, `programs/`, the guides | zips and installers are not committed (see `.gitignore`) |

## Build Start Here

```sh
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
.venv/bin/python "Start Here/source/build.py"
```

- The text is in `Start Here/source/slides.py` (English, retold from `zh-Hans.md`). Figures: `figs.py` writes `fig/*.svg` and `fig/*.png`. Screenshots: `img/`.
- `build.py` writes the PowerPoint and an HTML twin of it, prints the twin to the PDF, and reports text that does not fit its box. It needs Google Chrome and `playwright-core` from `~/Developer/smarshu.com`.
- After you edit the PowerPoint by hand on the company computer, that file is the newer one: do not rebuild over it.
- Phone review pages: `review_html.py <out.html>` (the Chinese draft with its figures and screenshots, and the cold-read record from `review-notes.md`); `preview_html.py <out.html>` (the English slides, page by page, after `build.py`).
