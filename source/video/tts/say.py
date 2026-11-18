#!/usr/bin/env python3
"""Speak text in a cloned voice with a local TTS model.

One sentence:
    python source/video/tts/say.py --model qwen3 --ref ref.wav --text "Hello." --out 01.wav

Many sentences, model loaded once (one "out<TAB>text" per line):
    python source/video/tts/say.py --model qwen3 --ref ref.wav --batch lines.tsv

The reference transcript is read from --ref-text, or else from the file next to
the reference with the same name and a .txt extension.

This script uses only the standard library. It runs the model's own Python
(an isolated venv under .claude/loops/tts/<env>/, see README.md) on
backends/<model>_backend.py and passes the job as JSON on stdin. Output is a 24 kHz
mono wav; any other extension (.mp3, .m4a) is converted with ffmpeg.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # source/video/tts -> repo root
TTS_HOME = Path(os.environ.get("TTS_HOME", REPO / ".claude" / "loops" / "tts"))

# model name -> (venv folder under TTS_HOME, backend script)
MODELS = {
    "chatterbox": ("chatterbox", "chatterbox_backend.py"),
    "chatterbox-turbo": ("chatterbox", "chatterbox_backend.py"),
    "f5": ("f5", "f5_backend.py"),
    "qwen3": ("mlx", "qwen3_backend.py"),
}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True, choices=sorted(MODELS))
    p.add_argument("--ref", required=True, help="reference wav of the voice (10-15 s works for all models)")
    p.add_argument("--ref-text", help="exact words spoken in --ref (default: <ref>.txt)")
    p.add_argument("--text", help="the sentence to speak")
    p.add_argument("--out", help="output file (.wav, or .mp3 etc. via ffmpeg)")
    p.add_argument("--batch", help="file of 'out<TAB>text' lines; loads the model once")
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()

    ref = Path(a.ref).resolve()
    if not ref.exists():
        sys.exit(f"reference not found: {ref}")
    ref_text = a.ref_text
    if ref_text is None and ref.with_suffix(".txt").exists():
        ref_text = ref.with_suffix(".txt").read_text(encoding="utf-8").strip()

    items = []
    if a.batch:
        for line in Path(a.batch).read_text(encoding="utf-8").splitlines():
            if line.strip():
                out, text = line.split("\t", 1)
                items.append({"out": str(Path(out).resolve()), "text": text.strip()})
    elif a.text and a.out:
        items.append({"out": str(Path(a.out).resolve()), "text": a.text.strip()})
    else:
        p.error("give --text and --out, or --batch")

    env, backend = MODELS[a.model]
    python = TTS_HOME / env / ".venv" / "bin" / "python"
    if not python.exists():
        sys.exit(f"model environment not installed: {python.parent.parent} (see README.md)")

    # Backends write wav; convert afterwards when another format was asked for.
    tmp = Path(tempfile.mkdtemp(prefix="say-"))
    convert = []
    for i, it in enumerate(items):
        if not it["out"].lower().endswith(".wav"):
            wav = str(tmp / f"{i:04d}.wav")
            convert.append((wav, it["out"]))
            it["out"] = wav
        Path(it["out"]).parent.mkdir(parents=True, exist_ok=True)

    job = {"model": a.model, "ref": str(ref), "ref_text": ref_text, "seed": a.seed, "items": items}
    env_vars = dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK="1", TOKENIZERS_PARALLELISM="false")
    r = subprocess.run([str(python), str(HERE / "backends" / backend)], input=json.dumps(job),
                       text=True, env=env_vars)
    if r.returncode:
        sys.exit(r.returncode)

    for wav, out in convert:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
