"""Chatterbox and Chatterbox Turbo (Resemble AI), PyTorch on Apple GPU (MPS). Env: tts/chatterbox.

Options (job["options"], from presets in say.py or --set):
  chatterbox:       exaggeration (0.5), cfg_weight (0.5), temperature (0.8)
  chatterbox-turbo: temperature (0.8), top_p (0.95), top_k (1000), repetition_penalty (1.2)
"""

import torch

from _common import read_job, run

KEYS = {
    "chatterbox": ("exaggeration", "cfg_weight", "temperature", "repetition_penalty", "min_p", "top_p"),
    "chatterbox-turbo": ("temperature", "top_p", "top_k", "repetition_penalty"),
}


def load(job):
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    turbo = job["model"].startswith("chatterbox-turbo")
    if turbo:
        from chatterbox.tts_turbo import ChatterboxTurboTTS as M
    else:
        from chatterbox.tts import ChatterboxTTS as M
    model = M.from_pretrained(device=device)
    opts = job.get("options", {})
    kw = {k: v for k, v in opts.items() if k in KEYS["chatterbox-turbo" if turbo else "chatterbox"]}
    if not turbo and "exaggeration" in kw:
        model.prepare_conditionals(job["ref"], exaggeration=kw["exaggeration"])
    else:
        model.prepare_conditionals(job["ref"])  # voice from the reference, computed once
    torch.manual_seed(job["seed"])
    return {"model": model, "kw": kw}


def speak(state, text):
    with torch.inference_mode():
        wav = state["model"].generate(text, **state["kw"])
    return wav.squeeze().cpu().numpy(), state["model"].sr


if __name__ == "__main__":
    run(read_job(), load, speak)
