# Voice-cloned narration, locally

Each spoken sentence of a video becomes one audio file, in the presenter's own voice, made on an Apple Silicon Mac with no paid API. This folder holds a small wrapper, `say.py`, that calls one of several open models, each installed in its own environment outside git.

Round 1 (below) chose for likeness to the presenter. Round 2 chose for natural English first and likeness second, because the round-1 winner sounded like the presenter but put odd melodies on some phrases. Round 2 comes first.

Tested November 2026 on an M1 Pro with 32 GB, macOS, Python 3.12.

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

With voice conversion the words, rhythm and melody are Kokoro's (trained on native speakers) and only the timbre is the presenter's. Seed-VC, a stronger converter, was left out: GPL-3.0.

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

Names with a suffix (`chatterbox-calm`, `chatterbox-turbo-calm`) are presets: the same model with other settings. `--set KEY=VALUE` (repeatable) changes one setting, for example `--set cfg_weight=0.3` or `--set voice=bm_george`; each backend's docstring lists its keys. Output wavs keep the model's own rate (48 kHz for `voxcpm2`, 22 kHz for `kokoro-openvoice`, 24 kHz for the rest).

`--ref-text "..."` overrides `ref.txt`. `--out` ending in `.mp3` or `.m4a` is converted with ffmpeg. `--seed` (default 1) makes a run repeatable; change it to get another take of a sentence. Timings go to stderr.

`say.py` uses only the standard library. It picks the environment for the model, runs `backends/<model>_backend.py` with that environment's Python, and passes the job as JSON on stdin. To add a model, add a backend with a `load` and a `speak` function (see `backends/_common.py`) and one line in `MODELS` in `say.py`; the backend gets the preset's settings in `job["options"]`.
