#!/usr/bin/env python3
"""Denoise takes with DeepFilterNet (MIT/Apache-2.0), in its own venv:

    uv venv --python 3.11 .claude/loops/tts/deepfilter/venv
    uv pip install --python .claude/loops/tts/deepfilter/venv/bin/python deepfilternet torch==2.1.2 torchaudio==2.1.2 'numpy<2'
    .claude/loops/tts/deepfilter/venv/bin/python source/video/denoise.py --atten 12 --batch jobs.json

jobs.json: [{"in": wav, "out": wav}], 48 kHz mono 16-bit both. The model (DeepFilterNet3) is loaded once.
--atten: the most it takes off, in dB (its attenuation limit). 12 dB keeps it gentle: on a say-made take with room tone
added it took 5 to 10 dB off the room tone and changed the voice by 0.1 to 0.2 dB in every band from 80 Hz to 16 kHz
(no limit: 7 to 16 dB off, 0.3 dB).
"""
import argparse, json, sys, wave
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--atten', type=float, default=12)
    ap.add_argument('--batch', required=True)
    a = ap.parse_args()
    import numpy as np, torch
    from df.enhance import enhance, init_df
    model, state, _ = init_df(log_level='ERROR', log_file=None)
    for j in json.loads(Path(a.batch).read_text(encoding='utf-8')):
        with wave.open(j['in']) as w:
            assert w.getframerate() == state.sr() and w.getnchannels() == 1, j['in']
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        y = enhance(model, state, torch.from_numpy(x)[None], atten_lim_db=a.atten).numpy()[0]
        tmp = j['out'] + '.part.wav'
        with wave.open(tmp, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(state.sr())
            w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
        Path(tmp).replace(j['out'])


if __name__ == '__main__':
    sys.exit(main())
