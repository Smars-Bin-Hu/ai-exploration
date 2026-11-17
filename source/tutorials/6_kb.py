# Harness tutorials · 6 Knowledge base: the team knowledge base, one small step per picture: open it, build it once,
# keep it true with a knowledge base task, and see how the agent reads it in your tasks.
# Build: .venv/bin/python source/tutorials/build.py 6_kb
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/); sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data). The book button and Go on in a chat come from
# harness 1.7.45 docs/images (dark theme), because no _board picture shows them. Placeholders are listed in shots/6_kb.md.
# Kept from the fact-check (review/5_kb-r1.md) and the newcomer test (test/5_kb-*): a skill chip only fills the box (press
# Send); the architecture step has no button (say `continue learn-<domain>`); which buttons open a Copilot chat;
# report.md only once the task is closed, its KB section only if it read any; Last read by a task is a date per domain;
# a team with none brings in a folder with README.md and an empty domains/ (1.7.45 has no button that makes an empty one). The task page does not list what a task read.

B = 'source/tutorials/img/_board/'
D = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/docs/images/'

COVER = dict(
 sub='The team knowledge base: short pages about your code that the agent reads before the code. '
     'How to open it, build it once, keep it true with a knowledge base task, and see what the agent read.',
 how=['Read **1 A day with the harness** first: a knowledge base task goes the same way, with a different write-back.'],
)

CONTENTS = True

