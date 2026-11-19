#!/usr/bin/env python3
"""Check a video's English script for flow problems before any voice is made.

    python3 source/video/lint_script.py <video>          # reads source/courses/<video>/scenes.md (and zh.md)
    python3 source/video/lint_script.py --scenes FILE [--zh FILE]

Flags, one line each (file:line · kind · text):
  split-thought   a sentence that starts with a joining word (But, So, Because, Though, Which, And then...)
                  right after a sentence end in the same paragraph: one thought cut in two; join it with a comma.
  short-alone     a sentence of under 5 words standing alone between two sentence ends in a paragraph:
                  it will sound clipped; join it to the sentence before or after.
  no-paragraphs   a scene with many spoken lines and no blank line: there is nowhere to pause.
  paragraphs      a scene whose paragraph count is far from the Chinese script's (when zh.md is given).
  bare-referent   a sentence or clause ending in this / these / that / those / them / it with no noun after it:
                  a listener may not know what it points to; name the thing.
  question        a line that reads as a question (starts with who/what/why/how/do/does/is/are/can...) but
                  does not end with "?", or ends with "?" but reads as a statement.
Exit status 1 when anything is flagged, so a build script can stop on it.
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
JOINERS = r'(but|so|because|though|although|which|whereas|yet|and then|or else|otherwise|unless|until|while)\b'
QWORDS = r'(who|what|when|where|why|how|which|do|does|did|is|are|was|were|can|could|would|should|will|have|has|isn\'t|aren\'t|don\'t|doesn\'t)\b'


def scenes(path):
    """-> [(scene title, [paragraph: [(line no, text)]])] from a scenes file (blank line = paragraph break)."""
    out, para = [], []
    for no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if line.startswith('## '):
            if out and para:
                out[-1][1].append(para)
            out.append((line[3:], []))
            para = []
        elif not line:
            if out and para:
                out[-1][1].append(para)
            para = []
        elif line.startswith(('@', '//', '# ')) or not out:
            continue
        else:
            para.append((no, re.sub(r'\s+', ' ', re.sub(r'\[(\d*\.\d+|\d+(?:\.\d+)?)\]', ' ', line)).strip()))  # pause marks [.3] are not words
    if out and para:
        out[-1][1].append(para)
    return out


def zh_paragraphs(path):
    """-> {scene number: paragraph count} from the Chinese script (blank-line paragraphs, notes skipped)."""
    counts, cur, n, inpara = {}, None, 0, False
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        m = re.match(r'##\s*(\d+)', line)
        if m:
            if cur is not None:
                counts[cur] = n
            cur, n, inpara = m.group(1), 0, False
        elif not line:
            inpara = False
        elif cur is not None and not re.match(r'^[〔（(].*画面', line):
            if not inpara:
                n += 1
            inpara = True
    if cur is not None:
        counts[cur] = n
    return counts


def lint(scene_file, zh_file=None):
    flags = []
    zh = zh_paragraphs(zh_file) if zh_file and zh_file.exists() else {}
    for title, paras in scenes(scene_file):
        lines = sum(len(p) for p in paras)
        if lines >= 8 and len(paras) == 1:
            flags.append((paras[0][0][0], 'no-paragraphs', f'scene "{title}": {lines} lines, no blank line'))
        num = re.match(r'(\d+)', title)
        if num and num.group(1) in zh and zh[num.group(1)] >= 2:
            want, have = zh[num.group(1)], len(paras)
            if have < want / 2 or have > want * 2 + 2:
                flags.append((paras[0][0][0] if paras else 0, 'paragraphs',
                              f'scene "{title}": {have} paragraphs, the Chinese has {want}'))
        for para in paras:
            text = ' '.join(t for _, t in para)
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
            for i, s in enumerate(sents):
                no = next((n for n, t in para if s[:25] in t), para[0][0])
                if i and re.match(JOINERS, s, re.I) and not s.endswith('?'):
                    flags.append((no, 'split-thought', s[:80]))
                if 0 < i < len(sents) - 1 and len(s.split()) < 5 and not s.endswith('?'):
                    flags.append((no, 'short-alone', s))
                if re.search(r'\b(this|these|that|those|them)[.!?:;,]?$', s, re.I) or re.search(r'\b(these|those)\s*[,:;.!?]', s, re.I):
                    flags.append((no, 'bare-referent', s[:80]))
                body = re.sub(r'^(but|and|so|ok|okay|well)\b,?\s*', '', re.sub(r'^[^:]{1,12}:\s*', '', s), flags=re.I)  # "Three: ..." lead-ins, "But what…?"
                asks = (re.match(QWORDS, body, re.I) or re.search(r',\s*' + QWORDS, body, re.I)) and not re.match(r'(which|what|how|when|where|who)\b[^?]*\b(is|are)\b[^?]*\.$', body, re.I)
                tag = re.search(r',\s*right\?$', s, re.I)  # a tag question ("…, right?") rises like one
                if s.endswith('?') and not asks and not tag and ' or ' not in s:
                    flags.append((no, 'question', f'ends with "?" but reads as a statement: {s[:80]}'))
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('video', nargs='?')
    ap.add_argument('--scenes')
    ap.add_argument('--zh')
    a = ap.parse_args()
    base = ROOT / 'source/courses' / (a.video or '')
    sf = Path(a.scenes) if a.scenes else base / 'scenes.md'
    zf = Path(a.zh) if a.zh else (base / 'zh.md' if a.video else None)
    flags = lint(sf, zf)
    for no, kind, text in flags:
        print(f'{sf.name}:{no} · {kind} · {text}')
    print(f'{len(flags)} flagged' if flags else 'clean')
    sys.exit(1 if flags else 0)


if __name__ == '__main__':
    main()
