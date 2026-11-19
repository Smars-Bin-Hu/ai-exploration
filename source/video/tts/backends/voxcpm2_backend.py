"""VoxCPM2 (OpenBMB, 2B), MLX on Apple Silicon via mlx-audio. Env: tts/mlx.

Uses "reference" cloning: the clip gives the timbre only, the model chooses the
prosody. Passing the transcript too (option continue=1) switches to continuation,
which copies the reference's rhythm and accent as well.
Options: cfg_value (2.0), inference_timesteps (10), continue (0).
"""

import mlx.core as mx
import numpy as np

from _common import read_job, run

REPOS = {"voxcpm2": "mlx-community/VoxCPM2-bf16"}


def load(job):
    from mlx_audio.tts.utils import load_model
    mx.random.seed(job["seed"])
    return {"model": load_model(REPOS[job["model"]]), "job": job, "opts": job.get("options", {})}


def speak(state, text):
    job, model, o = state["job"], state["model"], dict(state["opts"])
    kw = {"ref_audio": job["ref"], "cfg_value": float(o.get("cfg_value", 2.0)),
          "inference_timesteps": int(o.get("inference_timesteps", 10))}
    if int(o.get("continue", 0)) and job.get("ref_text"):
        kw.update(prompt_audio=job["ref"], prompt_text=job["ref_text"] + " ")
    parts = [r.audio for r in model.generate(text=text, **kw)]
    audio = np.concatenate([np.array(p, dtype=np.float32) for p in parts])
    return audio, model.sample_rate


if __name__ == "__main__":
    run(read_job(), load, speak)
