# Voice-cloned narration, locally

Each spoken paragraph of a video becomes one audio file (cut into its sentences afterwards, see `../FORMAT.md`), in the presenter's own voice, made on an Apple Silicon Mac with no paid API. This folder holds a small wrapper, `say.py`, that calls one of several open models, each installed in its own environment outside git.

Round 1 (below) chose for likeness to the presenter. Round 2 chose for natural English first and likeness second, because the round-1 winner sounded like the presenter but put odd melodies on some phrases. Round 3 makes the round-2 pick, `vibevoice`, clean and reliable: no background music, no runaway or wrong takes on short lines. Round 5 keeps Kokoro's native English and swaps OpenVoice for a stronger voice converter, Seed-VC, because `kokoro-openvoice` did not sound like the presenter. Round 6 makes questions sound like questions and lets Kokoro speak a whole paragraph at a time. The newest round comes first.

Tested November 2026 on an M1 Pro with 32 GB, macOS, Python 3.12.

## Round 6: questions that rise, and a paragraph per call

The presenter heard two things in the first full build: questions did not sound like questions, and the narration came out sentence by sentence, each one restarting flat ("Most of the time it listens." [a gap] "But every so often…"). The second is fixed in `build.py` (one call per paragraph, `../FORMAT.md`); the voice side of it is below. The first was measured.

### Where the rise is lost

Pitch by RMVPE (Seed-VC's own tracker), in semitones against the clip's median, over the last 0.25 s of voice; reference `ref-13s.wav`, `am_fenrir`, seed 1. A falling end reads about -6 to -10.

| Sentence | Kokoro alone | after Seed-VC v1 (as built) | after the f0 model, no bend |
| --- | --- | --- | --- |
| Is this how you use AI right now? | -6.3 | -5.3 | -10.0 |
| Do you use AI like this? | -8.3 | -4.5 | -8.1 |
| What do you do? | -8.5 | -5.3 | -10.6 |
| Which files did it change? | -8.3 | -6.5 | -7.2 |
| If a session dies, how does a new one pick up the task? | -7.2 | -6.0 | -6.9 |
| control: Is this how you use AI right now**.** | -7.2 | -5.3 | -8.5 |

So Kokoro itself says a question exactly like a statement: the yes/no question falls as far as the same words with a full stop. Seed-VC does not flatten a rise; there is none to keep (v1 even narrows the fall a little, as it re-makes the pitch). Kokoro's options do not help either (pYIN, `am_fenrir` unless named): `??` -5.1, `?!` -4.0, `…?` -5.4, a space before `?` -4.1, `, right now?` -4.5, a leading "So," -4.7, speed 0.9 or 1.1 -4.3; other voices `am_michael` -1.1, `am_onyx` -0.9, `af_heart` -1.0, `am_adam` -7.7, `bm_george` -11.0 (less fall, still no rise). Kokoro sees the `?` (its phonemes end in `?`), it just was not trained to rise on it.

### The fix: draw the rise into the pitch curve

Seed-VC has a second model, conditioned on pitch (`DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema_v2`, whisper-small content, 44 kHz BigVGAN, RMVPE for pitch; same GPL-3.0 code; about 1.2 GB more in the HF cache: model 0.4, BigVGAN 44 kHz 0.6, RMVPE 0.2). It follows the pitch curve it is given, moved to the reference's median (Seed-VC's "auto f0 adjust"). The backend (`f0=1`) takes Kokoro's own curve, finds each question from Kokoro's word timestamps, and over the question's last word (at least 0.35 s) bends the curve into a smooth rise up to `qrise` semitones above that question's median for a yes/no question, `whrise` for one with a question word (what, which, how, ...; "If a session dies, how does…?" counts as one, "So, is this…?" as yes/no). Pitch of the last 0.8 s, every 50 ms, after conversion:

```
Is this how you use AI right now?   no bend  ... -2.3 -4.0 -3.5 -2.6 -4.1 -6.8 -8.2   .  -12.4 -12.5
                                    6 / 3    ... -2.0 -4.4 -3.2 -4.1 -6.8 -3.9 -2.4 -0.2  +3.3  +5.6
Do you use AI like this?            no bend  ... -3.5 -4.3 -4.9 -6.2   .    .  -7.7 -9.2 -10.4
                                    6 / 3    ... -4.5 -5.0 -6.2 -6.7 -6.0 -6.2 -3.2 +1.6  +4.3
Which files did it change?          no bend  ... -3.7   .    .  -0.0 -3.7 -6.5 -7.3 -9.7  -9.4
                                    6 / 3    ... -3.8   .  -1.0 -1.1 -0.7 -0.0 +0.7 +1.6  +2.1
```

