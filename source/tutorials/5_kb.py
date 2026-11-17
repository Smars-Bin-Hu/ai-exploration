# Harness tutorials · 5 Knowledge base: what the team knowledge base is, how it is built once, how a `kb` task keeps it
# true, and how the agent reads it in your tasks.
# Build: .venv/bin/python source/tutorials/build.py 5_kb
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/, read only); sources in each page's notes.
# Names in examples (orders, returns, job:Nightly_Load, usp_load_orders) are made up.
# Where 1.7.45 shows what a task read: not on the task page. The knowledge base window (column "Last read by a task"),
# `harness kb reads --task <name>`, and the task report report.md (section "Knowledge base files read") do.

H = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/'
A = H + 'docs/images/'

COVER = dict(
 sub='What the team knowledge base is and why the agent reads it, how it is built once from your code, '
     'how a knowledge base task keeps it true, and how to see what the agent read.',
 how=['Read **1 A day with the harness** first: a knowledge base task goes the same way, with a different write-back.'],
)

PAGES = [
 dict(kicker='What it is', title='Short pages about your code, read before the code',
  text=[
   'The **knowledge base** is a folder of short pages about your team’s code, in a git repository of its own. '
   'The agent reads it before the code: cheaper, and more often right.',
   ('code', 'README.md — the list of domains\n'
            'domains/orders/architecture.md — the overview\n'
            'domains/orders/objects/index.jsonl — one line per object\n'
            'domains/orders/objects/jobs.md — the cards of the jobs'),
   'A **domain** is one area of the code; a **card** describes one object. The code stays the truth: each card names the commit it was read at.',
  ],
  notes='Sources: docs/08-knowledge-base.md "The idea" and "What a domain looks like"; .harness/contracts/kb/README.md; '
        '.github/skills/harness-rookie-new-knowledgebase/references/road.md "Say it like this"; docs/03-configure.md "Knowledge base" '
        '(knowledge-base/, its own git repository, registered with knowledge_base: true).'),

 dict(kicker='Step 1 · Find it', title='Open the knowledge base window',
  text=[
   'Press the **book** button at the bottom right of the board. A number on it counts **stale cards**: cards whose code changed since they were written.',
   ('small', 'Company Context, top left of the board: hover it to see what the knowledge base brought.'),
  ],
  pic=(A + 'board-list.png', (760, 0, 1360, 760)),
  caption='The book: third round button.',
  notes='Sources: web/dock.js L1 (the book opens the knowledge base window), badge() and messages dock.kb.badge.one/.n; '
        'web/board.js L450-468 (board.kb.mark = "Company Context", board.kb.found on hover); docs/08-knowledge-base.md "See where it stands".'),

 dict(kicker='Step 2 · Where it stands', title='Read the Overview',
  text=[
   ('list', ['The steps, from **Code repositories** to **Keeping it true**.',
             'The **Next** box says what is next, with its button.',
             'Per domain: **Cards**, **Learned**, **Stale**, **Requests**, **Last read by a task**.']),
   'A button with a speech bubble opens a Copilot chat; the rest costs nothing.',
   ('small', 'No knowledge base in this copy? Press Import a knowledge base (see the Install deck).'),
  ],
  pic=A + 'kb-overview.png',
  caption='The Overview of a knowledge base with five made-up domains.',
  notes='Sources: web/dock.js kbWindow, overview(), nextCard(), domainTable(), emptyState(); messages dock.kb.step.*, dock.kb.col.*, '
        'dock.kb.tile.*, dock.kb.legend, dock.kb.empty, dock.kb.empty.go = "Import a knowledge base"; tabs Overview, Map, Company, Domains, Look up, Health.'),

 dict(kicker='Build it · Start', title='Building it: once, led by the agent',
  text=[
   'None yet? One person builds it, once per code base. Needed first: **Code repositories** and **Knowledge base repository** done (button **Change the setup**).',
   'Then press **Do the next step in a chat**, or type `/harness-rookie-new-knowledgebase` in Copilot chat. The agent explains each step and asks only what you know.',
   ('small', 'Stop any time; later say “continue the knowledge base”.'),
  ],
  shot='The knowledge base window, tab Overview, with Toolkit as the next step: “Next is the toolkit…” and the button Do the next step in a chat',
  notes='Sources: .github/skills/harness-rookie-new-knowledgebase/SKILL.md (Prerequisites: targets and kb_repo; Opening; "continue the knowledge base"); '
        'web/dock.js nextButton() (targets/kb_repo: "Change the setup"; otherwise "Do the next step in a chat" starts harness-rookie-new-knowledgebase); '
        'messages dock.kb.next, dock.kb.what.toolkit, dock.setup; docs/08-knowledge-base.md "The quickest way"; road.md (about an hour of your time, once).'),

 dict(kicker='Build it · The first steps', title='Teach a script to read your code',
  text=[
   ('list', ['**Toolkit**: give 5 to 10 uses you know, like “job `Nightly_Load` runs `usp_load_orders`”. After its design, open a new chat and type `/generic-kb-toolkit-build`: only you may start it.',
             '**Map of the code**: the script lists objects and their uses.',
             '**Audit**: a sample scores it.',
             '**Domains**: confirm the cut into areas.']),
   ('small', 'Each step but the map is a task you approve.'),
  ],
  notes='Sources: road.md "The steps" (toolkit: 5 to 10 uses; map: nothing to give, no task; audit: approve the result; domains: confirm the cut); '
        'SKILL.md step 3 (one step, one task; the user types /generic-kb-toolkit-build in a new chat); messages dock.kb.what.toolkit/map/audit/domains, '
        'dock.kb.step.*; docs/08-knowledge-base.md table "The road" (the map runs with no task and no approval).'),

 dict(kicker='Build it · Learn a domain', title='Learn one domain in one task',
  text=[
   ('steps', ['Press **Learn** on the domain. Give its entry points (where work starts) and what is out of scope.',
              'On the task page, read the plan and its batches; press **Approve plan** once.',
              'Every two or three batches, press **Go on in a chat** (or **Go on**).',
              'Approve one write-back of the whole domain.']),
  ],
  pic=(A + 'kb-overview.png', (30, 185, 1130, 520)),
  caption='returns is half learned: Go on in a chat takes the next batch.',
  notes='Sources: road.md rows learn; SKILL.md step 3 (a domain in one task, from its plan to one write-back; "continue learn-<domain>" in a new chat); '
        'web/dock.js learn() (generic-kb-learn-plan, task learn-<domain>, kind kb), goOn() (generic-kb-learn-batch), nextCard(); '
        'messages dock.kb.learn = "Learn", dock.kb.go.chat = "Go on in a chat", dock.kb.next.batch, dock.kb.next.approve, dock.kb.next.finish; '
        'docs/08-knowledge-base.md "One task per domain" (the cards stay in the task until the whole domain is written back).'),

 dict(kicker='Keep it true · 1', title='When code changes: refresh the stale cards',
  text=[
   'When the agent fetches code whose card is older, it treats the card as history and checks the code.',
   'Stale cards show on the book, in the **Stale** column and in **Health**. Press **Refresh cards** on the domain: a task fixes them from the change.',
   ('small', 'Before you approve, read what changed in each card.'),
  ],
  shot='The knowledge base window, tab Health, section Stale cards listing a few changed cards of one made-up domain',
  notes='Sources: messages fetch.kb.stale, dock.kb.health.stale/changed/gone, dock.kb.refresh.cards = "Refresh cards"; '
        'web/dock.js action() (Refresh cards only on a learned domain with stale cards), refresh() (generic-kb-refresh, kind kb, task refresh-<domain>); '
        'docs/08-knowledge-base.md "Versions: as of when"; road.md "Keeping it true" 1.'),

 dict(kicker='Keep it true · 2', title='When a task teaches something: capture it',
  text=[
   'At the end of a task the agent may name what it learned, or cards it found wrong, and ask whether to capture them. Or press **Capture what was learned** under **Say something**.',
   'It only drafts `KB-DRAFT.md` in the task folder. You pick what stays; a knowledge base task writes it in.',
  ],
  notes='Sources: messages task.step.close (names them, asks, does not run it unasked); .github/skills/generic-capture-knowledge/SKILL.md '
        '(board-label "Capture what was learned", board-opens reply; writes KB-DRAFT.md only; "Putting it in is another job": a task of kind kb); '
        'web/reply.js fillSkills (the chip puts the slash command in the box; you press Send); .github/instructions/knowledgebase.instructions.md "Keeping it true: your part".'),

 dict(kicker='Keep it true · 3', title='A knowledge base task writes the change',
  text=[
   'A task of kind **knowledge base update** changes it like code: the agent copies the pages into the task folder and edits them there. Its edit tools cannot write the knowledge base itself.',
   'Confirm the requirement and approve the plan as on any task. Read the plan for which cards change and why.',
  ],
  notes='Sources: messages task.kind.kb = "knowledge base update"; docs/03-configure.md "Letting a task update the knowledge base" '
        '(task fetch kb/<path>, DEV/kb/, plan approval, promote); knowledgebase.instructions.md ("Never edit the knowledge base from another task"); '
        'web/desk.js WRITES_BACK = ["dev", "kb"]; taskdesk.py L534 (dev, test, kb stand on a confirmed requirement).'),

 dict(kicker='Keep it true · 4', title='Approve the write-back: one commit',
  text=[
   'Open **Changes** and read each card’s diff. Does each fact cite its source? Any secrets or customer data? Then press **Approve promote** and type the code.',
   'The harness commits once, straight on the knowledge base’s base branch (`main` by default). Push it yourself.',
   ('small', 'It stops if the knowledge base is on another branch or has uncommitted files.'),
  ],
  shot='A knowledge base task page, tab Changes, showing the diff of one card under kb/domains/<domain>/objects/, with Approve promote at the top',
  notes='Sources: messages desk.hint.approve-promote.kb, board.action.approve-promote, promote.done.kb ("The harness does not push"), '
        'promote.done.kb.local (no remote: nothing to push), promote.kb.branch, promote.kb.dirty, promote.kb.git_config; '
        'docs/03-configure.md table (knowledge base: straight into base_ref, one commit; needs a clean tree, the base branch checked out, git user.name and user.email); '
        'knowledgebase.instructions.md "Writing it" (no secrets, personal data, production rows); generic-capture-knowledge Gotchas (evidence per entry).'),

 dict(kicker='In your tasks', title='How the agent reads it during a task',
  text=[
   'In **New task**, tick the domains under **Knowledge base**, or **None**.',
   ('steps', ['`README.md`, then the domain’s `architecture.md`.',
              'One line of `objects/index.jsonl`, then that card only.',
              'Then only that object’s code.']),
   'Each step deeper gets a line in the task’s `LOG.md`. A wrong or missing card is noted and raised at the next stop.',
  ],
  notes='Sources: .github/instructions/knowledgebase.instructions.md "Reading, for a task" 1-6 and "Keeping it true: your part"; '
        'messages board.new.kb = "Knowledge base", board.new.kb.none = "None", board.new.kb.hint, fetch.kb.cards; '
        'web/chat.js L284-319; chatnew.py domain_line; docs/03-configure.md (README.md is the entry, read first).'),

 dict(kicker='In your tasks', title='See what it read',
  text=[
   'The task page does not list it. Look here:',
   ('list', ['the window’s **Last read by a task** column;',
             'in your own terminal:']),
   ('code', 'harness kb reads --task fix_order_totals'),
   'And the task report, `.workspace/reports/tasks/<task>/report.md`, section **Knowledge base files read**.',
   ('small', 'Only files a tool names count. A search over a folder counts the folder.'),
  ],
  notes='Sources: core/kbreads.py (paths of read and search tools and of terminal commands; names only); core/kbreads.py last_by_domain '
        '(any tool call, per domain) and dock.kb.col.read; modules/observe/commands.py kb reads (--task, --days); docs/04-reference.md "kb reads"; '
        'task_report.py L96-102 (mdreport.kb.title, written when the task is closed and on `task report`); common.py TASK_REPORTS_DIR; '
        'messages kb.reads.note; observe.json knowledge_base_reads (on by default). No tab of desk.js shows the kb field of the call log.'),
]

CLOSING = dict(title='The knowledge base, in short',
  text=[
   ('list', ['The agent reads the knowledge base before the code; the code stays the truth.',
             'It is built once, step by step, with `/harness-rookie-new-knowledgebase`.',
             'It changes only through a knowledge base task: you approve the plan and the write-back, which is one commit on its base branch. Push it yourself.']),
  ])
