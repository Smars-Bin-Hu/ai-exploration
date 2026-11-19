"""Slice the polished recordings into 3-12 s utterances at pauses, with their words. Env: whisper venv (mlx-whisper).
Step 1 of README.md, round 7; then make_list.py, features.sh, train_sovits.sh, train_gpt.sh.

    T=.claude/loops/tts
    $T/whisper/venv/bin/python source/video/tts/gptsovits/slices.py $T/gptsovits/data/raw/*.wav \
        --out $T/gptsovits/data/slices

1. Whisper (large-v3-turbo) with word times on each whole file.
2. Cut points: gaps between words of at least 0.18 s; a slice ends at a gap, preferring a sentence end, and is 3-12 s.
3. Each slice is cut at the middle of the gaps around it (at most 0.25 s of silence kept each side), 32 kHz mono.
4. Each slice is transcribed again on its own; a slice whose own transcript differs from the words of the long pass
   by more than one word is dropped (a cut through a word, a mumble).
Writes <out>/<name>.wav and <out>/slices.json.
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"


def norm(t):
    return [w for w in re.sub(r"[^a-z0-9' ]", " ", t.lower().replace("-", " ")).split() if w]


def edits(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[len(b)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wavs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min", type=float, default=3.0)
    ap.add_argument("--max", type=float, default=12.0)
    ap.add_argument("--gap", type=float, default=0.18)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for wav in a.wavs:
        stem = Path(wav).stem
        r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL, word_timestamps=True, language="en",
                                   condition_on_previous_text=False, verbose=None)
        words = [(w["word"].strip(), w["start"], w["end"]) for s in r["segments"] for w in s["words"]]
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    wav], capture_output=True, text=True).stdout)
        # greedy: from word i, take words while the slice stays under max; end at the best gap in [min, max]
        i, n = 0, 0
        while i < len(words):
            best = None
            for j in range(i, len(words)):
                span = words[j][2] - words[i][1]
                if span > a.max:
                    break
                gap = (words[j + 1][1] if j + 1 < len(words) else dur) - words[j][2]
                if span >= a.min and gap >= a.gap:
                    score = gap + (1.0 if words[j][0][-1:] in ".?!" else 0.3 if words[j][0][-1:] in ",;:" else 0)
                    if best is None or score >= best[1]:
                        best = (j, score)
            if best is None:  # no good end: skip to the next pause
                j = i
                while j + 1 < len(words) and words[j + 1][1] - words[j][2] < a.gap:
                    j += 1
                i = j + 1
                continue
            j = best[0]
            prev_end = words[i - 1][2] if i else 0.0
            next_start = words[j + 1][1] if j + 1 < len(words) else dur
            t0 = max(words[i][1] - 0.25, (prev_end + words[i][1]) / 2)
            t1 = min(words[j][2] + 0.25, (words[j][2] + next_start) / 2)
            name = f"{stem}_{n:03d}"
            dst = out / f"{name}.wav"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t0:.3f}", "-to",
                            f"{t1:.3f}", "-i", wav, "-ac", "1", "-ar", "32000", str(dst)], check=True)
            text = " ".join(w[0] for w in words[i:j + 1])
            rows.append(dict(name=name, wav=str(dst), src=stem, t0=round(t0, 3), t1=round(t1, 3), text=text))
            n += 1
            i = j + 1
    for row in rows:
        r = mlx_whisper.transcribe(row["wav"], path_or_hf_repo=MODEL, language="en",
                                   condition_on_previous_text=False, verbose=None)
        row["heard"] = r["text"].strip()
        row["edits"] = edits(norm(row["text"]), norm(row["heard"]))
        row["keep"] = row["edits"] <= 1
    (out / "slices.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    kept = [r for r in rows if r["keep"]]
    print(f"{len(rows)} slices, {len(kept)} kept, {sum(r['t1'] - r['t0'] for r in kept):.1f} s")
    for r in rows:
        print(f"{'+' if r['keep'] else '-'} {r['name']} {r['t1'] - r['t0']:5.1f}s e{r['edits']} {r['text'][:90]}")


if __name__ == "__main__":
    main()