| `qrise` / `whrise` | yes/no questions: highest point at the end | question-word questions: end | WavLM likeness of the six question clips |
| --- | --- | --- | --- |
| 0 / 0 (no bend) | -2.4, -3.5 | -7.2 to -9.7 | 0.796 |
| 4 / 2 | +4.0, +1.8 | -0.3 to +0.8 | 0.818 |
| **6 / 3** (the preset) | **+5.6, +4.3** | **+0.1 to +0.3**, peaks +1.9 to +3.1 | 0.811 |
| 8 / 4 | +4.3, +5.9 | +0.3 to +0.7 | 0.840 |

The model follows the bend only partly (a rise of 6 semitones asked comes out at 4 to 6), and going past 6 / 3 gains little. Question-word questions now end level or slightly up instead of dropping 8 to 10 semitones into the floor; whether that is the right amount is for the ear (`--set whrise=0` keeps Kokoro's fall, `--set qrise=…` changes the yes/no rise). The bend costs no likeness (0.796 without, 0.81 to 0.84 with, the spread is noise on 1 to 3 s clips).

Likeness of the f0 model against v1, `measure2.py` on round 2's six sentences, each said alone: 0.833 against 0.836 overall; on the four long sentences the same (0.859 against 0.860); on short clips said alone it is weaker: "Two: it forgets." scores the same (0.709 against 0.701) but Whisper heard "Do what forgets.", and the six question clips (1 to 3 s) score 0.786 against 0.822. In a video every clip is now a whole paragraph, so the short-clip weakness hardly applies. Speed: 2.9 s of compute per second of audio over the test build's 11 paragraph clips (2.5 on the long ones, up to 5.8 on a 2 s one), against 2.1 to 2.4 for v1 on single sentences.

### A paragraph per call

`build.py` now sends one paragraph per call. Kokoro speaks it in one go, so each sentence is said knowing the ones around it. Its own pause between sentences is uneven, though: in "Five: you can't see what it actually did. Which files did it change? Which commands did it run? Why did it do it that way? …" the voice is quiet (under -50 dBFS) for 0.17, 0.01, 0.00 and 0.21 s at the four sentence ends, so the questions ran into each other, while "Most of the time it listens. But every so often…" gets 0.35 s. `pause=0.3` (in the preset) tops each sentence end up to 0.3 s of silence, put in at the quietest 10 ms of Kokoro's pause before Seed-VC (faded 10 ms either side, timestamps moved with it); a pause already 0.3 s or longer is left alone, and commas are never touched. `--set pause=0` gives Kokoro's own. Seed-VC's window holds 30 s of reference plus speech, so with the 13 s reference it converts at most about 16.5 s at once; a longer take is converted in pieces cut in the middle of a sentence-end pause (or else a comma pause) that Kokoro's timestamps give, each piece kept exactly as long as its source, and the peak limit applied once to the whole clip. `build.py` keeps a paragraph to about 20 s per call (`--para-max`), so Whisper's 30 s window and Kokoro's 510-phoneme limit are never reached.

`kokoro-seedvc` is now `am_fenrir`, 30 steps, `f0=1`, `qrise=6`, `whrise=3`, `pause=0.3`, at 44 kHz; `kokoro-seedvc-v1` is round 5's setting (v1 model, 22 kHz, no bend). The preset's settings are part of `build.py`'s cache key, so changing them makes the clips again. Measured with the scripts in `.claude/loops/voice/` and `source/video/tts/`; the clips are in the session's scratch folder, not kept.

## Round 5: Kokoro with a stronger voice converter (Seed-VC)

`kokoro-openvoice` had the most natural English of round 2 but "is not my voice": OpenVoice changes the timbre only a little (likeness 0.806, against 0.968 for the presenter's own speech). Seed-VC (Plachtaa, `Plachta/Seed-VC`) is a zero-shot converter that rebuilds the whole spectrogram with a diffusion transformer, conditioned on the reference clip; Kokoro still decides the words, rhythm and melody. Used here: the v1 offline speech model (`DiT_seed_v2_uvit_whisper_small_wavenet_bigvgan_pruned`, whisper-small content encoder, BigVGAN vocoder, 22 kHz), on the Apple GPU through MPS, fp16, 30 diffusion steps, `inference-cfg-rate` 0.7 (its defaults). **Licence: Seed-VC's code is GPL-3.0**, and its weights are best treated the same: fine for making our own narration internally, but its code must not be copied into anything we distribute. The audio it makes is not covered by the GPL. Whisper-small and BigVGAN are MIT.

Same six sentences, whole sentence per call, reference `ref-13s.wav`, measured with `measure2.py` as in round 2:

| Kokoro voice into Seed-VC | Likeness, mean (per sentence) | Real word errors in 84 words | Clipped samples |
| --- | --- | --- | --- |
| `am_michael` (as round 2) | 0.856 (0.89, 0.74, 0.91, 0.87, 0.84, 0.90) | 0 | 0 (47 before the peak limit below) |
| **`am_fenrir`** (the preset) | **0.868** (0.87, 0.82, 0.88, 0.91, 0.85, 0.88) | **0** | 0 |
| `am_eric` | 0.862 | 1: "CloudCode" | 0 |
| `am_adam` | 0.869 | 0 ("2. It forgets.") | 0 |
| `am_onyx` | **0.885** (0.90, 0.82, 0.90, 0.92, 0.89, 0.88) | 1: "Two" heard as "To" | 0 |
| `am_fenrir`, 50 steps | 0.866 | 0 | 0 |
| for comparison: `kokoro-openvoice` (round 2) | 0.806 (0.73 to 0.86) | 0 | 0 |

So Seed-VC closes about a third of the gap to the true cloners (`vibevoice` 0.948 after round 3, `qwen3` 0.946), with Kokoro's English kept: no new word errors with `am_fenrir`. The choice of Kokoro voice moves likeness by up to 0.03; a deeper voice (`am_onyx`) converts closest but once said "To" for "Two". 50 diffusion steps bring nothing over 30 at 1.6 times the compute. A longer reference was not tried: the measure holds out every part of the 62 s recording except the 13 s reference, so a longer cut would be judged partly against itself, and Seed-VC's 30 s window holds reference and sentence together, so a 25 s reference would split each sentence into 5 s pieces.

Speed is the cost: 2.1 to 2.4 s of compute per second of audio at 30 steps (3.5 to 3.8 when the machine was busier), against 0.27 for `kokoro-openvoice`; the reference's 13 s are part of every diffusion pass. Loading takes about 20 s once the weights are cached (about 3.5 GB in the cache: Seed-VC 0.8, whisper-small 1.8, BigVGAN 0.9, CAM++ 0.1). BigVGAN can overshoot full scale, so the backend scales a clip down to a 0.95 peak when it goes over.

To listen to, in `.claude/loops/voice/test5/` (personal data, out of git), six sentences with 0.6 s between: `kokoro-seedvc.mp3` (`am_michael`, the direct counterpart of round 2's `kokoro-openvoice.mp3`), `kokoro-seedvc-am_fenrir.mp3` (the preset), `kokoro-seedvc-am_onyx.mp3` (most alike, one slip); single clips in the folders of the same names, and `kokoro-seedvc-am_eric/`, `-am_adam/`, `-am_fenrir-50/`.

`say.py --model kokoro-seedvc` (and `build.py --voice tts:kokoro-seedvc`) used `am_fenrir`, 30 steps in this round; since round 6 that is `kokoro-seedvc-v1`, and `kokoro-seedvc` uses the pitch-conditioned model. `--set voice=am_onyx`, `--set steps=50`, `--set cfg=0.7`, `--set ref_s=25` change that. It is not a checked model: no Demucs, Whisper or retakes, which Kokoro's clean takes did not need in this test.

## Round 3: VibeVoice without music, and reliable on short lines

VibeVoice was trained on podcasts and sometimes plays music of its own under or around the voice; on very short lines it also says something else or runs on ("Two: it forgets." gave 15 s, 1 s and 2.4 s in round 2). Now `say.py` cleans and checks every `vibevoice` take, retakes the bad ones, and speaks a short line together with the sentence before it. Same six sentences, same reference `ref-13s.wav`.

### Finding music by number

Demucs (`htdemucs`, MIT, 4.1.0, on the Apple GPU through MPS) splits a clip into a vocals stem and the rest (drums, bass, other). How loud the rest is, against the voice where it speaks, says whether there is music: on clips with no music only bleed is left there. The measure used is the loudest half second of the rest (`music_peak_db`).

| Clips | Loudest 0.5 s of non-voice, against the voice |
| --- | --- |
| Round-2 clips of `qwen3`, `voxcpm2`, `kokoro` (18) and the two reference clips | -25 to -39 dB |
| Round-2 `vibevoice` 1, 4, 5, 6 | -29 to -38 dB: no music |
| Round-2 `vibevoice` 3 | **-1 dB**: a half-second burst of music before the first word (the "0.7 s of silence at the start" was this) |
| Round-2 `vibevoice` 2 ("Thank you.") | **+13 dB**: music louder than the voice, at the start and in the last second |

The limit is set at -25 dB: everything without music lies below it. The reference clips are free of music (-36 dB), so the music does not come from them.

### Preventing it

Each setting was tried with three to nine seeds on the six sentences and measured with Demucs, Whisper and WavLM (likeness, as in round 2). "Music" counts long sentences over -25 dB; short line 2 is counted apart below.

| Setting | Music in the long sentences | Takes with more than 2 word errors | Likeness | Speed |
| --- | --- | --- | --- | --- |
| `cfg_scale` 1.3, 10 steps (round 2) | 3 of 39 (-13, -20, -25 dB) | 4 of 39 | 0.961 | 1.0 |
| **`cfg_scale` 1.8**, 10 steps | **0 of 39** | 2 of 39 | 0.962 to 0.964 | 1.0 |
| `cfg_scale` 1.3, 20 diffusion steps | 1 of 15, at -1 dB | 1 of 15 | 0.955 | 2.0 |
| `cfg_scale` 1.3, 9 s reference (`ref-9s.wav`) | 1 of 15 | 0 of 15 | **0.935** | 1.0 |

Kept: `cfg_scale` 1.8 is the new default (stronger guidance by the text: no music seen, fewer slips, likeness the same). More diffusion steps bring no gain at twice the time; the shorter reference loses likeness. Also kept:

- **A length limit.** VibeVoice stops on its own only after about twice its prompt, some 30 s; one take of line 2 ran to 34.5 s. The clip may now run at most 1.5 s plus 0.8 s per word.
- **A seed per clip.** The seed is set before each sentence, so a clip depends on its text and seed only, not on the other lines in the batch; this keeps build.py's cache honest and makes retakes reproducible.

Not changed: the text format. mlx-audio turns `Speaker 1: text` and plain text into the same prompt, and our lines have none of the openings ("Welcome to", "Hello") that Microsoft names as music triggers.

### Removing it, and retaking

Every take goes through Demucs and only the vocals stem is kept. On clean clips this changes nothing that can be measured: loudness by at most 0.02 dB, every octave band from 50 Hz to 12 kHz by at most 0.3 dB, the removed part is 27 to 38 dB below the clip (8 clips of four models), and likeness moves by -0.008 to +0.004 (30 clips, no change on average). So it is applied to every take, not only flagged ones. On music it works where the music is not too loud: round-2 clip 3 went from -1 to -34 dB, a 1.3 take of sentence 6 from -13 to -35 dB; round-2 clip 2 (+13 dB) still had -16 dB left.

Then each take is checked and retaken with another seed (seed + 101, + 202, ...; `--retakes`, default 3) when any of these holds:

- music still in the cleaned take: Demucs is run on the vocals stem once more and finds more than -25 dB of non-voice;
- the speed does not fit the words: under 5 or over 22 letters per second of voice (clean takes measured 6.7 to 13.7);
- Whisper (large-v3-turbo, no prompt, so it does not just repeat our text) hears other words: more than 10 % word edits (at least 1), none at all in a line under 5 words. "2" for "Two" counts as right.

If all takes are flagged, the one with the fewest wrong words is kept and say.py names it on stderr. Without the merge below, line 2 alone shows why the merge is needed: four takes in a row were flagged (music +10 dB with words from nowhere, "Parma... It forgets.", "Good. Let her clip.", "Thank you.").

### Short lines

A line under 5 words is spoken together with the sentence before it (the one after it, for the first line) in one call, and cut out again: Whisper gives the word times of the joined take, and the cut goes at the quietest 20 ms between the last word of the first sentence and the first word of the second. The short line ends the joined take, so it keeps its own falling end, and the cut lands in the natural pause between the sentences.

| Line 2, "Two: it forgets." | Right words | Notes |
| --- | --- | --- |
| On its own (12 takes: 4 settings x 3 seeds) | 0 | "It forgets.", "Bye.", "Baby blues", "Moi internet", a 34.5 s runaway |
| With the sentence before (4 seeds) | 2 | the other two flagged and retaken: "Two" left out once, music once |
| With the sentence after (4 seeds) | 3, but | no pause to cut at: one cut took "and" from the next sentence, two came out too slow |

`build.py` passes each sentence's neighbours to `say.py` (batch columns `before`, `after`), and a short sentence's cache key includes the neighbour it is spoken with; nothing changes for the other models.

### The result

`.claude/loops/voice/test3/` (personal data, out of git): `vibevoice-clean.mp3` is the six sentences, cleaned and checked, 0.6 s between them; `vibevoice-raw.mp3` beside it is the same takes before Demucs (line 2 already cut out of its joined take); `vibevoice-clean/0N.wav` the single clips, `vibevoice-takes/` every take raw and clean (and line 2's joined take), `vibevoice-report.json` every measure. With seed 1 all six passed at the first take:

| Line | Heard | Music before / after cleaning | Letters per second | Likeness |
| --- | --- | --- | --- | --- |
| 1 | "... like Cloud Code, Codex, or GitHub Copilot." | -28 / -35 dB | 10.3 | 0.964 |
| 2 | "Two, it forgets." (1.55 s, cut at 9.35 s of the joined take) | -35 / -35 dB | 7.7 | 0.892 |
| 3 | right | -34 / -33 dB | 13.7 | 0.951 |
| 4 | right | -37 / -36 dB | 12.1 | 0.943 |
| 5 | right | -36 / -37 dB | 10.3 | 0.965 |
| 6 | right | -35 / -36 dB | 10.5 | 0.975 |

Likeness 0.948 on average (round 2: 0.924, 0.79 to 0.98); the short clip scores lowest because 1.5 s is little to judge a voice by. "Claude" still comes out as "Cloud", as in round 2, and is not counted as an error by the check (1 edit in 20 words is allowed). Compute: VibeVoice took 1.3 s per second of audio in this run; the check adds about 0.7 s more (Whisper and two Demucs passes over five long clips, 38 s of audio, took 27 s with loading), and each retake round adds its own. `test3/cfg13/` holds the same run at `cfg_scale` 1.3 (also all passed at the first take), `test3/retake-demo/` the run without the merge whose line 2 is quoted above.

Measured with the scripts in `source/video/tts/` (`demucs_clean.py`, `check.py`) and the round-2 WavLM code in `.claude/loops/voice/measure2.py`.

## Round 2: natural English first

Nine candidates, the same six sentences from `courses/basic-01/en.md`, one call per sentence, reference `ref-13s.wav` for all:

1. Plenty of companies already pay for an AI chat tool or a coding agent, like Claude Code, Codex or GitHub Copilot.
2. Two: it forgets.
3. And the longer the chat gets, the more its attention drifts, and the less it remembers from earlier.
4. If a session dies, how does a new one pick up the task?
5. There's a simple formula: agent equals model plus harness.
6. Between a blacklist, a whitelist, a human making the call, and the account's own permissions, the agent's access stays safe.

| Name in `say.py` | What it is | Settings | Licence (code / weights) | Env |
| --- | --- | --- | --- | --- |
| `qwen3` | Round-1 choice, the baseline | as round 1 | Apache-2.0 / Apache-2.0 | `mlx` |
| `voxcpm2` | VoxCPM2 (OpenBMB, 2B, 2026), `mlx-community/VoxCPM2-bf16`, 48 kHz | "reference" cloning: the clip gives only the timbre, the model chooses the rhythm and melody; `cfg_value` 2.0, 10 steps. `--set continue=1` also feeds the transcript and copies the clip's rhythm and accent | Apache-2.0 / Apache-2.0 | `mlx` |
| `vibevoice` | VibeVoice 1.5B (Microsoft), `microsoft/VibeVoice-1.5B`, built for long-form podcasts | audio only, no transcript; `cfg_scale` 1.3, 10 diffusion steps, greedy | MIT / MIT | `mlx` |
| `chatterbox-turbo` | as round 1 | temperature 0.8, top_p 0.95 (defaults) | MIT / MIT | `chatterbox` |
| `chatterbox-turbo-calm` | Chatterbox Turbo, calmer sampling | temperature 0.5, top_p 0.9 (Turbo ignores exaggeration and cfg_weight) | MIT / MIT | `chatterbox` |
| `chatterbox-calm` | Chatterbox, calmer | exaggeration 0.3, cfg_weight 0.3, temperature 0.6 | MIT / MIT | `chatterbox` |
| `kokoro-openvoice` | Kokoro 82M (`hexgrad/Kokoro-82M`, voice `am_michael`) speaks; the OpenVoice v2 tone-colour converter (`myshell-ai/OpenVoiceV2`) swaps in the presenter's timbre | `tau` 0.3 (0.1 measured the same) | Kokoro Apache-2.0; OpenVoice MIT / MIT | `kvc` |
| `kokoro-cbvc` | Kokoro speaks; Chatterbox's own voice converter (S3Gen) swaps the timbre | defaults | Apache-2.0; MIT | `kvc` |
| `kokoro` | Kokoro alone, stock voice, no cloning: the "native English" yardstick | voice `am_michael` | Apache-2.0 / Apache-2.0 | `kvc` |

With voice conversion the words, rhythm and melody are Kokoro's (trained on native speakers) and only the timbre is the presenter's. Seed-VC, a stronger converter, was left out here for its GPL-3.0 licence; round 5 tries it.

### Measured

Similarity and word error as in round 1 (WavLM cosine against the presenter's own speech outside the reference, which scores 0.968 against the reference itself; Whisper large-v3-turbo). Word errors here count only real ones: Whisper writing "Two" as "2" is not counted. Speed is seconds of compute per second of audio, model loaded; the machine was shared with other work for part of the runs, so the quiet-machine figure is given where it was re-run.

| Name | Speed | Similarity, mean (range over the 6) | Real word errors in 84 words | Clipped samples | Sentence 1 pitch spread / range (semitones) |
| --- | --- | --- | --- | --- | --- |
| `qwen3` | 1.0 | 0.946 (0.90 to 0.97) | 2: "Claude Code, Codex" heard as "Cloud Codex" | 0 | 4.0 / 14.1 |
| `voxcpm2` | 1.55 (under load) | 0.940 (0.92 to 0.97) | 1: "Cloud Code" | 0 | 5.8 / 19.1 |
| `vibevoice` | 1.07 (under load) | 0.924 (0.79 to 0.98) | 5: sentence 2 came out as 6 s of "Thank you."; "There's a" became "The" | 0 | 3.1 / 10.1 |
| `chatterbox-turbo` | 1.7 | 0.902 (0.83 to 0.94) | 1: "Plenty" heard as "Friends" | 0 | 1.9 / 6.2 |
| `chatterbox-turbo-calm` | 6.7 (under load) | 0.878 (0.84 to 0.93) | 1: "Cloud Code"; a break before "Copilot" | 0 | 4.1 / 15.2 |
| `chatterbox-calm` | 5.6 | 0.905 (0.85 to 0.95) | 1: "chat" heard as "check" | 37 | 3.7 / 16.2 |
| `kokoro-openvoice` | 0.27 | 0.806 (0.73 to 0.86) | **0** | 0 | 3.1 / 9.3 |
| `kokoro-cbvc` | 0.80 | 0.805 (0.67 to 0.87) | 1: "the task" as "a task" | 20 | 5.4 / 19.2 |
| `kokoro` (stock voice) | 0.15 | 0.620 | 0 | 0 | 4.0 / 15.2 |

Pitch is pYIN on voiced frames, in semitones around the clip's median; it overstates spread wherever the voice creaks (pYIN then reads half the pitch), and the presenter's own speech reads 5.9 / 18.9 for that reason. What the numbers do show on sentence 1, word by word:

- `qwen3` and `voxcpm2` both say "Claude" so that Whisper hears "Cloud" (the clip's own pronunciation, copied), and both drop about 10 semitones into creak on "Claude"; `qwen3` also runs "Claude Code, Codex" together. That matches what the presenter heard as the odd melody.
- `vibevoice` reads the list the textbook way: a rise on "Code,", then a steady fall through "Codex, or GitHub Copilot", with the smallest frame-to-frame pitch jumps of all (0.21 semitones). On sentences 3, 5 and 6 it is also the most like the presenter (0.97 to 0.98). But it fails on short lines: "Two: it forgets." came out as "Thank you." (a retake with `cfg_scale` 1.5 gave 1 s, writing "Two. It forgets." gave 2.4 s), and it adds up to 0.7 s of silence at the start.
- `chatterbox-turbo` is the flattest (6 semitones over the whole sentence): clear, but close to monotone.
- The Kokoro-based three have no creak, rise and fall on each list item, and make at most one slip, because the melody is Kokoro's. OpenVoice keeps it intact (word by word the same shape as Kokoro alone, slightly narrower); Chatterbox's converter re-makes the pitch and clips. Likeness to the presenter drops to about 0.81: a different-sounding person with a similar timbre.

### Which to listen to

All in `.claude/loops/voice/test2/` (personal data, out of git): `<name>.mp3` is the six sentences with 0.6 s between them; `<name>/0N.wav` the single sentences. `ALL-compare.mp3` plays sentence 1 by every candidate with 1 s between, in this order: `qwen3`, `voxcpm2`, `vibevoice`, `chatterbox-turbo`, `chatterbox-turbo-calm`, `chatterbox-calm`, `kokoro-openvoice`, `kokoro-cbvc`, `kokoro`.

Measured guess, to be settled by ear: for natural English, `kokoro-openvoice` is the safe choice (native melody, no word errors, fastest, no clipping) at the cost of sounding less like the presenter; `vibevoice` has the best English melody among the true cloners and the best likeness on long sentences, but needs short lines merged with their neighbours or retaken. `voxcpm2` is a clean, licence-safe alternative to `qwen3` but copies the same "Cloud Code". The calm Chatterbox settings did not help: slower, less alike, and still a slip each.

Measurements come from `.claude/loops/voice/measure2.py` (run with the `chatterbox` env's Python).

## Round 1: the first four models

| Name in `say.py` | Model | Runs on | Code licence | Weights licence | Download |
| --- | --- | --- | --- | --- | --- |
| `qwen3` | Qwen3-TTS 12Hz 1.7B Base (Alibaba Qwen), MLX build `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16` via `mlx-audio` 0.6.6 | Apple GPU through MLX | Apache-2.0 (Qwen3-TTS), MIT (mlx-audio) | Apache-2.0 | 4.3 GB |
| `chatterbox` | Chatterbox (Resemble AI), `ResembleAI/chatterbox`, package `chatterbox-tts` 0.1.7 | Apple GPU through PyTorch MPS | MIT | MIT | 3 GB |
| `chatterbox-turbo` | Chatterbox Turbo, `ResembleAI/chatterbox-turbo`, same package | Apple GPU through PyTorch MPS | MIT | MIT | 3.7 GB |
| `f5` | F5-TTS v1 Base, `SWivid/F5-TTS`, package `f5-tts` 1.1.22 | Apple GPU through PyTorch MPS | MIT | CC-BY-NC-4.0: non-commercial only (trained on the Emilia data set) | 1.3 GB |

Chatterbox adds an inaudible Perth watermark to everything it makes; that is built into the package.

All three clone from a short reference clip with no training. Qwen3-TTS and F5-TTS also need the exact words spoken in the clip; Chatterbox only needs the audio.

### Measured on the five test sentences

Same 13 s reference for `qwen3` and `chatterbox`; a 9.3 s cut of it for `f5`, because F5 cuts any reference over 12 s and then speaks too fast. Speed is seconds of compute per second of audio, model already loaded (lower is faster; 1.0 is real time). Voice similarity is the cosine between WavLM speaker embeddings (`microsoft/wavlm-base-plus-sv`) of each clip and of the presenter's own speech that was not in the reference; the presenter's own speech against itself scores 0.976. Word error is Whisper large-v3-turbo's transcript against the text.

| Model | Speed | Voice similarity | Word error | Clipped samples | Model load |
| --- | --- | --- | --- | --- | --- |
| `qwen3` | 1.9 (1.3 to 1.8 after the first sentence) | **0.968** | 2 % | 0 | 5 s |
| `chatterbox-turbo` | 3.1 | 0.908 | 1 % | 0 | 105 s (first run, with download) |
| `chatterbox` | 4.3 | 0.878 | 0 % | 12 | 30 s |
| `f5` | 6.4 | 0.825 | 0 % | 135 | 10 s |

Word errors were "can't" heard as "can" and "hunt" as "hang", each once. F5 copies the reference's loudness, so its output clips like the slightly clipped recording did, and it starts each clip with about 0.5 s of silence.

### Dropped, and why

- **XTTS-v2**: Coqui closed in 2024; the community fork lives on, but the model is old and its weights are under the non-commercial CPML. The three above are newer and clone better.
- **GPT-SoVITS**: at its best after fine-tuning on the speaker; zero-shot English is weaker, and it is a web UI more than a library.
- **CosyVoice 2/3, Spark-TTS, IndexTTS-2, MaskGCT, Fish Audio S2, Higgs Audio**: built and tuned for CUDA; on Apple Silicon they are slow (IndexTTS-2 about 0.1x real time on an M4) or need large GPUs; Spark-TTS and Fish carry non-commercial licences. CosyVoice is strongest in Chinese, not English.
- **OmniVoice** (k2-fsa, 2026): promising and available through `mlx-audio`, but its weights are reported as non-commercial and reviews note dropped words. A good next one to try, with the same `mlx` environment.
- **Kokoro, Supertonic, Piper, MeloTTS**: fast and good, but fixed voices, no cloning.

## Install

Everything goes under `.claude/loops/tts/<env>/` in this repository (ignored by git); the weights go to the Hugging Face cache (`~/.cache/huggingface`). Nothing is installed machine-wide. `uv` and `ffmpeg` must be on the path; any Python 3.12 works as the base.

```bash
T=.claude/loops/tts
PY=python3.12   # any Python 3.12

# Qwen3-TTS through MLX
mkdir -p $T/mlx && uv venv --python $PY $T/mlx/.venv
uv pip install -p $T/mlx/.venv/bin/python mlx-audio

# Chatterbox and Chatterbox Turbo
mkdir -p $T/chatterbox && uv venv --python $PY $T/chatterbox/.venv
uv pip install -p $T/chatterbox/.venv/bin/python chatterbox-tts "setuptools<81"
# setuptools<81 brings back pkg_resources, which the watermarker needs; without it loading fails
# with "'NoneType' object is not callable".

# F5-TTS
mkdir -p $T/f5 && uv venv --python $PY $T/f5/.venv
uv pip install -p $T/f5/.venv/bin/python f5-tts

# VoxCPM2 and VibeVoice: nothing to install, mlx-audio 0.6.6 in the mlx env has both.

# Demucs, which say.py runs on every vibevoice take (round 3); weights (htdemucs, 80 MB) download on first use
mkdir -p $T/demucs && uv venv --python $PY $T/demucs/.venv
uv pip install -p $T/demucs/.venv/bin/python demucs soundfile "torch<2.9" "torchaudio<2.9"
# vibevoice's check also needs the whisper env that source/video/build.py uses:
# python3 -m venv $T/whisper/venv && $T/whisper/venv/bin/pip install mlx-whisper

# Kokoro with voice conversion (OpenVoice v2, Chatterbox VC)
mkdir -p $T/kvc && uv venv --python $PY $T/kvc/.venv
uv pip install -p $T/kvc/.venv/bin/python chatterbox-tts "setuptools<81" kokoro "misaki[en]" \
  eng_to_ipa inflect unidecode pypinyin cn2an jieba \
  "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
git clone --depth 1 https://github.com/myshell-ai/OpenVoice.git $T/kvc/src-openvoice
uv pip install -p $T/kvc/.venv/bin/python --no-deps $T/kvc/src-openvoice
# --no-deps: OpenVoice pins 2023 versions (numpy 1.22, gradio, faster-whisper) it does not need for
# conversion; the small text packages above are what its import chain needs. Its watermarker (wavmark)
# is stubbed out in the backend.

# Kokoro with Seed-VC (round 5); Seed-VC is GPL-3.0. Weights (about 3.5 GB) go to the HF cache on first use.
mkdir -p $T/seedvc && git clone --depth 1 https://github.com/Plachtaa/seed-vc.git $T/seedvc/src
uv venv --python $PY $T/seedvc/.venv
uv pip install -p $T/seedvc/.venv/bin/python "torch==2.6.0" "torchaudio==2.6.0" "numpy==1.26.4" "scipy==1.13.1" \
  "librosa==0.10.2" "huggingface-hub>=0.28.1,<1" "munch==4.0.0" "einops==0.8.0" "descript-audio-codec==1.0.0" \
  "transformers==4.46.3" soundfile pyyaml "hydra-core==1.3.2" accelerate pydub kokoro "misaki[en]" \
  "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
# Only what its offline inference needs from requirements-mac.txt (no gradio, funasr, modelscope or GUI); the
# backend imports Seed-VC's modules from $T/seedvc/src.
```

The model weights download the first time each model runs. Set `TTS_HOME` to use another folder than `.claude/loops/tts`.

## The reference clip

A clean 10 to 15 s stretch of the presenter's own voice: whole sentences, no music, cut at pauses. Convert it to 24 kHz mono wav, and save the exact words spoken next to it with the same name and `.txt`:

```bash
ffmpeg -i recording.m4a -ss <start> -to <end> -ac 1 -ar 24000 -af "adeclip,volume=-2dB" ref.wav
echo "The exact words, as spoken, including slips." > ref.txt
```

`adeclip` repairs light clipping in the recording. Write what was actually said, not the script: the models line up the words with the sound. For `f5`, use a clip of at most 12 s. Keep the recording and the clip out of git.

## Make audio

One sentence:

```bash
python3 source/video/tts/say.py --model qwen3 --ref ref.wav --text "Agent equals model plus harness." --out 04.wav
```

Many sentences with the model loaded once; the batch file has one `output<TAB>sentence` per line:

```bash
python3 source/video/tts/say.py --model qwen3 --ref ref.wav --batch lines.tsv
```

A batch line may also name the sentences around it, `output<TAB>sentence<TAB>before<TAB>after` (either may be empty); `vibevoice` speaks a line under 5 words together with one of them and cuts it out (round 3). `vibevoice` takes are always cleaned with Demucs, checked and retaken when flagged; `--retakes N` (default 3), `--keep-takes DIR` (every take, raw and cleaned), `--report FILE` (every measure, JSON), `--no-merge` and `--no-check` change that.

Names with a suffix (`chatterbox-calm`, `chatterbox-turbo-calm`) are presets: the same model with other settings. `--set KEY=VALUE` (repeatable) changes one setting, for example `--set cfg_weight=0.3` or `--set voice=bm_george`; each backend's docstring lists its keys. Output wavs keep the model's own rate (48 kHz for `voxcpm2`, 44 kHz for `kokoro-seedvc`, 22 kHz for `kokoro-openvoice` and `kokoro-seedvc-v1`, 24 kHz for the rest).

`--ref-text "..."` overrides `ref.txt`. `--out` ending in `.mp3` or `.m4a` is converted with ffmpeg. `--seed` (default 1) makes a run repeatable; change it to get another take of a sentence. Timings go to stderr.

`say.py` uses only the standard library. It picks the environment for the model, runs `backends/<model>_backend.py` with that environment's Python, and passes the job as JSON on stdin. To add a model, add a backend with a `load` and a `speak` function (see `backends/_common.py`) and one line in `MODELS` in `say.py`; the backend gets the preset's settings in `job["options"]`.

## Removed (2026-11-18)

Rejected after listening, deleted to free disk (~19 GB): F5-TTS, Chatterbox and Chatterbox Turbo, VoxCPM2, Qwen3-TTS 0.6B, Kokoro + OpenVoice / Chatterbox converter (the `kvc` env). Their backends stay in `say.py` for the record but need a reinstall (install steps above) before use. Kept: Qwen3-TTS 1.7B, VibeVoice, Kokoro + Seed-VC (the `seedvc` env has Kokoro), Demucs, DeepFilterNet, mlx-whisper, WavLM, GPT-SoVITS.
