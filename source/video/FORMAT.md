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
  - a picture holds at least `--min-hold` 2.2 s before a different picture comes; a step of one `@ fig` (or one `list`, `loop`, `timeline` or `formula` with another `lit=`/`now=`) only `--step-min-hold` 1.0 s before its next step, so each step stays on its own words. A shorter beat is merged: the short picture is skipped and the one before stays (a later step never shows early); only the first picture of a scene is replaced by the next one instead. The build lists every merge. Words are never moved or cut;
  - cross-dissolves: `--xfade` 0.5 s between different pictures, `--step-xfade` 0.35 s between steps of one `@ fig` or one `@ list` (so the newly lit parts fade in). In the FCPXML they are real Cross Dissolve transitions on the primary storyline; in the rough mp4, ffmpeg `xfade`.
- Word times: `mlx-whisper` (MIT) in its own venv, `.claude/loops/tts/whisper/venv` (`python3 -m venv .claude/loops/tts/whisper/venv && .claude/loops/tts/whisper/venv/bin/pip install mlx-whisper`), model `mlx-community/whisper-large-v3-turbo`. The known script words are matched to what it heard; a word it missed is placed by character count between its neighbours, and a sentence with under half its words matched (or no venv) is timed by character count. The build says how often.

## Recorded voice

The author can read the script instead of a synthetic voice: `--voice rec`. One take per sentence, the build does the rest as before (loudness, word times, cutting, timeline, subtitles, avatar).

