#!/usr/bin/env python3
"""Speak text in a cloned voice with a local TTS model.

One sentence:
    python source/video/tts/say.py --model qwen3 --ref ref.wav --text "Hello." --out 01.wav

Many sentences, model loaded once (one "out<TAB>text" per line):
    python source/video/tts/say.py --model qwen3 --ref ref.wav --batch lines.tsv

A batch line may name the sentences around it: "out<TAB>text<TAB>before<TAB>after" (either may be empty). For a
checked model (vibevoice) a line under 7 words is then spoken between its two neighbours (or with the one there is)
and cut out again.

Checked models (vibevoice): every take goes through Demucs (vocals kept: removes the background music VibeVoice
sometimes adds), Whisper and the voice gate (likeness.py: WavLM likeness to the reference and median pitch); a take
with music left in it, too fast or slow for its words, whose words do not match the text, or in another voice (a
woman's, another man's, or all creak) is retaken with another seed, up to --retakes times. See README.md, rounds 3-4.

The reference transcript is read from --ref-text, or else from the file next to
the reference with the same name and a .txt extension.

This script uses only the standard library. It runs the model's own Python
(an isolated venv under .claude/loops/tts/<env>/, see README.md) on
backends/<model>_backend.py and passes the job as JSON on stdin. Output is a mono wav
at the model's own rate (24 kHz; 48 kHz for voxcpm2, 32 kHz for gptsovits, 44 kHz for kokoro-seedvc, 22 kHz for
kokoro-openvoice and kokoro-seedvc-v1);
any other extension (.mp3, .m4a) is converted with ffmpeg.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import re
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # source/video/tts -> repo root
TTS_HOME = Path(os.environ.get("TTS_HOME", REPO / ".claude" / "loops" / "tts"))

# name -> (venv folder under TTS_HOME, backend script, model the backend loads, default options).
# A name with options is a preset; --set KEY=VALUE overrides any option.
MODELS = {
    "chatterbox": ("chatterbox", "chatterbox_backend.py", "chatterbox", {}),
    "chatterbox-calm": ("chatterbox", "chatterbox_backend.py", "chatterbox",
                        {"exaggeration": 0.3, "cfg_weight": 0.3, "temperature": 0.6}),
    "chatterbox-turbo": ("chatterbox", "chatterbox_backend.py", "chatterbox-turbo", {}),
    "chatterbox-turbo-calm": ("chatterbox", "chatterbox_backend.py", "chatterbox-turbo",
                              {"temperature": 0.5, "top_p": 0.9}),
    "f5": ("f5", "f5_backend.py", "f5", {}),
    "gptsovits": ("gptsovits", "gptsovits_backend.py", "gptsovits", {}),
    "kokoro": ("kvc", "kokoro_vc_backend.py", "kokoro", {"voice": "am_michael"}),
    "kokoro-cbvc": ("kvc", "kokoro_vc_backend.py", "kokoro-cbvc", {"voice": "am_michael"}),
    "kokoro-openvoice": ("kvc", "kokoro_vc_backend.py", "kokoro-openvoice", {"voice": "am_michael", "tau": 0.3}),
    "kokoro-seedvc": ("seedvc", "kokoro_seedvc_backend.py", "kokoro-seedvc",
                      {"voice": "am_fenrir", "steps": 30, "f0": 1, "qrise": 6, "whrise": 3, "pause": 0.3}),
    "kokoro-seedvc-v1": ("seedvc", "kokoro_seedvc_backend.py", "kokoro-seedvc", {"voice": "am_fenrir", "steps": 30}),
    "qwen3": ("mlx", "qwen3_backend.py", "qwen3", {}),
    "vibevoice": ("mlx", "vibevoice_backend.py", "vibevoice", {}),
    "voxcpm2": ("mlx", "voxcpm2_backend.py", "voxcpm2", {}),
}


# Models whose takes are cleaned and checked, and the limits a take must meet (README.md, round 3).
CHECKED = {"vibevoice"}
CHECK_VERSION = "c4"      # bump when cleaning, checks or merging change: build.py then remakes those clips
OLD_VERSIONS = ("c3", "c2")  # clips made by these versions stay in use when they pass the voice gate (build.py checks)
SHORT_WORDS = 7           # a line with fewer words is spoken together with its neighbours, when the batch names them
MUSIC_LEFT_DB = -25.0     # loudest 0.5 s of music still in the cleaned take, against the voice
CPS = (5.0, 22.0)         # letters per second of voice; clean takes measured 6.7 to 12.7
MAX_EDITS = 0.1           # word edits allowed, as a share of the words (at least 1; none in a short line)
# The voice gate (README.md, round 4): WavLM likeness to the reference, which falls with the clip's length even for the
# presenter's own speech (5th percentile 0.68 at 1 s, 0.81 at 1.5 s, 0.87 at 2 s, 0.92 at 3 s), so the limit rises
# with the seconds of voice; and the median pitch, which catches the woman's voice VibeVoice sometimes switches to,
# and a line spoken all in creak (pitch at the floor of the tracker), as the end of a joined take often was.
LIKE_LIMIT = (0.50, 0.16, 0.66, 0.88)  # limit = a + b * seconds of voice, kept between the last two
PITCH_UP_ST = 6.0         # median pitch more than this many semitones over the reference's (117 Hz -> 165 Hz)
PITCH_DOWN_ST = 8.0       # or more than this many under it (117 Hz -> 74 Hz): creak all through
DEMUCS_PY = TTS_HOME / "demucs" / ".venv" / "bin" / "python"
LIKENESS_PY = Path(os.environ.get("LIKENESS_PY", TTS_HOME / "chatterbox" / ".venv" / "bin" / "python"))
WHISPER_PY = TTS_HOME / "whisper" / "venv" / "bin" / "python"
HEARD = {"sql": "sequel", "claude": "clawed"}  # how Whisper writes words that pronounce.tsv respells for the model
NUM = dict(zip("0 1 2 3 4 5 6 7 8 9 10".split(), "zero one two three four five six seven eight nine ten".split()))


def _value(v):
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return v


def _norm(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return HEARD.get(w, NUM.get(w, w))


def _tokens(text):
    return [t for t in (_norm(w) for w in text.split()) if t]


def _edits(ref, hyp):
    """Word-level edit distance (substitutions, deletions, insertions)."""
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[len(hyp)]


def _boundary(synth, first_n, words):
    """Whisper words of the joined clip -> (t0, t1): from the end of the first sentence's last word to the start of the
    second's first word, as far as the words can be matched; None if nothing matches."""
    import difflib
    toks = _tokens(synth)
    hyp = [(_norm(w), s0, e0) for w, s0, e0 in words if _norm(w)]
    sm = difflib.SequenceMatcher(None, toks, [h[0] for h in hyp], autojunk=False)
    at = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            at[blk.a + k] = hyp[blk.b + k]
    before = [at[k][2] for k in range(first_n) if k in at]
    after = [at[k][1] for k in range(first_n, len(toks)) if k in at]
    if not before and not after:
        return None
    t0 = before[-1] if before else after[0] - 0.4
    t1 = after[0] if after else before[-1] + 0.4
    if t1 < t0 + 0.04:
        t0, t1 = min(t0, t1) - 0.1, max(t0, t1) + 0.1
    return round(max(t0 - 0.03, 0), 3), round(t1 + 0.03, 3)


