"""What did the clip actually say? Whisper transcripts with word times, for say.py's checks. Env: the whisper venv
(.claude/loops/tts/whisper/venv, mlx-whisper, MIT).

The job is JSON on stdin, {"model": ..., "items": [{"wav": ...}, ...]}; one line of JSON per clip on stdout:
{"wav": ..., "text": transcript, "words": [[word, start, end], ...]}.

No prompt is given: with the script's own words as the prompt Whisper tends to write them even where the clip says
something else ("Thank you.", or nothing over music), which is what the check is for.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from align import DEFAULT_MODEL, resolve_model  # noqa: E402


def main():
    job = json.load(sys.stdin)
    import mlx_whisper
    model = resolve_model(job.get("model") or DEFAULT_MODEL)
    for it in job["items"]:
        try:
            r = mlx_whisper.transcribe(it["wav"], path_or_hf_repo=model, word_timestamps=True, language="en",
                                       condition_on_previous_text=False, verbose=None)
            words = [[w["word"].strip(), round(w["start"], 3), round(w["end"], 3)]
                     for s in r.get("segments", []) for w in s.get("words", [])]
            text = r.get("text", "").strip()
        except Exception as e:  # a bad clip is reported as unheard, so say.py retakes it
            print(f"check.py: {Path(it['wav']).name}: {e}", file=sys.stderr)
            words, text = [], ""
        print(json.dumps(dict(wav=it["wav"], text=text, words=words)), flush=True)


if __name__ == "__main__":
    main()
