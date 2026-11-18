"""Kokoro (hexgrad, 82M) for the English, then Seed-VC (Plachtaa, GPL-3.0) for the timbre: zero-shot voice
conversion by a diffusion transformer conditioned on the reference clip. Stronger than OpenVoice's tone-colour
swap (README.md, round 5). PyTorch on the Apple GPU (MPS); Kokoro itself on the CPU. Env: tts/seedvc, with the
Seed-VC source checked out in tts/seedvc/src.

  kokoro-seedvc   Kokoro, then Seed-VC. Two Seed-VC models:
                  f0=0: v1 offline speech model (whisper-small content encoder, BigVGAN 22 kHz); the pitch is
                        re-made by the model from the content, so Kokoro's melody is only roughly kept
                  f0=1: the pitch-conditioned (singing) model, 44 kHz BigVGAN: Kokoro's own pitch curve (RMVPE)
                        moved to the reference's median is fed in, so the melody is Kokoro's (README.md, round 6)

Options: voice (am_michael here; the say.py preset uses am_fenrir, round 5), speed (1.0), steps (30, diffusion steps),
cfg (0.7, inference-cfg-rate), ref_s (25, seconds of the reference used; Seed-VC's window is 30 s for reference plus
source together), length (1.0, length_adjust), fp16 (1), pause (0: at least this many seconds of pause at each
sentence end of Kokoro's take, which sometimes has none), f0 (0), and with f0=1 only: qrise (0, semitones above the
question's median that a yes/no question's last word rises to) and whrise (0, the same for a question with a question
word: what, which, how, ...), semi (0, semitones the whole pitch curve is moved after matching the reference's median).
Kokoro speaks a question with the same falling end as a statement (round 6), so the rise is drawn into the pitch
curve that the f0 model follows.
"""

import os
import re
import sys
from pathlib import Path

import numpy as np
import torch

SRC = Path(os.environ.get("TTS_HOME", Path(sys.executable).parents[3])) / "seedvc" / "src"
sys.path.insert(0, str(SRC))

from _common import read_job, run  # noqa: E402

KSR = 24000
AUX = set("is are am was were do does did can could will would should shall have has had may might must "
          "isn't aren't wasn't weren't don't doesn't didn't can't couldn't won't wouldn't shouldn't haven't hasn't".split())
WH = set("what which why how where when who whom whose".split())
END = re.compile(r"[.?!]+[\"')\]\u201d\u2019]*")  # a sentence-end token


def _kokoro(pipe, text, voice, speed):
    """-> (audio at 24 kHz, [(word, start, end)] in seconds; punctuation tokens included)."""
    chunks, toks, at = [], [], 0.0
    for r in pipe(text, voice=voice, speed=speed):
        if r.audio is None:
            continue
        a = r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
        for t in (r.tokens or []):
            if t.start_ts is not None and t.end_ts is not None:
                toks.append((t.text, at + t.start_ts, at + t.end_ts))
        chunks.append(a)
        at += len(a) / KSR
    return np.concatenate(chunks).astype(np.float32), toks


def question_kind(words):
    """Words of one question -> 'yn' (yes/no: rises) or 'wh' (has a question word). The last clause that starts with
    an auxiliary or a question word decides ('So, is this ...?' yn; 'If a session dies, how does ...?' wh)."""
    text = " ".join(words)
    for clause in reversed(re.split(r"[,:;—–]", text)):
        w = re.sub(r"[^a-z']", "", (clause.split() or [""])[0].lower())
        if w in AUX:
            return "yn"
        if w in WH:
            return "wh"
    return "wh" if any(re.sub(r"[^a-z]", "", w.lower()) in WH for w in words) else "yn"


