"""slices.json (from slices.py) -> the GPT-SoVITS list file, "<wav>|<speaker>|en|<text>" per line. Step 2 of README.md,
round 7. Plain Python.

    python3 source/video/tts/gptsovits/make_list.py $T/gptsovits/data/slices/slices.json $T/gptsovits/data/train.list \\
        --hold pain_011 --drop hook_008 hook_011 --force hook_003 hook_009 hook_016 --heard hook_001

Kept: the slices slices.py kept (own transcript within 1 word of the long pass), plus --force; minus --drop and --hold
(held out to score likeness on). The text is the long pass's, or the slice's own transcript for --heard (when the cut
clipped a word the long pass still has). Whisper's "Cloud Code" is written "Claude Code".
"""

import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("slices")
ap.add_argument("out")
ap.add_argument("--hold", nargs="*", default=[])
ap.add_argument("--drop", nargs="*", default=[])
ap.add_argument("--force", nargs="*", default=[])
ap.add_argument("--heard", nargs="*", default=[])
ap.add_argument("--speaker", default="me")
a = ap.parse_args()
lines, total = [], 0.0
for r in json.load(open(a.slices)):
    if r["name"] in a.drop or r["name"] in a.hold or not (r["keep"] or r["name"] in a.force):
        continue
    t = (r["heard"] if r["name"] in a.heard else r["text"]).replace("Cloud Code", "Claude Code").replace(" %", "%")
    lines.append(f'{r["name"]}.wav|{a.speaker}|en|{t[:1].upper() + t[1:]}')
    total += r["t1"] - r["t0"]
open(a.out, "w").write("\n".join(lines) + "\n")
print(f"{len(lines)} slices, {total:.1f} s -> {a.out}")
