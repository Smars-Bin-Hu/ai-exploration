"""Find and remove background music in speech clips with Demucs (MIT). Env: tts/demucs.

Run with the demucs env's Python; the job is JSON on stdin, one result line of JSON per clip on stdout:

    {"model": "htdemucs", "items": [{"wav": "in.wav", "out": "vocals.wav"}, ...]}

"out" is optional: without it the clip is only measured. Further keys of an item, all optional:
- "cut": [t0, t1, "before" | "after"]: first cut the clip at its quietest 20 ms between t0 and t1 (seconds) and keep
  the part before or after; for a short line spoken together with its neighbour. The result's "cut_at" says where.
  [t0, t1, "middle", t2, t3]: cut twice and keep the part between (a short line spoken between both neighbours);
  "cut_at" is then [first, second].
- "trim": seconds of margin: write the vocals stem cut to where its voice is (loudness), with this much around it;
  the result's "voice_s" is the length of the voice, margins not counted.
- "raw_out": also write the clip itself, uncleaned, cut and trimmed the same way (to compare by ear).
- "recheck": true: separate the written vocals stem once more and report what is still not voice as left_music_db,
  left_music_peak_db: music that Demucs could not take out. Each clip is split into a vocals stem and a no-vocals stem
(drums + bass + other). The measures, in dB:
- music_db: loudness of the no-vocals stem over the whole clip, against the vocals stem where it speaks (its loud
  frames). Clean speech leaves only bleed, far below the voice; a music bed comes out as a few dB to -20 dB.
- music_peak_db: the loudest 0.5 s of the no-vocals stem, against the same voice level; catches a short jingle.
- pause_music_db: the no-vocals stem in the pauses (where the vocals stem is 35 dB below its loudest), against the
  same voice level; music is easiest to hear there.
The vocals stem is written at the clip's own rate, mono, 16-bit.
"""

import json
import sys
import wave

import numpy as np
import torch

FRAME = 0.05  # seconds per loudness frame


def read_wav(path):
    with wave.open(path) as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        a = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    return a.reshape(-1, ch).mean(axis=1), sr


def write_wav(path, a, sr):
    a = np.clip(np.asarray(a, dtype=np.float32), -1.0, 1.0)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(sr))
        w.writeframes((a * 32767.0).astype("<i2").tobytes())


def frame_db(a, sr):
    n = max(1, int(FRAME * sr))
    k = len(a) // n
    if k == 0:
        return np.array([-120.0])
    f = a[: k * n].reshape(k, n)
    return 10 * np.log10(np.mean(f ** 2, axis=1) + 1e-12)


def measures(voc, nov, sr):
    vdb, ndb = frame_db(voc, sr), frame_db(nov, sr)
    active = vdb > vdb.max() - 25
    voice = 10 * np.log10(np.mean(10 ** (vdb[active] / 10)) + 1e-12)
    music = 10 * np.log10(np.mean(nov ** 2) + 1e-12)
    w = max(1, int(0.5 / FRAME))
    lin = 10 ** (ndb / 10)
    peak = max(10 * np.log10(np.mean(lin[i:i + w]) + 1e-12) for i in range(0, max(1, len(lin) - w + 1)))
    pause = vdb < vdb.max() - 35
    pause_db = 10 * np.log10(np.mean(lin[pause]) + 1e-12) if pause.sum() >= 4 else None
    return dict(voice_db=round(float(voice), 1), music_db=round(float(music - voice), 1),
                music_peak_db=round(float(peak - voice), 1),
                pause_music_db=None if pause_db is None else round(float(pause_db - voice), 1),
                pause_s=round(float(pause.sum() * FRAME), 2))


def quietest(a, sr, t0, t1):
    """The middle of the quietest 20 ms between t0 and t1 seconds, in samples."""
    n = int(0.02 * sr)
    i0, i1 = max(0, int(t0 * sr)), min(len(a) - n, int(t1 * sr))
    if i1 <= i0:
        return min(max(int((t0 + t1) / 2 * sr), 0), len(a))
    hop = max(1, n // 4)
    best = min(range(i0, i1 + 1, hop), key=lambda i: float(np.mean(a[i:i + n] ** 2)))
    return best + n // 2


def voice_span(a, sr):
    """Start and end of the voice (in samples): frames within 40 dB of the loudest, as build.py's trim does."""
    db = frame_db(a, sr)
    loud = np.nonzero(db > max(db.max() - 40, -55))[0]
    if not len(loud):
        return 0, len(a)
    n = max(1, int(FRAME * sr))
    return int(loud[0] * n), min(len(a), int((loud[-1] + 1) * n))


def main():
    job = json.load(sys.stdin)
    from demucs.apply import apply_model
    from demucs.pretrained import get_model
    import torchaudio.functional as AF

    model = get_model(job.get("model", "htdemucs"))
    model.eval()
    dev = job.get("device") or ("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(dev)
    msr = model.samplerate
    vi = model.sources.index("vocals")
    def separate(a, sr):
        x = torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32))[None]
        x = AF.resample(x, sr, msr) if sr != msr else x
        mix = x.expand(2, -1)
        ref = mix.mean(0)
        mean, std = ref.mean(), ref.std() + 1e-8
        with torch.no_grad():
            src = apply_model(model, ((mix - mean) / std)[None].to(dev), device=dev, shifts=1, split=True,
                              overlap=0.25, progress=False)[0].cpu()
        src = src * std + mean
        voc = src[vi].mean(0)
        nov = (src.sum(0) - src[vi]).mean(0)
        if sr != msr:
            voc = AF.resample(voc[None], msr, sr)[0]
            nov = AF.resample(nov[None], msr, sr)[0]
        return voc.numpy()[: len(a)], nov.numpy()[: len(a)]

    for it in job["items"]:
        a, sr = read_wav(it["wav"])
        res = dict(wav=it["wav"])
        if it.get("cut"):
            t0, t1, keep = it["cut"][:3]
            c = quietest(a, sr, t0, t1)
            if keep == "middle":  # [t0, t1, "middle", t2, t3]: keep what lies between the two cuts
                c2 = quietest(a, sr, *it["cut"][3:5])
                a = a[c:c2]
                res["cut_at"] = [round(c / sr, 3), round(c2 / sr, 3)]
            else:
                a = a[:c] if keep == "before" else a[c:]
                res["cut_at"] = round(c / sr, 3)
        voc, nov = separate(a, sr)
        res.update(measures(voc, nov, sr))
        v0, v1 = voice_span(voc, sr)
        res["voice_s"] = round((v1 - v0) / sr, 3)
        if it.get("trim") is not None:
            m = int(float(it["trim"]) * sr)
            voc, nov, a = voc[max(0, v0 - m):v1 + m], nov[max(0, v0 - m):v1 + m], a[max(0, v0 - m):v1 + m]
        if it.get("raw_out"):
            write_wav(it["raw_out"], a, sr)
        if it.get("out"):
            write_wav(it["out"], voc, sr)
            res["out"] = it["out"]
        if it.get("nov"):
            write_wav(it["nov"], nov, sr)
        if it.get("recheck"):
            v2, n2 = separate(voc, sr)
            m2 = measures(v2, n2, sr)
            res["left_music_db"], res["left_music_peak_db"] = m2["music_db"], m2["music_peak_db"]
        print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