def questions(toks):
    """Kokoro's tokens -> [(kind, sentence start, start, end)]: where each question starts, and where its last word is
    spoken (at least 0.35 s, reaching back into the word before when the last one is short)."""
    out, sent = [], []
    for i, (txt, s, e) in enumerate(toks):
        if END.fullmatch(txt.strip()):
            if "?" in txt and sent:
                end = sent[-1][2]
                start = sent[-1][1]
                for w in reversed(sent):
                    if end - start >= 0.35:
                        break
                    start = w[1]
                out.append((question_kind([w[0] for w in sent]), sent[0][1], start, end))
            sent = []
        elif re.search(r"\w", txt):
            sent.append((txt, s, e))
    return out


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
          "fp16": bool(int(o.get("fp16", 1))), "dev": dev, "f0": bool(int(o.get("f0", 0))),
          "qrise": float(o.get("qrise", 0)), "whrise": float(o.get("whrise", 0)), "semi": float(o.get("semi", 0)),
          "pause": float(o.get("pause", 0))}
    st["pipe"] = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")

    if st["f0"]:
        ckpt = hf_hub_download("Plachta/Seed-VC", "DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema_v2.pth")
        cfg = yaml.safe_load(open(hf_hub_download("Plachta/Seed-VC", "config_dit_mel_seed_uvit_whisper_base_f0_44k.yml")))
    else:
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

    if st["f0"]:
        from modules.rmvpe import RMVPE
        rm = RMVPE(hf_hub_download("lj1995/VoiceConversionWebUI", "rmvpe.pt"), is_half=False, device=dev)
        st["pitch"] = lambda w16: rm.infer_from_audio(w16.squeeze(0), thred=0.03)  # 100 frames per second

    sp = cfg["preprocess_params"]["spect_params"]
    sr = cfg["preprocess_params"]["sr"]
    margs = {"n_fft": sp["n_fft"], "win_size": sp["win_length"], "hop_size": sp["hop_length"],
             "num_mels": sp["n_mels"], "sampling_rate": sr, "fmin": sp.get("fmin", 0),
             "fmax": None if sp.get("fmax", "None") == "None" else 8000, "center": False}
    st["mel"] = lambda x: mel_spectrogram(x, **margs)
    st["sr"], st["hop"] = sr, sp["hop_length"]

    # The reference: prompt mel, its content features (and pitch) and the speaker style, computed once.
    ref = librosa.load(job["ref"], sr=sr)[0][: int(sr * float(o.get("ref_s", 25)))]
    ref = torch.tensor(ref).unsqueeze(0).float().to(dev)
    r16 = torchaudio.functional.resample(ref, sr, 16000)
    with torch.no_grad():
        st["mel2"] = st["mel"](ref)
        f0r = None
        if st["f0"]:
            f0r = torch.from_numpy(st["pitch"](r16)).float().to(dev)[None]
            st["ref_logf0"] = float(torch.median(torch.log(f0r[f0r > 1])))
        st["prompt"] = model.length_regulator(semantic(r16), ylens=torch.LongTensor([st["mel2"].size(2)]).to(dev),
                                              n_quantizers=3, f0=f0r)[0]
        fb = torchaudio.compliance.kaldi.fbank(r16.cpu(), num_mel_bins=80, dither=0, sample_frequency=16000)
        st["style"] = st["camp"]((fb - fb.mean(dim=0, keepdim=True)).unsqueeze(0).to(dev))
    return st


def bend(f0, regions, qrise, whrise):
    """Pitch curve (100 frames/s, 0 = unvoiced) -> the same with each question's end rising instead of Kokoro's fall:
    over the last word the voiced frames glide smoothly from where they start up to `qrise` (yes/no) or `whrise`
    (question word) semitones above the question's own median pitch (and at least 2 semitones above the start)."""
    f0 = f0.copy()
    for kind, s0, t0, t1 in regions:
        rise = qrise if kind == "yn" else whrise
        i0, i1 = int(t0 * 100), min(len(f0), int(round(t1 * 100)) + 1)
        idx = [i for i in range(i0, i1) if f0[i] > 1]
        sent = f0[int(s0 * 100):i1]
        if not rise or len(idx) < 3 or not (sent > 1).any():
            continue
        base = float(np.median(f0[idx[:3]]))
        top = max(float(np.median(sent[sent > 1])) * 2 ** (rise / 12), base * 2 ** (2 / 12))
        x = (np.array(idx) - idx[0]) / max(idx[-1] - idx[0], 1)
        f0[idx] = base * (top / base) ** (3 * x ** 2 - 2 * x ** 3)
    return f0


@torch.no_grad()
def convert(st, audio24, regions=()):
    import librosa
    import torchaudio
    dev, sr, hop = st["dev"], st["sr"], st["hop"]
    src = torch.tensor(librosa.resample(audio24, orig_sr=KSR, target_sr=sr)).unsqueeze(0).float().to(dev)
    s16 = torchaudio.functional.resample(src, sr, 16000)
    S = st["semantic"](s16)  # paragraphs are cut to well under Whisper's 30 s
    mel = st["mel"](src)
    f0 = None
    if st["f0"]:
        f = st["pitch"](s16)
        v = f > 1
        if v.any():  # Kokoro's curve, moved so its median is the reference's (auto f0 adjust), then the questions
            f[v] = np.exp(np.log(f[v]) - np.median(np.log(f[v])) + st["ref_logf0"]) * 2 ** (st["semi"] / 12)
        f = bend(f, regions, st["qrise"], st["whrise"])
        f0 = torch.from_numpy(f).float().to(dev)[None]
    cond = st["model"].length_regulator(S, ylens=torch.LongTensor([int(mel.size(2) * st["length"])]).to(dev),
                                        n_quantizers=3, f0=f0)[0]
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
    return np.concatenate(out).astype(np.float32)


