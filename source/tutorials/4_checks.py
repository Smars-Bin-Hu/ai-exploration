# Harness tutorials · 4 Independent checks: a second agent, the reviewer, checks the work before it is written back.
# Build: .venv/bin/python source/tutorials/build.py 4_checks
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/); sources in each page's notes.
# Where docs and code disagree, the code wins: `review set` (the Independent review chips) works while the agent is at work
# (boardserve.py SETTINGS, L96), though docs/04-reference.md says it does not.

A = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/'

COVER = dict(
 sub='A second agent, the reviewer, checks the work before it goes back to your repository. '
     'How to ask for checks, how they are counted, and what to do when one fails or they run out.',
 how=['Read **1 A day with the harness** first: this deck adds checks to that day.'],
)

PAGES = [
 dict(kicker='What it is', title='A reviewer that has not seen how the work was made',
  text=[
   'An **independent check** is done by the **reviewer**: a second agent, new for every check.',
   ('list', ['It reads the requirement (`REQ.md`), the plan, the work and the diff, not the author’s reasoning.',
             'It changes no file.',
             'It answers PASS or FAIL, with a file and line for each finding.']),
   'The harness saves its answer; the agent cannot change it.',
  ],
  notes='Sources: .github/agents/reviewer.agent.md (tools read, search, execute; no file written; never LOG.md or TODO.md; '
        'VERDICT first line, file:line per finding); docs/02-features.md "Independent checks"; '
        'taskreview.py L1-22; gate.json L131-136 (person-only commands); hook PostToolUse writes verdict.md (docs/04-reference.md L281).'),

 dict(kicker='When to ask', title='Nothing is checked unless you ask',
  text=[
   'An agent checking its own work keeps its blind spots. A fresh reviewer does not share them.',
   ('list', ['**1** check: enough day to day.',
             '**2** in a row: an important change. Reviewers can disagree on the same work.',
             'At most **5**.']),
   'Each check runs its own reviewer and costs Credits.',
   ('small', 'Only you set the number; the harness refuses the agent’s attempts.'),
  ],
  notes='Sources: docs/02-features.md L93, L105 (1 day to day, 2 more certain, n at most 5); taskreview.py DEFAULTS max_n 5; '
        'messages.en.json desk.rv.cost, review.off ("Do not switch them on yourself"); gate.json person-only commands '
        '(task review set, extend, waive, dismiss); guide 11-task.md "Left to a person".'),

 dict(kicker='Step 1 · Switch checks on', title='Pick a number on the task page',
  text=[
   ('steps', ['Open the task page on the board.',
              'Press **Independent review** at the top.',
              'Pick a number, or **off**.']),
   'No code is asked. You may change it while the agent works; the agent is told with the next message it gets.',
  ],
  pic=(A + 'task-overview.png', (20, 0, 1000, 125)), wide=True,
  caption='The head of a task page: Independent review 2. The marks beside the stages are its checks.',
  notes='Sources: web/desk.js L803-838 (reviewButton: chips 0..max_n, 0 shown as "off"; served board, open task only); '
        'messages.en.json desk.rv.button, desk.rv.off, desk.rv.hint, review.set.next; boardserve.py L96 SETTINGS and L798-801 '
        '(review set: one click, no code, works while the agent is at work); taskreview.py set_by_person L476-494.'),

 dict(kicker='Step 1 · Or in a message', title='Or write [review]=n in the chat',
  text=[
   'In any message of the task, write `[review]=1` (or 2, 3…). Once is enough; later messages need not repeat it. `[review]=0` switches the checks off.',
   'No task yet? The agent opens one first, and the number goes with it.',
   ('code', '[review]=1 check the work of sales_report_fix; do not change files'),
   ('small', 'This line asks only for a check of work already written.'),
  ],
  shot='A Copilot chat in VS Code with a message that starts with [review]=1, sent in a task',
  notes='Sources: taskreview.py marker() L63-66 and set_n L265-276 (capped at max_n); messages.en.json rules.review.no_task; '
        'docs/01-quickstart.md L166 and L174-176 (the "only checking existing work" line); docs/02-features.md L93.'),

 dict(kicker='Step 2 · Let it check', title='When the work is written, the reviewer is called',
  text=[
   ('steps', ['The agent runs `harness task review start`: this version is saved.',
              'It calls the reviewer, with no reasoning.',
              'The answer is saved in `REVIEW/`.']),
   'Meanwhile **Live** shows the reviewer’s steps.',
   'If `REQ.md` asks for a run you do first, the task **waits for your run**: do it and send the result in the chat. No check starts before.',
  ],
  shot='The Live tab of a task while a check runs: the reviewer call, with its latest steps under it',
  notes='Sources: messages.en.json review.start.next (one sentence, no reasoning), review.call.no_round; taskreview.py L6-8; '
        'docs/02-features.md L266 (Live shows a subagent’s steps), L338 (working while a subagent runs), L314 (Review tab says which round is out); '
        'not_ready L320-329, mark_run L338-356 (no check used while the person’s run is not back); messages.en.json review.runs_missing, review.runs_marked, task.waiting.run; docs/02-features.md L102.'),

 dict(kicker='How they count', title='Passes count in a row, on the work as it is now',
  text=[
   'Counting back from the newest check, each PASS in a row on this exact version counts.',
   'The version is the work files, `REQ.md` and `PLAN.md`. Change any of them and the earlier passes stop counting: the work is checked again.',
   'Notes such as `TASK.md`, `TODO.md` and `LOG.md` do not count as a change.',
  ],
  pic=(A + 'board-list.png', (40, 225, 1190, 470)), wide=True,
  caption='The board’s Checks column: one dot per check asked, green for each pass in a row.',
  notes='Sources: taskreview.py passes() L151-158, summary L240-257; tasksnap.py L30-50 (SKIP_FILES: TASK.md, TODO.md, LOG.md, '
        'the diffs; REQ.md and PLAN.md are in the digest); rounds_now L141-143 (a new round of the task starts again); '
        'docs/02-features.md L245 (the dots); messages.en.json board.col.reviews.'),

 dict(kicker='Step 3 · When a check fails', title='A FAIL: the agent fixes it and checks again',
  text=[
   'On a FAIL the agent fixes the findings itself and starts a new check, with a new reviewer. From the 2nd check on, only what affects correctness is reported.',
   'A finding must name a file and line that exist, or it is dropped. A FAIL left with none is given back, at most twice.',
   ('small', 'Nothing for you to do yet.'),
  ],
  pic=(A + 'task-review.png', (40, 1055, 990, 1265)),
  caption='A FAIL on the Review tab, each finding with its file and line.',
  notes='Sources: messages.en.json review.next.fix, review.package.later, review.package.output; reviewcheck.py and '
        'docs/02-features.md L103 (dropped findings; an invalid FAIL is given back, review.free_invalid = 2); '
        'reviewer.agent.md "Do not" (findings only, no fixes).'),

 dict(kicker='Before the write-back', title='Why the dry run is refused',
  text=[
   'The **write-back** copies the approved files into your repository. First the agent runs a **dry run** (`task promote --dry-run`): it makes the plan you approve.',
   'With checks on, the dry run is refused until the passes in a row reach your number, or you waive them.',
   ('small', 'A task with no write-back has no dry run; the agent is reminded instead.'),
  ],
  shot='The Copilot chat when the dry run is refused: the line “It cannot be promoted yet: independent check passes needed in a row”',
  notes='Sources: task.py run_promote L911-928 (taskreview.require on --dry-run); taskreview.py require L563-568, satisfied L260-262; '
        'messages.en.json review.promote.refused; handler.py review_stop L315-332 (the Stop hook reminds once per prompt).'),

 dict(kicker='Step 4 · When checks run out', title='Checks used up: you decide',
  text=[
   'You get your number + 2 checks, plus any you give. Used up without enough passes, the agent stops: **the checks are used up and wait for your decision**.',
   'Read the newest FAIL on **Review**, then press:',
   ('list', ['**More checks**: 2 more.',
             '**Waive checks**: this version goes through, until the work changes.']),
   ('small', 'Each asks for its code. Or, in a terminal:'),
   ('code', 'harness task review extend --task <name> --checks 2'),
  ],
  shot='The task page of a task whose checks are used up: the waiting box with More checks and Waive checks',
  notes='Sources: taskreview.py limit L161-163 (n + extra_checks 2 + extra), extend L496-509, waive L512-528; boardserve.py L150-151 '
        '(the board’s More checks gives 2); tasklife.py L297-303 (waits "review"); taskboard.py L117; messages.en.json '
        'task.waiting.review, board.action.review-extend, board.action.review-waive, desk.hint.review-waive, review.limit.'),

 dict(kicker='Step 4 · Stop checks early', title='Stop checks early, then tell the agent',
  text=[
   '**Waive checks** appears only once the checks are used up. Before that, either:',
   ('list', ['set **Independent review** to **off** (no code); or',
             'waive this version in your own terminal, any time it lacks passes; it asks for its code.']),
   ('code', 'harness task review waive --task <name>'),
   'After **More checks** or a waive, nothing tells the agent: press **Send to agent** or say so in the chat.',
  ],
  notes='Sources: taskboard.py L117 ACTIONS_BY_WAIT (review extend/waive offered only when the task waits "review", i.e. used up) and '
        'tasklife.py L297-303; web/desk.js shows desk.actions only (no other waive button); taskreview.py waive L512-528 '
        '(refused only when n is 0 or passes are enough; the waiver holds for this digest); set_by_person L476-494 (off, no code); '
        'L507, L527 (waiting "go-review"); chatsend.py L48; messages.en.json board.action.send, task.waiting.go-review; '
        'commands.py L236-242 (extend --checks 1-9, default 2); paths.py SHORT_COMMAND "harness".'),

 dict(kicker='Step 5 · A check you judge wrong', title='Dismiss a check that judged wrong',
  text=[
   'When the task waits for you and the newest check did not pass, the board offers **Dismiss check**.',
   'Read the findings and the lines they name first. Dismiss only when the reviewer was wrong: the check then counts neither as used nor as a FAIL, and `LOG.md` says so. It asks for its code; then **Send to agent**.',
   ('code', 'harness task review dismiss --task <name>'),
  ],
  notes='Sources: taskboard.py L137-138 (offered when the task waits and dismiss_of is set); tasklife.py dismiss_of L376-383; '
        'taskreview.py dismissable L531-534, dismiss L537-559 (LOG.md line, waiting go-review); messages.en.json '
        'board.action.review-dismiss, desk.hint.review-dismiss, review.dismiss.screen; commands.py L243-246.'),

 dict(kicker='Step 6 · Read the results', title='Read the results on the Review tab',
  text=[
   'On the task page open **Results**, then **Review**.',
   ('list', ['The top line: checks asked in a row, passes on the version as it is now, checks used of the limit.',
             'Each check, newest first: PASS or FAIL, on **this version of the work** or **an earlier version of the work**.',
             '**What the reviewer was given** opens what it read.']),
  ],
  pic=(A + 'task-review.png', (40, 300, 990, 760)),
  caption='Two passes on this version; 3 of 4 checks used.',
  notes='Sources: messages.en.json desk.group.deliver ("Results"), desk.tab.review, desk.review.sum, desk.review.current, '
        'desk.review.earlier, desk.review.given; docs/02-features.md L300, L314; taskdesk.py L72 (a settled task shows the checks as they stood).'),
]

CLOSING = dict(title='Checks help; they do not replace you',
  text=[
   'A PASS means a fresh reviewer read the work against the requirement and found nothing. It does not run your repository’s code. '
   'You still read the changes before you approve the write-back.',
   'Only you set the number, give more checks, waive them or dismiss one.',
  ])