def like_limit(voice_s):
    a, b, lo, hi = LIKE_LIMIT
    return round(min(hi, max(lo, a + b * voice_s)), 3)


def voice_flags(m):
    """A likeness.py result -> what is wrong with the voice ([] if it is the presenter's)."""
    flags = []
    if m["sim"] < like_limit(m["voice_s"]):
        flags.append(f'likeness {m["sim"]:.2f} under {like_limit(m["voice_s"]):.2f} for {m["voice_s"]:.1f} s')
    if m["f0"] and m["ref_f0"] and 12 * math.log2(m["f0"] / m["ref_f0"]) > PITCH_UP_ST:
        flags.append(f'pitch {m["f0"]:.0f} Hz, {12 * math.log2(m["f0"] / m["ref_f0"]):+.0f} semitones')
    if m["f0"] and m["ref_f0"] and 12 * math.log2(m["f0"] / m["ref_f0"]) < -PITCH_DOWN_ST:
        flags.append(f'creak: pitch {m["f0"]:.0f} Hz, {12 * math.log2(m["f0"] / m["ref_f0"]):+.0f} semitones')
    return flags


def likeness(wavs, ref):
    """-> {wav: likeness.py result}: WavLM likeness to ref, seconds of voice, median pitch (and the reference's)."""
    if not LIKENESS_PY.exists():
        sys.exit(f"the voice gate needs {LIKENESS_PY} (torch, transformers, librosa; see README.md); "
                 "or set LIKENESS_PY to a Python that has them")
    return {x["wav"]: x for x in _jobs(LIKENESS_PY, HERE / "likeness.py",
                                       {"ref": str(ref), "items": [{"wav": str(w)} for w in wavs]})}


