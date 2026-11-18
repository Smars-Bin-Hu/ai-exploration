# Harness tutorials · 1 A day with the harness: one development task (show-delivery-date) from New task to your own commit, then the next days.
# Build: .venv/bin/python source/tutorials/build.py 1_day
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/); sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data). The main line uses one-*.png: the same task on every screen.
# Optional branches (Intake, a run, checks, a task that changes no repository) are one group, "Only if", after the main line.
# The lifecycle picture is drawn in img/1_day/lifecycle.html (rendered to lifecycle.png with headless Chrome).
# Placeholders (VS Code, and the board while a linked chat works) are listed in shots/1_day.md.

B = 'source/tutorials/img/_board/'
ROW = (28, 455, 2350, 665)      # one-* list pictures: the column heads and the row of show-delivery-date
CARD = (72, 294, 2146, 540)     # one-* task pages: the card of what waits for you

COVER = dict(
 sub='One development task, from **New task** to your own commit, on the same task all the way. '
     'Then what comes on the next days.',
 how=['Start once **Install the harness** is done and the board opens in your browser.',
      'Steps that begin “Only if” are for when that case is yours.'],
)

CONTENTS = True

PAGES = [
 # ---- The idea ----------------------------------------------------------------------------------------------
 dict(kicker='Before you start', title='One development task, start to commit',
  text=[('list', [
        'The task folder is the memory: a new chat picks the task up from it.',
        'The agent edits copies in `DEV/`. Only the write-back reaches your repository.',
        'Talk to it in the Copilot chat or on the board. Approve on the board.'])],
  pic='source/tutorials/img/1_day/lifecycle.png', wide=True,
  notes='Sources: docs/01-quickstart.md step 5 (confirm requirement, approve plan, approve promote, each with a code; '
        'the agent changes files in DEV/ and can write the task folder only; promote makes feature/<name> and does not commit; you commit and open the PR); '
        'core/tasks.py L1-8 (a task is a folder that outlives the chat); gate/handler.py L38-88 (edit tools: DEV/ after the plan, never a target working tree); '
        'messages.en.json queue.note (the next task can write into the same repository only after the files of the one before it are committed). '
        'The picture is drawn from img/1_day/lifecycle.html.'),

 # ---- Get ready ---------------------------------------------------------------------------------------------
 dict(group='Get ready', steps=[
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
        'messages.en.json board.enter.g.required / board.enter.g.optional; Start Harness.command L2 (keep this window open).'),

 dict(steps=[
   dict(pic=(B + 'state-get-ready-repos.png', (0, 0, 1464, 225)),
        text='Your repository must be under **Code repositories** (gear, **Change the setup**). The agent changes only these.'),
   dict(pic=(B + 'tour-readybar-red.png', (40, 175, 1790, 445)),
        text='Red, **The agent cannot work right now**: press the button it shows.'),
   dict(pic=(B + 'tour-readybar-yellow.png', (40, 170, 1790, 445)),
        text='Yellow, **Not fully ready for your company’s tasks**: fix it there, or **Hide**.'),
  ],
  notes='Sources: docs/01-quickstart.md step 1 (Get ready / Change the setup, card 3 From the company: code repositories); docs/03-configure.md L3, L105 '
        '(code repositories are the target repositories); setup.repos, setup.repos.hint; gate refusal "only promote writes to it"; '
        'readybar.js L1-5 (red cannot be hidden, yellow has Hide); board.ready.red.title, board.ready.yellow.title, board.ready.hide.'),

 # ---- Start a task ------------------------------------------------------------------------------------------
 dict(group='Start a task', steps=[
   dict(pic=B + 'one-03-list-asked.png',
        text='**List** (or **Lobby**, a robot each): click a task to open it. **Do** holds your next button.'),
   dict(pic=(B + 'one-03-list-asked.png', (1415, 25, 2365, 122)),
        text='Press **New task**, top right.'),
  ],
  notes='Sources: board.js L247 (the name links to the task page), lobby.js L1-5, L20-32 (a click on a robot opens the page); messages.en.json board.mode.*, board.col.*, board.new.*; '
        'tasklife.py L856-870 (tasks waiting for you first).'),

 dict(steps=[
   dict(pic=(B + 'one-01-new-task.png', (35, 115, 1070, 250)),
        text='A **Name**. **Kind**: **development** for a code change or a bug fix.'),
   dict(pic=(B + 'one-01-new-task.png', (35, 970, 1070, 1185)),
        text='**What to do**: what, in which repository, and when it is done.'),
  ],
  notes='Sources: messages.en.json board.new.* (New task, Name, Kind, What to do, Create and send), task.kind.dev; docs/01-quickstart.md §7 '
        '(one sentence: what and which repository; the scope and the standard for done); tasklife.py L33-69 (name rules).'),

 dict(steps=[
   dict(pic=(B + 'one-01-new-task.png', (35, 1480, 1070, 1660)),
        text='Tick **Ask me first**. Its chat runs on allow all; the gate still checks every call.'),
   dict(pic=(B + 'one-01-new-task.png', (1100, 110, 2125, 895)),
        text='On the right: the first message the board will send.'),
   dict(pic=(B + 'one-01-new-task.png', (35, 1700, 450, 1775)),
        text='Press **Create and send**.'),
   dict(shot='VS Code: the new Copilot chat the board made, with the agent opening the task (harness task new)', aspect=16/10,
        text='A Copilot chat opens in VS Code. The agent opens the task folder.'),
  ],
  notes='Sources: chatnew.py first_message (name and kind given; the agent does not ask for them); web/chat.js L261-306 (Ask me first adds generic-grill-me); '
        'the fixed line under Ask me first (interactive mode and allow all permissions; the harness gate still runs before every tool call); messages.en.json board.new.first, board.new.go.'),

 dict(steps=[
   dict(pic=(B + 'one-03-list-asked.png', ROW),
        text='**waits for you**: the agent asked what is unclear. Read its questions.'),
   dict(shot='VS Code: the Copilot chat with the agent’s numbered questions and an answer typed in the chat box', aspect=16/6,
        text='Answer in the chat. With a linked chat, **Answer...** on the board works too.'),
  ],
  notes='Sources: SKILL.md harness-my-task step 2 (numbered options); messages.en.json task.waiting.stopped ("waits for you"), task.waiting.asking, board.action.question; '
        'desk.hint.newchat (no chat linked: Answer... is greyed, as in the picture).'),

 # ---- Approve -----------------------------------------------------------------------------------------------
 dict(group='Approve', steps=[
   dict(pic=(B + 'one-04-list-req.png', ROW),
        text='**the requirement waits for your confirmation**. Open the task, tab **Requirement**.'),
   dict(pic=(B + 'one-05-requirement.png', (66, 760, 1710, 1290)),
        text='Read `REQ.md`. Not what you meant? Say so in the chat.'),
  ],
  notes='Sources: messages.en.json task.waiting.req, desk.tab.req; templates/task/en/REQ.md (What to do / What not to do / Done when); '
        'taskdesk.py L533-535 (waits on every full-tier task: dev, test, kb, and a task raised to change a repository).'),

 dict(steps=[
   dict(pic=(B + 'one-05-requirement.png', CARD),
        text='It says what you meant? Press **Confirm requirement**.'),
   dict(pic=(B + 'one-06-approve-code.png', (0, 170, 1124, 605)),
        text='A window shows the file to read and a six-character code. Type it, press **Approve**.'),
  ],
  notes='Sources: messages.en.json board.action.confirm-req, desk.hint.confirm-req, req.screen.*, req.question, approval.ask; approval.py CODE_LENGTH 6; task.py L570-612.'),

 dict(steps=[
   dict(pic=B + 'one-08-send-to-agent.png',
        text='The board usually wakes the agent. If it says “… tell the agent …”, press **Send to agent**.'),
   dict(pic=(B + 'one-09-send-panel.png', (0, 760, 1124, 1005)),
        text='It shows the message first. No chat linked? Nothing is sent: **Copy message**, paste it into the chat.'),
  ],
  notes='Sources: messages.en.json task.waiting.go-req, task.waiting.go-plan, task.waiting.go-promote, board.action.send; tasklife.py L273 GO_MARKS '
        '(an approval was given and the agent has not been told); the Send to agent window (no chat linked: nothing is sent; Copy message); docs/01-quickstart.md step 5 points 5 and 8.'),

 dict(steps=[
   dict(pic=(B + 'one-11-plan.png', (0, 0, 2216, 1640)),
        text='Next, the plan. Read tab **Plan**. Agree? **Approve plan**, its own code. Changes? Say so in the chat.'),
  ],
  notes='Sources: messages.en.json task.waiting.plan, desk.hint.approve-plan (after you approve, the agent may change files under DEV/), plan.question; '
        'task.py L428-475 (--with-req: one code confirms the requirement too); docs/01-quickstart.md step 5 points 4-5.'),

 # ---- Follow the work ---------------------------------------------------------------------------------------
 dict(group='Follow the work', steps=[
   dict(pic=(B + 'one-12-list-working.png', ROW),
        text='**working**: it changes copies under `DEV/`, never your repository. Tab **Live** shows its chat.'),
   dict(pic=B + 'state-busy-greyed.png',
        text='Buttons grey while it works: wait until it stops. **Stop** in VS Code halts it.'),
  ],
  notes='Sources: docs/01-quickstart.md step 5 point 6; gate/handler.py L38-88 (edit tools: DEV/ after the plan, never a target working tree); messages.en.json desk.tab.live; '
        'desk.busy.note.nochat ("Nothing here can be pressed until it has stopped ... use the stop button in VS Code"); desk.js L1015.'),

 dict(steps=[
   dict(pic=(B + 'one-14-todo.png', (44, 266, 2175, 1000)),
        text='**TODO** shows the steps of the plan as it ticks them off.'),
   dict(pic=(B + 'tour-reply.png', (20, 20, 1210, 345)),
        text='Chat linked? **Say something** (key **R**) writes to it from the board.'),
   dict(shot='A task page while its linked chat works: Stop beside Say something; the panel open with Steer and Queue', aspect=1.0,
        text='While it works: **Stop** halts it; **Send** becomes **Steer** (now) or **Queue** (after).'),
  ],
  notes='Sources: messages.en.json desk.tab.todo, desk.reply.pill, desk.reply.steer, desk.reply.queue, board.action.stop; '
        'reply.js L1-3 (only for an open task that has a chat), L174, L189 (Stop shows while the chat is busy); desk.busy.note (with a chat: "use Stop on this page or in VS Code").'),

 dict(steps=[
   dict(pic=(B + 'tour-tab-overview.png', (40, 562, 1300, 735)),
        text='Tabs in groups: **Live**, **Overview**, **Changes**, **Records**, **Files**. Click a group to open it.'),
   dict(pic=(B + 'tour-tab-log.png', (44, 210, 900, 468)),
        text='**Records › Log**: the agent’s decisions and findings, newest first.'),
   dict(pic=B + 'tour-task-more.png',
        text='**…**: **Pause** puts it aside; **Close** ends it (it can be opened again).'),
   dict(pic=(B + 'tour-files-edit.png', (68, 690, 2147, 1150)),
        text='**Files**: you can edit a file. A saved `PLAN.md` needs approval again.'),
  ],
  notes='Sources: desk.js L15-22 (tab groups; a group of one goes straight to its tab); messages.en.json desk.tab.*, desk.group.*, desk.tab.log; '
        'desk.hint.pause, desk.hint.close, board.close.warn (the folder stays, the task can be opened again); desk.files.plan.note (saving PLAN.md: an approved plan must be approved again), desk.files.busy.'),

 # ---- Write back and commit ---------------------------------------------------------------------------------
 dict(group='Write back and commit', steps=[
   dict(pic=(B + 'one-15-list-promote.png', ROW),
        text='Done: “the promote (write-back repo) waits for your approval”.'),
   dict(pic=(B + 'one-16-changes-promote.png', (80, 722, 2132, 1560)),
        text='Read every diff on **Changes**: exactly what goes into your repository.'),
  ],
  notes='Sources: messages.en.json task.waiting.promote, desk.tab.changes and the line under it (also what goes into the target repository; the last dry run holds the same changes); promote_target.py L1-14.'),

 dict(steps=[
   dict(pic=(B + 'one-16-changes-promote.png', (75, 296, 2143, 576)),
        text='Commit your own changes in that repository first. Then **Approve promote** and the code.'),
   dict(pic=(B + 'one-17-list-closed.png', ROW),
        text='Files go on a new branch, uncommitted. The board then closes the task: not committed yet.'),
  ],
  notes='Sources: messages.en.json desk.hint.approve-promote, promote.question; promote_target.py L156-163 (a working tree that is not clean refuses the promote); '
        'task.py L984-1024; accept.py L186 QUIET_WAITS ("", "stopped", "commit"), L189-218; boardserve.py SWEEP_EVERY 5 s; docs/02-features.md L249.'),

 dict(steps=[
   dict(pic=(B + 'one-18-closed-changes.png', (78, 321, 2133, 875)),
        text='Open it under **Closed**, tab **Changes**: **Copy commit message**.'),
   dict(pic=(B + 'one-18-closed-changes.png', (110, 886, 2133, 1024)),
        text='Or **Copy commands**. Commit on `feature/show_delivery_date`, push, open the PR yourself.'),
  ],
  notes='Sources: messages.en.json desk.changes.commit, desk.commit.copy, desk.commit.copy_commands; task.py default_branch L60-72 (feature/<name>, - becomes _); docs/01-quickstart.md step 5 point 10.'),

 # ---- Only if -----------------------------------------------------------------------------------------------
 dict(group='Only if', steps=[
   dict(pic=(B + 'intake.png', (78, 835, 2139, 1150)),
        text='Only if the requirement came as files: tab **Intake**, drop them. A program converts them, no AI.'),
   dict(pic=(B + 'intake-files.png', (66, 22, 1385, 294)),
        text='Press **Create INTAKE.md**: a short goal the agent reads first.'),
   dict(pic=(B + 'intake-files.png', (66, 814, 2139, 1125)),
        text='Under **Tell the agent**, **Copy message** and paste it into the chat.'),
  ],
  notes='Sources: docs/09-intake.md; intake.py L1-10; messages.en.json desk.intake.*, desk.intake.tell, desk.intake.message, desk.go.copy; taskdesk.py intake_view L509-516.'),

 dict(steps=[
   dict(pic=(B + 'run.png', (73, 299, 2144, 483)),
        text='Only if it says **waits for your run**: a check needs a run you do, such as on DEV.'),
   dict(pic=(B + 'run.png', (73, 1420, 2144, 2060)),
        text='Run it. Paste the **Output**, add pictures, then **Save and send to the agent**.'),
   dict(pic=(B + 'run.png', (73, 2050, 520, 2425)),
        text='No chat linked? **Save to the task** only saves: copy the message it shows into the chat.'),
  ],
  notes='Sources: messages.en.json task.waiting.run, desk.wait.run.form, desk.inbox.* (Save and send to the agent; Save to the task when no chat is linked), desk.inbox.done; '
        'web/desk.js L945-989 (no bound chat: told false, promptLine); docs/02-features.md L102-103; taskreview.py L320-373.'),

 dict(steps=[
   dict(pic=(B + 'review.png', (1300, 105, 2200, 200)),
        text='Only if you want checks: **Independent review**, pick 1. Or write `[review]=1`.'),
   dict(pic=(B + 'review.png', (74, 716, 1150, 960)),
        text='A separate reviewer checks the work. **Review** lists each check. This task asked for 2.'),
   dict(pic=(B + 'review.png', (74, 2001, 2137, 2446)),
        text='A FAIL: the agent fixes it. Checks used up? See tutorial 4.'),
  ],
  notes='Sources: docs/01-quickstart.md §7 marks and step 5 point 7; docs/02-features.md (limit n + 2); messages.en.json desk.rv.button, desk.rv.hint, desk.tab.review, '
        'task.waiting.review, board.action.review-extend, board.action.review-waive; task.py L911-928.'),

 dict(steps=[
   dict(pic=(B + 'accept.png', (72, 299, 2144, 650)),
        text='Only if no repository changes (a question, an RCA, a design): it ends **to accept**.'),
   dict(pic=(B + 'accept.png', (72, 640, 1000, 754)),
        text='Done: **Accept and close**. Something missing: **Not yet**, and say what.'),
  ],
  notes='Sources: SKILL.md harness-my-task step 5; docs/01-quickstart.md step 5 point 10; messages.en.json task.waiting.accept, desk.accept.*, board.action.accept; accept.py L45-68, L167-181.'),

 # ---- After your first task ---------------------------------------------------------------------------------
 dict(group='After your first task', steps=[
   dict(pic=(B + 'tour-off-work.png', (30, 150, 2190, 410)),
        text='Leaving? **Off work** pauses idle tasks. **Back to work** takes them back.'),
   dict(pic=(B + 'tour-enter-open.png', (930, 1505, 1810, 1650)),
        text='After a reboot: **Start Harness** again. **Restart VS Code** if it shows, then **Enter**.'),
   dict(pic=(B + 'tour-tab-overview.png', (40, 765, 1070, 1290)),
        text='Next morning: open the task, **Overview**: where it stands and the next step.'),
   dict(pic=(B + 'tour-lobby-left-alone.png', (88, 375, 780, 700)),
        text='**Left alone**: no chat holds it. **Go on in a new chat** (uses credits), or say `Go on with <task>`.'),
  ],
  notes='Sources: messages.en.json board.offwork(.hint), board.onwork(.hint); docs/01-quickstart.md step 1 (Restart VS Code: starts it with this computer’s settings); ready.vs.restart; '
        'desk.tab.overview (TASK.md); lobby.js L20-23 (lost -> Left alone), board.lobby.zone.left, desk.actions.unheld.hint; desk.newchat.tip (what was said only in the old chat does not come along); '
        'desk.hint.newchat (a new chat in VS Code; you see the whole message first); rules.task.entry, docs/01-quickstart.md §7 (Go on with <task name>).'),

 dict(steps=[
   dict(shot='VS Code: a Copilot chat with “Task show-delivery-date needs more changes: also show the date in the email” typed in the box, not sent', aspect=1.2,
        text='The PR needs changes? In a chat: `Task show-delivery-date needs more changes: <what>`.'),
   dict(pic=(B + 'state-round-one.png', (0, 100, 2216, 443)),
        text='Round 2 starts: a new plan, new approvals. **Round 1** stays, read only.'),
   dict(pic=(B + 'state-round-two.png', (0, 100, 2216, 600)),
        text='The requirement changed? Say `The requirement changed: <what>`. Confirm it, approve the plan again.'),
  ],
  notes='Sources: docs/01-quickstart.md §7 ("Task <task name> needs more changes: <the new request>"; "The requirement changed: <the new condition>"); '
        'docs/02-features.md L70, L82 (a task open after a write-back starts a new round: new plan and approval; earlier rounds read only behind the round switch); '
        'task.py L140-212 attach / archive_round (round + 1; a closed task is opened again), default_branch L60-72 (round 2: feature/<name>_r2); '
        'messages.en.json desk.round.pick, desk.round.pick.current, desk.round.past, desk.req.changed.'),

 dict(steps=[
   dict(pic=B + 'state-queue-held.png',
        text='A second task on the same repository waits until you commit the first one’s files. **>_**: `harness task queue`.'),
   dict(pic=B + 'state-promote-dirty.png',
        text='Promote refused, **working tree is not clean**: commit, stash or discard. Then ask for a new dry run.'),
   dict(pic=B + 'state-promote-branch.png',
        text='**Branch … exists already**: delete it, or ask the agent for another name.'),
  ],
  notes='Sources: messages.en.json queue.note, queue.next.held, queue.blocked, promote.blocked ("Promote cannot run now, and nothing was written. Fix these first, then run --dry-run again"), '
        'promote.repo.dirty, promote.repo.dirty.fix (commit, stash or discard; not git clean), promote.repo.branch_exists, promote.hint.rename_branch (task set-branch), '
        'promote.approve.changed (let the agent run task promote --dry-run again, then come back to approve); '
        'promote_target.py L156-167; task.py approve_promote L984-996 (the check runs when you approve); commands.py L203 (task queue); taskqueue.py (prints JSON).'),

 dict(steps=[
   dict(pic=B + 'state-recover.png',
        text='**the promote failed halfway**: **Recover the repository**, type the code, then let the agent try again.'),
   dict(pic=(B + 'tour-list-closed.png', (24, 355, 2356, 662)),
        text='Under **Closed**, **Archive** moves a task out of the repository. There is no restore.'),
  ],
  notes='Sources: messages.en.json task.waiting.recover, board.action.recover, desk.hint.recover, recover.next, task.waiting.go-recover; '
        'docs/01-quickstart.md Common cases (A promote fails partway: Recover the repository, with a code); '
        'task.py L176-177 (a task whose promote is partial cannot be opened until it is recovered); board.archive.warn (One way: there is no restore).'),
]

CLOSING = dict(title='That is the day',
  text=[
   'A task that changes a repository always goes this way: you say what, the agent writes, and you read before each code: requirement, plan, write-back.',
   'Any other task (a question, an RCA, a design) ends with a summary **to accept**.',
   'Refused, or a call waits for you? Read **3 When the agent is stopped**.',
  ])
