# AI Exploration

The source of the company SharePoint folder "AI Exploration". Two parts:

- **`AI Exploration/`** is what people read. Only two folders in it are in git: `2 Ask the Harness Guide/` and `3 Courses/`. The other three items are made and edited on the company computer and are never committed (see below).
- **`source/`** is how it is built: sources, build scripts, the Guide's questions and rules. Never copied to SharePoint.

## What people find in `AI Exploration/`

| Folder | What is in it | Built from |
|---|---|---|
| `0 MUST READ.pdf` | the one page map of the folder, one colour per group: what to read, what to ask M365 Copilot, what not to open. Sorts first. Other files do not draw their own map; they point here. **Company computer only** | Template: `source/must-read/` |
| `1 Showcase/` | `Why AI-assisted development has not taken off.pdf` (the entry for a leader), `Real Tasks/` (one folder per real task: a picture book and the task page saved as HTML). **Company computer only** | The deck: `source/start-here/`. The Real Tasks template and a sample with fake data: `source/showcase/template/` |
| `2 Ask the Harness Guide/` | `Knowledge/pdf/`: the knowledge of the M365 Copilot agent that helps people understand the harness, PDF only (the agent reads this folder only) | `source/guide/` |
| `3 Courses/` | Videos, one topic each, in `Basic/`, `Advanced/`, `Harness tutorials/` and `Lessons/` (wrong turns while building the harness); `Course list.pdf` shows what is out and what is planned | Videos: `source/video/` (pipeline) and `source/courses/<video>/` (scripts). Course list: `source/courses/course-list/` (`node source/courses/course-list/build.cjs`). The old tutorial decks are kept as reference in `source/tutorials/` |
| `4 Install the harness/` | the install guide, the install package, the knowledge base, `programs/`. **Company computer only**; zips and installers never leave it | The guide: `source/install/` |

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
```

Every build needs Google Chrome and `playwright-core` from `~/Developer/smarshu.com`. Run from the repository root.

- **0 MUST READ** (the folder's map): the PowerPoint `source/must-read/0 MUST READ.pptx` is the one to edit (text boxes and pictures; right-click a picture > Change Picture). Export its PDF from PowerPoint to `AI Exploration/0 MUST READ.pdf` (git ignores it). `.venv/bin/python source/must-read/build.py` writes both files from its own layout, so run it only to start over: it overwrites hand edits. It checks that the page is one A4 page and that every folder it names exists. The pictures are in `source/must-read/img/` (`thumbs.py` makes them).
- **Harness Guide:** `python3 source/guide/build.py` (also needs pandoc). How it is written: `source/guide/RULES.md`. How to build the agent in M365 Copilot: `source/guide/AGENT.md`. The questions it is tested with, with their expected answers: `source/guide/questions.md`; never put this file where the agent can read it.
- **Why AI-assisted development has not taken off** (the leader deck): the PowerPoint `source/start-here/Why AI-assisted development has not taken off.pptx` is the one to edit. Once it is edited by hand it is the newer one: export its PDF from PowerPoint to `AI Exploration/1 Showcase/Why AI-assisted development has not taken off.pdf`, and do not run `source/start-here/build.py` over it (that script writes both files from `slides.py`).
- **Real Tasks template** (the `.pptx` and a sample, in `source/showcase/template/`): `.venv/bin/python source/showcase/build.py`.
- **Deep Dive (retired, no longer published):** `python3 source/deep-dive/build.py 04-task`.

## Publish to SharePoint (company computer)

The company computer has the clone, and a folder that SharePoint syncs. `tools/publish.ps1` copies from the first to the second. Edit in the clone, publish when it is ready: nobody sees half-done work.

| Item | Where it comes from | How it reaches SharePoint |
|---|---|---|
| `2 Ask the Harness Guide/`, `3 Courses/` | git (built at home, pushed, pulled here) | mirrored: the destination becomes identical, and files that only it has are deleted |
| `0 MUST READ.pdf`, `1 Showcase/`, `4 Install the harness/` | made and edited in the clone, git ignores them | copied: nothing is deleted at the destination; a file that is newer there is left alone |

Nothing else at the destination is touched. The path of the synced folder is not in this repository (it is public): the first run asks for it and keeps it in `%USERPROFILE%\.ai-exploration-publish.json`.

```powershell
.\tools\publish.ps1                 # preview: lists what would be copied and deleted, changes nothing
.\tools\publish.ps1 -Pull -Apply    # git pull --ff-only, then really publish
```

- `-Apply` is needed for anything to change. It asks "copy to ...?", and asks again if files will be deleted.
- `-Mirror` also deletes, in the three made-here items, files that are no longer in the clone.
- A file open in PowerPoint or Acrobat cannot be copied: the script says so at the end. Close it and run again.
- Do not run `git clean -x` in the clone: it deletes the ignored files.
- The Real Task template and a sample are in `source/showcase/template/`.

### Once, when moving to this way of working

Until now `0 MUST READ.pdf`, `1 Showcase/` and `4 Install the harness/` were in git. The first pull that stops tracking them would delete them from the clone, so save them first. In PowerShell, in the clone:

```powershell
$keep = "$env:USERPROFILE\ai-exploration-keep"
New-Item -ItemType Directory $keep -Force | Out-Null
Copy-Item "AI Exploration\0 MUST READ.pdf", "AI Exploration\1 Showcase", "AI Exploration\4 Install the harness" $keep -Recurse
git restore "AI Exploration"     # drop edits to tracked files, or the pull refuses
git pull
Copy-Item "$keep\*" "AI Exploration\" -Recurse -Force
git status                       # clean: git now ignores those three
.\tools\publish.ps1             # preview, and check the list
```

Delete `_Archive/` in the SharePoint folder by hand once: the script never deletes at the top level.

## Home

1. Build what changed, commit, push (`2 Ask the Harness Guide/` and `3 Courses/` are what the company computer pulls).
2. A build may still write the other three items into `AI Exploration/` on this machine; git ignores them.
