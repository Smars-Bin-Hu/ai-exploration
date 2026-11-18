"""Kokoro (hexgrad, 82M) for the English, then Seed-VC (Plachtaa, GPL-3.0) for the timbre: zero-shot voice
conversion by a diffusion transformer conditioned on the reference clip. Stronger than OpenVoice's tone-colour
swap (README.md, round 5). PyTorch on the Apple GPU (MPS); Kokoro itself on the CPU. Env: tts/seedvc, with the
Seed-VC source checked out in tts/seedvc/src.

  kokoro-seedvc   Kokoro, then Seed-VC v1 offline speech model (whisper-small content encoder, BigVGAN 22 kHz)

Options: voice (am_michael here; the say.py preset uses am_fenrir, round 5), speed (1.0), steps (30, diffusion steps), cfg (0.7, inference-cfg-rate),
ref_s (25, seconds of the reference used; Seed-VC's window is 30 s for reference plus source together),
length (1.0, length_adjust), fp16 (1).
"""

import os
import sys
from pathlib import Path

import numpy as np
import torch

SRC = Path(os.environ.get("TTS_HOME", Path(sys.executable).parents[3])) / "seedvc" / "src"
sys.path.insert(0, str(SRC))

from _common import read_job, run  # noqa: E402

KSR = 24000


def _kokoro(pipe, text, voice, speed):
    chunks = [r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
              for r in pipe(text, voice=voice, speed=speed) if r.audio is not None]
    return np.concatenate(chunks).astype(np.float32)


