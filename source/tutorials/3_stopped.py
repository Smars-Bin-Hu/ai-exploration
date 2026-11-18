# Harness tutorials · 3 When the agent is stopped: first by symptom (what you see -> what it means -> what you do),
# then the four ways to say yes, then why the gate refuses or holds a call and what you do. One small step per picture.
# Step 29 (learner-r1 problems 3 and 7): the symptom pages and "Four ways to say yes" were added in front.
# Build: .venv/bin/python source/tutorials/build.py 3_stopped
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/, read only); sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data). Two rows come from 1.7.43 screens with the same words
# (source/start-here/img/refusals-list.png, held-both.png): the 1.7.45 demo has no such refusal or approved card to capture.
# Placeholders (VS Code, terminal, and two board states that need a live chat) are listed in shots/3_stopped.md.
# Fact-check fixes kept (review/2_stopped-r1.md): a guardrail edit trips the integrity check (doctor --accept, or admin mode
# switched on in your own terminal); the VS Code ask is only a reminder. Newcomer-test fixes kept: where the held call's code is;
# what Allow / Deny do; never paste approval commands into the chat.

B = 'source/tutorials/img/_board/'
OLD = 'source/start-here/img/'

COVER = dict(
 sub='Why the harness stops the agent, where you see it, and what you do next: '
     'answer, approve, run it yourself, or let it be.',
 how=['Read **1 A day with the harness** first: this deck starts where the agent is stopped.',
      'Something stopped? Find what you see in steps 1–17, and do what that step says.'],
)

CONTENTS = True