- **Sentences and ids.** `.venv/bin/python source/video/build.py <video> --list-sentences` prints the sentences as JSON, nothing else: `[{"id": "97d6c35d9481", "scene": "0 Hook", "para": 0, "n": 0, "text": "It's 2026, and a lot of teams …"}]`. A sentence is the build's sentence (lines joined until `.` `?` `!`, or the paragraph or scene ends); `para` and `n` count from 0 over the whole video; `id` is the first 12 hex of the sha1 of the text (UTF-8, whitespace collapsed). Change a sentence and it gets a new id, so it needs a new take; a sentence said twice in a video shares one take.
- **Takes.** `.claude/loops/voice/rec/<video>/<id>.wav` is the current take (any rate or channels); `<id>.take<N>.wav` are older takes, never used. `--rec-dir` points somewhere else (tests). `--rec-status` prints per scene how many sentences have a take and which do not.
- **Missing takes** stop the build with the list (scene, sentence, id, text). `--rec-missing tts` speaks them with the default voice (`tts:kokoro-seedvc`; or any `--voice` value) so a partly recorded video can be watched; the report lists them as filled.
- **Checking a take.** `build.py <video> --check-take <id>` (the recording pane calls it after each take) prints `{"id", "ok", "heard", "missing", "extra", "cut": [{"start", "end", "why"}], "seconds"}`: one Whisper pass on the take as recorded (no denoise, about 4 s), what it heard, the words of the sentence it did not hear and the words it heard that are not in it (after the cuts below; `ok` is true when both are empty, null without Whisper), the stretches the build will cut (seconds in the take; `why` is `filler`, `repeat`, `restart` or `pause`), and the voice's length after them. The words are cached under the take's hash, so the build does not hear it again. A take with `ok` false is still used; the build lists it under `check`.
- **The polish**, each take on its own, cached under its hash (`source/video/rec.py` has the steps, `build.py` the settings):
  1. Whisper word times with fillers kept: the prompt is itself disfluent ("Umm, so, uh, I- I mean, the the thing is…") followed by the sentence's words as a list. The clean sentence as prompt made Whisper drop a false start.
  2. Cuts: fillers (um, uh, er, hmm …, unless the script has them), the first copy of a word or words said twice (an unfinished last word counts: "fi- find"), and a false start: everything before the last place a complete attempt starts (80% of the sentence's words). Each cut is at the quietest point within 0.1 s of the Whisper word edges (they can be that far off), keeping up to 0.35 s of the pause around it, joined with a 10 ms crossfade.
  3. Denoise: DeepFilterNet 3 (MIT/Apache-2.0), at most 12 dB off (`source/video/denoise.py`, its venv `.claude/loops/tts/deepfilter/venv`); without that venv, or `--rec-denoise afftdn`, ffmpeg `afftdn=nr=8:nf=-55:tn=1`. Measured on a say-made take with room tone added: DeepFilterNet took 5 to 10 dB off the room tone and changed the voice by 0.1 to 0.2 dB in every band from 80 Hz to 16 kHz; afftdn took 3 to 5 dB off and left the voice as it was (at nr=20 the room tone warbles).
  4. Dynamics: 80 Hz high-pass; the take set to −20 LUFS, so takes from different days match; a gentle compressor (2:1 above −18 dB, 6 dB knee, only the loud words); a de-esser (`deesser=i=0.4`) that takes back the s the compressor brings forward. Measured: each band within −0.1 to +1.1 dB of the take.
  5. A pause inside the sentence longer than 0.5 s is cut to 0.35 s.
  6. Cut to the voice, 80 ms before and 150 ms after it. The voice is found from its voiced core (loud 10 ms frames with few sign changes, in runs of 50 ms or more), so a click or a breath before or after it is left out; from the core it reaches 0.2 s back and 0.3 s on over quieter sound (a first s, a last t after its closure).
  7. Room tone: the take's quietest stretches (100 ms or more), up to 2 s, kept next to the piece.
- **Joining.** A paragraph's pieces are joined with `--rec-gap` 0.35 s from the end of one sentence's voice to the start of the next one's; what their own 80 ms and 150 ms do not cover is the take's room tone, crossfaded, not digital silence. The joined clip is one paragraph clip (a paragraph is never split by `--para-max`) and goes on like a spoken one: set to −18 LUFS, word times, cut into sentences.
- **What is made again.** A paragraph clip's key is the hashes of its pieces, so a new take polishes one take and makes one paragraph clip, one loudness pass and one alignment again; the rest is reused. Changing a polish setting polishes every take again.

### Talk: a scene in the author's own words

The author does not have to read the script. They look at a scene (a module, one `## ` heading) and talk it through in their own words, naturally, with light fillers ("like", "so", "you know"), other wording than the script's, the points roughly in its order. One take per scene; the build cuts it back into paragraphs. A paragraph can be recorded again on its own (a punch-in), which replaces that paragraph's part of the scene take. As soon as the take folder has any scene or paragraph take, `--voice rec` uses these instead of sentence takes. The text work is in `source/video/talk.py`.

- **Paragraphs, points and ids.** `build.py <video> --list-paragraphs` prints JSON, nothing else: `[{"id", "sid", "scene", "para", "text", "lines": [{"k", "text", "beat", "bold"}]}]`. A paragraph is the lines between blank lines (as above); each spoken line is a **point**; `beat` is true when an `@` line comes before it (a picture changes there). `id` is the first 12 hex of the sha1 of the paragraph's lines joined by single spaces (whitespace collapsed), `sid` the same of the scene's lines; `para` counts from 0 over the video. `bold` are the point's key phrases, the words a speaker must not lose (nouns, numbers, product names, the contrast word), from `source/courses/<video>/bold.json` (`{"<line text>": ["phrase", …]}`, each an exact part of the line; written by the AI from the script; a line not in it has `[]`). They weigh double when the build looks for a point.
- **Takes.** `.claude/loops/voice/rec/<video>/scene/<sid>.wav` is a scene's current take, `para/<id>.wav` a punch-in; `<…>.take<N>.wav` are older takes, never used. A punch-in is used only while it is newer (file time) than its scene's take: a scene recorded again after it wins. `--rec-status` prints per scene whether it is recorded, its punch-ins (a stale one as "older than the scene take, unused") and, for a scene with no take, its paragraphs.
- **Checking a take.** `build.py <video> --check-scene <sid>` prints `{"sid", "ok", "heard", "paras": [{"id", "para", "t0", "t1", "points": [{"k", "said", "t"}], "order_ok", "missing"}], "fillers", "seconds"}` and writes it to `<sid>.check.json` next to the take; `--check-para <id>` the same for a punch-in, flat: `{"id", "ok", "heard", "points", "order_ok", "missing", "fillers", "seconds"}`. One Whisper pass on the take as recorded (in windows, as below; cached by the take's hash, so the build does not hear it again): 11 s for a 77 s scene take, the model's loading included, then about 1 s from the cache. `heard` is the transcript with fillers kept; times are seconds in the take as recorded; `t0`, `t1` where the paragraph's points were said (null if none was); `fillers` counts um, uh, er, hmm; `seconds` is the voice's length after the polish's cuts and pauses. `said` is true when the point's content words were found, in order, `missing` lists the points that were not found at all, `order_ok` is false when a point was found only out of order; `ok` is true when every point was said in order (null without Whisper).
- **Finding the points.** No language model: the script's content words (not function words; numbers as digits; a few irregular verbs; rough stems: -s, -ed, -ing, -ly off) are aligned to what was heard in one monotonic pass (a weighted longest common subsequence; a match scores 1 for the same stem, 0.9 for a close synonym from a short list in `talk.py`, 0.8 when one stem starts the other, 0.7 for nearly the same letters). Words that more than one point of the scene has weigh less; key phrases double. A point is said where the densest run of its matched words (at most 12 words apart) carries half its weight; it starts at the run's first word, or up to three function words before it ("and lots of …"). A point not found in order is looked for anywhere, in a window about three times its length, at 60% of its weight. A point made only of function words ("What do you do?") is matched on those. Measured on `say`-made takes (two scene takes paraphrasing six paragraphs with likes, ums, a restart, a stutter and long pauses, one point left out on purpose, and a punch-in): every point said was found and the one left out reported missing, nothing found that was not said; in the built video, Whisper on the final audio put 24 of 27 picture changes within 0.3 s of the first word of their paraphrased clause (median 0.04 s); the worst, 0.96 s late, was "It. Like. Forget stuff", where `say`'s full stops kept the point from starting at "it".
- **The polish** of a talk take, the whole take at once, cached under its hash:
  1. Whisper with fillers kept, in windows of at most 25 s cut at the quietest moment (Whisper keeps its prompt only for its first 30 s), each with the prompt: the script's content words (names first), then a disfluent sample at the end ("Umm, so, like, uh, I- I mean, the the thing is, you know..."), which survives when Whisper trims a long prompt from the front.
  2. Cut: fillers (um, uh, er, hmm, ah, mm); stutters (a word said twice, or a cut-off fragment and the word: "fi- find"; the first copy goes); restarts (a false start, then its first two or more words again: "the business side, the business team" keeps "the business team"). Not cut: words the script has that way, and a repeat that closes a list item the first time ("find the code, paste the code"). Kept: like, so, you know, right, I mean. Each cut at the quietest point near the word edges, as for sentence takes.
  3. Denoise, de-plosive, high-pass, level, compression, de-ess: as for sentence takes.
  4. A pause over 0.8 s is cut to 0.4 s, inside a paragraph and between paragraphs alike.
  5. Cut to the voice, room tone kept, as for sentence takes.
  6. Flagged, not cut: "like" more than once in 8 words (beyond the script's own). The build lists it.
- **Into paragraphs.** The scene's points are found over the polished take's words (moved through the cuts, so no second Whisper pass). Between two paragraphs the cut is at the longest pause between the last point of one and the first point of the next (a sentence end counts 0.3 s extra), at its quietest 10 ms. A run of paragraphs from one scene take is one clip: they stay back to back in the timeline, with the author's own (shortened) pause between them, not `--para-gap` or `--dwell`; the clip is cut into one piece per paragraph at those pauses. A punch-in, or a paragraph filled in, is its own clip, with the usual gaps around it.
- **Pictures.** A picture lands where its point was said: its line starts at the point's first word (the fade `--lead` before it). A point not found is placed by letter count between the points either side of it, and the build lists it. Min-hold, merges, transitions, avatar and loudness as for any clip.
- **Subtitles** are what was said, not the script: the words kept (um and uh cut, "like" and "so" kept), cut at clause breaks and at pauses over 0.6 s, the clauses packed into cues of at most two rows of 42 letters, a new cue after a sentence end once a cue has 25 letters, each from its first word to 0.5 s after its last (at least 0.8 s). A paragraph filled in has the script's lines. `--subs` in another language still reads one line per script line, timed by where the points were said.
- **spoken.md.** Every build with talk takes writes `spoken.md` next to the scenes file: per scene (`## `) and paragraph, what was said, cleaned as the subtitles show it; a paragraph not recorded yet has the script under a `// not recorded yet` line. The author edits from it next time (it is the English as spoken).
- **Missing paragraphs.** A paragraph in no scene take (its scene not recorded, or none of its points heard in it) and with no punch-in stops the build with the list, unless `--rec-missing tts`, which speaks the script paragraph with the default voice (or any `--voice` value) as its own clip, timed by its words like a made voice; the report lists it.

## Outputs (not in git)

`.claude/loops/video-out/<video>/` (in this repository; `--out` for another root): `audio/` (one file per paragraph as made, as normalised and cut into its sentences; `align/` the word times; `rec/` the polished takes, their room tone, `takes.json` what was cut and heard, `words/` Whisper's words per take), `frames/` (one PNG per `@`), `segments/` (the rough mp4's pieces: a still held, or a dissolve), `<video>.fcpxml` (opens in Final Cut Pro), `<video>-rough.mp4` (a quick preview).

## Checks before any voice is made

Run `python3 source/video/lint_script.py <video>` after the English script is cut into scenes, and again after every edit. Each flag is either fixed in the script or kept on purpose (say why in a `//` line next to it):

- **split-thought** — a sentence starting with But / So / Because / Though / Which… right after another sentence in the same paragraph: one thought cut in two, which TTS reads as two unrelated sentences. Join with a comma.
- **short-alone** — a sentence under five words between two others: sounds clipped; join it to a neighbour.
- **no-paragraphs / paragraphs** — no blank lines in a long scene, or far fewer paragraphs than the Chinese: nowhere to pause. Blank line = paragraph = where the voice pauses and the picture may rest.
- **question** — a question without "?", or a "?" on a statement: the voice will not rise.

The cold read (`ref/coldread-brief.md` in the loop folder) checks the same by ear; this script catches what it misses.