def load(job):
    import librosa
    import yaml
    from huggingface_hub import hf_hub_download
    from kokoro import KPipeline
    from modules.commons import build_model, load_checkpoint, recursive_munch
    from modules.audio import mel_spectrogram
    from modules.campplus.DTDNN import CAMPPlus
    from modules.bigvgan import bigvgan
    from transformers import AutoFeatureExtractor, WhisperModel
    import torchaudio

    torch.manual_seed(job["seed"])
    o = job.get("options", {})
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    st = {"voice": o.get("voice", "am_michael"), "speed": float(o.get("speed", 1.0)),
          "steps": int(o.get("steps", 30)), "cfg": float(o.get("cfg", 0.7)), "length": float(o.get("length", 1.0)),
          "fp16": bool(int(o.get("fp16", 1))), "dev": dev}
    st["pipe"] = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")

    ckpt = hf_hub_download("Plachta/Seed-VC", "DiT_seed_v2_uvit_whisper_small_wavenet_bigvgan_pruned.pth")
    cfg = yaml.safe_load(open(hf_hub_download("Plachta/Seed-VC", "config_dit_mel_seed_uvit_whisper_small_wavenet.yml")))
    mp = recursive_munch(cfg["model_params"])
    mp.dit_type = "DiT"
    model = build_model(mp, stage="DiT")
    model, *_ = load_checkpoint(model, None, ckpt, load_only_params=True, ignore_modules=[], is_distributed=False)
    for k in model:
        model[k].eval().to(dev)
    model.cfm.estimator.setup_caches(max_batch_size=1, max_seq_length=8192)
    st["model"] = model

    camp = CAMPPlus(feat_dim=80, embedding_size=192)
    camp.load_state_dict(torch.load(hf_hub_download("funasr/campplus", "campplus_cn_common.bin"), map_location="cpu"))
    st["camp"] = camp.eval().to(dev)

    voc = bigvgan.BigVGAN.from_pretrained(mp.vocoder.name, use_cuda_kernel=False)
    voc.remove_weight_norm()
    st["voc"] = voc.eval().to(dev)

    wname = mp.speech_tokenizer.name
    wm = WhisperModel.from_pretrained(wname, torch_dtype=torch.float16).to(dev)
    del wm.decoder
    wfe = AutoFeatureExtractor.from_pretrained(wname)

    def semantic(w16):
        x = wfe([w16.squeeze(0).cpu().numpy()], return_tensors="pt", return_attention_mask=True)
        f = wm._mask_input_features(x.input_features, attention_mask=x.attention_mask).to(dev)
        with torch.no_grad():
            s = wm.encoder(f.to(wm.encoder.dtype), return_dict=True).last_hidden_state.float()
        return s[:, :w16.size(-1) // 320 + 1]
    st["semantic"] = semantic

    sp = cfg["preprocess_params"]["spect_params"]
    sr = cfg["preprocess_params"]["sr"]
    margs = {"n_fft": sp["n_fft"], "win_size": sp["win_length"], "hop_size": sp["hop_length"],
             "num_mels": sp["n_mels"], "sampling_rate": sr, "fmin": sp.get("fmin", 0),
             "fmax": None if sp.get("fmax", "None") == "None" else 8000, "center": False}
    st["mel"] = lambda x: mel_spectrogram(x, **margs)
    st["sr"], st["hop"] = sr, sp["hop_length"]

    # The reference: prompt mel, its content features and the speaker style, computed once.
    ref = librosa.load(job["ref"], sr=sr)[0][: int(sr * float(o.get("ref_s", 25)))]
    ref = torch.tensor(ref).unsqueeze(0).float().to(dev)
    r16 = torchaudio.functional.resample(ref, sr, 16000)
    with torch.no_grad():
        st["mel2"] = st["mel"](ref)
        _ = st["mel2"].size(2)
        st["prompt"] = model.length_regulator(semantic(r16), ylens=torch.LongTensor([st["mel2"].size(2)]).to(dev),
                                              n_quantizers=3, f0=None)[0]
        fb = torchaudio.compliance.kaldi.fbank(r16.cpu(), num_mel_bins=80, dither=0, sample_frequency=16000)
        st["style"] = st["camp"]((fb - fb.mean(dim=0, keepdim=True)).unsqueeze(0).to(dev))
    return st


@torch.no_grad()
def convert(st, audio24):
    import librosa
    import torchaudio
    dev, sr, hop = st["dev"], st["sr"], st["hop"]
    src = torch.tensor(librosa.resample(audio24, orig_sr=KSR, target_sr=sr)).unsqueeze(0).float().to(dev)
    s16 = torchaudio.functional.resample(src, sr, 16000)
    S = st["semantic"](s16)  # sentences are well under Whisper's 30 s
    mel = st["mel"](src)
    cond = st["model"].length_regulator(S, ylens=torch.LongTensor([int(mel.size(2) * st["length"])]).to(dev),
                                        n_quantizers=3, f0=None)[0]
    mel2, prompt, style = st["mel2"], st["prompt"], st["style"]
    window = sr // hop * 30 - mel2.size(2)
    ov_f, ov_w = 16, 16 * hop
    out, prev, done = [], None, 0
    while done < cond.size(1):
        chunk = cond[:, done:done + window]
        last = done + window >= cond.size(1)
        cat = torch.cat([prompt, chunk], dim=1)
        with torch.autocast(device_type=dev.type, dtype=torch.float16 if st["fp16"] else torch.float32):
            vc = st["model"].cfm.inference(cat, torch.LongTensor([cat.size(1)]).to(dev), mel2, style, None,
                                           st["steps"], inference_cfg_rate=st["cfg"])[:, :, mel2.size(-1):]
        w = st["voc"](vc.float()).squeeze().cpu().numpy()
        if prev is not None:
            fo = np.cos(np.linspace(0, np.pi / 2, ov_w)) ** 2
            w[:ov_w] = w[:ov_w] * fo[::-1] + prev * fo
        if last:
            out.append(w)
            break
        out.append(w[:-ov_w])
        prev = w[-ov_w:]
        done += vc.size(2) - ov_f
    w = np.concatenate(out).astype(np.float32)
    peak = float(np.max(np.abs(w))) if w.size else 0.0
    return w * (0.95 / peak) if peak > 0.95 else w  # BigVGAN can overshoot: 47 clipped samples in 6 lines unscaled


def speak(st, text):
    return convert(st, _kokoro(st["pipe"], text, st["voice"], st["speed"])), st["sr"]


if __name__ == "__main__":
    run(read_job(), load, speak)
