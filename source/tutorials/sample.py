# A two-page test deck for build.py: one page with a screenshot, one with a placeholder.
# Build: .venv/bin/python source/tutorials/build.py sample   -> source/tutorials/_sample/Sample.pdf
# No COVER and no CLOSING: only the sample may leave out the closing page.

COVER = None

PAGES = [
 dict(kicker='Step 1 · Open the board', title='Press Enter on the board',
  text=[
   'Start the harness with the **Start Harness** shortcut. The board opens in your browser.',
   'When every line at the bottom left is green, press **Enter**.',
   ('small', 'If Enter stays grey, open the line that is not green: it says what to fix.'),
  ],
  pic='.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/enter.png',
  caption='The Enter screen. Its words here are not checked: this is a test page.',
  notes='Source: docs/01-quickstart.md step 1.'),

 dict(kicker='Step 2 · Open a task', title='Type what you want done',
  text=[
   ('steps', ['Press **New task**.',
              'Type one sentence: what to do, and in which repository.',
              'Press **Start**. A Copilot chat opens in VS Code.']),
  ],
  shot='The New task box on the board, with one sentence typed in',
  notes='Placeholder: take this screenshot on the company computer.'),
]

CLOSING = None
