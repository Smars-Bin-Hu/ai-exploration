# Harness tutorials · 1 A day with the harness: how to operate the harness, one small step per picture.
# Build: .venv/bin/python source/tutorials/build.py 1_day
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/); sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data), cropped to the part each step is about.
# Placeholders (VS Code, and board states with no picture yet) are listed in shots/1_day.md.

B = 'source/tutorials/img/_board/'

COVER = dict(
 sub='How to work with the harness, step by step: start a task, give the requirement, approve, '
     'follow the work, finish it, and pick it up the next day.',
 how=['Start here once the Install deck is done and the board opens in your browser.'],
)

CONTENTS = True

PAGES = [
 # ---- Start -------------------------------------------------------------------------------------------------
 dict(group='Start', steps=[
   dict(shot='Finder (or Explorer) with the harness folder open and Start Harness selected', aspect=16/10,
        text='Double-click **Start Harness**. Keep its terminal window open.'),
   dict(pic=(B + 'enter.png', (40, 925, 910, 1165)),
        text='Wait until every line under **Harness & Local** is green.'),
   dict(pic=(B + 'enter.png', (40, 1180, 910, 1585)),
        text='**From the company** is optional: yellow there never stops Enter.'),
   dict(pic=(B + 'enter.png', (934, 1505, 1810, 1650)),
        text='Press **Enter**. The board opens.'),
  ],
  notes='Sources: docs/01-quickstart.md step 1 (the Enter screen: Harness & Local required, From the company optional, never stops Enter); '
        'messages.en.json board.enter.g.required / board.enter.g.optional.'),

 dict(steps=[
   dict(pic=(B + 'lobby.png', (80, 480, 1900, 1020)),
        text='The **board**: every task, and what waits for you. **Lobby** shows tasks as robots.'),
   dict(pic=(B + 'list.png', (24, 720, 1877, 1270)),
        text='**List** shows a table. The **Do** column has the button for your next move.'),
  ],
  notes='Sources: messages.en.json board.col.*, board.offwork, board.onwork; tasklife.py L856-870 (tasks waiting for you first).'),

 # ---- Start a task ------------------------------------------------------------------------------------------
 dict(group='Start a task', steps=[
   dict(pic=(B + 'lobby.png', (1700, 20, 2200, 130)),
        text='Press **New task**.'),
   dict(pic=(B + 'new-task.png', (32, 105, 1066, 250)),
        text='Give a **Name**. As **Kind**, pick **development** for a code change or bug fix.'),
   dict(pic=(B + 'new-task.png', (32, 940, 1066, 1240)),
        text='**What to do**: what, in which repository (one set up in **Get ready**), when done.'),
  ],
  notes='Sources: messages.en.json board.new.* (New task, Name, Kind, What to do, Ask me first, Create and send), task.kind.dev; '
        'web/chat.js L261-306 (Ask me first adds generic-grill-me); docs/03-configure.md L11 (Code repositories in Get ready); tasklife.py L33-69 (name rules).'),

 dict(steps=[
   dict(pic=(B + 'new-task.png', (32, 1435, 1066, 1515)),
        text='Tick **Ask me first** to have the agent ask what is unclear before it starts.'),
   dict(pic=(B + 'new-task.png', (1098, 113, 2126, 817)),
        text='On the right: the first message the board will send.'),
   dict(pic=(B + 'new-task.png', (20, 1655, 700, 1765)),
        text='Press **Create and send**.'),
   dict(shot='VS Code: the new Copilot chat the board made, with the agent opening the task (harness task new)', aspect=16/10,
        text='A Copilot chat opens in VS Code, and the agent opens the **task**: a folder that outlives the chat.'),
  ],
  notes='Sources: chatnew.py first_message (name and kind given; the agent does not ask for them); messages.en.json board.new.first, board.new.go; core/tasks.py L1-8.'),

 # ---- Give the requirement ----------------------------------------------------------------------------------
 dict(group='Give the requirement', steps=[
   dict(pic=(B + 'live-waiting.png', (277, 1095, 1983, 1673)),
        text='The agent asks what is unclear. Press **Answer...** and pick an option or type.'),
   dict(shot='VS Code: the Copilot chat with the agent’s numbered questions and a typed answer', aspect=16/10,
        text='Or answer in the chat in VS Code.'),
   dict(pic=(B + 'intake.png', (44, 520, 2172, 676)),
        text='Requirement came as documents? Open the task’s **Intake** tab.'),
  ],
  notes='Sources: SKILL.md harness-my-task step 2 (numbered options); messages.en.json task.waiting.asking, task.waiting.question, board.action.question, desk.hint.question.'),

 dict(steps=[
   dict(pic=(B + 'intake.png', (78, 835, 2139, 1150)),
        text='Drop the files, or press **Choose files**. A program converts them, with no AI.'),
   dict(pic=(B + 'intake-files.png', (66, 280, 1000, 700)),
        text='Open **Conversion reports** to see what was left out. Click a file to trim it.'),
   dict(pic=(B + 'intake-files.png', (66, 22, 1385, 294)),
        text='Press **Create INTAKE.md**: a short goal the agent reads first.'),
   dict(pic=(B + 'intake-files.png', (66, 814, 2139, 1125)),
        text='Under **Tell the agent**, press **Copy message** and paste it into the chat.'),
  ],
  notes='Sources: docs/09-intake.md; intake.py L1-10; desk.intake.tell, desk.intake.message, desk.go.copy; taskdesk.py intake_view L509-516 (an open task with REQ.md: no Intake tab on a Q&A task); messages.en.json desk.intake.*.'),


 # ---- Approve -----------------------------------------------------------------------------------------------
 dict(group='Approve', steps=[
   dict(pic=(B + 'requirement.png', (66, 1050, 1720, 1673)),
        text='Open **Requirement** (`REQ.md`). Is each item what you meant? If not, say so in the chat.'),
   dict(pic=(B + 'requirement.png', (72, 290, 2144, 515)),
        text='Right? Press **Confirm requirement**. Needed on development, testing, knowledge base and repository-changing tasks.'),
  ],
  notes='Sources: messages.en.json board.action.confirm-req, desk.hint.confirm-req; taskdesk.py L533-535 (full tier only); templates/task/en/REQ.md.'),

 dict(steps=[
   dict(pic=B + 'approve-code.png',
        text='A window shows the file and a six-character code. Type the code, press **Approve**.'),
   dict(pic=(B + 'plan.png', (66, 764, 1150, 1884)),
        text='Open **Plan**: the files that change, the steps, how it is checked, the risks.'),
  ],
  notes='Sources: messages.en.json board.action.confirm-req, desk.hint.confirm-req, req.screen.*, req.question, approval.ask; approval.py CODE_LENGTH 6; '
        'taskdesk.py L533-535 (waits on every full-tier task: dev, test, kb, and a task raised to change a repository); task.py L570-612.'),

 dict(steps=[
   dict(pic=(B + 'plan.png', (72, 290, 1730, 515)),
        text='Agree? Press **Approve plan**: the same window, its own code, **Approve**. Changes? Say them in the chat.'),
   dict(shot='A task page whose state reads “the plan is approved: tell the agent to go on”, with the Send to agent button', aspect=16/5,
        text='The board usually wakes the agent. If it says “… tell the agent …”, press **Send to agent**.'),
  ],
  notes='Sources: messages.en.json task.waiting.plan, desk.hint.approve-plan, plan.question, task.waiting.go-req, task.waiting.go-plan, task.waiting.go-promote, board.action.send; tasklife.py L273 GO_MARKS; '
        'task.py L428-475 (--with-req: one code confirms the requirement too); docs/01-quickstart.md step 5 points 4-5.'),

 # ---- Follow the work ---------------------------------------------------------------------------------------
 dict(group='Follow the work', steps=[
   dict(pic=(B + 'todo.png', (60, 420, 1250, 1010)),
        text='Now it works on copies in the task folder. **TODO** shows the steps it ticks off.'),
   dict(pic=(B + 'live-waiting.png', (222, 399, 1983, 1064)),
        text='**Live** shows what it does now. Its edit tools cannot write your repository.'),
  ],
  notes='Sources: docs/01-quickstart.md step 5 point 6; gate/handler.py L38-88 (edit tools: DEV/ after the plan, never a target working tree); messages.en.json desk.tab.todo, desk.tab.live.'),

 dict(steps=[
   dict(pic=(B + 'run.png', (73, 299, 2144, 483)),
        text='**waits for your run**: some checks need a run you do, such as on DEV.'),
   dict(pic=(B + 'run.png', (73, 1420, 2144, 2060)),
        text='Run it. Paste the **Output**, add pictures, then press **Save and send to the agent**.'),
   dict(pic=(B + 'run.png', (73, 2050, 520, 2425)),
        text='No chat linked? **Save to the task** only saves. Then **Copy message** it shows into the chat.'),
  ],
  notes='Sources: messages.en.json task.waiting.run, desk.wait.run.form, desk.inbox.* (Save and send to the agent; Save to the task when no chat is linked, as in the picture); '
        'desk.inbox.save, desk.inbox.done (Saved in {folder}/. Now tell the agent:), web/desk.js L945-989 (no bound chat: told false, promptLine); docs/02-features.md L102-103; taskreview.py L320-373 (no check or write-back until the run is back).'),

 dict(steps=[
   dict(pic=(B + 'review.png', (1300, 105, 2200, 200)),
        text='Want checks? Press **Independent review** and pick 1, or write `[review]=1`.'),
   dict(pic=(B + 'review.png', (74, 716, 1150, 960)),
        text='A separate reviewer checks the work. **Review** lists each check. This task asked for 2.'),
   dict(pic=(B + 'review.png', (74, 2001, 2137, 2446)),
        text='A FAIL says what to fix; the agent fixes it. Checks used up? See deck 3.'),
  ],
  notes='Sources: docs/01-quickstart.md step 3 and step 5 point 7; docs/02-features.md (limit n + 2); messages.en.json desk.rv.button, desk.rv.hint, desk.tab.review, '
        'task.waiting.review, board.action.review-extend, board.action.review-waive; task.py L911-928.'),

 # ---- Finish ------------------------------------------------------------------------------------------------
 dict(group='Finish', steps=[
   dict(pic=(B + 'changes-promote.png', (66, 720, 2144, 1518)),
        text='“the promote (write-back repo) waits for your approval”: read every diff on **Changes**.'),
   dict(pic=(B + 'changes-promote.png', (72, 299, 2144, 576)),
        text='That diff is exactly what goes in. Press **Approve promote** and type the code: new branch, uncommitted.'),
  ],
  notes='Sources: messages.en.json task.waiting.promote, desk.hint.approve-promote, promote.question, promote.screen.repo; promote_target.py L1-14; task.py L941-944, L984-1024.'),

 dict(steps=[
   dict(pic=(B + 'list.png', (24, 2030, 1600, 2145)),
        text='Once the agent stops, the board closes the task. Closed does not mean committed.'),
   dict(pic=B + 'commit-message.png',
        text='Open it under **Closed**, tab **Changes**: **Copy commit message**. Commit, push, open the PR yourself.'),
  ],
  notes='Sources: accept.py L186 QUIET_WAITS ("", "stopped", "commit"), L189-218; boardserve.py SWEEP_EVERY 5 s; docs/02-features.md L249; '
        'messages.en.json desk.changes.commit, desk.commit.copy, desk.commit.copy_commands; task.py default_branch L60-72 (feature/<name>, - becomes _).'),

 dict(steps=[
   dict(pic=(B + 'accept.png', (72, 299, 2144, 650)),
        text='A task that changes no repository ends with a summary: **to accept**. Read it.'),
   dict(pic=(B + 'accept.png', (72, 640, 1000, 754)),
        text='Done: **Accept and close**. Something missing: **Not yet**, and say what.'),
  ],
  notes='Sources: SKILL.md harness-my-task step 5; messages.en.json task.waiting.accept, desk.accept.*, board.action.accept; accept.py L45-68, L167-181.'),

 # ---- Next day ----------------------------------------------------------------------------------------------
 dict(group='Next day', steps=[
   dict(pic=(B + 'list.png', (1431, 30, 2352, 120)),
        text='Leaving? **Off work** pauses idle tasks. **Back to work** takes them back.'),
   dict(pic=(B + 'go-on-new-chat.png', (72, 260, 2144, 488)),
        text='Chat gone? **Go on in a new chat**. Words only in the old chat are lost.'),
   dict(shot='VS Code: a new Copilot chat with “Go on with add-gift-wrap” typed in the chat box', aspect=16/10,
        text='Or in a new Copilot chat, type `Go on with <task name>`.'),
  ],
  notes='Sources: messages.en.json board.offwork(.hint), board.onwork(.hint), board.go.new, desk.newchat.tip, desk.hint.newchat; '
        'web/desk.js L405-435; handler.py L124-137; SKILL.md steps 1-3 (task open).'),
]

CLOSING = dict(title='That is the day',
  text=[
   'A task that changes a repository always goes this way: you say what, the agent writes, and you read before each approval: requirement, plan, write-back.',
   'Any other task (a question, an RCA, a design) ends with a summary **to accept**.',
   'Refused, or a call waits for you? Read **2 When the agent is stopped**.',
  ])
