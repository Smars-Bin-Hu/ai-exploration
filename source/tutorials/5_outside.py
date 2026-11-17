# Harness tutorials · 5 Outside systems and connections: how the gate judges a call to a listed system, how you approve a held call,
# and what opening a connection for a task means. One small step per picture.
# Build: .venv/bin/python source/tutorials/build.py 5_outside
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/, read only); sources in each page's notes.
# Board pictures: source/tutorials/img/_board/ (1.7.45, made-up data: the demo ticket board `demo`, task answer-ticket-t7).
# Placeholders (terminal output, board states not captured) are listed in shots/5_outside.md.
# Kept from the fact-check (review/4_outside-r1.md) and the newcomer test (test/4_outside-*): type rules change the defaults; an opened dev
# connection passes a drop its type allows; the gate is a net, not a sandbox; tickets linked on the board while open are opened too;
# Tell the agent to run it only if offered; close anything you did not open.

B = 'source/tutorials/img/_board/'

COVER = dict(
 sub='What happens when the agent calls a system your company listed (a database, a ticket board, a pipeline, a server): '
     'which calls run, which wait for you, how you approve one, and what opening a connection for a task means.',
 how=['Read **1 A day with the harness** and **3 When the agent is stopped** first.'],
)

CONTENTS = True

PAGES = [
 # ---- What it can reach ----------------------------------------------------------------------------------------------------
 dict(group='What it can reach', steps=[
   dict(pic=(B + 'outside-tools-packs.png', (45, 382, 1600, 530)),
        text='A **tool pack** brings the program for one kind of system, the gate’s rules for it, and skills.'),
   dict(pic=(B + 'outside-tools-connections.png', (45, 205, 1600, 295)),
        text='A **connection** is one place, with its environment (dev, ist, qat, prod or none) and your sign-in.'),
   dict(pic=(B + 'outside-enter-not-ready.png', (60, 1470, 900, 1580)),
        text='The Enter screen lists both under **From the company**. You signed in during Install.'),
   dict(pic=(B + 'outside-enter-not-ready.png', (60, 1015, 900, 1222)),
        text='**VS Code** red, **no settings**? Press **Restart VS Code**: the agent needs the pack’s program.'),
  ],
  notes='Sources: messages tools.packs.title/lead ("A pack brings a program, the rules the gate judges it by, and skills"), tools.conn.title/lead, '
        'connections.signin, connections.test; core/systems.py ENVS (dev, ist, qat, prod, none); docs/01-quickstart.md (Enter screen: From the company, '
        'Restart VS Code when VS Code runs without this copy\'s tool folders); the red box text is the board\'s own. Install deck, Get ready card 3.'),

 dict(steps=[
   dict(shot='Your own terminal in the demo workspace after `harness connections find demo`: the lines it prints for the demo connection', aspect=16/7,
        text='The agent picks one with `harness connections find`. More than one fits? It asks you.'),
  ],
  notes='Sources: docs/04-reference.md connections find (a read the agent runs; says to ask when more than one fits); '
        'docs/12-guardrails-and-gate.md "The agent is told a little at a time" (never guesses); messages connections.find.many.'),

 # ---- How a call is judged ------------------------------------------------------------------------------------------------
 dict(group='How a call is judged', steps=[
   dict(pic=(B + 'outside-held-card.png', (100, 320, 2145, 480)),
        text='The **gate** checks each call first. A **read** runs. A **write** waits for you.'),
   dict(pic=(B + 'run.png', (73, 298, 2145, 485)),
        text='A **job** (a pipeline, a load) is yours: the task **waits for your run**.'),
   dict(pic=(B + 'stop-agent-actions.png', (88, 832, 2130, 965)),
        text='A **destroy** is refused. On **prod**, only a read runs.'),
  ],
  notes='Sources: core/systems.py DEFAULT_RULES {read: allow, write: outbox, exec: human, destroy: deny} and PROD_RULES (prod: read only), '
        '"when the company wrote no rule"; modules/gate/external.py decide() (prod takes only a rule written for prod by name); messages task.waiting.outbox, '
        'task.waiting.run, gate.external.human ("a person does it"; task handoff run), gate.external.denied ("the kind destroy is not allowed there").'),

 dict(steps=[
   dict(pic=(B + 'outside-tools-packs.png', (45, 545, 1600, 692)),
        text='Defaults only: a type or your company changes them. Sample **sqlserver** holds a dev job or destroy for you.'),
   dict(pic=(B + 'plan.png', (72, 290, 1730, 515)),
        text='A call your company marks **task** is refused until you approve the plan; then it runs.'),
   dict(pic=(B + 'stop-agent-actions.png', (86, 576, 2128, 716)),
        text='What the gate cannot judge does not run. It reads no scripts: your account’s rights are the limit.'),
  ],
  notes='Sources: toolpacks/sqlserver/types/sqlserver.json rules (dev, ist: exec and destroy outbox; qat: destroy deny) and open (dev, ist all); '
        'core/connections.py (a connection\'s rules win, else its type\'s); policies/tools.json rules values allow|task|outbox|human|deny; '
        'handler.py _judge_one L266-270 (task passes once tasks.plan_approved), messages gate.external.task; docs/12-guardrails-and-gate.md '
        '"What the gate cannot judge, it does not pass" (no server or an unknown one: refused; a hidden command: refused; a faulty pack file: held), '
        '"A guardrail, not a sandbox", "What is still not covered" (python3 query.py not read; the rights of the account); docs/03-configure.md:300.'),

 # ---- Approve a held call -------------------------------------------------------------------------------------------------
 dict(group='Approve a held call', steps=[
   dict(pic=(B + 'outside-held-card.png', (100, 320, 2120, 615)),
        text='Read the card at the top of the task page: **what**, **system**, and what will be written.'),
   dict(pic=(B + 'outside-held-card.png', (100, 732, 1000, 808)),
        text='Press **View**.'),
   dict(pic=(B + 'outside-held-view.png', (40, 110, 1780, 340)),
        text='Read the command. Click **the code**: it fills the card’s box.'),
   dict(pic=(B + 'outside-held-card.png', (540, 732, 1700, 808)),
        text='Press **Approve**, or **Do not approve** and pick why.'),
  ],
  notes='Sources: messages task.waiting.outbox, desk.outbox.what, desk.outbox.system, desk.outbox.zone ("Why held", on cards of typed systems), desk.outbox.view, '
        'desk.outbox.window, desk.outbox.code_tip, board.serve.code, desk.outbox.approve, desk.outbox.dismiss, desk.outbox.reason.*; handler.py L395-411.'),

 dict(steps=[
   dict(shot='The card of the held call answer-ticket-t7 right after Approve: the green Approved card with its code', aspect=16/6,
        text='If the card offers **Tell the agent to run it**, press it. Usually the agent was waiting and goes on.'),
   dict(pic=(B + 'outside-held-view.png', (40, 240, 1780, 330)),
        text='It runs once, exactly as written, within 10 minutes. A changed command needs a new approval.'),
  ],
  notes='Sources: messages desk.outbox.tell, desk.outbox.tell.hint, desk.outbox.told.wait, desk.outbox.asked; modules/task/web/desk.js L1172, L1186-1187 '
        '(no button when the agent\'s wait returned: it goes on by itself); core/approvals.py DEFAULT_MINUTES = 10.'),

 # ---- Open a connection ---------------------------------------------------------------------------------------------------
 dict(group='Open a connection', steps=[
   dict(pic=(B + 'outside-held-card.png', (540, 732, 1700, 808)),
        text='A card may offer **Open <connection> for this task**. It needs the code, like **Approve**.'),
   dict(shot='The same card after its Open button was pressed with the code: Opened, and Tell the agent to run it again if shown', aspect=16/6,
        text='The card says **Opened**. If it offers **Tell the agent to run it again**, press it.'),
   dict(shot='Your own terminal after `harness task allow --conn demo --on --task answer-ticket-t7` and then `--off`: both answers', aspect=16/7,
        text='Or in your own terminal: `harness task allow --conn <connection> --on`; `--off` closes it.'),
   dict(pic=(B + 'outside-tools-connections.png', (45, 205, 1600, 295)),
        text='Open only a place you could repair, like a dev database. Prod is never opened.'),
  ],
  notes='Sources: messages desk.outbox.open = "Open {name} for this task", desk.outbox.open.tip.all ("It needs the code, like Approve"), desk.outbox.opened, '
        'desk.outbox.opened.tell; core/outbox.py offer_for; task/commands.py "allow" (--conn, --on/--off, person only, terminal); tasklife.set_allow; '
        'handler.py _judge_one L288-292 (an offer only on a held write); messages task.allow.no.'),

 dict(steps=[
   dict(pic=(B + 'outside-open-to-agent.png', (20, 30, 600, 205)),
        text='Once open, its writes and runs in this task pass with no approval. Nobody checks them.'),
   dict(pic=(B + 'outside-tools-packs.png', (45, 545, 1600, 692)),
        text='Even a destroy its type allows: with the sample **sqlserver** type, a table drop on dev.'),
   dict(pic=(B + 'stop-agent-actions.png', (44, 270, 2172, 440)),
        text='They are only logged, in **Records** › **Agent actions**. A statement on no list still waits.'),
  ],
  notes='Sources: messages task.allow.conn.on ("A destroy passes only where the tool pack\'s type lets it (the SQL Server sample: a table drop on DEV and IST)"), '
        'desk.set.open.tip.conn, desk.set.open.never; handler.py _judge_one L279-286 (opened: task, outbox, human pass; listed_write destroy passes; '
        '"unjudged" zones wait), messages gate.external.zone_ask; sqlserver.json open dev/ist all; systems.open_scope (prod never); '
        'docs/12-guardrails-and-gate.md "What is still not covered" (WHERE id > 0 passes on an open connection; the account\'s rights are the limit); '
        'desk.tab.trace = "Agent actions", desk.group.records = "Records".'),

 # ---- Close it ------------------------------------------------------------------------------------------------------------
 dict(group='Close it', steps=[
   dict(pic=(B + 'outside-task-head.png', (1300, 118, 2190, 188)),
        text='At the head of the task page, **Open to the agent** names what is open.'),
   dict(pic=(B + 'outside-open-to-agent.png', (20, 380, 600, 610)),
        text='Click it, then **Close** beside it. It also closes when the task closes.'),
   dict(pic=(B + 'outside-open-to-agent.png', (20, 380, 600, 670)),
        text='Anything listed there that you did not open: close it.'),
  ],
  notes='Sources: modules/task/web/desk.js envButton L752-800 ("Open to the agent", list "Open in this task", Close = task allow --conn <name> --off, no code); '
        'messages desk.set.open, desk.set.open.off ("none"), desk.set.open.list, desk.set.open.conn.close, desk.set.open.cannot (paired browser, open task), '
        'task.allow.conn.off; set_allow docstring ("the switch ends with the task"). The last line: policies/gate.json L136 lists `task allow --env` among '
        'person-only commands but not `--conn`; only core/approval.py require_person (a terminal with a keyboard and a screen) stands in front of it.'),

 # ---- Ticket boards -------------------------------------------------------------------------------------------------------
 dict(group='Ticket boards', steps=[
   dict(pic=(B + 'outside-held-card.png', (925, 738, 1460, 806)),
        text='A ticket board opens less: **Open linked items of <connection> for this task**.'),
   dict(pic=(B + 'outside-open-to-agent.png', (20, 380, 600, 600)),
        text='Then writes to the tickets linked to the task pass. A write to an unlinked ticket is refused.'),
   dict(pic=(B + 'outside-link.png', (36, 172, 940, 256)),
        text='A ticket you add with **Link a ticket** while they are open is opened too.'),
   dict(pic=(B + 'outside-task-head.png', (36, 180, 560, 248)),
        text='A ticket the agent links itself, or a new one, still waits for you.'),
  ],
  notes='Sources: toolpacks/ado/types "open": "items"; handler.py _item_scope (unlinked refused, opened passes) and _judge_one L273-277; '
        'messages desk.outbox.open.items, desk.outbox.open.tip.items, gate.external.unlinked, desk.links.add = "Link a ticket"; '
        'tasklife.link by_person (a ticket the person links on the board while open is opened too; boardserve.py:791); tasklife._set_allow_links. '
        'The pop-up\'s own tip says "a ticket linked ... later still waits": the code wins (review/4_outside-r1.md finding 1).'),
]

CLOSING = dict(title='Outside systems, in short',
  text=[
   ('list', ['By default a read runs, a write waits for you, a job is yours, a destroy is refused, prod is read only; tool packs and your company change this.',
             'Approve a held call on its card: **View**, the code, **Approve**.',
             'Open a connection only where you could repair the damage, and close it when you are done.']),
  ])
