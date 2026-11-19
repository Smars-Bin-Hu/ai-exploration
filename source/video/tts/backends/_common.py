"""Shared by the backends: read the job, write wav, report timing."""

import json
import sys
import time
import wave

import numpy as np


def read_job():
    return json.load(sys.stdin)


def write_wav(path, audio, sr):
    a = np.asarray(audio, dtype=np.float32).reshape(-1)
    a = np.clip(a, -1.0, 1.0)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sr))
        w.writeframes((a * 32767.0).astype("<i2").tobytes())
    return len(a) / float(sr)


def run(job, load, speak):
    """load() -> state; speak(state, text) -> (audio float array, sample rate). A speak() with a third parameter also
    gets the batch item (its "seed", if it has one)."""
    import inspect
    with_item = len(inspect.signature(speak).parameters) >= 3
    t0 = time.perf_counter()
    state = load(job)
    print(f"[say] model loaded in {time.perf_counter() - t0:.1f} s", file=sys.stderr)
    total_c = total_a = 0.0
    for it in job["items"]:
        t = time.perf_counter()
        audio, sr = speak(state, it["text"], it) if with_item else speak(state, it["text"])
        compute = time.perf_counter() - t
        dur = write_wav(it["out"], audio, sr)
        total_c += compute
        total_a += dur
        print(f"[say] {compute:6.2f} s compute  {dur:6.2f} s audio  rtf {compute / max(dur, 1e-6):5.2f}  {it['out']}",
              file=sys.stderr)
    if len(job["items"]) > 1:
        print(f"[say] total {total_c:.1f} s compute for {total_a:.1f} s audio, rtf {total_c / max(total_a, 1e-6):.2f}",
              file=sys.stderr)
