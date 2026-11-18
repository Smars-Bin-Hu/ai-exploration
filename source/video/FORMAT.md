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
- **Every other non-empty line is spoken.** A line may be a whole sentence or a piece of one (cut at a comma so a new picture can come in on that word). Lines are joined into sentences until a line ends with `.`, `?` or `!` (or the paragraph or scene ends). Where a picture changes inside a sentence, it lands on the word its line starts with (word times from mlx-whisper, see below).
- **A blank line between spoken lines is a paragraph break.** Spoken lines with no blank line between them are one paragraph, whatever `@` lines sit between them; a scene heading also ends a paragraph. Mark paragraphs as the text runs (one paragraph of `en.md` = one paragraph here): **one paragraph = one audio clip**, spoken in one go, so each sentence is said knowing the ones around it ("Most of the time it listens. But every so often…" flows on, instead of "But" starting cold), and the voice keeps its own pauses between its sentences (the default voice makes each at least 0.3 s, `tts/README.md` round 6). The blank line may go before or after the `@` line that opens the paragraph. A paragraph that would run over `--para-max` (20 s of speech) is spoken in runs of whole sentences of about equal length. A line on its own as a paragraph is fine (a question set apart, a one-line beat).
- **A line starting with `@` is a picture.** It fades in just before the next line's first word and stays until the next `@`. This is the beat (the `[>]` of the script).
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

  **The speaking avatar.** The person's round picture sits bottom right (`--avatar`; default `.claude/loops/voice/avatar.jpg` or `.png`, else the smarshu.com portrait). It is not drawn into the stills but is its own small video over them (`source/video/avatar.py`): still, with its thin teal ring, while nobody speaks; while the narration speaks, a soft teal glow whose brightness and width follow the voice's loudness frame by frame, and a faint ring that ripples outward at each sentence start and loudness peak. It is made from the timeline's audio and made again only when a clip or its time changes. `--avatar-static` draws the plain picture into each still instead (the old way), `--avatar none` leaves it out; `--frames-only` draws it into the stills so they can be looked at. The look is in `source/video/figs.css`; `--theme navy` uses smarshu.com's navy background instead of the grey. To see every kind of picture without making audio: `.venv/bin/python source/video/build.py samples --scenes source/video/samples.md --frames-only` (pictures land in `.claude/loops/video-out/samples/`).
- A line starting with `//` is a note to the editor, not spoken, not shown.

## How changes stay small

- Each paragraph's audio is cached under its text's hash (and the voice settings). Change one sentence → only its paragraph is spoken again; the timeline after it shifts by itself. The clip is then cut into one piece per sentence, at the quietest point between the last word of one sentence and the first word of the next (word times from mlx-whisper; on a frame boundary, so the pieces back to back are the clip exactly). Each piece is one clip in the FCPXML.
- Each picture is cached under its `@` line, the image's date, `figs.css`, the figure's HTML, the avatar and the theme. Change one `@` line or one figure → only those pictures are made again; change `figs.css` → all of them (about 0.1 s each, in one browser).
- Each paragraph clip's word times are cached under the clip's own hash: change one sentence → one clip and one alignment are made again.
- Nobody edits times by hand. The timing rules (`source/video/timing.py`, each a flag of `build.py`):
  - inside a paragraph the timeline inserts nothing: the sentences keep the voice's own pauses, and a picture that changes there fades in on the word, `--lead` before it, with no dwell; between two runs of one long paragraph `--gap` 0.3 s;
  - `--para-gap` 0.5 s between paragraphs on the same picture;
  - when the picture changes at a paragraph break, the outgoing picture stays `--dwell` 0.8 s after the words end (`--busy` +0.4 s for a screenshot, a list of 4+ items, a quote or a figure with 30+ words), then the next one fades in; `--scene-gap` 1.4 s of silence between scenes (at least dwell + lead);
  - a new picture starts fading in `--lead` 0.3 s before its first word;
  - a picture holds at least `--min-hold` 2.2 s; a shorter beat is merged (a later step of the same figure or list shows from the short one's start; otherwise the short picture is skipped and the one before stays). The build lists every merge. Words are never moved or cut;
  - cross-dissolves: `--xfade` 0.5 s between different pictures, `--step-xfade` 0.35 s between steps of one `@ fig` or one `@ list` (so the newly lit parts fade in). In the FCPXML they are real Cross Dissolve transitions on the primary storyline; in the rough mp4, ffmpeg `xfade`.
- Word times: `mlx-whisper` (MIT) in its own venv, `.claude/loops/tts/whisper/venv` (`python3 -m venv .claude/loops/tts/whisper/venv && .claude/loops/tts/whisper/venv/bin/pip install mlx-whisper`), model `mlx-community/whisper-large-v3-turbo`. The known script words are matched to what it heard; a word it missed is placed by character count between its neighbours, and a sentence with under half its words matched (or no venv) is timed by character count. The build says how often.

## Outputs (not in git)

`.claude/loops/video-out/<video>/` (in this repository; `--out` for another root): `audio/` (one file per paragraph as made, as normalised and cut into its sentences; `align/` the word times), `frames/` (one PNG per `@`), `segments/` (the rough mp4's pieces: a still held, or a dissolve), `<video>.fcpxml` (opens in Final Cut Pro), `<video>-rough.mp4` (a quick preview).

## Checks before any voice is made

Run `python3 source/video/lint_script.py <video>` after the English script is cut into scenes, and again after every edit. Each flag is either fixed in the script or kept on purpose (say why in a `//` line next to it):

- **split-thought** — a sentence starting with But / So / Because / Though / Which… right after another sentence in the same paragraph: one thought cut in two, which TTS reads as two unrelated sentences. Join with a comma.
- **short-alone** — a sentence under five words between two others: sounds clipped; join it to a neighbour.
- **no-paragraphs / paragraphs** — no blank lines in a long scene, or far fewer paragraphs than the Chinese: nowhere to pause. Blank line = paragraph = where the voice pauses and the picture may rest.
- **question** — a question without "?", or a "?" on a statement: the voice will not rise.

The cold read (`ref/coldread-brief.md` in the loop folder) checks the same by ear; this script catches what it misses.
