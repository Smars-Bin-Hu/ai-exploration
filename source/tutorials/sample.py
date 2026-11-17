# A test deck for build.py: a contents page, steps pages of 2, 3 and 4 shots (one of them a placeholder),
# then one page of each older kind (a screenshot page and a placeholder page with a kicker and title).
# Build: .venv/bin/python source/tutorials/build.py sample   -> source/tutorials/_sample/Sample.pdf
# The words test the layout only: they are not checked against the harness. Only the sample may leave out COVER and CLOSING.

A = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/'

COVER = None
CONTENTS = True

PAGES = [
 dict(group='Start', steps=[
   dict(pic=A + 'enter.png', text='When every line at the bottom left is green, press **Enter**.'),
   dict(pic=A + 'board-list.png', text='The board lists your tasks. Press **New task**.'),
  ]),

 dict(group='Give the requirement', steps=[
   dict(pic=(A + 'task-intake.png', (0, 0, 1160, 1300)), text='Say what to do, and in which repository.'),
   dict(pic=A + 'talk-to-agent.png', text='Answer the agent’s questions in the chat.'),
   dict(pic=A + 'task-overview.png', text='The task page shows where it stands.'),
  ]),

 dict(group='Approve', steps=[
   dict(pic=A + 'task-plan.png', text='Read the plan.'),
   dict(pic=A + 'approve-dialog.png', text='Press **Approve** when it is right.'),
   dict(shot='The Copilot chat in VS Code after the plan is approved', text='The agent starts the work.'),
   dict(pic=A + 'held-write.png', text='A held write waits for you.'),
  ],
  notes='Steps pages take notes too: list the sources here.'),

 dict(group='Older page kinds', kicker='Step 1 · Open the board', title='Press Enter on the board',
  text=[
   'Start the harness with the **Start Harness** shortcut. The board opens in your browser.',
   'When every line at the bottom left is green, press **Enter**.',
   ('small', 'If Enter stays grey, open the line that is not green: it says what to fix.'),
  ],
  pic=A + 'enter.png',
  caption='The Enter screen. Its words here are not checked: this is a test page.'),

 dict(kicker='Step 2 · Open a task', title='Type what you want done',
  text=[
   ('steps', ['Press **New task**.',
              'Type one sentence: what to do, and in which repository.',
              'Press **Start**. A Copilot chat opens in VS Code.']),
  ],
  shot='The New task box on the board, with one sentence typed in'),
]

CLOSING = None
