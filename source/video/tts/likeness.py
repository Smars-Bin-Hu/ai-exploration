"""Is this still the presenter? WavLM speaker likeness and pitch of each clip against the reference, for say.py's
voice gate and build.py's check of clips made before the gate (README.md, round 4). Env: any Python with torch,
transformers and librosa; say.py uses the chatterbox env (.claude/loops/tts/chatterbox/.venv), which has them.

The job is JSON on stdin, {"ref": ref.wav, "items": [{"wav": ...}, ...]}; one line of JSON per clip on stdout:
{"wav": ..., "sim": cosine of the WavLM x-vectors (microsoft/wavlm-base-plus-sv) of clip and reference,
 "voice_s": seconds from the first to the last sound, "f0": median pitch of the voiced frames (pYIN, Hz),
 "ref_f0": the same for the reference}.
"""

import json
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

warnings.filterwarnings("ignore")


def f0(path):
    """Median pitch of the voiced frames (pYIN on 16 kHz), or None; one clip, in a worker process."""
    import librosa
    import numpy as np
    warnings.filterwarnings("ignore")
    try:
        y, _ = librosa.load(path, sr=16000)
        f, v, _ = librosa.pyin(y, fmin=60, fmax=500, sr=16000, frame_length=1024, hop_length=160)
        f = f[v]
        return round(float(np.median(f)), 1) if len(f) else None
    except Exception:
        return None


def main():
    job = json.load(sys.stdin)
    import librosa
    import numpy as np
    import torch
    from transformers import AutoFeatureExtractor, WavLMForXVector
    from transformers.utils import logging
    logging.set_verbosity_error()
    logging.disable_progress_bar()
    fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-base-plus-sv")
    model = WavLMForXVector.from_pretrained("microsoft/wavlm-base-plus-sv").eval()

    def embed(y):
        with torch.no_grad():
            x = fe(y, sampling_rate=16000, return_tensors="pt", padding=True)
            return torch.nn.functional.normalize(model(**x).embeddings[0], dim=-1).numpy()

    pool = ProcessPoolExecutor(max(1, min(8, (os.cpu_count() or 2) // 2)))  # pYIN is the slow part: in parallel
    pitches = [pool.submit(f0, it["wav"]) for it in job["items"]]
    ref_f0 = f0(job["ref"])
    ref, _ = librosa.load(job["ref"], sr=16000)
    e_ref = embed(ref)
    for it, pitch in zip(job["items"], pitches):
        try:
            y, _ = librosa.load(it["wav"], sr=16000)
            nz = np.where(np.abs(y) > 0.01)[0]
            out = dict(sim=round(float(e_ref @ embed(y)), 3), f0=pitch.result(),
                       voice_s=round(float((nz[-1] - nz[0]) / 16000), 2) if len(nz) else 0.0)
        except Exception as e:  # an unreadable clip fails the gate
            print(f"likeness.py: {it['wav']}: {e}", file=sys.stderr)
            out = dict(sim=0.0, f0=None, voice_s=0.0)
        print(json.dumps(dict(wav=it["wav"], ref_f0=ref_f0, **out)), flush=True)
    pool.shutdown()


if __name__ == "__main__":
    main()