PAGES = [
 # ---- Open it -----------------------------------------------------------------------------------------------
 dict(group='Open it', steps=[
   dict(pic=(D + 'board-list.png', (1230, 555, 1360, 680)),
        text='Press the **book** at the bottom right of the board. Its number counts stale cards.'),
   dict(pic=(B + 'kb-overview.png', (36, 100, 2364, 306)),
        text='The **Knowledge base** window. **Overview** shows the steps of a build.'),
   dict(pic=(B + 'kb-overview.png', (36, 330, 2364, 486)),
        text='**Next** says what comes next, with its button.'),
  ],
  notes='Sources: web/dock.js L1 (the book opens the knowledge base window), badge(), messages dock.kb.badge.n ("their sources changed since they were written"); '
        'dock.js kbWindow tabs overview/atlas/company/domains/lookup/health; messages dock.kb.step.*, dock.kb.next.plan, dock.kb.learn. '
        'The book picture is docs/images/board-list.png (1.7.45 docs, dark theme): no _board picture shows the buttons at the bottom right.'),

 dict(steps=[
   dict(pic=(B + 'kb-overview.png', (36, 714, 2364, 920)),
        text='Per domain: cards, how much is learned, stale cards, requests, **Last read by a task**.'),
   dict(pic=(B + 'kb-overview.png', (36, 950, 1320, 1000)),
        text='A speech bubble, or “in a chat” in a button’s name: it opens a Copilot chat.'),
   dict(pic=(B + 'kb-map.png', (36, 192, 2364, 948)),
        text='**Map**: which domain uses which. Click a domain. Free: no Copilot.'),
   dict(pic=(B + 'kb-lookup.png', (36, 192, 2364, 690)),
        text='**Look up**: an object’s name; what uses it, and what it uses.'),
  ],
  notes='Sources: messages dock.kb.col.*, dock.kb.legend ("opens a chat in VS Code and uses Copilot. Everything else here runs on this computer"); '
        'dock.js nextButton() ("Do the next step in a chat" has no bubble but starts harness-rookie-new-knowledgebase), audit buttons "Run the audit in a chat"; '
        'dock.atlas.* and docs/08-knowledge-base.md "See how the domains hang together"; dock.kb.lookup, dock.kb.lookup.usedby/uses (from the map, kb near).'),

 dict(steps=[
   dict(pic=(B + 'kb-company.png', (36, 216, 2364, 800)),
        text='**Company**: what your agent has (tools, skills, standards) and where each comes from.'),
   dict(pic=(B + 'kb-domains.png', (36, 204, 2364, 420)),
        text='**Domains**: every domain, its state, and **Learn** or **Refresh cards**.'),
  ],
  notes='Sources: docs/08-knowledge-base.md "See how the domains hang together" (the Company tab lists tools, skills, standards); '
        'web/companytab.js; dock.js domains(), domainTable(full) with State (dock.kb.state.done/listed/task), action() (Learn, Refresh cards).'),

 # ---- Build it once -----------------------------------------------------------------------------------------
 dict(group='Build it once', steps=[
   dict(pic=(B + 'lobby.png', (44, 311, 2176, 383)),
        text='No knowledge base yet? First make a folder holding a `README.md` and an empty `domains/` folder.'),
   dict(pic=(B + 'tour-setup-window.png', (80, 495, 1560, 615)),
        text='The gear above the book (**Change the setup**) › **Knowledge base** › **Folder**: its path, **Save**.'),
   dict(shot='The knowledge base window, tab Overview, with Toolkit as the next step: “Next is the toolkit…” and the button Do the next step in a chat',
        aspect=16/5,
        text='It is now a git repository. Then build it from your code: **Do the next step in a chat**.'),
   dict(shot='VS Code: a Copilot chat with /harness-rookie-new-knowledgebase typed in the chat box, not sent', aspect=16/10,
        text='Or type `/harness-rookie-new-knowledgebase` in a Copilot chat. Later: “continue the knowledge base”.'),
  ],
  notes='Sources: messages dock.kb.empty.go = "Import a knowledge base", ready.p.kb.short; setupjob.py check (Folder: refused when it holds nothing but README.md, '
        'setup.kb.nothing; KB_IGNORED; README.md wanted as the entry, setup.kb.noreadme), copy_folder (into knowledge-base/), repository() (kbsetup.init: git init, '
        'one first commit on main, registered as kb with knowledge_base true; setup.kb.git); dock.js L535 (the gear is Change the setup), setup.save = "Save"; '
        'the build (toolkit/, domains/) is then written into that repository by kb tasks; setupjob.py L82-83 and L111 (a folder with no content is '
        'not copied; Not yet makes nothing); kbsetup.py init (kb.init.empty: no content, no repository); targets.KB_IGNORED (a README alone is no content). '
        'dock.js nextButton() (targets/kb_repo: "Change the setup"; otherwise "Do the next step in a chat" starts harness-rookie-new-knowledgebase); '
        'SKILL.md harness-rookie-new-knowledgebase (Prerequisites; "continue the knowledge base"); road.md (about an hour of your time, once).'),

 dict(steps=[
   dict(shot='VS Code: the toolkit-design chat in which the agent asks for 5 to 10 uses the person knows', aspect=16/10,
        text='**Toolkit**: in the chat, the agent asks for 5 to 10 uses you know (“job X runs Y”).'),
   dict(shot='VS Code: a new Copilot chat with /generic-kb-toolkit-build typed in the chat box, not sent', aspect=16/10,
        text='After its design, open a new chat and type `/generic-kb-toolkit-build`: only you may start it.'),
  ],
  notes='Sources: road.md "The steps" (toolkit: 5 to 10 uses); kbstatus.next.toolkit; SKILL.md step 3 (the user types /generic-kb-toolkit-build '
        'in a new chat; disable-model-invocation). The use in the picture is from Look up (the map).'),

 dict(steps=[
   dict(pic=(B + 'kb-health.png', (36, 216, 2364, 324)),
        text='**Map of the code**: a script, no task. **Audit**: a sample scores the map.'),
   dict(pic=(B + 'kb-domains.png', (36, 204, 1400, 420)),
        text='**Domains**: confirm the cut into areas once. Each step but the map is a task you approve.'),
  ],
  notes='Sources: road.md "The steps" (toolkit: 5 to 10 uses; map: nothing to give, no task; audit: approve; domains: confirm the cut); '
        'kbstatus.next.toolkit; SKILL.md step 3 (the user types /generic-kb-toolkit-build in a new chat; disable-model-invocation); '
        'messages dock.kb.audit, dock.kb.audit.done = "Passed for this toolkit."; docs/08-knowledge-base.md "The road".'),

 dict(steps=[
   dict(pic=(B + 'kb-overview.png', (36, 330, 2364, 486)),
        text='Press **Learn**: the **New task** window opens, filled in (Kind **knowledge base update**).'),
   dict(pic=(B + 'new-task.png', (43, 1447, 1058, 1728)),
        text='Add the entry points (where work starts) and the scope, then press **Create and send**.'),
   dict(pic=(B + 'plan.png', (78, 300, 2148, 533)),
        text='On the task page, read the plan and its batches; press **Approve plan** once.'),
  ],
  notes='Sources: dock.js learn() (generic-kb-learn-plan, kind kb, task learn-<domain>); generic-kb-learn-plan step 7 (the plan lists every batch, approved once); '
        'board.action.approve-plan. Plan picture: a development task, for the Approve plan card.'),

 dict(steps=[
   dict(pic=('source/tutorials/img/6_kb/kb-go-on-docs.png', (37, 192, 1123, 244)),
        text='Every two or three batches: **Go on in a chat** (a new chat).'),
   dict(shot='The knowledge base window, tab Overview, with “Next: finish <domain> in the task learn-<domain>: write its architecture, then promote it.” and no button',
        aspect=16/4,
        text='No batch left: no button. Say `continue learn-<domain>` in a new chat; it writes the architecture.'),
  ],
  notes='Sources: dock.js learn() (generic-kb-learn-plan, kind kb, task learn-<domain>), goOn() (generic-kb-learn-batch), nextCard() '
        '(dock.kb.next.finish has no button); dock.js taskChat → CHAT.create (Learn and Refresh cards fill the New task window; board.new.go = "Create and send", dock.task.note); messages dock.kb.next.plan/approve/batch/finish, dock.kb.go.chat; generic-kb-learn-plan step 7 (approve once); '
        'generic-kb-learn-batch SKILL.md step 6 ("continue learn-<d>"; a new chat every two or three batches); kbstatus.next.task_architecture. '
        'Plan picture: a development task, for the Approve plan card. Go on in a chat: docs/images/kb-overview.png (1.7.45 docs, dark theme).'),

 dict(steps=[
   dict(pic=(B + 'kb-changes-promote.png', (78, 733, 2142, 1232)),
        text='Then read the cards in **Changes**: one write-back of the whole domain.'),
   dict(pic=(B + 'kb-changes-promote.png', (78, 300, 2148, 577)),
        text='Press **Approve promote** and type the code.'),
  ],
  notes='Sources: docs/08-knowledge-base.md "One task per domain" (the cards stay in the task until the whole domain is written back); '
        'road.md row learn (no flows): approve the write-back; messages desk.hint.approve-promote.kb, board.action.approve-promote.'),

 # ---- Keep it true ------------------------------------------------------------------------------------------
 dict(group='Keep it true', steps=[
   dict(pic=(B + 'kb-health.png', (36, 480, 2364, 696)),
        text='Code changed? **Health** lists stale cards. **Refresh cards** fills **New task**: press **Create and send**.'),
   dict(pic=(B + 'tour-reply.png', (40, 345, 1185, 480)),
        text='A task taught something? Under **Say something**, press **Capture what was learned**.'),
   dict(pic=(B + 'tour-reply.png', (30, 950, 1195, 1050)),
        text='That only fills the box. Press **Send** when the chat is idle; here it waits for an answer.'),
  ],
  notes='Sources: messages fetch.kb.stale (a fetched card that is older is history), dock.kb.health.stale/changed, dock.kb.refresh.cards; '
        'dock.js refresh() (generic-kb-refresh, kind kb, task refresh-<domain>); task.step.close (the agent may offer it at the end, never unasked); '
        'web/reply.js L170-186 (Send only when the chat is idle; Steer while busy; off while it waits for an answer); web/reply.js L60-69 (a chip puts the slash command in the box; the person presses Send); generic-capture-knowledge SKILL.md '
        '(writes KB-DRAFT.md only; putting it in is a kb task).'),

 dict(steps=[
   dict(pic=(B + 'new-task.png', (43, 119, 1058, 243)),
        text='It drafts `KB-DRAFT.md` only. To write it in: **New task**, Kind **knowledge base update**; point at the draft.'),
   dict(pic=(B + 'kb-changes-promote.png', (33, 22, 2198, 111)),
        text='That task has a requirement and a plan to approve, as on any task.'),
   dict(pic=(B + 'kb-changes-promote.png', (78, 733, 2142, 1232)),
        text='In **Changes**, read each card’s diff: is its source cited? Any secrets or customer data?'),
  ],
  notes='Sources: messages task.kind.kb = "knowledge base update"; core/tasks.py DEFAULT_TIER kb full (requirement and plan); docs/03-configure.md '
        '"Letting a task update the knowledge base" (task fetch kb/<path>, DEV/kb/; the edit tools cannot write it); knowledgebase.instructions.md "Writing it".'),

 dict(steps=[
   dict(pic=(B + 'kb-changes-promote.png', (78, 300, 2148, 577)),
        text='**Approve promote**: the harness makes one commit, straight on the base branch (`main` by default).'),
   dict(shot='Terminal in the knowledge-base folder: git log -1 showing the harness’s commit, then git push typed', aspect=16/6,
        text='It does not push: push it yourself. Another branch or uncommitted files stop it.'),
  ],
  notes='Sources: messages task.kind.kb = "knowledge base update"; core/tasks.py DEFAULT_TIER kb full (requirement and plan); docs/03-configure.md '
        '"Letting a task update the knowledge base" (task fetch kb/<path>, DEV/kb/; the edit tools cannot write it; straight into base_ref, one commit); '
        'messages desk.hint.approve-promote.kb, promote.done.kb ("The harness does not push"), promote.done.kb.local, promote.kb.branch, promote.kb.dirty, '
        'promote.kb.git_config; knowledgebase.instructions.md "Writing it" (no secrets, personal data, production rows).'),

 # ---- In your tasks -----------------------------------------------------------------------------------------
 dict(group='In your tasks', steps=[
   dict(pic=(B + 'new-task.png', (43, 513, 1058, 670)),
        text='In **New task**, tick the domains under **Knowledge base**, or **None**. Here none exist yet.'),
   dict(shot='VS Code: the Copilot chat of a demo task, showing the agent reading knowledge-base/README.md and the domain’s architecture.md', aspect=16/10,
        text='It reads `README.md` and the domain’s `architecture.md`; an index line, a card, the code only if needed.'),
  ],
  notes='Sources: messages board.new.kb = "Knowledge base", board.new.kb.none = "None", board.new.kb.hint, board.new.kb.empty; web/chat.js L284-319; '
        '.github/instructions/knowledgebase.instructions.md "Reading, for a task" 1-6 (a LOG.md line per step deeper; a wrong card noted and raised at the next stop); '
        'docs/08-knowledge-base.md (README.md is the entry); fetch.kb.cards.'),

 dict(steps=[
   dict(shot='Terminal: the output of harness kb reads --task <a demo task> listing knowledge base files and their reads', aspect=16/7,
        text='The task page does not list what it read. In your terminal: `harness kb reads --task <name>`.'),
   dict(shot='VS Code: report.md of a closed demo task open at the section “Knowledge base files read”', aspect=16/7,
        text='Once the task is closed, `.workspace/reports/tasks/<task>/report.md` lists them, if it read any.'),
   dict(pic=(B + 'kb-domains.png', (36, 204, 2364, 345)),
        text='**Last read by a task** gives only a date per domain, not which files.'),
  ],
  notes='Sources: core/kbreads.py (paths of read and search tools and of terminal commands; a search over a folder counts the folder; kb.reads.note); '
        'modules/observe/commands.py kb reads (--task, --days); task_report.py L1-5 and L96-104 (written when the task is closed or on `task report`; '
        'the section only if read); kbreads.last_by_domain and dock.js readText() (today, n days ago, never). No tab of desk.js shows the kb field of the call log.'),
]

CLOSING = dict(title='The knowledge base, in short',
  text=[
   ('list', ['The agent reads the knowledge base before the code; the code stays the truth.',
             'None yet? Bring in a folder with `README.md` and an empty `domains/` (Change the setup), then build it once, step by step.',
             'It changes only through a knowledge base task: you approve the plan and the write-back, one commit on its base branch. Push it yourself.']),
  ])
