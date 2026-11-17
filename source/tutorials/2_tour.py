# Harness tutorials · 2 A tour of the harness: every screen of the board, one picture and one line each, so a colleague knows what is there.
# Build: .venv/bin/python source/tutorials/build.py 2_tour
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/): web/*.js, core/messages.en.json; sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data), cropped to the part each step is about. No placeholders: every screen is a board screen.
# A tour, not a how-to: where a screen belongs to another tutorial, one line and "tutorial n".

B = 'source/tutorials/img/_board/'

COVER = dict(
 sub='Every screen of the harness board, one picture each, and what you can do there.',
 how=['Read it after tutorial 1. Nothing here needs to be pressed: it is a map of the buttons.'],
)

CONTENTS = True

PAGES = [
 # ---- Enter -------------------------------------------------------------------------------------------------
 dict(group='Enter', steps=[
   dict(pic=(B + 'tour-enter-open.png', (40, 1000, 910, 1268)),
        text='**Harness & Local**: this copy, the browser, `harness doctor`, VS Code, Copilot. All must be green.'),
   dict(pic=(B + 'tour-enter-open.png', (40, 1280, 910, 1585)),
        text='**From the company**: knowledge base, skills, standards, tool packs, connections, repositories. Optional.'),
   dict(pic=(B + 'tour-enter-open.png', (930, 1505, 1810, 1650)),
        text='**Restart VS Code** starts it with this copy’s settings. **Enter** opens the board.'),
  ],
  notes='Sources: messages.en.json board.enter.t.* (This copy is set up, Browser paired, harness doctor, VS Code, Copilot; Knowledge base ... Code repositories), '
        'board.enter.g.required / optional; ready.vs.restart; board.vs.running.why (tool folders, CA bundle are given only to a VS Code the board starts).'),

 # ---- The board ---------------------------------------------------------------------------------------------
 dict(group='The board', steps=[
   dict(pic=(B + 'tour-lobby.png', (1235, 30, 2180, 120)),
        text='Top right: **Off work**, **Back to work**, **Lobby** or **List**, and **New task**.'),
   dict(pic=(B + 'tour-lobby.png', (85, 350, 830, 680)),
        text='**Lobby**: a robot per task. **Waiting for you** comes first. What it holds shows the kind.'),
   dict(pic=(B + 'tour-lobby.png', (85, 960, 520, 1640)),
        text='Then **At work**, **Left alone**, **Resting** (quiet or paused).'),
   dict(pic=(B + 'tour-lobby.png', (85, 1715, 560, 2075)),
        text='Closed tasks rest on the dock. Click a robot to open its task.'),
  ],
  notes='Sources: lobby.js L1-5, L20-32 (zones: Waiting for you, At work, Left alone when no session holds it, Resting = quiet or paused; the thing in the hand is the kind; '
        'hover opens a card, a click opens the page); messages.en.json board.lobby.zone.*, board.offwork.hint, board.onwork.hint (a task paused by hand stays paused).'),

 dict(steps=[
   dict(pic=(B + 'tour-lobby-left-alone.png', (88, 375, 780, 700)),
        text='**Left alone**: no session holds the task; its robot’s plug hangs loose. Open a chat and name the task.'),
   dict(pic=(B + 'tour-readybar-red.png', (30, 176, 2190, 452)),
        text='Red, **The agent cannot work right now**: a required line broke after Enter. Its button fixes it.'),
   dict(pic=(B + 'tour-readybar-yellow.png', (30, 168, 2190, 447)),
        text='Yellow, **Not fully ready for your company’s tasks**: each problem with its button. **Hide** puts it away.'),
  ],
  notes='Sources: lobby.js L20-23 (lost -> Left alone); messages.en.json board.lobby.zone.left, desk.actions.unheld.hint; readybar.js L1-5 (red cannot be hidden, yellow has Hide); '
        'board.ready.red.title, board.ready.yellow.title, board.ready.hide.'),

 dict(steps=[
   dict(pic=(B + 'tour-lobby.png', (30, 20, 790, 125)),
        text='Beside **Task board**: **VS Code linked**, browser **Paired**, **Company Context** (a knowledge base is in).'),
   dict(pic=(B + 'tour-list.png', (22, 148, 2350, 335)),
        text='**List**: open tasks, waiting for you, the longest wait, agent time, **Credits**.'),
   dict(pic=(B + 'tour-list.png', (22, 355, 2290, 428)),
        text='Filters: **Quiet** means no sign of the agent for minutes; **No session**, no chat holds it.'),
   dict(pic=(B + 'tour-list.png', (22, 455, 2350, 810)),
        text='A row per task: its state, checks, time waited, and in **Do** your next button.'),
  ],
  notes='Sources: board.js L445-461 (VS Code pill, pair mark, kb mark: Company Context, hover lists what the knowledge base has); '
        'messages.en.json board.kpi.*, board.filter.*, desk.actions.quiet(.hint), desk.actions.unheld(.hint), board.col.*.'),

 dict(steps=[
   dict(pic=(B + 'tour-list-search.png', (24, 355, 2356, 690)),
        text='**All kinds** shows one kind. **Search tasks** keeps tasks whose name or kind has the word.'),
   dict(pic=(B + 'tour-list-closed.png', (24, 355, 2356, 662)),
        text='**Closed**: **Archive** moves a task out of the repository, with no restore. Tick several at once.'),
   dict(pic=(B + 'tour-off-work.png', (30, 150, 2190, 410)),
        text='**Off work** pauses idle tasks for the night. **Back to work** takes them back.'),
  ],
  notes='Sources: board.js L41, L54-56 (search: name + kind text); messages.en.json task.kind.*, board.filter.kind, board.search, board.select.*, board.archive.* (One way: there is no restore), board.offwork(.hint), board.onwork(.hint).'),

 dict(steps=[
   dict(pic=(B + 'new-task.png', (38, 115, 1058, 485)),
        text='**New task**: **Name**, **Kind**, and **Fork from a task** to start from an old one.'),
   dict(pic=(B + 'new-task.png', (38, 510, 1058, 910)),
        text='**Knowledge base** names a domain (tutorial 6). **Link tickets** names tickets (tutorial 5).'),
   dict(pic=B + 'tour-new-task-fields.png',
        text='**What to do**: the task in your own words. Model, **Context window**, **Ask me first**, then **Create and send**.'),
  ],
  notes='Sources: chat.js L271-301 (form order); messages.en.json board.new.text(.ph), board.new.context, board.new.* (Name, Kind, Fork from a task, board.new.source.hint: copies the old task’s conclusions and materials into REF/), '
        'board.new.first, board.new.go; chatnew.py first_message.'),

 # ---- A task page -------------------------------------------------------------------------------------------
 dict(group='A task page', steps=[
   dict(pic=(B + 'tour-task-head.png', (30, 18, 2190, 100)),
        text='The head: back, name, state, the stages, the checks passed; VS Code and **…** at the right.'),
   dict(pic=(B + 'tour-task-head.png', (1320, 120, 2190, 186)),
        text='**Independent review** sets how many checks (tutorial 4). **VS Code linked**, **Paired**: the links.'),
   dict(pic=(B + 'tour-task-head.png', (30, 118, 315, 246)),
        text='The icon shows the kind. **+ Link a ticket** names a ticket of an outside tool (tutorial 5).'),
   dict(pic=(B + 'tour-tab-overview.png', (72, 295, 2148, 538)),
        text='When the task waits for you, a card says why and gives the button.'),
  ],
  notes='Sources: messages.en.json desk.rv.button, desk.rv.hint, board.vscode.ready, board.vscode.nochat, board.vs.open, board.vs.nochat (brings the VS Code window forward), '
        'board.serve.mark.paired, desk.links.add(.tip); task.waiting.plan, desk.hint.approve-plan.'),

 dict(steps=[
   dict(pic=B + 'tour-task-more.png',
        text='**…**: **Time and usage**, **Save as HTML**, **Autorun on**, **Pause**, **Close** (it can be opened again).'),
   dict(pic=(B + 'tour-reply.png', (30, 40, 1200, 560)),
        text='**Say something** (key **R**) writes to the task’s chat. A skill button puts its command in the box.'),
  ],
  notes='Sources: messages.en.json desk.report, desk.save(.hint), desk.hint.close; reply.js L1-10 (pill “Say something”, key R), L60 (a skill click puts the slash command in the box; nothing goes by itself).'),

 dict(steps=[
   dict(pic=(B + 'tour-reply.png', (30, 570, 1200, 1050)),
        text='Model, thinking, context, permissions: the settings of this task’s chat. **Save draft** or **Send**.'),
   dict(shot='A task page while the agent works: Stop beside Say something; the panel open with Steer and Queue', aspect=16/10,
        text='While it works: **Stop** halts it. **Send** becomes **Steer** (now) or **Queue** (after). **Withdraw**, **Try again**.'),
  ],
  notes='Sources: messages.en.json desk.report, desk.save(.hint), board.close.*, desk.reply.*; reply.js L1-10 (pill “Say something”, key R; the task settings and drafts), '
        'L60 (a skill click puts the slash command in the box; nothing goes by itself); reply.js L28-33, messages desk.reply.stop.tip, board.action.stop, desk.reply.steer, desk.reply.queue, desk.reply.back, desk.reply.retry. Autorun is not in this first batch of tutorials.'),

 # ---- Task tabs ---------------------------------------------------------------------------------------------
 dict(group='Task tabs', steps=[
   dict(pic=(B + 'tour-tab-overview.png', (40, 562, 2180, 735)),
        text='Tab groups: **Live**, **Overview**, **Results**, **Records**, **Files**. A group of one, like **Changes**, shows its tab.'),
   dict(pic=(B + 'live-waiting.png', (222, 399, 1983, 1064)),
        text='**Live**: what the agent does now in its chat.'),
   dict(pic=(B + 'tour-tab-overview.png', (40, 765, 1070, 1290)),
        text='**Overview**: `TASK.md`, where the task stands and the next step.'),
   dict(pic=(B + 'plan.png', (66, 764, 1150, 1290)),
        text='**Requirement**, **Intake**, **Plan**, **TODO**: what is asked, your papers, the plan, the steps.'),
  ],
  notes='Sources: desk.js L15-22 (groups live / overview: overview, req, intake, plan, todo / deliver: changes, test, rca, design, evidence, review / records: log, history, trace / files: docs, files; '
        'a group with one tab goes straight to it), L70-87 (when each tab is there); messages.en.json desk.tab.*, desk.group.*.'),

 dict(steps=[
   dict(pic=(B + 'changes-promote.png', (66, 720, 2144, 1518)),
        text='**Changes** (development, knowledge base): the diff that would go into the repository.'),
   dict(pic=(B + 'review.png', (74, 716, 1150, 960)),
        text='**Review**: each independent check and its verdict (tutorial 4).'),
   dict(pic=(B + 'tour-tab-test.png', (40, 620, 1735, 1645)),
        text='**Test** (testing tasks): the guide for each environment, then the results.'),
   dict(pic=(B + 'tour-tab-evidence.png', (40, 735, 2140, 975)),
        text='**Evidence**: every run saved in the task, numbered **E1**, **E2**, to be cited.'),
  ],
  notes='Sources: desk.js L77-80 (Changes only on dev and kb tasks; Test when the task has a test; Evidence when runs are saved; Review when checks were asked); '
        'messages.en.json desk.tab.changes, desk.tab.review, desk.tab.test, desk.tab.evidence.'),

 dict(steps=[
   dict(pic=(B + 'tour-tab-design.png', (40, 620, 1760, 1340)),
        text='**Design** (design tasks): `DESIGN.md`. Read it here; tell the agent what to change.'),
   dict(pic=(B + 'tour-tab-rca.png', (72, 298, 1700, 1250)),
        text='**RCA** (RCA tasks): `RCA.md`. Any kind can end **to accept**: **Accept and close** or **Not yet**.'),
   dict(pic=(B + 'tour-run-block.png', (60, 30, 1760, 330)),
        text='A shell block: **Ask agent** sends it to the chat, and the gate holds. **▶ Run** runs it yourself.'),
   dict(pic=B + 'tour-run-dialog.png',
        text='The gate does not check **▶ Run**: the board runs it as you. Read the whole command, then **Run now**.'),
  ],
  notes='Sources: desk.js L76 (Design and RCA when the file is there, or the kind is open); messages.en.json desk.tab.design, desk.tab.rca, desk.accept.*, task.waiting.accept; accept.py L25 (DELIVER_KINDS: any kind; a Q&A closes itself, a promote is the acceptance); '
        'run.js L1-3, L11-15 (Ask agent: the gate holds; Run: the board starts it, the gate does not see it); taskrun.py L44-46 (bash; powershell, batch on Windows); messages desk.run, desk.run.hint, desk.run.ask(.hint), desk.run.warn, desk.run.go.'),

 dict(steps=[
   dict(pic=(B + 'tour-tab-log.png', (40, 208, 2180, 712)),
        text='**Records › Log**: the agent’s decisions and findings, newest first.'),
   dict(pic=(B + 'tour-tab-history.png', (40, 208, 2180, 1112)),
        text='**Task Record**: what happened to the task, with times: approvals, write-back, close.'),
   dict(pic=(B + 'stop-agent-actions.png', (85, 570, 2140, 1490)),
        text='**Agent actions**: every tool call. A refused one shows the call and the gate’s reason; ▶ opens it all.'),
   dict(pic=(B + 'tour-files-edit.png', (68, 690, 2147, 1150)),
        text='**Files**: edit a text file, add, rename, delete. Not while the agent works. A saved `PLAN.md` needs approval again.'),
  ],
  notes='Sources: messages.en.json desk.tab.log, desk.tab.history, desk.tab.trace (stop-agent-actions: Blocked and failed, each row the call, blocked, and the gate’s reason), desk.tab.files and the lines under each tab (as in the pictures); desk.js L21 (Files group: Other documents, Files); desk.files.hint.edit (a text file can be edited), desk.files.busy (not while the agent is in a turn), desk.files.plan.note (saving PLAN.md: an approved plan must be approved again).'),

 # ---- Reports -----------------------------------------------------------------------------------------------
 dict(group='Reports', steps=[
   dict(pic=(B + 'tour-report.png', (36, 55, 2044, 628)),
        text='One task: **…** › **Time and usage**: time, prompts, **Credits**, premium requests, gate blocks. **Ask why** opens a chat.'),
   dict(pic=(B + 'tour-list.png', (22, 148, 2350, 335)),
        text='All tasks: the **List** strip totals every task listed, open and closed, whatever the filter. No view by week.'),
   dict(pic=(B + 'tour-report.png', (42, 950, 2040, 1310)),
        text='**Open** shows the review page. **Agent Performance Review** opens a new review task, which is costly.'),
   dict(pic=(B + 'tour-performance.png', (20, 40, 2140, 1160)),
        text='The review page: each prompt’s Credits or time. **Credits** are Copilot’s own usage count, not money.'),
  ],
  notes='Sources: messages.en.json desk.report, report.back, report.save, report.why(.hint: opens a chat), report.perf.start(.hint: opens an rca task with harness-agent-performance-review), '
        'report.perf.open(.hint), dock.costly.hint; report.footer.note (Credits and premium requests are the usage Copilot records, added up as they are, not turned into money); copilot_events.py L153-157 (Credits = copilotUsage.totalNanoAiu, AI credits; premium requests are a separate count); board.js L328-337 (the strip sums `rows`, every task on the board, not the filter), taskboard.py L187, L240-250 (the board lists open tasks and the newest 50 closed ones; archived tasks are gone); board.js filters: state, kind, search (no date); the In short line of the page (no review yet: accounts made from the record, at no cost).'),

 # ---- Round buttons -----------------------------------------------------------------------------------------
 dict(group='Round buttons', steps=[
   dict(pic='source/tutorials/img/2_tour/tour-dock-wide.png',
        text='Bottom right: house (**Back to the Enter screen**), gear (setup), book (knowledge base), **?** (help), sliders (settings).'),
   dict(pic=(B + 'tour-enter.png', (2120, 15, 2545, 180)),
        text='Top right: **Search** (⌘K or Ctrl+K) and **>_**, the terminal.'),
   dict(pic=B + 'tour-search.png',
        text='Search: type to go to a task, a view, a filter, a tab or a setting.'),
  ],
  notes='Sources: dock.js L506-540 (help panel, book, gear = Change the setup, house = Back to the Enter screen, hidden on Enter: dock.css L3); dock.js L466-478 (badge: stale cards); '
        'shell.js L301 (Cmd or Ctrl + K); dock.js L536-538, dock.css L3, L9 (the house, Back to the Enter screen, above the gear, hidden on Enter); messages.en.json board.shell.search.ph, board.shell.*, board.shell.restart.hint. On the board and task pages a house also takes you back to Enter.'),

 dict(steps=[
   dict(pic=B + 'tour-help.png',
        text='**?**: ask how the harness works, or **How the harness works**, or **First lesson**. Each opens a chat.'),
   dict(pic=(B + 'tour-everything.png', (0, 0, 1524, 700)),
        text='**Everything you can ask for**: every skill. **Start** shows the message first; **Open** is a web page.'),
   dict(pic=B + 'tour-settings.png',
        text='Sliders, **Settings**: theme, Glass or Lite, a background, the language, **Restart board**.'),
   dict(pic=B + 'tour-terminal.png',
        text='**>_**: a terminal for `harness` commands only, such as `harness doctor`. No agent.'),
  ],
  notes='Sources: dock.js L506-523 (Ask and How the harness works start harness-rookie-wondering, First lesson harness-rookie-quick-start), L20-48 (start shows the whole message and a model, then Send), '
        'L51-100 (Everything you can ask for: Start through the message dialog, a skill that opens a task through New task, Open for a link, a tag In a task for reply-panel skills, costly tag); messages.en.json term.refused.other (harness commands only), term.ph.'),

 # ---- Setup -------------------------------------------------------------------------------------------------
 dict(steps=[
   dict(pic=(B + 'tour-setup-window.png', (40, 385, 1644, 1080)),
        text='Gear, **Change the setup**: card **3 From the company**; above it, **2 You** (name, language).'),
   dict(pic=(B + 'tour-setup-repos.png', (60, 15, 1570, 440)),
        text='**Code repositories**: type a folder, **Add**, **Save**. The agent may change only these, only through the write-back.'),
   dict(pic=B + 'tour-setup-local.png',
        text='**4 Local**: programs, network, MCP; **Open** for the details. Then **Save**.'),
   dict(pic=(B + 'outside-tools-packs.png', (0, 0, 1644, 545)),
        text='**Tool packs** and **Connections** › **Open**: outside systems, where the agent may reach, sign-ins (tutorial 5).'),
  ],
  notes='Sources: setup.js L401-408 (card 1 The short command), L654, L660-662 (cards 2 You, 3 From the company with the Code repositories row last, 4 Local); setup.repos, setup.repos.hint, setup.refused.add (Add), setup.browse; docs/03-configure.md L3, L105 (code repositories are the target repositories); gate refusal "A target repository is never changed directly: only promote writes to it" (stop-agent-actions); messages.en.json dock.setup, setup.*, machine.* (Local: programs, network, MCP); '
        'the lines under Tool packs and Connections & sign-ins (as in the pictures).'),

 # ---- Knowledge base ----------------------------------------------------------------------------------------
 dict(group='Knowledge base', steps=[
   dict(pic=(B + 'kb-overview.png', (36, 105, 1400, 925)),
        text='Book, **Knowledge base**: the eight steps, what is next, each domain. Its number: stale cards.'),
   dict(pic=(B + 'kb-map.png', (36, 105, 1200, 960)),
        text='**Map**: which domain uses which. **Company**: what the agent gets. **Domains**: each domain.'),
   dict(pic=(B + 'kb-lookup.png', (36, 105, 1300, 700)),
        text='**Look up**: one object, what uses it, and what it uses.'),
   dict(pic=(B + 'kb-health.png', (36, 105, 1150, 770)),
        text='**Health**: the audit, the cards, stale cards, gaps. A button with a speech bubble opens a chat.'),
  ],
  notes='Sources: dock.js L105-110 (the window is read only; a chat button opens a chat); messages.en.json dock.kb.* (Overview, Map, Company, Domains, Look up, Health; the eight steps dock.kb.step.*), '
        'dock.atlas.*; the line on the Overview tab (opens a chat in VS Code and uses Copilot; everything else costs nothing).'),
]

CLOSING = dict(title='That is the whole board',
  text=[
   'A chat button shows you the message first: nothing goes until **Send** or **Create and send**.',
   'The exception: **▶ Run** on a shell block runs after **Run now**, as you, and the gate does not check it.',
   'When something stops the agent: **3 When the agent is stopped**. 4, 5 and 6 only when you need them.',
  ])