def _jobs(python, script, job):
    """Run a helper script in its own env with a JSON job on stdin -> its JSON result lines."""
    r = subprocess.run([str(python), str(script)], input=json.dumps(job), text=True, capture_output=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-2000:])
        sys.exit(f"{Path(script).name} failed (exit {r.returncode})")
    return [json.loads(x) for x in r.stdout.splitlines() if x.startswith("{")]


def checked(a, items, job, python, backend, env_vars, tmp):
    """Speak, clean (Demucs, vocals kept), check (Whisper, speed) and retake each flagged clip with another seed."""
    for need in (DEMUCS_PY, WHISPER_PY):
        if not need.exists():
            sys.exit(f"{a.model} is checked, which needs {need.parent.parent} (see README.md); or give --no-check")
    def plan_for(it, k):
        """How take k of a line is spoken. A short line with two neighbours is spoken between them; its retakes go
        round the ways to say it (between, after the one before, between, before the one after), since a line that
        keeps coming out in creak or another voice one way often comes out right another way (README.md, round 4)."""
        text, n = it["text"], len(it["text"].split())
        p = dict(it, synth=text, keep=None, first_n=0)
        b, f = it.get("before") or "", it.get("after") or ""
        if n < a.short_words and not a.no_merge and (b or f):
            if b and f:
                b, f = [(b, f), (b, ""), (b, f), ("", f)][k % 4]
            if b and f:  # in the middle of three sentences: the voice, level and pitch of a line inside a paragraph
                p.update(synth=f"{b} {text} {f}", keep="middle", first_n=len(_tokens(b)),
                         second_n=len(_tokens(b)) + len(_tokens(text)))
            elif b:  # the short line ends the joined clip, so it keeps its own falling end
                p.update(synth=f"{b} {text}", keep="after", first_n=len(_tokens(b)))
            else:
                p.update(synth=f"{text} {f}", keep="before", first_n=len(_tokens(text)))
        return p

    takes = [[] for _ in items]
    pending = list(range(len(items)))
    for k in range(a.retakes + 1):
        seed = a.seed + 101 * k
        plan = {i: plan_for(items[i], k) for i in pending}
        raws = {i: str(tmp / f"{i:04d}-t{k}-raw.wav") for i in pending}
        cleans = {i: str(tmp / f"{i:04d}-t{k}-clean.wav") for i in pending}
        sub = dict(job, items=[{"out": raws[i], "text": plan[i]["synth"], "seed": seed} for i in pending])
        r = subprocess.run([str(python), str(HERE / "backends" / backend)], input=json.dumps(sub), text=True,
                           env=env_vars)
        if r.returncode:
            sys.exit(r.returncode)
        heard = {x["wav"]: x for x in _jobs(WHISPER_PY, HERE / "check.py", {"items": [{"wav": raws[i]} for i in pending]})}
        dj = []
        for i in pending:
            d = {"wav": raws[i], "out": cleans[i], "trim": 0.1, "recheck": True}
            if a.keep_takes:
                d["raw_out"] = raws[i][:-8] + "-part.wav"
            if plan[i]["keep"]:
                win = _boundary(plan[i]["synth"], plan[i]["first_n"], heard[raws[i]]["words"])
                if plan[i]["keep"] == "middle":
                    win2 = _boundary(plan[i]["synth"], plan[i]["second_n"], heard[raws[i]]["words"])
                    if win and win2 and win2[0] > win[1]:
                        d["cut"] = [win[0], win[1], "middle", win2[0], win2[1]]
                elif win:
                    d["cut"] = [win[0], win[1], plan[i]["keep"]]
            dj.append(d)
        sep = {x["wav"]: x for x in _jobs(DEMUCS_PY, HERE / "demucs_clean.py", {"items": dj})}
        like = likeness([cleans[i] for i in pending], a.ref)
        still = []
        for i, d in zip(pending, dj):
            m, h = sep[raws[i]], heard[raws[i]]
            words = h["words"]
            if plan[i]["keep"] and "cut_at" in m:
                c = m["cut_at"]
                if plan[i]["keep"] == "middle":
                    words = [w for w in words if c[0] < (w[1] + w[2]) / 2 < c[1]]
                else:
                    words = [w for w in words if ((w[1] + w[2]) / 2 < c) == (plan[i]["keep"] == "before")]
            ref = _tokens(plan[i]["text"])
            ed = _edits(ref, [t for t in (_norm(w[0]) for w in words) if t])
            letters = len(re.sub(r"[^A-Za-z0-9]", "", plan[i]["text"]))
            cps = letters / max(m["voice_s"], 0.05)
            flags = []
            if m["left_music_peak_db"] > MUSIC_LEFT_DB:
                flags.append(f'music left {m["left_music_peak_db"]:+.0f} dB')
            if not CPS[0] <= cps <= CPS[1]:
                flags.append(f"{cps:.0f} letters/s")
            if ed > (max(1, round(MAX_EDITS * len(ref))) if len(ref) >= SHORT_WORDS else 0):
                flags.append(f"{ed} word edits")
            if plan[i]["keep"] and "cut" not in d:
                flags.append("no boundary found")
            lk = like[cleans[i]]
            vflags = voice_flags(lk)
            flags += vflags
            heard_text = " ".join(w[0] for w in words)
            takes[i].append(dict(take=k, seed=seed, flags=flags, heard=heard_text, edits=ed, cps=round(cps, 1),
                                 voice_s=m["voice_s"], music_db=m["music_db"], music_peak_db=m["music_peak_db"],
                                 left_music_peak_db=m["left_music_peak_db"], cut_at=m.get("cut_at"),
                                 sim=lk["sim"], f0=lk["f0"], ref_f0=lk["ref_f0"], voice_flags=vflags,
                                 full=raws[i], raw=d.get("raw_out"), clean=cleans[i], keep=plan[i]["keep"],
                                 spoken=plan[i]["synth"]))
            if flags:
                still.append(i)
        pending = still
        if not pending:
            break
    report = []
    for it, tk in zip(items, takes):
        ok = [t for t in tk if not t["flags"]]
        # none passed: rather a word wrong than another voice; then the fewest wrong words, then the most alike
        best = ok[0] if ok else min(tk, key=lambda t: (len(t["voice_flags"]), t["edits"], len(t["flags"]), -t["sim"]))
        p = dict(keep=best["keep"], synth=best["spoken"])
        shutil.copyfile(best["clean"], it["out"])
        if a.keep_takes:
            kd = Path(a.keep_takes)
            kd.mkdir(parents=True, exist_ok=True)
            stem = Path(it["out"]).stem
            for t in tk:  # raw: as the model made it (cut out of the joined clip for a short line); clean: as kept
                for kind in ("raw", "clean") + (("full",) if t["keep"] else ()):
                    dst = kd / f'{stem}-take{t["take"]}-seed{t["seed"]}-{kind}.wav'
                    shutil.copyfile(t[kind], dst)
                    t[kind] = str(dst)
        line = f'[check] {Path(it["out"]).name}: take {best["take"]} of {len(tk)}'
        line += " ok" if not best["flags"] else f' still flagged: {", ".join(best["flags"])}'
        if p["keep"]:
            line += f' (spoken with the {dict(after="sentence before", before="sentence after", middle="sentences around it")[p["keep"]]})'
        for t in tk:
            if t["flags"]:
                line += f'\n[check]     take {t["take"]} seed {t["seed"]}: {", ".join(t["flags"])}; heard "{t["heard"][:80]}"'
        print(line, file=sys.stderr)
        report.append(dict(out=it["out"], text=it["text"], spoken=p["synth"], chosen=best["take"], takes=tk))
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True, choices=sorted(MODELS))
    p.add_argument("--ref", required=True, help="reference wav of the voice (10-15 s works for all models)")
    p.add_argument("--ref-text", help="exact words spoken in --ref (default: <ref>.txt)")
    p.add_argument("--text", help="the sentence to speak")
    p.add_argument("--out", help="output file (.wav, or .mp3 etc. via ffmpeg)")
    p.add_argument("--batch", help="file of 'out<TAB>text' lines; loads the model once")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                   help="model option, e.g. --set cfg_weight=0.3 (see the backend's docstring)")
    p.add_argument("--no-check", action="store_true", help="checked models: no Demucs, no Whisper, no retakes")
    p.add_argument("--no-merge", action="store_true", help="checked models: speak short lines on their own")
    p.add_argument("--short-words", type=int, default=SHORT_WORDS,
                   help=f"checked models: a line under this many words is spoken with its neighbours (default {SHORT_WORDS})")
    p.add_argument("--retakes", type=int, default=3, help="checked models: retakes of a flagged clip (default 3)")
    p.add_argument("--keep-takes", metavar="DIR", help="checked models: keep every raw and cleaned take here")
    p.add_argument("--report", metavar="FILE", help="checked models: write every take's measures here (JSON)")
    a = p.parse_args()

    ref = Path(a.ref).resolve()
    if not ref.exists():
        sys.exit(f"reference not found: {ref}")
    ref_text = a.ref_text
    if ref_text is None and ref.with_suffix(".txt").exists():
        ref_text = ref.with_suffix(".txt").read_text(encoding="utf-8").strip()

    items = []
    if a.batch:
        for line in Path(a.batch).read_text(encoding="utf-8").splitlines():
            if line.strip():
                out, text, *around = line.split("\t")
                it = {"out": str(Path(out).resolve()), "text": text.strip()}
                if around:
                    it["before"] = around[0].strip()
                if len(around) > 1:
                    it["after"] = around[1].strip()
                items.append(it)
    elif a.text and a.out:
        items.append({"out": str(Path(a.out).resolve()), "text": a.text.strip()})
    else:
        p.error("give --text and --out, or --batch")

    env, backend, base, options = MODELS[a.model]
    options = dict(options)
    for kv in a.set:
        k, _, v = kv.partition("=")
        options[k.strip()] = _value(v.strip())
    python = TTS_HOME / env / ".venv" / "bin" / "python"
    if not python.exists():
        sys.exit(f"model environment not installed: {python.parent.parent} (see README.md)")

    # Backends write wav; convert afterwards when another format was asked for.
    tmp = Path(tempfile.mkdtemp(prefix="say-"))
    convert = []
    for i, it in enumerate(items):
        if not it["out"].lower().endswith(".wav"):
            wav = str(tmp / f"{i:04d}.wav")
            convert.append((wav, it["out"]))
            it["out"] = wav
        Path(it["out"]).parent.mkdir(parents=True, exist_ok=True)

    job = {"model": base, "preset": a.model, "options": options, "ref": str(ref), "ref_text": ref_text,
           "seed": a.seed, "items": items}
    env_vars = dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK="1", TOKENIZERS_PARALLELISM="false")
    if base in CHECKED and not a.no_check:
        checked(a, items, job, python, backend, env_vars, tmp)
    else:
        job["items"] = [{"out": it["out"], "text": it["text"]} for it in items]
        r = subprocess.run([str(python), str(HERE / "backends" / backend)], input=json.dumps(job),
                           text=True, env=env_vars)
        if r.returncode:
            sys.exit(r.returncode)

    for wav, out in convert:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