def pieces(toks, total_s, max_s):
    """Where to cut Kokoro's take so each piece fits Seed-VC's window (max_s seconds of speech): in the middle of the
    pause of a sentence end (or else a comma) as late as fits. -> cut times in seconds."""
    pauses = [((s + e) / 2, 0 if re.search(r"[.?!]", t) else 1) for t, s, e in toks
              if re.fullmatch(r"[^\w\s]+", t.strip() or "x")]
    cuts, last = [], 0.0
    while total_s - last > max_s:
        fit = [p for p in pauses if last + 1.0 < p[0] <= last + max_s]
        if not fit:
            cuts.append(last + max_s)
        else:
            best = min(p[1] for p in fit)
            cuts.append(max(p[0] for p in fit if p[1] == best))
        last = cuts[-1]
    return cuts


def lengthen_pauses(audio, toks, least):
    """Kokoro's take of a paragraph sometimes runs one sentence into the next (0.05 s for the "?" in "Which files did it
    change? Which commands did it run?", the voice never going quiet). At each sentence end (. ? !) where the voice is
    quiet (under -50 dBFS) for less than `least` seconds, silence is put in at the quietest 10 ms of the pause, faded
    10 ms either side, to make it `least`. -> (audio, tokens with their times moved)."""
    if least <= 0:
        return audio, toks
    out, last, moved = [], 0, []
    fade, hop = int(0.01 * KSR), int(0.01 * KSR)
    audio = audio.copy()
    for txt, s, e in toks[:-1]:  # not after the last sentence
        if not END.fullmatch(txt.strip()):
            continue
        a, b = max(int((s - 0.03) * KSR), last + fade), min(int((e + 0.03) * KSR), len(audio) - fade)
        if b - a < hop:
            continue
        rms = [float(np.sqrt(np.mean(audio[i:i + hop] ** 2))) for i in range(a, b - hop + 1, hop)]
        at = a + int(np.argmin(rms)) * hop + hop // 2
        quiet, run = 0, 0  # the longest stretch under -50 dBFS around the pause, in 10 ms steps
        for i in range(max(int((s - 0.25) * KSR), 0), min(int((e + 0.25) * KSR), len(audio)) - hop, hop):
            run = run + 1 if np.sqrt(np.mean(audio[i:i + hop] ** 2)) < 10 ** (-50 / 20) else 0
            quiet = max(quiet, run)
        add = least - quiet * hop / KSR
        if add < 0.02:
            continue
        head = audio[last:at].copy()
        head[-fade:] *= np.linspace(1, 0, fade)
        audio[at:at + fade] *= np.linspace(0, 1, fade)
        out += [head, np.zeros(int(add * KSR), np.float32)]
        moved.append((at / KSR, add))
        last = at
    out.append(audio[last:])

    def mv(t):
        return t + sum(d for at, d in moved if at <= t)
    return np.concatenate(out).astype(np.float32), [(txt, mv(s), mv(e)) for txt, s, e in toks]


def speak(st, text):
    """Kokoro speaks the whole text in one go (a paragraph: it hears the sentences around each one); Seed-VC converts
    it in pieces cut at pauses when it is longer than the window the reference leaves."""
    audio, toks = _kokoro(st["pipe"], text, st["voice"], st["speed"])
    audio, toks = lengthen_pauses(audio, toks, st["pause"])
    regions = questions(toks) if st["f0"] else []
    max_s = (st["sr"] // st["hop"] * 30 - st["mel2"].size(2)) * st["hop"] / st["sr"] - 0.5
    cuts = [0.0] + pieces(toks, len(audio) / KSR, max_s) + [len(audio) / KSR]
    out = []
    for a, b in zip(cuts, cuts[1:]):
        seg = audio[int(a * KSR):int(b * KSR)]
        reg = [(k, max(s0 - a, 0), t0 - a, t1 - a) for k, s0, t0, t1 in regions if a <= t0 < b]
        w = convert(st, seg, reg)
        n = int(round((b - a) * st["sr"]))  # keep the timing: each piece exactly as long as its source
        out.append(np.pad(w, (0, max(0, n - len(w))))[:n])
    w = np.concatenate(out)
    peak = float(np.max(np.abs(w))) if w.size else 0.0  # BigVGAN can overshoot: 47 clipped samples in 6 lines unscaled
    return (w * (0.95 / peak) if peak > 0.95 else w), st["sr"]


if __name__ == "__main__":
    run(read_job(), load, speak)
