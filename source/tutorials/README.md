# Harness tutorials

Picture-book slidedocs for a colleague who has the harness installed and now opens tasks of their own: one step per page, a screenshot and at most about 60 words. English, plain words. Same engine and look as *Install the harness* (`source/install/`, `source/tools/deck.py`).

## Build

From the repo root:

```
.venv/bin/python source/tutorials/build.py 1_day     # one deck
.venv/bin/python source/tutorials/build.py all       # every deck that has a text file (not the sample)
.venv/bin/python source/tutorials/build.py sample    # the two-page test deck, into source/tutorials/_sample/
```

Needs Chrome, and playwright-core from `~/Developer/smarshu.com`. Each deck gives two files: the PowerPoint master `source/tutorials/<slug>.pptx` and the PDF in `AI Exploration/3 Courses/Harness tutorials/`. Page images to look at are in `source/tutorials/_build/<slug>/pages/` (not in git). Once a `.pptx` is edited by hand it is the newer one: export its PDF from PowerPoint and do not rebuild over it.

The build prints `WARNING` when a page has more than about 60 words, a caption longer than one line, or text that runs below the page, and `overflow [...]` lists any text box whose text does not fit. It stops on a screenshot that does not exist, and on a deck (other than the sample) with no closing page.

## The decks

| Slug | Text file | PDF in `AI Exploration/3 Courses/Harness tutorials/` |
| --- | --- | --- |
| `0_must_read` | `0_must_read.py` | `0 MUST READ.pdf` |
| `1_day` | `1_day.py` | `1 A day with the harness.pdf` |
| `2_stopped` | `2_stopped.py` | `2 When the agent is stopped.pdf` |
| `3_checks` | `3_checks.py` | `3 Independent checks.pdf` |
| `4_outside` | `4_outside.py` | `4 Outside systems and connections.pdf` |
| `5_kb` | `5_kb.py` | `5 Knowledge base.pdf` |
| `sample` | `sample.py` | `source/tutorials/_sample/Sample.pdf` (a test, not published) |

The titles and file names are set in `DECKS` at the top of `build.py`, so a text file does not repeat them.

## The text file

One Python file per deck, `source/tutorials/<slug>.py`, with three names:

- `COVER`: a dict, or `None` for no cover. Keys: `sub` (one or two sentences under the title), `how` (optional extra lines). The build puts the title, the kicker *Harness tutorials · n*, the harness version (1.7.45) and the line on bold and Courier there itself.
- `PAGES`: a list of pages, in order (below).
- `CLOSING`: the last page. Keys: `title`, `text` (blocks), optional `kicker` (default *What next*). The build adds, on every deck, the line that points to `AI Exploration/0 MUST READ.pdf` for where to go next. No deck draws its own map of the folder.

A one-page deck, such as `0_must_read`, sets `COVER = None` and `PAGES = []`, and writes its page as `CLOSING`.

### Page kinds

Every page has `kicker` (the small orange line, e.g. `'Step 3 · Answer its questions'`) and `title` (a short heading). Optional on any page: `notes`, the speaker notes, where you list the sources you checked (file and line in harness 1.7.45). The kind follows from the keys:

| Kind | Keys | Layout |
| --- | --- | --- |
| Step with a screenshot | `text`, `pic`, optional `caption`, optional `wide=True` | Text on the left, the screenshot on the right with a thin border, the caption in grey italics under it. `wide=True`: the text across the top, the picture across the page under it. |
| Step with a placeholder | `text`, `shot` | Text on the left; on the right a dashed grey box that says *[Company: screenshot]* and what to take on the company computer. Same look as the placeholders in Install. |
| Step with no picture | `text` only | Text alone, in a wider column. For a short list or a page of explanation. |
| Closing | `CLOSING` (not in `PAGES`) | Your text, an orange rule, then the pointer to `0 MUST READ.pdf`. |

`pic` is a path from the repo root, or a pair `(path, (left, top, right, bottom))` to crop it in pixels. Screenshots can come from anywhere in the repo, for example `.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/` (harness 1.7.45, the first choice) or `source/guide/img/`. The build copies each one into `source/tutorials/img/<slug>/`, and uses that copy when the source is gone, so commit `img/` with the deck. Two screenshots with the same file name in one deck are refused: rename one copy, or use one.

`shot` is one sentence: what the screenshot shows, precise enough for someone to take it without asking, e.g. `'The task page, tab Plan, with Approve plan visible'`. Every placeholder goes into the screenshot list for the person.

### Blocks of text

`text` is a list of blocks. About 60 words a page in all (code is not counted).

- `'A paragraph.'` Inside a string, `**bold**` is what you see on the screen (a button, a label), and `` `code` `` is what you type.
- `('steps', ['First.', 'Then.'])`: a numbered list.
- `('list', ['One.', 'Another.'])`: a list with bullets.
- `('code', 'harness task list\nharness doctor')`: a grey box with what to type, one command per line.
- `('small', 'A side note.')`: a small grey line.
- `('co', ['[Company: what our team does here.]'])`: a dashed grey box the author fills in for the company; every line starts with `[Company:`.

### Example

```python
COVER = dict(sub='What a normal day looks like, from opening the board to your own commit.')

PAGES = [
 dict(kicker='Step 1 · Open the board', title='Press Enter',
  text=['Start the harness with the **Start Harness** shortcut.',
        'When every line at the bottom left is green, press **Enter**.'],
  pic='.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/enter.png',
  caption='The Enter screen.',
  notes='Source: docs/01-quickstart.md step 1.'),

 dict(kicker='Step 2 · Open a task', title='Say what you want done',
  text=[('steps', ['Press **+ New task**.', 'Type what to do, and in which repository.'])],
  shot='The new task form on the board, with one sentence typed in'),
]

CLOSING = dict(title='You are done for today',
  text=['Tomorrow, open the board: the task waits where it stopped.'])
```

`sample.py` is a working file of two pages: one with a screenshot, one with a placeholder. Its words are a test of the layout, not checked against the harness.
