# Video script format

One video = one folder `source/courses/<video>/`:

| File | Who writes it | What |
| --- | --- | --- |
| `outline.md` | the person | the skeleton |
| `zh.md` | the person | the Chinese script, by scene (`## 0 Hook` …) |
| `en.md` | AI, the person approves | the English script, same scenes |
| `scenes.md` | AI, the person approves | `en.md` cut into sentences, with the pictures |

## scenes.md

```
# Basic 01 · Stop using AI the 2024 way

## 0 Hook
@ basic-01/p03
Suppose you want to build a feature with AI today.
What do you do?
@ board/one-05-requirement box=0.08,0.30,0.60,0.25 text="Confirm requirement"
First you hunt down the code files you think matter, and paste them in.

## 1 Pain points
@ card "Pain 1 · It doesn't know your project"
...
```

- `# ...` is the video title. `## ...` starts a scene; the title is not spoken.
- **Every other non-empty line is one spoken sentence = one audio clip.** Keep it to one or two short sentences, the length a person says in one breath.
- **A line starting with `@` is a picture.** It appears when the next sentence starts and stays until the next `@`. This is the beat (the `[>]` of the script).
  One `@` line is one picture, written on one line. Words with spaces go in double quotes; options are `name=value`.

  **An image** (a screenshot or a page), shown as a white card with rounded corners on the dark background:
  - `@ <id>`: an image from `source/video/catalog.md` (e.g. `board/state-busy-greyed`, `tutorials/1_day/lifecycle`), or a path to a .png.
  - `box=x,y,w,h`: a highlight box, in fractions of the image (0–1), drawn in teal.
  - `crop=x,y,w,h`: show only this part of the image (same fractions), enlarged to fill the frame. `box=` keeps the whole image's fractions and is drawn if it falls inside the crop.
  - `text="..."`: a short caption under the image (a few words).

  **A template**, drawn in code, no image:

  | Line | Shows |
  | --- | --- |
  | `@ card "Big words" kicker="Basic 01" icon=bot` | a title card; the small orange line above is `kicker=`, else the scene's title |
  | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Harness engineering" now=3` | steps on a line, `year\|label`; `now=` lights one in teal, the ones before it greyed, the ones after it faint |
  | `@ loop "LLM\|bot" "Tool" "Result" "Next step" lit=2` | boxes in a cycle, joined by arrows clockwise from the top; `lit=` lights one box and the arrow into it |
  | `@ formula "Agent" "Model" "Harness"` | big words: `Agent = Model + Harness`; the last term in teal, or `lit=N` |
  | `@ list "Title" "item 1\|icon" "item 2" ... lit=3` | a numbered list; with `lit=` only items 1..lit show, the last one in teal, so one list builds up over sentences (`lit=1`, `lit=2`, ...) without moving; more than 5 items go in two columns |
  | `@ big "5" "chats at most, before you are the bottleneck" icon=messages-square` | a big teal number (or short word) and one line under it |
  | `@ quote "..." by="..."` | a pull quote |
  | `@ logos github-copilot claude-code codex` | official logos in a row, from `.claude/loops/assets/logos/` (`<name>.svg`, else its `-white`, `-ivory`, `-lockup-white` file); `name\|Label` sets the label; a missing logo is a dashed box with the name |

  - Icons are [Lucide](https://lucide.dev/icons) names (ISC licence), from `.claude/loops/assets/lucide/node_modules/lucide-static/icons/`, drawn in the colour of the text around them: `icon=<name>` on `card` and `big`, `"text|<name>"` on a `list` or `loop` item.

  **A figure**, drawn for the script by hand:
  - `@ fig <name> step=N`: the page `source/courses/<video>/figs/<name>.html` (for a scenes file `x.md`, `x-figs/<name>.html` next to it if that folder exists), shot at 1920×1080.
  - The page is plain HTML/SVG and links `figs.css` (from `source/courses/<video>/figs/`: `../../../video/figs.css`), which gives the look: the background, Source Serif 4, the colours as `var(--fg)`, `var(--muted)`, `var(--teal)`, `var(--orange)`, and parts to use: `.stage` (the area clear of subtitles and avatar), `.kicker`, `.title`, `.caption`, `.pill` (a box; `.pill.warn` dashed orange), `.arrow`, `.tag`.
  - `<i data-icon="hammer"></i>` puts a Lucide icon there; `<img data-logo="claude-code">` puts a logo there.
  - Steps: an element with `data-step="k"` is hidden while k > N (it keeps its place), lit in teal when k = N (class `lit`), and plain when k < N (class `done`). From step N on, the page also has the classes `at-1` … `at-N`, so `.at-5 .plan { ... }` changes `.plan` from step 5 on (e.g. to show it was skipped). Without `step=`, nothing is hidden.
  - Example: `source/video/samples-figs/process.html` (five steps, `plan` skipped at step 5).

  Every frame gets the person's round picture bottom right (`--avatar`; default `.claude/loops/voice/avatar.jpg` or `.png`, else the smarshu.com portrait). The look is in `source/video/figs.css`; `--theme navy` uses smarshu.com's navy background instead of the grey. To see every kind of picture without making audio: `.venv/bin/python source/video/build.py samples --scenes source/video/samples.md --frames-only` (pictures land in `.claude/loops/video-out/samples/`).
- A line starting with `//` is a note to the editor, not spoken, not shown.

## How changes stay small

- Each sentence's audio is cached under its text's hash. Change one sentence → only that clip is made again; the timeline after it shifts by itself.
- Each picture is cached under its `@` line, the image's date, `figs.css`, the figure's HTML, the avatar and the theme. Change one `@` line or one figure → only those pictures are made again; change `figs.css` → all of them (about 0.1 s each, in one browser).
- Nobody edits times by hand: a picture lasts from the start of its first sentence to the start of the next `@`'s sentence, plus a short pause between sentences.

## Outputs (not in git)

`/Users/smars/Developer/ai-exploration/.claude/loops/video-out/<video>/`: `audio/` (one file per sentence), `frames/` (one PNG per `@`), `<video>.fcpxml` (opens in Final Cut Pro), `<video>-rough.mp4` (a quick preview).
