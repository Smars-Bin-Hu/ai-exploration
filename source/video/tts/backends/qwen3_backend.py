"""Qwen3-TTS Base (Alibaba Qwen), MLX on Apple Silicon via mlx-audio. Env: tts/mlx.

With the reference transcript the model uses in-context cloning (best);
without it, only a speaker embedding.
"""

import mlx.core as mx
import numpy as np

from _common import read_job, run

REPOS = {
    "qwen3": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16",
}


def load(job):
    from mlx_audio.tts.utils import load_model
    mx.random.seed(job["seed"])
    return {"model": load_model(REPOS[job["model"]]), "job": job}


def speak(state, text):
    job, model = state["job"], state["model"]
    parts = [r.audio for r in model.generate(text=text, ref_audio=job["ref"], ref_text=job.get("ref_text"),
                                             lang_code="english")]
    audio = np.concatenate([np.array(p, dtype=np.float32) for p in parts])
    return audio, model.sample_rate


if __name__ == "__main__":
    run(read_job(), load, speak)