PAGES = [
 # ---- What you see -> what it means -> what you do ----------------------------------------------------------
 dict(group='What you see', steps=[
   dict(pic=(B + 'live-waiting.png', (40, 265, 1250, 450)),
        text='First, always: open the task, tab **Live**. The agent’s latest items say what happened.'),
   dict(pic=(B + 'live-waiting.png', (270, 1100, 2000, 1250)),
        text='**waits for your answer**: the agent asked you. Read the question, press **Answer...**.'),
   dict(pic=(B + 'state-waits-for-you.png', (30, 0, 1100, 105)),
        text='**waits for you**: its turn ended, the next move is yours. Often it asked in the chat: answer there.'),
   dict(pic=(B + 'state-waits-for-you.png', (60, 285, 2160, 495)),
        text='No chat linked: **Answer...** is grey. **Go on in a new chat** opens one, and spends credits.'),
  ],
  notes='Sources: messages desk.tab.live / "Live the latest items of the agent\'s chat"; task.waiting.asking = "waits for your answer" (tasklife.ask_text: the ask tool), '
        'board.action.answer = "Answer..."; task.waiting.stopped = "waits for you" (tasklife.waiting(): the Stop hook\'s mark, "the agent of the task\'s session stopped: the next move is the person\'s"); '
        'desk.hint.newchat, desk.newchat.go / desk.newchat.tip (a new chat in VS Code picks the task up from its files); web/desk.js offersChat, newChatButton. '
        'A new chat sends a message to the model, so it spends credits. Screens: 1.7.45 demo board.'),

 dict(steps=[
   dict(pic=(B + 'state-busy-greyed.png', (70, 295, 2150, 615)),
        text='**working**, buttons grey: the agent is in a turn. Wait until it stops, or stop it.'),
   dict(pic=(B + 'state-stuck.png', (40, 460, 2376, 665)),
        text='⚠ after the state: a health warning. Open the task, **Records** › **Agent actions**.'),
   dict(pic=(B + 'state-stuck-page.png', (40, 300, 2200, 640)),
        text='**Stuck?**: no tool call for 10 minutes. Check the chat in VS Code; if it hangs, stop it.'),
  ],
  notes='Sources: messages desk.busy.note / desk.busy.note.nochat ("Nothing here can be pressed until it has stopped ... To stop it now, use Stop on this page or in VS Code" / "the stop button in VS Code"), '
        'board.action.busy, board.action.stop = "Stop"; docs/02-features.md "States, and when you can press a button" (working; quiet = a session holds it, 5 minutes with no call and no stop); '
        'tasklife.py state_of, STATES; messages board.state.quiet, desk.actions.quiet.hint ("A long step may be running, or the VS Code window may be closed. If it is closed, open a session and say the task name"); '
        'modules/task/health.py lines 7 and 27 (stuck: at work, no tool call for stuck_minutes = 10; also repeat, idle, cost, context), board.warn.label = "Health warning", board.warn.stuck; docs/02-features.md line 86 (the ⚠ tag; Agent actions).'),

 dict(steps=[
   dict(pic=(B + 'state-quiet.png', (40, 460, 2376, 665)),
        text='**quiet**: no call for 5 minutes, not stopped. A long step, or VS Code closed: look there.'),
   dict(pic=(B + 'tour-lobby-left-alone.png', (80, 370, 2100, 705)),
        text='**Left alone** (in List: **no session**): no chat holds the task. Open a chat, name the task.'),
   dict(pic=(B + 'state-cancelled-page.png', (60, 290, 2160, 450)),
        text='**cancelled, waits for you**: the last message was cancelled. Send the agent a new one.'),
   dict(pic=(B + 'stop-agent-actions.png', (88, 1145, 2128, 1280)),
        text='A red **blocked** row in **Agent actions**: the gate refused a call. ▶ gives why. Steps 24–33.'),
  ],
  notes='Sources: web/lobby.js lines 21-30 (state "unheld" goes to the zone "lost" = board.lobby.zone.left "Left alone"); board.state.unheld = "no session"; '
        'desk.actions.unheld.hint ("Nothing happens until you open a session and ask for the task by name"); docs/02-features.md states table (no session). '
        'task.waiting.cancelled, desk.wait.cancelled ("The last message was cancelled, so the agent stopped. Send it a new message here or in VS Code"); tasklife.cancelled_at (Copilot\'s record). '
        'desk.trace.deny = "blocked"; desk.tab.trace = "Agent actions". How to start again next day: 1 A day with the harness, Next day.'),

 dict(steps=[
   dict(pic=(B + 'tour-list.png', (20, 2046, 1700, 2180)),
        text='**an outside call waits for your approval**: press **Approve a call**. Steps 38–43.'),
   dict(pic=(B + 'stop-agent-actions.png', (88, 990, 2128, 1125)),
        text='**git change waits for you**: the row says only **waits for you**. Steps 44–47.'),
   dict(pic=(B + 'state-recover.png', (30, 0, 2216, 480)),
        text='**the promote failed halfway…**: press **Recover the repository**. How: **1 A day with the harness**, recover.'),
  ],
  notes='Sources: task.waiting.outbox, board.action.approve-action; desk.trace.rule.git-approval; tasklife.waiting() (a held git write is no wait reason of its own: the Stop mark shows "waits for you"); '
        'task.waiting.recover, board.action.recover = "Recover the repository", desk.hint.recover; recover.next ("Let the agent run task promote --dry-run again, then the user approves"); '
        'task.waiting.go-recover. How to recover step by step: 1 A day with the harness, after your first task (recover).'),

 dict(steps=[
   dict(pic=B + 'state-promote-dirty.png',
        text='**Promote cannot run now**: commit or stash those files in your repository, then retry. See deck 1, refused promote.'),
   dict(pic=B + 'state-promote-branch.png',
        text='**Branch … exists already**: deal with that branch, or have the agent pick another name.'),
   dict(pic=(B + 'state-queue-held.png', (15, 15, 975, 560)),
        text='A write-back waits until you commit the earlier task’s files. `harness task queue` shows it. Deck 1: queue.'),
  ],
  notes='Sources: messages promote.repo.dirty, promote.repo.dirty.fix (commit, stash or discard; never git clean), promote.repo.branch_exists ("Pick another branch name (task set-branch), or deal with that branch first"), '
        'queue.blocked, queue.next.held, queue.note ("the next task can write into the same repository only after the files of the one before it are committed"); task.waiting.commit = "promoted: commit the files". '
        'The queue picture is the board\'s Terminal window running harness task queue (a read). Step by step: 1 A day with the harness, after your first task (refused promote, queue).'),

 # ---- Four ways to say yes ----------------------------------------------------------------------------------
 dict(group='Four ways to say yes', steps=[
   dict(pic=B + 'approve-code.png',
        text='A code in a board window: requirement, plan, write-back, recover. Only your paired board sends it.'),
   dict(pic=(B + 'outside-held-view.png', (0, 30, 1804, 470)),
        text='The code you click in **View**: one outside call, exactly as written. You press **Approve**.'),
   dict(shot='Your own terminal: harness approve-command listing one git command, asking for the code', aspect=16/7,
        text='`harness approve-command` in your own terminal: one git write. It needs your keyboard; the agent is refused.'),
   dict(shot='VS Code chat: an agent command waiting for confirmation, the Allow button under it (menu closed)', aspect=16/7,
        text='VS Code’s **Allow**: deletes, `curl`, installs. Your click, not the agent’s; on **Allow all** it never asks.'),
  ],
  notes='Board window: boardserve.py lines 11-15 (approvals need the paired browser; preview shows the code, act runs it with the code typed; a changed plan has another code), '
        'lines 95-121 (board actions: confirm-req, approve-plan, approve-promote, recover, review ..., approve-action; no approve-command); core/approval.py lines 1-8 and code_of (6 characters of the sha256 of what is approved). '
        'Held call: core/outbox.py lines 1-7 (the gate refuses the call, records it with a code; the same command runs once within the time limit; a changed command is a new draft with a new code); desk.outbox.code_tip. '
        'Git write: core/approvals.py lines 1-5; gate.git.needs_approval ("do not run approve-command yourself"); approval.ask uses input(): approval.no_input (the board\'s Terminal window has no keyboard); '
        'gate.json terminal.deny (approve-command, approve-action, task approve-plan ... are the user\'s; the gate denies an agent that runs them). '
        'VS Code Allow: gate.json terminal.ask; docs/02-features.md line 50 (only a reminder: Allow all shows no box); chatnew.py PERMISSIONS (a board chat is Allow all).'),

 dict(steps=[
   dict(pic=(B + 'tour-list.png', (420, 527, 1880, 1212)),
        text='Approvals are yours: press the board’s button, or run the command in your own terminal.'),
   dict(pic=(B + 'stop-git-code.png', (380, 315, 2010, 365)),
        text='Never paste an approval command into the agent’s chat: the gate refuses it there.'),
  ],
  notes='Sources: gate.json terminal.deny (the person-only harness commands: task approve-plan, confirm-req, approve-promote, recover, review ..., '
        'approve-command, approve-action, admin on, doctor --accept; and task close); harnesscmd.py (read as the shell reads them); core/approval.py require_person.'),

 # ---- Refusals: where you see them ---------------------------------------------------------------------------
 dict(group='Refusals', steps=[
   dict(pic=(B + 'stop-agent-actions.png', (40, 275, 1300, 440)),
        text='Open the task, then **Records** › **Agent actions**.'),
   dict(pic=(B + 'stop-agent-actions.png', (86, 570, 2128, 720)),
        text='The **gate**, harness code, checks each agent call first. **blocked by a hook** counts its refusals.'),
   dict(shot='Task page, Live: a command marked “Refused by the gate”, its reason on hover', aspect=16/7,
        text='**Live** marks a refused command **Refused by the gate**. Point at it for the reason.'),
   dict(shot='VS Code chat: a refused command, and the agent saying what was refused and why', aspect=16/10,
        text='In the chat, the agent is told to stop and say what was refused, and why.'),
  ],
  notes='Sources: messages.en.json desk.group.records = "Records", desk.tab.trace = "Agent actions", desk.trace.stat.blocked = "blocked by a hook", '
        'desk.trace.problems = "Blocked and failed: {n}", desk.trace.deny = "blocked"; web/desk.js GROUPS (trace is in records); '
        'modules/gate/handler.py lines 1-12 (what the gate guards); gate.json "description". '
        'messages desk.live.refused = "Refused by the gate"; web/live.js lines 169-225 (the reason is the title on hover); gate.* texts end with "stop and tell the user" / "Do not retry".'),

 # ---- What is refused ---------------------------------------------------------------------------------------
 dict(steps=[
   dict(pic=(B + 'stop-agent-actions.png', (88, 1305, 2128, 1445)),
        text='Repositories set up in **Get ready**? A file in one is refused. Only the approved write-back writes there.'),
   dict(pic=(OLD + 'refusals-list.png', (0, 458, 2410, 600)),
        text='The harness’s own files (engine, policies, hooks) and any `.git` folder: refused.'),
   dict(pic=(OLD + 'refusals-list.png', (0, 80, 2410, 250)),
        text='In a task, edits stay in its folder. `DEV/` opens when you approve the plan.'),
  ],
  notes='Sources: gate/handler.py check_write (lines 38-61), check_task_write (64-88; a chat with no open task is not bound), check_terminal (96-108: '
        'a terminal write that names the path); gate.json guardrail_paths, cli_owned_paths; messages gate.target.direct, gate.guardrail.file, '
        'gate.git_folder.file, gate.task.plan_first. The two lower pictures are 1.7.43 rows with the same words as 1.7.45.'),

 dict(steps=[
   dict(pic=(B + 'stop-agent-actions.png', (88, 1145, 2128, 1280)),
        text='`sudo`, `rm -rf ~`: always refused. With repositories set up, `git push`, `reset --hard`, `clean`, any force too.'),
   dict(pic=(B + 'stop-agent-actions.png', (88, 990, 2128, 1125)),
        text='Other git writes then wait for your code. No repositories in **Get ready**? These git and repository rules are off.'),
   dict(pic=(B + 'stop-agent-actions.png', (88, 830, 2128, 965)),
        text='A destroy on an outside system: refused by default. A tool pack can hold it for you instead (deck 5).'),
  ],
  notes='Sources: gate.json terminal.deny (sudo, rm -rf of root/home/current folder, download piped into a shell, mkfs, terraform apply ...); '
        'gitcmd.py NEVER (push, clean, filter-branch, update-ref, prune, reset --hard, branch -D, any force, gh pr); handler.py line 109 and 770: '
        'the git rules apply only when target repositories are configured; otherwise only the ask rules of gate.json look at git (line 763): '
        'push / reset --hard / clean ask, git commit passes. core/systems.py DEFAULT_RULES (destroy: deny); messages gate.git.never, gate.git.needs_approval, gate.external.denied.'),

 # ---- Commands that ask -------------------------------------------------------------------------------------
 dict(group='Commands that ask', steps=[
   dict(shot='VS Code chat: a curl command waiting for your confirmation, the Allow menu open', aspect=16/10,
        text='Deletes, `curl`, installs: the gate has VS Code ask you. A reminder, not a lock: never **Allow in this Session**.'),
   dict(pic=(B + 'tour-reply.png', (40, 575, 1190, 835)),
        text='A chat the board made starts with **Permissions** **Allow all**: then nothing asks, they just run.'),
   dict(shot='Board, List: a task in state “the agent asks to run: …”, Do shows Allow · deny', aspect=16/5,
        text='In a chat made in VS Code, or not on **Allow all**: **State** reads **the agent asks to run: …**'),
   dict(shot='Board: the Allow · deny window, with the command and its buttons', aspect=16/9,
        text='**Allow · deny** in **Do** shows the command: **Allow** runs that one call, **Deny** refuses it.'),
  ],
  notes='Sources: gate.json terminal.ask (deletes, network, package installs, git history); handler.py end of check_terminal (permission "ask"); '
        'docs/02-features.md line 50 ("only a reminder, not protection": Allow all shows no box; after Allow in this Session the session is not asked again); '
        'messages board.new.fixed and create.refused.permission ("A chat made here is always allow all"), desk.set.permission = "Permissions"; chatnew.py PERMISSIONS; '
        'task.waiting.confirm = "the agent asks to run: {what}", board.action.confirm = "Allow · deny", board.ask.allow, board.ask.deny, board.ask.confirm.hint; '
        'web/chat.js confirm() (Allow, Deny, Cancel).'),

 # ---- Approve a held call -----------------------------------------------------------------------------------
 dict(group='Approve a held call', steps=[
   dict(pic=(B + 'tour-list.png', (20, 2046, 1700, 2180)),
        text='**an outside call waits for your approval**: press **Approve a call**.'),
   dict(pic=(B + 'outside-held-card.png', (75, 300, 2140, 640)),
        text='The card says what the call does. Press **View** for the whole command.'),
   dict(pic=(B + 'outside-held-view.png', (0, 230, 1804, 340)),
        text='In that window, click the code (after **The code**). It fills the card’s box.'),
   dict(pic=(B + 'outside-held-card.png', (75, 735, 2140, 800)),
        text='Press **Approve**. Or **Do not approve**, and pick why.'),
  ],
  notes='Sources: messages task.waiting.outbox, board.action.approve-action = "Approve a call", desk.outbox.view = "View", desk.outbox.window, '
        'desk.outbox.asked (ends "The code:"), desk.outbox.code_tip ("Click: the code is copied and put in the card\'s box"), desk.outbox.approve, '
        'desk.outbox.dismiss = "Do not approve", desk.outbox.reason.*; web/desk.js line 1296 (the code button); docs/04-reference.md approve-action row.'),

 dict(steps=[
   dict(pic=(OLD + 'held-both.png', (30, 624, 2448, 955)),
        text='Shows **Tell the agent to run it**? Press it. It runs once, as written, within 10 minutes.'),
   dict(pic=(B + 'outside-held-card.png', (75, 680, 2140, 855)),
        text='**Open … for this task** lets such writes pass without asking. See deck 5 first.'),
  ],
  notes='Sources: messages desk.outbox.tell = "Tell the agent to run it", desk.outbox.tell.hint, desk.outbox.same_as; core/approvals.py DEFAULT_MINUTES = 10 '
        '(gate.json git.approval_minutes); desk.outbox.open.items, desk.outbox.open.tip.items. The upper picture is a 1.7.43 card with the same words as 1.7.45.'),

 # ---- Approve a git write -----------------------------------------------------------------------------------
 dict(group='Approve a git write', steps=[
   dict(pic=B + 'stop-git-code.png',
        text='A held git write: the agent gives you the whole command and a six-character code.'),
   dict(pic=(B + 'tour-list.png', (20, 667, 1890, 801)),
        text='The board shows only **waits for you**: a git write has no button of its own.'),
   dict(shot='Terminal: harness approve-command listing one git command, asking for the code', aspect=16/7,
        text='In your own terminal, not the board’s **Terminal**: `harness approve-command`. Read it, type the code.'),
   dict(pic=(B + 'tour-reply.png', (40, 40, 1190, 345)),
        text='Then tell the agent to run the same command again, within 10 minutes.'),
  ],
  notes='Sources: messages gate.git.needs_approval, gate.approve.header, gate.approve.prompt, gate.approve.next, desk.trace.rule.git-approval; '
        'modules/gate/commands.py approve() (terminal only; reads the code with input(): the board\'s Terminal window gives no keyboard input, docs/04-reference.md line 9); '
        'core/approvals.py _code (6 characters); tasklife.py waiting() (a git approval is no wait reason: the Stop mark shows "waits for you").'),

 # ---- When there is no approval -----------------------------------------------------------------------------
 dict(group='When there is no approval', steps=[
   dict(pic=(B + 'stop-agent-actions.png', (88, 1145, 2128, 1280)),
        text='`git push` or a harmful command really needed? Ask what it is for, read it, run it yourself.'),
   dict(shot='Enter screen (or the notice on the board): guardrail files differ, with Accept these files', aspect=16/6,
        text='Changed an engine, hook or shipped policy file yourself? Until it is accepted, the agent can only read.'),
   dict(shot='Terminal: harness doctor --accept, listing the guardrail files it takes in', aspect=16/7,
        text='Put the file back, press **Accept these files**, or run `harness doctor --accept` in your own terminal.'),
   dict(shot='VS Code: a new chat with /harness-admin typed in the box, not sent', aspect=16/10,
        text='Or admin mode: `/harness-admin` in a chat with no task gives a `harness admin on` command for your terminal.'),
  ],
  notes='Sources: messages gate.git.never, gate.terminal.denied ("the user runs it in their own terminal"); the gate is a hook on the agent\'s tool calls only. '
        'integrity.py lines 1-8 and 20-27 (listed: .harness/engine, .harness/bin, .github/hooks, .harness/toolpacks, registry.json, shipped policies; not *.override.json, *.company.json, .vscode/settings.json); hook.py:177 hook.integrity (commands and writes refused, reads pass); doctor.py:1018-1021 (doctor --accept needs a person: refused in the board Terminal); web/readyui.js acceptFiles, board.integrity.button = "Accept these files"; '
        'docs/12-guardrails-and-gate.md "The guardrail files are checked" (doctor --accept, or put the files back); messages gate.guardrail.file ("harness admin on"), '
        'gate.admin.has_task; .github/skills/harness-admin/SKILL.md lines 11 and 23 (the person runs harness admin on --session-id <id> in their terminal); '
        'commands.py admin_switch_off (ending admin mode accepts the files).'),

]

CLOSING = dict(title='When the agent is stopped',
  text=[
   ('list', ['Look at **Live** first, then the state (steps 1–17). A refusal: read its reason.',
             'Held outside call: approve it on its card. Git write: `harness approve-command` in your own terminal.',
             'No approval, and really needed: run it yourself. A harness file you changed: **Accept these files**, or `harness doctor --accept` in your own terminal.',
             'Never hand an approval command to the agent.']),
  ])
