# Harness tutorials · 4 Independent checks: a second agent, the reviewer, checks the work before it is written back.
# Build: .venv/bin/python source/tutorials/build.py 4_checks
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/); sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data), cropped to the part each step is about.
# Placeholders (VS Code, a terminal, a board state with no picture yet) are listed in shots/4_checks.md.
# Where docs and code disagree, the code wins: `review set` (the Independent review chips) works while the agent is at work
# (boardserve.py SETTINGS, L96), though docs/04-reference.md says it does not; Waive checks is on the board only when the checks are
# used up (taskboard.py L117), while `task review waive` in a terminal works whenever the passes are short (taskreview.py L512-528).

B = 'source/tutorials/img/_board/'

COVER = dict(
 sub='A second agent, the reviewer, checks the work before it goes back to your repository. It reads the requirement, '
     'the plan and the work, never the author’s reasoning, and answers PASS or FAIL. A new reviewer every time.',
 how=['Nothing is checked unless you ask, and only you set how many checks. Read **1 A day with the harness** first.'],
)

CONTENTS = True

PAGES = [
 # ---- Switch checks on --------------------------------------------------------------------------------------
 dict(group='Switch checks on', steps=[
   dict(pic=(B + 'checks-chip.png', (270, 10, 625, 75)),
        text='On the task page, press **Independent review**.'),
   dict(pic=(B + 'checks-chip.png', (20, 95, 625, 315)),
        text='The number of passes in a row the work needs before the write-back. Only you can set it.'),
   dict(pic=(B + 'checks-chip.png', (20, 320, 625, 525)),
        text='Pick one; **off** stops checks. No code. Each check costs Credits: **1** day to day, **2** for important work.'),
   dict(shot='VS Code: the Copilot chat of a task, with “[review]=1” typed at the start of a message', aspect=16/10,
        text='Or write `[review]=1` in a message of the task. `[review]=0` turns checks off.'),
  ],
  notes='Sources: web/desk.js L803-838 (reviewButton: chips 0..max_n, 0 shown as "off"; served board, open task); messages.en.json desk.rv.button, desk.rv.off, '
        'desk.rv.hint ("Only you can set this"), desk.rv.cost, review.set.next; boardserve.py L96 SETTINGS, L798-801 (review set: no code, works while the agent is at work); '
        'taskreview.py set_by_person L476-494, marker L63-66, set_n L265-276 (max_n 5); docs/02-features.md L93, L105 (1 day to day, 2 more certain); '
        'gate.json L131-136 (task review set|extend|waive|dismiss refused to the agent); messages.en.json review.off; task.py L191-200 (no task yet: n goes into the task opened).'),

 # ---- While it checks ---------------------------------------------------------------------------------------
 dict(group='While it checks', steps=[
   dict(pic=(B + 'review.png', (74, 716, 2137, 770)),
        text='When the work is written, the agent runs `harness task review start` and calls the reviewer.'),
   dict(pic=(B + 'run.png', (73, 299, 2144, 483)),
        text='Task **waits for your run**? No check starts until you give the result of that run.'),
   dict(pic=(B + 'run.png', (73, 1440, 2144, 2040)),
        text='Do the run. Paste the result under **Give the results here**, or give it in the chat.'),
  ],
  notes='Sources: messages.en.json review.start.next (one sentence, no reasoning), desk.review.hint ("The agent cannot change an answer"); taskreview.py L6-8, record L412-436; '
        'not_ready L320-329, mark_run L338-356, start L359-373 (refused, no check used, while the person’s run is not back or a handoff is open); '
        'messages.en.json review.runs_missing, review.runs_marked, review.handoff_open, task.waiting.run, desk.wait.run.form; docs/02-features.md L102-103.'),

 # ---- Read the results --------------------------------------------------------------------------------------
 dict(group='Read the results', steps=[
   dict(pic=(B + 'review.png', (74, 790, 1150, 830)),
        text='**Results › Review**: checks asked, passes on this version, checks used of the limit.'),
   dict(pic=(B + 'review.png', (74, 2001, 2137, 2446)),
        text='A FAIL names a file and line per finding. The agent fixes it; a new reviewer checks again.'),
   dict(pic=(B + 'review.png', (74, 860, 1000, 945)),
        text='Passes count in a row on **this version of the work**. Changing the work, `REQ.md` or `PLAN.md` restarts the count.'),
   dict(pic=(B + 'list.png', (1060, 726, 1369, 1060)),
        text='On the board list, **Checks** has one dot per check asked; green is a pass.'),
  ],
  notes='Sources: messages.en.json desk.group.deliver, desk.tab.review, desk.review.sum, desk.review.current, desk.review.earlier, review.next.fix, review.package.later '
        '(from the 2nd check only what affects correctness), board.col.reviews; taskreview.py passes L151-158, summary L240-257; tasksnap.py L30-50 '
        '(TASK.md, TODO.md, LOG.md not in the digest; REQ.md and PLAN.md are); reviewcheck.py (findings with no real file:line dropped; an empty FAIL given back, '
        'review.free_invalid 2); docs/02-features.md L245 (the dots).'),

 # ---- Before the write-back ---------------------------------------------------------------------------------
 dict(group='Before the write-back', steps=[
   dict(shot='VS Code: the agent’s terminal call “harness task promote --dry-run” and its output “It cannot be promoted yet: '
             'independent check passes needed in a row: 1; so far: 0.”', aspect=16/6,
        text='With checks on, the dry run of the write-back is refused until the passes reach your number, or you waive.'),
  ],
  notes='Sources: task.py run_promote L911-928 (taskreview.require on --dry-run); taskreview.py require L563-568, satisfied L260-262; messages.en.json review.promote.refused; '
        'handler.py review_stop L315-332 (a task that writes nothing back has no dry run: the Stop hook reminds the agent once per prompt).'),

 # ---- Checks used up ----------------------------------------------------------------------------------------
 dict(group='Checks used up', steps=[
   dict(pic=(B + 'checks-used-up.png', (40, 20, 1130, 95)),
        text='Your number + 2 checks, plus any you give, used up without enough passes: the agent stops.'),
   dict(pic=(B + 'checks-used-review.png', (86, 960, 2128, 1365)),
        text='First read the newest FAIL on **Review**.'),
   dict(pic=(B + 'checks-used-up.png', (78, 300, 2145, 660)),
        text='Then choose on the task page. Each button asks for its code.'),
  ],
  notes='Sources: taskreview.py limit L161-163 (n + extra_checks 2 + extra); tasklife.py L297-303 (waits "review"); taskboard.py L117 (More checks, Waive checks), '
        'L137-138 (Dismiss check); messages.en.json task.waiting.review, board.action.review-extend, board.action.review-waive, board.action.review-dismiss, '
        'desk.hint.review-extend, desk.hint.review-waive, review.limit.'),

 dict(steps=[
   dict(pic=B + 'checks-more.png',
        text='**More checks**: two more; type the code, **Approve**. Terminal: `harness task review extend --task <name>`.'),
   dict(pic=B + 'checks-waive.png',
        text='**Waive checks**: this version goes through without the passes, until the work changes.'),
   dict(shot='A task page whose state reads “the checks are decided: tell the agent to go on”, with the Send to agent button', aspect=16/5,
        text='Unlike a plan approval, this does not wake the agent: press **Send to agent**, or say so in the chat.'),
  ],
  notes='Sources: boardserve.py L150-151 (the board’s More checks gives 2; Waive checks); taskreview.py extend L496-509, waive L512-528 (digest-bound; refused if '
        'the work changed while confirming), L507, L527 (waiting "go-review"); messages.en.json review.extend.ask, review.waive.screen, task.waiting.go-review, '
        'board.action.send, desk.wait.go-review; chatsend.py L48 (“The checks are decided. Go on.”); approval.py CODE_LENGTH 6; boardserve.py L97, L842 WAKING (confirm-req, approve-plan, approve-promote only: review extend/waive/dismiss do not wake the agent).'),

 # ---- A check you judge wrong -------------------------------------------------------------------------------
 dict(group='A check you judge wrong', steps=[
   dict(pic=(B + 'checks-used-up.png', (78, 545, 2145, 640)),
        text='The newest check did not pass and the task waits? Read its findings and the lines they name.'),
   dict(pic=B + 'checks-dismiss.png',
        text='Reviewer wrong? **Dismiss check**: it counts neither as used nor as a FAIL. Then **Send to agent**.'),
  ],
  notes='Sources: taskboard.py L137-138 (offered when the task waits and the newest counted check did not pass); tasklife.py dismiss_of L376-383; taskreview.py dismissable '
        'L531-534, dismiss L537-559 (LOG.md line, waiting go-review); messages.en.json board.action.review-dismiss, desk.hint.review-dismiss, review.dismiss.screen; '
        'commands.py L243-246 (harness task review dismiss --task, --round).'),

 # ---- Stop checks early -------------------------------------------------------------------------------------
 dict(group='Stop checks early', steps=[
   dict(pic=(B + 'checks-chip.png', (20, 440, 625, 525)),
        text='Before checks are used up, the board has no **Waive checks**. You can set **off**.'),
   dict(shot='A terminal: “harness task review waive --task check-coupon-codes” waiting at “To stop checking and let this version through, type …”', aspect=16/7,
        text='Or waive in your own terminal, any time the passes are short: `harness task review waive --task <name>`.'),
  ],
  notes='Sources: taskboard.py L117 ACTIONS_BY_WAIT (review extend/waive offered only when the task waits "review", i.e. used up); web/desk.js shows desk.actions only; '
        'taskreview.py waive L512-528 (refused only when n is 0 or the passes are enough; holds for this digest); set_by_person L476-494 (off, no code); '
        'commands.py L236-242 (extend --checks 1-9, default 2; waive; --task); paths.py SHORT_COMMAND "harness"; messages.en.json review.waive.ask.'),
]

CLOSING = dict(title='Checks help; they do not replace you',
  text=[
   'A PASS: a fresh reviewer found nothing against the requirement. It does not run your code. You still read the changes before the write-back.',
   'A task with no write-back has no dry run; the agent is reminded to finish its checks.',
   'Only you set the number, give more checks, waive or dismiss.',
  ])
