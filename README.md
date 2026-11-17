# AI Exploration

The source of the company OneDrive folder "AI Exploration". Two parts:

- **`AI Exploration/`** is what people read. Copy this folder, and only this folder, to the team OneDrive. On the company computer, add the company-only files inside it (see below).
- **`source/`** is how it is built: sources, build scripts, the Guide's questions and rules. Never copied to OneDrive.

## What people find in `AI Exploration/`

| Folder | What is in it | Built from |
|---|---|---|
| `1 Showcase/` | `Why AI-assisted development has not taken off.pdf` (the entry for a leader), `Real Tasks/` (one folder per real task: a deck and the task page saved as HTML), `Lessons/` | That deck: `source/start-here/`. The Real Tasks template: `source/showcase/`. Real tasks are company only, never committed |
| `2 Ask the Harness Guide/` | `Knowledge/`: the files of the M365 Copilot agent that answers questions about the harness (the agent reads this folder only) | `source/guide/` |
| `3 Courses/` | slidedoc PDFs: `Basic/`, `Advanced/` | exported from the smarshu.com repository (`npm run export:team`) |
| `4 Install the harness/` | the harness install package, the knowledge base, `programs/`, the guides | zips and installers are company only, never committed |
| `_Archive/` | earlier material kept for reference (the Deep Dive Task sample) | `source/deep-dive/` |

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
```

Every build needs Google Chrome and `playwright-core` from `~/Developer/smarshu.com`. Run from the repository root.

- **Harness Guide:** `python3 source/guide/build.py` (also needs pandoc). How it is written: `source/guide/RULES.md`. How to build the agent in M365 Copilot: `source/guide/AGENT.md`. The questions it is tested with, with their expected answers: `source/guide/questions.md`; never put this file where the agent can read it.
- **Why AI-assisted development has not taken off** (the leader deck): the PowerPoint `source/start-here/Why AI-assisted development has not taken off.pptx` is the one to edit. Once it is edited by hand it is the newer one: export its PDF from PowerPoint to `AI Exploration/1 Showcase/Why AI-assisted development has not taken off.pdf`, and do not run `source/start-here/build.py` over it (that script writes both files from `slides.py`).
- **Real Tasks template:** `.venv/bin/python source/showcase/build.py`.
- **Deep Dive (archived):** `python3 source/deep-dive/build.py 04-task`.

## Update the OneDrive folder

1. Build what changed and push.
2. On the company computer: pull, then copy `AI Exploration/` over the OneDrive folder. The company-only files in OneDrive (real tasks, zips, installers) are not in the repository, so a copy does not remove them.
