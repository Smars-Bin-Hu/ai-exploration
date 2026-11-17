# Harness tutorials · 1 A day with the harness: one task from the board to your own commit, and the next day.
# Build: .venv/bin/python source/tutorials/build.py 1_day
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/); sources in each page's notes.

A = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/'

COVER = dict(
 sub='One task from start to finish: open the board, give the requirement, approve the plan and the write-back, '
     'commit. Then how a task that changes no repository ends, and how to pick a task up the next day.',
 how=['Start here once the Install deck is done and the board opens in your browser.'],
)

PAGES = [
 dict(kicker='Step 1 · Open the board', title='Open the board',
  text=[
   'Double-click **Start Harness** and keep its black window open. When every line under **Harness & Local** is green, press **Enter**. **From the company** may stay yellow.',
   'The **board** is the harness’s page in your browser: every task and what waits for you. '
   '**Lobby** shows tasks as robots, **List** as a table.',
  ],
  pic=A + 'board-list.png',
  caption='The List view. The Do column has the button for your next move.',
  notes='Sources: docs/01-quickstart.md steps 1 and 3; messages.en.json board.offwork, board.onwork, board.col.*; '
        'tasklife.py L856-870 (waiting first); guide 21-start-a-task.md Step 5.'),

 dict(kicker='Step 2 · Start a task', title='Say what you want done',
  text=[
   'A **task** is one piece of work kept as a folder, so it outlives any chat.',
   ('steps', ['Press **New task**.',
              'Give a **Name** and a **Kind**.',
              'Under **What to do**: what, in which repository, and what “done” means.',
              'Press **Create and send**. A Copilot chat opens in VS Code; the agent opens the task.']),
   ('small', 'Or just ask in a Copilot chat.'),
  ],
  pic='source/start-here/img/new-task.png',
  caption='From 1.7.43; 1.7.45 may add a Context window field.',
  notes='Sources: messages.en.json board.new.* (New task, Name, Kind, What to do, Create and send, Ask me first); '
        'chatnew.py first_message (name and kind given, the agent does not ask for them); web/chat.js L261-306; '
        'tasklife.py L33-69 (name rules); docs/01-quickstart.md step 7.'),

 dict(kicker='Step 3 · Answer its questions', title='Answer what the agent asks',
  text=[
   'The agent asks what is not clear, often with numbered options: answer with the numbers. **Ask me first** in New task makes it ask before it starts.',
   'When it stops, the board says **waits for you**; the **Live** tab shows its last words. Press **Answer...**: your reply goes to its chat in VS Code.',
   ('small', 'Or reply in the chat itself.'),
  ],
  pic=A + 'talk-live.png',
  caption='The Live tab of a task that waits for you.',
  notes='Sources: .github/skills/harness-my-task/SKILL.md step 2; messages.en.json board.new.grill, task.waiting.stopped, '
        'task.waiting.question, board.action.answer, desk.reply.pill, desk.hint.answer; web/chat.js L306 (Ask me first adds generic-grill-me).'),

 dict(kicker='Step 4 · Give it the documents', title='Put the requirement documents on Intake',
  text=[
   'Came as documents? Open the task’s **Intake** tab and drop the files.',
   'A program turns them into Markdown and CSV, with no AI. Read its report of what was left out; trim what the agent does not need.',
   'Press **Create INTAKE.md**, then **Copy message** under **Tell the agent**, and paste it into the chat.',
  ],
  pic=(A + 'task-intake.png', (40, 395, 990, 1560)),
  caption='The Intake tab. A Q&A task has no Intake tab.',
  notes='Sources: docs/09-intake.md; intake.py L1-10; taskdesk.py intake_view L509-516 (only an open task with REQ.md); '
        'messages.en.json desk.intake.*, desk.go.copy; guide 21-start-a-task.md Step 3.'),

 dict(kicker='Step 5 · Confirm the requirement', title='Check that it understood you',
  text=[
   'The agent writes the **requirement** (`REQ.md`): what to do and not, when it is done, what is unclear.',
   'Open **Requirement**: is each item what you meant, nothing added? If not, tell the agent. If so, press **Confirm requirement** and type the code.',
   ('small', 'Needed on development, testing and knowledge base tasks, and on tasks raised to change a repository.'),
  ],
  shot='A development task page, tab Requirement open, with the Confirm requirement button at the top',
  notes='Sources: messages.en.json board.action.confirm-req, desk.hint.confirm-req, req.changed, desk.tab.bang.unfinished; '
        'task.py L570-612; tasklife.py L310-315 (full tier waits); SKILL.md Gotchas (only full tier stands on a confirmed requirement); '
        'templates/task/en/REQ.md.'),

 dict(kicker='Step 6 · Approve the plan', title='Read the plan, then approve it',
  text=[
   'The agent writes a **plan**, then stops: **the plan waits for your approval**. Open **Plan**. Look at which files change, the steps, how it will check the result, and the risks.',
   'To change it, tell the agent. If you agree, press **Approve plan** and type the code. If the requirement is not confirmed yet, the same code confirms it too.',
  ],
  pic=(A + 'task-plan.png', (40, 135, 990, 1090)),
  caption='The Plan tab, with Approve plan on the card at the top.',
  notes='Sources: messages.en.json task.waiting.plan, desk.hint.approve-plan, plan.question, approval.ask; '
        'task.py L428-475 (--with-req, one code); docs/01-quickstart.md step 5 points 4-5; approve-dialog.png shows the code window.'),

 dict(kicker='Step 7 · Let it work', title='Let it work, and follow it',
  text=[
   'Now the agent copies the files it changes into the task folder (`DEV/`) and works there. Its edit tools cannot write your repository; the write-back does.',
   'Follow it on the **TODO** and **Live** tabs. Press **Say something** to add a word.',
   ('small', 'If the board says “the plan is approved: tell the agent to go on”, press Send to agent.'),
  ],
  pic=(A + 'task-todo.png', (40, 135, 990, 705)),
  caption='The TODO tab: the steps the agent ticks off.',
  notes='Sources: docs/01-quickstart.md step 5 points 5-6; gate/handler.py L38-88 (edit tools: DEV/ after the plan, never a target working tree); '
        'messages.en.json board.action.send, task.waiting.go-plan, desk.hint.steer, desk.reply.pill.'),

 dict(kicker='Step 8 · Read the checks', title='Read the check results',
  text=[
   'Only when you asked: press **Independent review** on the task page and pick 1, or write `[review]=1`. A separate reviewer checks the work.',
   'The **Review** tab lists each check, PASS or FAIL, and what it found. The agent fixes a FAIL; the write-back waits for enough passes.',
   ('small', 'Checks used up? You decide: More checks or Waive checks (deck 3).'),
  ],
  pic=(A + 'task-review.png', (40, 300, 990, 1380)),
  caption='This task asked for 2: one FAIL, then two passes.',
  notes='Sources: docs/01-quickstart.md step 3 and step 5 point 7; messages.en.json desk.rv.button, desk.rv.hint, desk.tab.review; '
        'task.py L911-928 and taskreview.py L563-568 (dry run needs the passes); SKILL.md (checks on only when the user sets them).'),

 dict(kicker='Step 9 · Approve the write-back', title='Read the changes, then approve the write-back',
  text=[
   'The **write-back** (the board says promote) puts the changed files into your repository. The agent first runs a dry run; then **the promote (write-back repo) waits for your approval**.',
   'Open **Changes** and read every file’s diff: it is exactly what goes in. If you agree, press **Approve promote** and type the code.',
  ],
  pic=(A + 'task-changes.png', (40, 135, 990, 740)),
  caption='The Changes tab, side by side.',
  notes='Sources: messages.en.json task.waiting.promote, desk.hint.approve-promote, promote.question, promote.screen.repo; '
        'task.py L941-944, L984-1024; docs/01-quickstart.md step 5 point 8.'),

 dict(kicker='Step 10 · Commit', title='Commit the branch yourself',
  text=[
   'The files land on a new branch named after the task, such as `feature/fix_login_timeout`, uncommitted. Once the agent stops, the board closes the task by itself: closed does not mean committed.',
   'Find it under **Closed**, open **Changes**, and press **Copy commit message** or **Copy commands**. Commit, push and open the PR yourself.',
  ],
  shot='A closed development task, tab Changes: “Promoted: commit it with this message”, with Copy commit message and Copy commands',
  notes='Sources: promote_target.py L1-14 (new branch from the base branch, never commits); task.py default_branch L60-72; '
        'messages.en.json task.waiting.commit, promote.done.person, desk.changes.commit, desk.commit.copy, desk.commit.copy_commands; '
        'accept.py L184-218 (board closes; QUIET_WAITS includes commit; boardserve.py SWEEP_EVERY 5 s); docs/02-features.md L249. A knowledge base task is different: one commit on its base branch (deck 5).'),

 dict(kicker='Another ending', title='A task that changes no repository: Accept and close',
  text=[
   'A question, an RCA, a design or a test ends with a short summary from the agent. The board then says **to accept**.',
   'Read **What the agent delivered**, and look where it points. Done: press **Accept and close** (no message, no tokens). Something missing: press **Not yet** and say what.',
  ],
  shot='A task page that says to accept, with the summary and the Accept and close and Not yet buttons',
  notes='Sources: SKILL.md step 5; messages.en.json task.waiting.accept, desk.accept.summary, board.action.accept, desk.accept.hint, desk.accept.not_yet; '
        'accept.py L45-68, L167-181.'),

 dict(kicker='The next day', title='Pick the task up again',
  text=[
   'The work lives in the task folder. Leaving? **Off work** pauses the tasks not at work, so the night is not counted; **Back to work** takes them back.',
   'Chat gone? Press **Go on in a new chat** on the task page, or say `Go on with <task name>` in a new chat. Words only in the old chat are lost.',
  ],
  pic=(A + 'board.png', (0, 0, 1130, 560)),
  caption='The Lobby, with Off work and Back to work.',
  notes='Sources: messages.en.json board.offwork(.hint), board.onwork(.hint), board.go.new, desk.newchat.go, desk.newchat.tip; '
        'web/desk.js L405-435 (offered when no chat is linked, or from the Context card when the chat is idle); '
        'handler.py L124-137; SKILL.md step 1-3 (task open).'),
]

CLOSING = dict(title='That is the day',
  text=[
   'Every task goes the same way: you say what, the agent asks and writes, and you read before each approval: the requirement, the plan, the write-back.',
   'When the agent is refused, or a call waits for your approval, read **2 When the agent is stopped**.',
  ])
