"""GPT-SoVITS v2ProPlus (RVC-Boss, MIT), fine-tuned on the presenter's own recordings (README.md, round 7).
Env: tts/gptsovits (its own venv; the repo is cloned to tts/gptsovits/src, the fine-tuned weights are in
src/SoVITS_weights_v2ProPlus and src/GPT_weights_v2ProPlus).

The reference should be a 3-10 s slice the model was trained on, with its exact words (--ref-text or <ref>.txt):
GPT-SoVITS continues the reference's semantic tokens, so the reference sets the tone of each line.

Options (--set KEY=VALUE):
  sovits, gpt    weights files (default: the newest of each in the folders above)
  device         cpu (default) or mps
  top_k, top_p, temperature, repetition_penalty   GPT sampling (defaults 15, 1.0, 1.0, 1.35, the repo's)
  speed          speed factor (1.0)
"""

import glob
import os
import sys
from pathlib import Path

import numpy as np

from _common import read_job, run

HOME = Path(os.environ.get("GPTSOVITS_HOME", Path(sys.prefix).parent / "src"))  # sys.prefix: tts/gptsovits/.venv


def newest(pattern):
    files = sorted(glob.glob(str(HOME / pattern)), key=os.path.getmtime)
    if not files:
        sys.exit(f"gptsovits: no weights match {HOME / pattern}; train first (README.md, round 7)")
    return files[-1]


def load(job):
    o = job.get("options", {})
    os.chdir(HOME)  # the repo loads its pretrained models by relative path
    sys.path[:0] = [str(HOME), str(HOME / "GPT_SoVITS")]
    from TTS_infer_pack.TTS import TTS, TTS_Config
    cfg = {"custom": {
        "device": o.get("device", "cpu"), "is_half": False, "version": "v2ProPlus",
        "t2s_weights_path": o.get("gpt") or newest("GPT_weights_v2ProPlus/*.ckpt"),
        "vits_weights_path": o.get("sovits") or newest("SoVITS_weights_v2ProPlus/*.pth"),
        "bert_base_path": "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large",
        "cnhuhbert_base_path": "GPT_SoVITS/pretrained_models/chinese-hubert-base",
    }}
    print(f"[gptsovits] {Path(cfg['custom']['t2s_weights_path']).name} + "
          f"{Path(cfg['custom']['vits_weights_path']).name} on {cfg['custom']['device']}", file=sys.stderr)
    tts = TTS(TTS_Config(cfg))
    return {"tts": tts, "job": job, "o": o}


def speak(state, text, item):
    job, o = state["job"], state["o"]
    seed = item.get("seed", job.get("seed", 1))
    req = {
        "text": text, "text_lang": "en",
        "ref_audio_path": job["ref"], "prompt_text": job.get("ref_text") or "", "prompt_lang": "en",
        "top_k": o.get("top_k", 15), "top_p": o.get("top_p", 1.0), "temperature": o.get("temperature", 1.0),
        "repetition_penalty": o.get("repetition_penalty", 1.35), "speed_factor": o.get("speed", 1.0),
        "text_split_method": "cut5", "batch_size": 1, "seed": seed, "parallel_infer": False,
        "fragment_interval": 0.3,
    }
    sr, audio = None, []
    for sr, chunk in state["tts"].run(req):
        audio.append(np.asarray(chunk))
    a = np.concatenate(audio)
    a = a.astype(np.float32) / 32768.0 if a.dtype == np.int16 else a.astype(np.float32)  # the repo returns int16
    return a, sr


if __name__ == "__main__":
    run(read_job(), load, speak)
