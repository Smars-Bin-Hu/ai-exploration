"""Qwen3-TTS Base (Alibaba Qwen), MLX on Apple Silicon via mlx-audio. Env: tts/mlx.

With the reference transcript the model uses in-context cloning (best);
without it, only a speaker embedding.

The model sometimes does not stop: it runs on to max_new_tokens (8192 in its generation config, 11 minutes at 12.5
tokens a second) in near-silence and murmur. So each line gets a cap from its words: 2.5x the seconds expected at
3.2 words a second, plus 3 s; say.py's check (LEN_CAP, 2x + 2 s) then flags the take and retakes it.
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


TOKENS_PER_S = 12.5


def max_tokens(text):
    return int(TOKENS_PER_S * (2.5 * len(text.split()) / 3.2 + 3))


def speak(state, text):
    job, model = state["job"], state["model"]
    parts = [r.audio for r in model.generate(text=text, ref_audio=job["ref"], ref_text=job.get("ref_text"),
                                             lang_code="english", max_tokens=max_tokens(text))]
    audio = np.concatenate([np.array(p, dtype=np.float32) for p in parts])
    return audio, model.sample_rate


if __name__ == "__main__":
    run(read_job(), load, speak)
