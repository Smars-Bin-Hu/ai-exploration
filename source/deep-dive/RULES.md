# Writing a Deep Dive topic

One topic = one PDF of 16:9 pages. Readers are senior engineers and architects. They know distributed systems, databases and CI. They may not know LLM agents. They will doubt the harness and look for mistakes. After reading, they must be able to draw the architecture of the topic without opening the code.

## Sources

- **The only source of facts is the harness code at the pinned tag** (`harness_tag` in `pages.md`, now `1.7.41`), in `~/Developer/DE-agentic-harness`. Read files with `git -C ~/Developer/DE-agentic-harness show 1.7.41:<path>`, or `git worktree add` a read-only checkout of the tag. Code, tests, contracts, policies, agent and skill files and `registry.json` all count as code. The git history (`git log`, removed files, reverted designs) is the source for lessons.
- **Do not use existing prose as a source**: the harness `docs/*.md` and `README.md`, the book (`~/Developer/copilot-harness-engineering`), smarshu.com, and anything in `ai-exploration`. Understand the code yourself and write from that. `build.py` rejects any run of 8 words shared with them.
- Screenshots are allowed: `git -C ~/Developer/DE-agentic-harness show 1.7.41:docs/images/<name>.png > img/<name>.png`. If a screenshot you need does not exist, write it into `NOTES.md` under "Screenshots wanted": what the screen shows and why.
- Never invent. If the code does not show it, do not say it. If you are unsure, say what the code does and leave the why out.

## Structure: no cover, no titles

No cover page and no page titles: they take space and say nothing. A page is a figure and a few sentences. **The first sentence of each page states its point** (a claim the page proves: "A task outlives the session that started it."), the rest says what to see in the figure and why it matters. The topic name and page number are in the footer.

Readers are busy. Most will read the first pages and stop. So a topic has two parts, and the first part must be enough on its own.

**Part 1 — The pattern (2–3 pages, `part: pattern`).** The design as a whole, so that someone who stops here can explain it to a colleague. Simple diagrams: 4–7 boxes, plain names, no file paths on the boxes, no field names. One idea per page:
1. The problem and the idea that solves it, in one picture.
2. The design: the parts and how they work together (the whole lifecycle or flow at a glance).
3. (Optional) The one guarantee that matters most, and what enforces it.

**Part 2 — In depth (4–9 pages, `part: depth`).** For the reader who wants to check it. Each page zooms into one box of the pattern: the detailed diagram with code locations on the boxes (the code map style), the states and transitions, the files. Then:
- **Design decisions**: the alternatives, which was taken, the trade-off. Rejected designs from the git history go here, with what broke.
- **Limits**: what the design does not cover, failure modes, open problems.
- **Code map**: component → path, one line each (layout `text`), last page.

Each depth page should say which part of the pattern it opens up, so the reader always knows where they are. Keep each depth page to one mechanism; split a page rather than crowd it.

## Style

- **Few words.** At most 120 words per page outside figures (checked). The figure carries the content.
- **Academic register.** Precise, declarative, neutral. Define each term at first use. Name things by their real names (file, state, field, agent), not by metaphors. No press-release words (checked: see `BANNED` in `check.py`), no hype, no "simply", no rhetorical questions, no exclamation marks.
- **Absolute words must hold without exception.** "only", "every", "never", "cannot", "all", "the guarantee": check each against every code path, the terminal as well as the edit tools, a session that holds no task, the board as well as the CLI. When one does not hold, scope it ("for the session that holds the task", "the edit tools") and put the exception in Limits. In the Task sample, most fact-check findings across three rounds were absolute words that did not hold.
- **No code.** Give the location, not the code. An inline name in backticks (`state.json`, `advance()`) is fine; a code block is rejected.
- **Every statement about how the harness works carries a source**: `{src:path}` or `{src:path#L10-L40}`. It renders as a footnote with a link to GitHub at the tag. Every `split` and `figure` page needs at least one (checked); paths and line ranges must exist at the tag (checked).

## `pages.md` format

```
---
title: <topic name, for the PDF metadata>
number: 04
short: <topic name for the footer>
series: Harness Deep Dive
file: <PDF file name, no extension>
harness_tag: 1.7.41
---
=== figure           (the figure takes the page; one or two sentences under it)
part: pattern        (or depth; shown in the footer)
fig: fig/<name>.svg  (or img/<name>.png for a screenshot)
caption: <one line: what the figure shows>

<body: paragraphs, "- " lists, **bold**, `name`, {src:path#L1-L9}>

=== split            (text left, figure right)
=== text             (two columns of text, no figure: code map, open questions)
```

There is no `cover` layout and no `title:` or `kicker:` on a page (checked).

## Figures

Hand-written SVG in `fig/`. Diagrams are the main content: make them exact and readable.

- Size the `viewBox` to the slot: `split` figure ≈ 1050 × 910; `figure` layout ≈ 1800 × 740.
- Font Arial; at least 16 px at those sizes for labels, 13 px Menlo for code paths. Text must not touch borders.
- Colours: ink `#141414`, muted `#6b6b6b`, rule `#d6d6d2`, wash `#f2f1ec`, accent `#e8590c` (only for the thing the page is about).
- A component: rectangle, `rx=6`, wash fill, ink stroke 1.5; its code path in Menlo, muted, under its name. The focus of the page: accent stroke 2.5.
- Data flow: solid arrow. Control (who calls whom, who decides): dashed arrow. Say which in the caption or a small legend.
- A state machine: states as rounded boxes, transitions labelled with the event and the code that fires it.
- People: the role in a plain box with a bold label ("Person"), never an icon.

## Done

- `python3 source/deep-dive/build.py <id>` passes every check.
- Open every `_pages/pNN.png` and look at it: nothing cut off, nothing overlapping, labels readable.
- `NOTES.md` lists every claim with the file and lines that prove it, so a reviewer can check them; then the screenshots wanted, if any.
