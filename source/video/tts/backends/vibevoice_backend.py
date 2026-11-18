"""VibeVoice 1.5B (Microsoft), MLX on Apple Silicon via mlx-audio. Env: tts/mlx.

Clones from the reference audio alone (no transcript). Text is sent as a
one-speaker script ("Speaker 1: ...").
Options: cfg_scale (1.3), ddpm_steps (10), do_sample (0), temperature (0.7).
"""

import mlx.core as mx
import numpy as np

from _common import read_job, run

REPOS = {"vibevoice": "microsoft/VibeVoice-1.5B"}


def load(job):
    from mlx_audio.tts.utils import load_model
    mx.random.seed(job["seed"])
    return {"model": load_model(REPOS[job["model"]]), "job": job, "opts": job.get("options", {})}


def speak(state, text):
    job, model, o = state["job"], state["model"], state["opts"]
    kw = {"ref_audio": job["ref"], "cfg_scale": float(o.get("cfg_scale", 1.3)),
          "ddpm_steps": int(o.get("ddpm_steps", 10)), "do_sample": bool(int(o.get("do_sample", 0))),
          "temperature": float(o.get("temperature", 0.7))}
    parts = [r.audio for r in model.generate(text=f"Speaker 1: {text}", **kw)]
    audio = np.concatenate([np.array(p, dtype=np.float32) for p in parts])
    return audio, model.sample_rate


if __name__ == "__main__":
    run(read_job(), load, speak)
