"""VibeVoice 1.5B (Microsoft), MLX on Apple Silicon via mlx-audio. Env: tts/mlx.

Clones from the reference audio alone (no transcript). Text is sent as a
one-speaker script ("Speaker 1: ...").
Options: cfg_scale (1.8; 1.3 made music in 3 of 39 test clips, 1.8 in none: README round 3), ddpm_steps (10),
do_sample (0), temperature (0.7), max_s_per_word (0.8): the clip may run at most 1.5 s + this many seconds per
word; VibeVoice's own limit is about twice the prompt (some 30 s), which a short line can fill with "Thank you." or
music. 0 turns the limit off.

Each item is seeded on its own (the item's "seed", else the job's), so a clip depends only on its text and seed,
not on what else is in the batch.
"""

import math

import mlx.core as mx
import numpy as np

from _common import read_job, run

REPOS = {"vibevoice": "microsoft/VibeVoice-1.5B"}
STEP_S = 3200 / 24000  # one speech step of VibeVoice's tokenizer: 7.5 per second


def load(job):
    from mlx_audio.tts.utils import load_model
    return {"model": load_model(REPOS[job["model"]]), "job": job, "opts": job.get("options", {})}


def speak(state, text, item=None):
    job, model, o = state["job"], state["model"], state["opts"]
    mx.random.seed(int((item or {}).get("seed", job["seed"])))
    kw = {"ref_audio": job["ref"], "cfg_scale": float(o.get("cfg_scale", 1.8)),
          "ddpm_steps": int(o.get("ddpm_steps", 10)), "do_sample": bool(int(o.get("do_sample", 0))),
          "temperature": float(o.get("temperature", 0.7))}
    per_word = float(o.get("max_s_per_word", 0.8))
    if per_word > 0:
        kw["max_tokens"] = math.ceil((1.5 + per_word * len(text.split())) / STEP_S) + 4  # + the control tokens
    parts = [r.audio for r in model.generate(text=f"Speaker 1: {text}", **kw)]
    audio = np.concatenate([np.array(p, dtype=np.float32) for p in parts])
    return audio, model.sample_rate


if __name__ == "__main__":
    run(read_job(), load, speak)
