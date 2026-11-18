"""Chatterbox (Resemble AI), PyTorch on Apple GPU (MPS). Env: tts/chatterbox."""

import torch

from _common import read_job, run


def load(job):
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    if job["model"] == "chatterbox-turbo":
        from chatterbox.tts_turbo import ChatterboxTurboTTS as M
    else:
        from chatterbox.tts import ChatterboxTTS as M
    model = M.from_pretrained(device=device)
    model.prepare_conditionals(job["ref"])  # voice from the reference, computed once
    torch.manual_seed(job["seed"])
    return model


def speak(model, text):
    with torch.inference_mode():
        wav = model.generate(text)  # default exaggeration 0.5, cfg_weight 0.5
    return wav.squeeze().cpu().numpy(), model.sr


if __name__ == "__main__":
    run(read_job(), load, speak)
