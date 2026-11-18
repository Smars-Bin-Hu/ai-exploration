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
  - `@ <id>`: an image from `source/video/catalog.md` (e.g. `board/state-busy-greyed`, `tutorials/1_day/lifecycle`, `basic-01/p03`).
  - `box=x,y,w,h`: a highlight box, in fractions of the image (0–1), drawn in the accent colour.
  - `crop=x,y,w,h`: show only this part of the image (same fractions), enlarged to fill the frame; use it to take just the figure off a page whose text the narration already says. `box=` keeps the whole image's fractions and is drawn if it falls inside the crop.
  - `text="..."`: a short caption under the image (a few words).
  - `@ card "Big words"`: a plain title card in the deck style, no image.
- A line starting with `//` is a note to the editor, not spoken, not shown.

## How changes stay small

- Each sentence's audio is cached under its text's hash. Change one sentence → only that clip is made again; the timeline after it shifts by itself.
- Each picture is cached under its `@` line. Change one `@` line → only that picture is made again.
- Nobody edits times by hand: a picture lasts from the start of its first sentence to the start of the next `@`'s sentence, plus a short pause between sentences.

## Outputs (not in git)

`/Users/smars/Developer/ai-exploration/.claude/loops/video-out/<video>/`: `audio/` (one file per sentence), `frames/` (one PNG per `@`), `<video>.fcpxml` (opens in Final Cut Pro), `<video>-rough.mp4` (a quick preview).
