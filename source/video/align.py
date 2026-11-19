#!/usr/bin/env python3
"""Word times for each sentence clip, so a picture that changes mid-sentence lands on the word where its line starts.

Two halves:
- run in the whisper venv (`.claude/loops/tts/whisper/venv`, mlx-whisper, MIT) as a batch:
      python align.py --model <hf id or folder> --batch jobs.json
  jobs.json: [{"wav": ..., "text": ..., "out": ...}]; each out gets {"words": [[word, start, end], ...]} in seconds.
  The model is loaded once. The script's own text goes in as the prompt, which keeps the words close to ours; a job's
  "prompt", if it has one, goes in instead (a recorded take: rec.verbatim(), which keeps fillers and repeats).
- imported by build.py (no mlx needed): line_times() matches those words to the known script words and returns where
  each line of the sentence starts; words it cannot match are placed by character count between matched neighbours,
  and a sentence with too few matches falls back to character-proportional timing.
"""
import difflib, json, re, sys
from pathlib import Path

DEFAULT_MODEL = 'mlx-community/whisper-large-v3-turbo'


def norm(w):
    return re.sub(r'[^a-z0-9]', '', w.lower())


def line_times(lines, words, vs, ve, min_match=0.5):
    """lines: the sentence's spoken lines in order. words: [[word, start, end]] in seconds within the clip (or None).
    vs, ve: where the voice starts and ends in the clip (from its loudness).
    -> (starts: one time per line, how: 'aligned' | 'interpolated' | 'proportional', matched fraction)
    'interpolated' means at least one line after the first starts on a word whisper did not give us."""
    toks, pos = [], 0  # (normalised word, line index, char position)
    first_tok = []
    for j, ln in enumerate(lines):
        first_tok.append(len(toks))
        for w in ln.split():
            n = norm(w)
            if n:
                toks.append((n, j, pos))
            pos += len(w) + 1
    total = max(pos - 1, 1)
    line_pos = []
    p = 0
    for ln in lines:
        line_pos.append(p); p += len(ln) + 1

    def proportional():
        return [vs + (ve - vs) * lp / total for lp in line_pos]

    hyp = [(norm(w), s, e) for w, s, e in (words or []) if norm(w)]
    if not toks or not hyp:
        return proportional(), 'proportional', 0.0
    sm = difflib.SequenceMatcher(None, [t[0] for t in toks], [x[0] for x in hyp], autojunk=False)
    start = [None] * len(toks)
    anchors = [(0, vs)]
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            start[a + k] = hyp[b + k][1]
            anchors.append((toks[a + k][2], hyp[b + k][1]))
    anchors.append((total, ve))
    frac = sum(s is not None for s in start) / len(toks)
    if frac < min_match:
        return proportional(), 'proportional', frac
    anchors.sort()
    mono = []  # times must not run backwards
    for cp, t in anchors:
        if not mono or (t >= mono[-1][1] and cp > mono[-1][0]):
            mono.append((cp, t))

    def at(cp):
        for (c0, t0), (c1, t1) in zip(mono, mono[1:]):
            if c0 <= cp <= c1:
                return t0 + (t1 - t0) * (cp - c0) / max(c1 - c0, 1)
        return mono[-1][1]

    starts, how = [vs], 'aligned'
    for j in range(1, len(lines)):
        k = first_tok[j]
        if k < len(toks) and toks[k][1] == j and start[k] is not None:
            t = start[k]
        else:
            t = at(line_pos[j]); how = 'interpolated'
        starts.append(min(max(t, starts[-1] + 0.1), ve))
    return starts, how, frac


def resolve_model(model):
    """A Hugging Face id that is already downloaded -> its local folder (works offline, even if the cache lacks the
    README); else the id as given (mlx-whisper downloads it)."""
    if Path(model).is_dir():
        return model
    snaps = Path.home() / '.cache/huggingface/hub' / f'models--{model.replace("/", "--")}' / 'snapshots'
    for d in sorted(snaps.glob('*')) if snaps.exists() else []:
        if (d / 'config.json').exists() and (any(d.glob('*.safetensors')) or (d / 'weights.npz').exists()):
            return str(d)
    return model


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default=DEFAULT_MODEL)
    ap.add_argument('--batch', required=True)
    a = ap.parse_args()
    import mlx_whisper
    model = resolve_model(a.model)
    jobs = json.loads(Path(a.batch).read_text(encoding='utf-8'))
    for i, j in enumerate(jobs, 1):
        try:
            r = mlx_whisper.transcribe(j['wav'], path_or_hf_repo=model, word_timestamps=True, language='en',
                                       initial_prompt=j.get('prompt', j['text']), condition_on_previous_text=False, verbose=None)
            words = [[w['word'].strip(), round(w['start'], 3), round(w['end'], 3)]
                     for s in r.get('segments', []) for w in s.get('words', [])]
        except Exception as e:  # one bad clip falls back to proportional timing in build.py, it does not stop the run
            print(f'align.py: {Path(j["wav"]).name}: {e}', file=sys.stderr)
            words = None
        tmp = Path(j['out'] + '.part')
        tmp.write_text(json.dumps(dict(words=words, model=a.model)), encoding='utf-8')
        tmp.replace(j['out'])
        if i % 10 == 0 or i == len(jobs):
            print(f'  aligned {i}/{len(jobs)}', flush=True)


if __name__ == '__main__':
    main()
