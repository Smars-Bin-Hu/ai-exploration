"""F5-TTS v1 Base, PyTorch on Apple GPU (MPS). Env: tts/f5. Needs the reference transcript."""

import torch

from _common import read_job, run


def load(job):
    from f5_tts.api import F5TTS
    if not job.get("ref_text"):
        raise SystemExit("f5 needs the reference transcript (--ref-text or <ref>.txt)")
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    return {"tts": F5TTS(model="F5TTS_v1_Base", device=device), "job": job}


def speak(state, text):
    job = state["job"]
    wav, sr, _ = state["tts"].infer(job["ref"], job["ref_text"], text, seed=job["seed"],
                                    show_info=lambda *a, **k: None, progress=None)
    return wav, sr


if __name__ == "__main__":
    run(read_job(), load, speak)
