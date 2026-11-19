"""Kokoro (hexgrad, 82M) for the English, then voice conversion to the reference's
timbre. PyTorch on Apple GPU (MPS); Kokoro itself runs on the CPU. Env: tts/kvc.

  kokoro-openvoice   Kokoro, then the OpenVoice v2 tone-colour converter (MyShell)
  kokoro-cbvc        Kokoro, then Chatterbox's voice converter (Resemble AI, S3Gen)
  kokoro             Kokoro alone, the stock voice (no cloning), for comparison

The converters keep Kokoro's words, rhythm and melody and replace the timbre.
Options: voice (am_michael), speed (1.0), tau (0.3, OpenVoice only: lower = closer
to the target voice, higher = keeps more of the source).
"""

import os
import sys
import tempfile

import numpy as np
import soundfile as sf
import torch

from _common import read_job, run

SR = 24000
# A neutral paragraph spoken once by Kokoro, to measure its own timbre for OpenVoice.
SOURCE_TEXT = ("Every morning I open the board, read the plan, and check what changed overnight. "
               "Then I pick one task, explain what I want, and let the agent do the work while I watch.")


def _kokoro(pipe, text, voice, speed):
    chunks = [r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
              for r in pipe(text, voice=voice, speed=speed) if r.audio is not None]
    return np.concatenate(chunks).astype(np.float32)


def load(job):
    from kokoro import KPipeline
    torch.manual_seed(job["seed"])
    o = job.get("options", {})
    st = {"model": job["model"], "voice": o.get("voice", "am_michael"), "speed": float(o.get("speed", 1.0)),
          "tau": float(o.get("tau", 0.3)), "tmp": tempfile.mkdtemp(prefix="kvc-")}
    st["pipe"] = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    if job["model"] == "kokoro-openvoice":
        from huggingface_hub import snapshot_download
        from openvoice.api import ToneColorConverter
        d = snapshot_download("myshell-ai/OpenVoiceV2", allow_patterns=["converter/*"])
        # OpenVoice always loads its watermarker (wavmark, not installed); hand it a stub, then switch it off.
        import types
        sys.modules.setdefault("wavmark", types.SimpleNamespace(
            load_model=lambda: types.SimpleNamespace(to=lambda *_: None)))
        conv = ToneColorConverter(os.path.join(d, "converter", "config.json"), device=device)
        conv.watermark_model = None
        conv.load_ckpt(os.path.join(d, "converter", "checkpoint.pth"))
        src = os.path.join(st["tmp"], "source.wav")
        sf.write(src, _kokoro(st["pipe"], SOURCE_TEXT, st["voice"], st["speed"]), SR)
        st["conv"] = conv
        st["src_se"] = conv.extract_se([src])
        st["tgt_se"] = conv.extract_se([job["ref"]])
    elif job["model"] == "kokoro-cbvc":
        from chatterbox.vc import ChatterboxVC
        st["conv"] = ChatterboxVC.from_pretrained(device=device)
        st["conv"].set_target_voice(job["ref"])
    return st


def speak(st, text):
    audio = _kokoro(st["pipe"], text, st["voice"], st["speed"])
    if st["model"] == "kokoro":
        return audio, SR
    path = os.path.join(st["tmp"], "kokoro.wav")
    sf.write(path, audio, SR)
    if st["model"] == "kokoro-openvoice":
        out = st["conv"].convert(path, st["src_se"], st["tgt_se"], tau=st["tau"])
        return out, st["conv"].hps.data.sampling_rate
    wav = st["conv"].generate(path)
    return wav.squeeze().cpu().numpy(), st["conv"].sr


if __name__ == "__main__":
    run(read_job(), load, speak)
