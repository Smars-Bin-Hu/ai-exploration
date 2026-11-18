# Voice-cloned narration, locally

Each spoken sentence of a video becomes one audio file, in the presenter's own voice, made on an Apple Silicon Mac with no paid API. This folder holds a small wrapper, `say.py`, that calls one of three open models, each installed in its own environment outside git.

Tested November 2026 on an M1 Pro with 32 GB, macOS, Python 3.12.

## The three models

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

`--ref-text "..."` overrides `ref.txt`. `--out` ending in `.mp3` or `.m4a` is converted with ffmpeg. `--seed` (default 1) makes a run repeatable; change it to get another take of a sentence. Timings go to stderr.

`say.py` uses only the standard library. It picks the environment for the model, runs `backends/<model>_backend.py` with that environment's Python, and passes the job as JSON on stdin. To add a model, add a backend with a `load` and a `speak` function (see `backends/_common.py`) and one line in `MODELS` in `say.py`.
