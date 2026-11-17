# Tutorial 3: When the agent is stopped. Checked against harness 1.7.45 (ref/harness-1.7.45, read only).
# Build: .venv/bin/python source/tutorials/build.py 3_stopped

H = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/'
DOCIMG = H + 'docs/images/'

COVER = dict(
    sub='Why the harness stops the agent, where you see it, and what you do next: approve it, run it yourself, or let it be.',
    how=['Read **A day with the harness** first: this one starts where the agent is stopped.'],
)

PAGES = [
 dict(kicker='Step 1 · Know the gate', title='A refusal is the gate at work',
  text=[
   'The **gate** is harness code that checks the agent\u2019s file writes and terminal commands before they run. It answers:',
   ('list', ['**passes**: most work, like reading and tests;',
             '**refused**: the agent is told why, and what to do instead;',
             '**waits for you**: you decide.']),
   ('small', 'A refusal is not a fault. The agent is told not to look for a way round it.'),
  ],
  notes='Sources (harness 1.7.45): .harness/engine/modules/gate/handler.py lines 1-12 (what the gate guards); '
        '.harness/policies/gate.json "description"; docs/12-guardrails-and-gate.md "Three answers: pass, refuse, ask". '
        'Each refusal text ends with "Do not retry" / "do not get around this": core/messages.en.json gate.* keys.'),

 dict(kicker='Step 2 · Files it will not touch', title='Files the agent is refused',
  text=[
   'The agent’s edit tools are refused on:',
   ('list', ['the harness’s own **guardrail files**: its engine, policies and hooks;',
             'any `.git` folder;',
             'a **target repository**, where your team’s code lives: only the write-back, after your approval, writes there;',
             'files only harness commands write, such as a task’s `.task/`.']),
   ('small', 'A terminal command that writes to one of these, by name, is refused too.'),
  ],
  pic=('source/start-here/img/refusals-list.png', (0, 250, 2410, 600)),
  caption='Two refusals: a file of a target repository, and a guardrail file (1.7.43).',
  wide=True,
  notes='Sources: modules/gate/handler.py check_write (lines 38-61) and check_terminal (lines 96-108); '
        'policies/gate.json guardrail_paths and cli_owned_paths; messages gate.guardrail.file, gate.git_folder.file, '
        'gate.target.direct, gate.cli_owned.file. Terminal: only a write that names the path (in full or after a cd in the same line).'),

 dict(kicker='Step 3 · Inside a task', title='In a task, the agent writes in its folder',
  text=[
   'A **task** is one piece of work, kept as a folder. In the chat that holds an open task, its edit tools are also refused:',
   ('list', ['outside the task folder;',
             'in `DEV/`, where code goes, until you approve the plan;',
             'in `REQ/`, `REF/`, `INBOX/`: what you gave.']),
   ('small', 'A refusal in DEV/ means the plan waits: read it, then press Approve plan.'),
  ],
  pic=('source/start-here/img/refusals-list.png', (0, 80, 2410, 250)),
  caption='DEV/ is refused until the plan is approved (1.7.43; same words in 1.7.45).',
  wide=True,
  notes='Sources: modules/gate/handler.py check_task_write (lines 64-88): a chat with no open task is not bound; '
        'messages gate.task.outside, gate.task.plan_first, gate.task.person_files; board.action.approve-plan = "Approve plan".'),

 dict(kicker='Step 4 · Commands it will not run', title='Some commands are refused outright',
  text=[
   'In the terminal, the gate refuses:',
   ('list', ['harmful ones: `sudo`, `rm -rf ~`, a download piped into a shell, `terraform apply`;',
             'git commands that publish or drop work: `git push`, `git reset --hard`, `git clean`, any force;',
             'other git writes (`git commit`) until you approve them;',
             'harness commands only you run.']),
   ('small', 'The git rules apply once target repositories are set up.'),
  ],
  notes='Sources: policies/gate.json terminal.deny (each "why"); modules/gate/gitcmd.py NEVER (push, clean, filter-branch, update-ref, prune, '
        'reset --hard, branch -D, any force, gh pr); handler.py line 109: the git rules apply only when targets are configured '
        '(guard_git=found.configured, line 770). Messages gate.terminal.denied, gate.git.never.'),

 dict(kicker='Step 5 · Some commands ask you', title='VS Code asks before some commands',
  text=[
   'Some commands need your yes: deletes, network calls (`curl`, `ssh`), package installs. VS Code shows each in the chat: read it.',
   'This is a reminder, not a lock: with **Allow all**, or after **Allow in this Session**, VS Code stops asking. Choose neither.',
   ('small', 'Before target repositories are set up, git push and reset --hard only ask, and git commit passes.'),
  ],
  shot='The VS Code chat with an agent’s terminal command (for example a curl) waiting for your confirmation, its buttons visible',
  notes='Sources: policies/gate.json terminal.ask ("it deletes files", "it goes on the network", "it installs packages"); '
        'handler.py end of check_terminal: permission "ask" with gate.terminal.ask. Board: tasklife.py LIVE_WAITS, '
        'messages task.waiting.confirm = "the agent asks to run: {what}", board.action.confirm = "Allow · deny". '
        'Only a reminder: docs/02-features.md line 50 (Allow all shows no box; Allow in this Session is not asked again). '
        'Without target repositories only the ask rules of gate.json look at git (handler.py lines 763, 770): git commit passes.'),

 dict(kicker='Step 6 · Where you see it', title='The chat tells you; the board keeps it',
  text=[
   'In the **chat**: the agent gets the gate’s reason, and is told to stop and say what was refused and why.',
   'On the task page of the **board**: **Live** marks a refused command **Refused by the gate**. **Records** › **Agent actions** counts them (**blocked by a hook**) and lists each one with its reason.',
  ],
  pic='source/start-here/img/refusals.png',
  caption='Records › Agent actions (1.7.43; the same words in 1.7.45).',
  wide=True,
  notes='Sources: messages desk.live.refused = "Refused by the gate", desk.tab.trace = "Agent actions", desk.group.records = "Records", '
        'desk.trace.stat.blocked = "blocked by a hook", desk.trace.problems = "Blocked and failed: {n}", desk.trace.deny = "blocked"; '
        'modules/task/web/desk.js GROUPS (trace is in records); web/live.js lines 169-225 (the reason shows on hover).'),

 dict(kicker='Step 7 · Waiting for you', title='What “waits for you” asks of you',
  text=[
   'On the board, **State** says what is needed; **Do** has the button:',
   ('list', ['**waits for you**: read its chat, then reply (**Answer...**).',
             '**the agent asks to run: \u2026**: **Allow \u00b7 deny** shows the command; **Allow** runs that one call, **Deny** refuses it.',
             '**an outside call waits for your approval**: **Approve a call**.']),
   ('small', 'A held git write shows as waits for you.'),
  ],
  pic=(DOCIMG + 'board-list.png', (40, 225, 965, 690)),
  caption='The board, List view: the button for each wait is under Do.',
  notes='Sources: modules/task/tasklife.py waiting() (lines 276-336) and LIVE_WAITS (line 346); modules/task/taskboard.py ACTIONS_BY_WAIT '
        '(line 117) and actions(); messages task.waiting.stopped, task.waiting.confirm, task.waiting.outbox, task.waiting.plan, '
        'board.action.answer, board.action.confirm, board.action.approve-action, board.action.approve-plan. '
        'A git approval is not a wait reason: the agent stops, so the Stop hook marks the task "waits for you" (task/handler.py lines 398-411).'),

 dict(kicker='Step 8 · Approve a held call', title='A held call waits on its card',
  text=[
   ('steps', ['The held call is a card on the task page.',
              'Press **View** and read the command.',
              'In that window, click the code after **The code:** to fill the card\u2019s box.',
              'Press **Approve**, or **Do not approve** and say why.',
              'If the card shows **Tell the agent to run it**, press it.']),
   ('small', 'It runs once, exactly as written, within 10 minutes.'),
  ],
  pic=DOCIMG + 'held-write.png',
  caption='A write to a database, held on the task page.',
  notes='Sources: messages desk.outbox.view = "View", desk.outbox.code_tip, desk.outbox.approve = "Approve", desk.outbox.dismiss = "Do not approve", '
        'desk.outbox.reason.*, desk.outbox.tell = "Tell the agent to run it", desk.outbox.tell.hint, desk.outbox.same_as; '
        'docs/04-reference.md approve-action row; core/approvals.py DEFAULT_MINUTES = 10 (gate.json git.approval_minutes). '
        'The card’s "Open <connection> for this task" button is tutorial 5.'),

 dict(kicker='Step 9 · Approve a git write', title='A git write: approve it in your terminal',
  text=[
   'The agent’s chat shows the whole git command and a six-character code.',
   ('steps', ['Open your own terminal (not the board’s **Terminal** window).',
              'Run the command below. It lists the git commands that wait.',
              'Read the command, then type its code.',
              'Tell the agent to run the same command again, within 10 minutes.']),
   ('code', 'harness approve-command'),
  ],
  shot='A terminal after harness approve-command: one waiting git command listed, and the line that asks for the code',
  notes='Sources: messages gate.git.needs_approval, gate.approve.header, gate.approve.prompt, gate.approve.next; '
        'modules/gate/commands.py approve() (terminal only, reads the code with input()); core/approval.py lines 58-63: '
        'the board’s Terminal window gives no keyboard input; docs/04-reference.md line 9. Code: core/approvals.py _code (6 characters, capitals). '
        'Time: gate.json git.approval_minutes = 10.'),

 dict(kicker='Step 10 · When it is really needed', title='Run it yourself, in your own terminal',
  text=[
   '`git push` and dangerous commands have no approval.',
   'If one is really needed, ask the agent what it is for, read it, and run it yourself in your own terminal. The gate stops the agent, not you.',
   ('small', 'Do not ask the agent to find another way round: it is told not to.'),
  ],
  notes='Sources: messages gate.git.never ("the user runs it in their own terminal"), gate.terminal.denied ("the user runs it"). '
        'The gate is a hook on the agent\u2019s tool calls only (.github/hooks/harness.json), so a command you type yourself is not judged by it. '
        'Guardrail files are the next page.'),

 dict(kicker='Step 11 · Guardrail files', title='A guardrail file needs one more step',
  text=[
   'Settings go in `*.override.json` files: those are not checked.',
   'After you edit a guardrail file, the agent is refused every command and write until you run `harness doctor --accept` in your terminal, or undo it.',
   'Or admin mode: `/harness-admin`, in a chat with no task, gives you a `harness admin on` command for your terminal. Ending it accepts the files.',
  ],
  notes='Sources: .harness/engine/integrity.py lines 1-8 (what is listed; the hook refuses commands and writes) and lines 23-27 '
        '(*.override.json and *.company.json are skipped); docs/12-guardrails-and-gate.md "The guardrail files are checked" '
        '(a hand edit: harness doctor --accept in your terminal, or put the files back); messages gate.guardrail.file '
        '("switches admin mode on for a session (harness admin on)"), gate.admin.has_task (admin mode needs a chat with no task); '
        '.github/skills/harness-admin/SKILL.md lines 11 and 23 (the person runs harness admin on --session-id <id>; not in a chat with a task); docs/01-quickstart.md Common cases; modules/gate/commands.py admin_switch_off '
        '(the end of an admin session accepts the files).'),

 dict(kicker='Step 12 · Commands only you run', title='Never paste an approval command into the chat',
  text=[
   'These `harness` commands are yours: `task approve-plan`, `task confirm-req`, `task approve-promote`, `task recover`, `approve-command`, `approve-action`, `task close`, `admin on`, `doctor --accept`, and more.',
   'The gate refuses them when the agent runs them, so pasting one into its chat only gets a refusal. Press its button on the board, if it has one, or run it in your own terminal.',
  ],
  notes='Sources: policies/gate.json terminal.deny, the two rules for person-only harness commands and task close (the full list is in their "why"); '
        'modules/gate/harnesscmd.py (read as the shell reads them); core/approval.py require_person (a terminal with keyboard and screen, '
        'or the board’s Terminal window for commands that ask no code). approve-command and approve-action ask for a typed code: '
        'your own terminal or the board’s button (docs/04-reference.md line 9).'),
]

CLOSING = dict(title='When the agent is stopped',
  text=[
   ('list', ['Read the reason first: it says why, and what to do next.',
             'Held outside call: approve it on its card. Git write: `harness approve-command` in your own terminal.',
             'No approval possible, and really needed: run it yourself. A guardrail file you change: `harness doctor --accept`.',
             'Never hand an approval command to the agent.']),
  ])
