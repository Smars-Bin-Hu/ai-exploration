# Harness tutorials · 5 Outside systems and connections: how the gate judges a call to a database, a ticket board,
# a pipeline or a server, how you approve a held call, and what opening a connection for a task means.
# Build: .venv/bin/python source/tutorials/build.py 5_outside
# Checked against harness 1.7.45 (.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/, read only); sources in each page's notes.
# Names in examples (orders-dev, orders-prod, tracker) are made up.

H = '.claude/loops/2026-11-17-ai-exploration-map/ref/harness-1.7.45/'
A = H + 'docs/images/'

COVER = dict(
    sub='What happens when the agent calls a system your company listed: a database, a ticket board, a pipeline, a server. '
        'Which calls run, which wait for you, how you approve one, and what it means to open a connection for a task.',
    how=['Read **A day with the harness** and **When the agent is stopped** first.'],
)

PAGES = [
 dict(kicker='Step 1 · What the agent can reach', title='Your company lists the systems',
  text=[
   'A **tool pack** brings the program for one kind of system, the rules the gate judges it by, and skills. '
   'A **connection** is one place, such as `orders-dev`, with its environment: dev, ist, qat or prod.',
   'You signed in to them in Install. The agent looks one up with `harness connections find` and asks you when more than one fits.',
  ],
  pic=A + 'tools.png',
  caption='The Tool packs window, opened from Change the setup.',
  notes='Sources: messages tools.packs.title/lead, tools.conn.title, dock.setup = "Change the setup"; docs/13-tool-packs-and-mcp.md; '
        'docs/12-guardrails-and-gate.md "The agent is told a little at a time" (find; asks when more than one fits, never guesses); '
        'core/systems.py ENVS; policies/connections.json description. Install deck, Get ready card 3.'),

 dict(kicker='Step 2 · How a call is judged', title='The gate judges a call by what it does',
  text=[
   'The **gate** (harness code that checks the agent’s commands first) judges a call by what it does. With no rule:',
   ('list', ['**read**: runs;',
             '**write**: waits for you;',
             '**run a job**: yours to run;',
             '**destroy**: refused;',
             'on **prod**: only a read runs.']),
   ('small', 'Tool packs and your company change these: the sample SQL Server type holds a dev job or destroy for you.'),
  ],
  notes='Sources: core/systems.py DEFAULT_RULES {read: allow, write: outbox, exec: human, destroy: deny} and PROD_RULES (prod: read only); '
        'modules/gate/external.py decide() (a company rule per env or "*"; prod takes only a rule written for prod by name); '
        'policies/tools.json description (rules: allow|task|outbox|human|deny); docs/12-guardrails-and-gate.md table "What the call does"; '
        'toolpacks/sqlserver/types/sqlserver.json rules (dev, ist: exec and destroy outbox; qat: destroy deny); core/connections.py (connection rules win, else the type\'s).'),

 dict(kicker='Step 3 · When the gate cannot tell', title='What the gate cannot judge does not pass',
  text=[
   'What the gate cannot judge does not run:',
   ('list', ['a database call with no server, or an unknown one: refused;',
             'a command hidden in a variable or encoded: refused;',
             'a broken rule file: its pack’s calls wait for you.']),
   'The gate is a net, not a sandbox: it does not read scripts the agent runs. Your account’s rights are the limit.',
  ],
  notes='Sources: docs/12-guardrails-and-gate.md "What the gate cannot judge, it does not pass"; modules/gate/handler.py _judge_one '
        '(zone unpinned/blocked refused; unseen held); messages gate.external.unpinned, gate.external.unseen, gate.external.encoded, '
        'gate.external.broken, gate.external.noconn. The server check is only for a type with `pin` (sqlserver); ado and demotracker have none. '
        'docs/12 "A guardrail, not a sandbox" and "What is still not covered" (python3 query.py is not read; the rights of the account); docs/03-configure.md:300. Left out for words: a call no verb pattern names is judged a write (policies/tools.json; desk.outbox.unnamed).'),

 dict(kicker='Step 4 · Calls that need a plan', title='Some calls wait for the approved plan',
  text=[
   'Your company can mark a kind of call on a system as **task**. Such a call is refused while there is no approved plan; the agent is told to get **PLAN.md** approved.',
   'Once you approve the plan of the task, these calls run, with no card for each.',
   ('small', 'Read the plan for them before you press Approve plan.'),
  ],
  notes='Sources: modules/gate/handler.py _judge_one lines 266-270 (decision task passes when tasks.plan_approved, or a test runner you allowed); '
        'messages gate.external.task ("allowed only in a task whose plan the user approved"); policies/tools.json rules values; '
        'board.action.approve-plan = "Approve plan".'),

 dict(kicker='Step 5 · A write is held', title='Read the card of the held call',
  text=[
   'On the board the task says **an outside call waits for your approval**. Its card is at the top of the task page.',
   'Before you decide, read:',
   ('list', ['**what**: write, or another kind;',
             '**system** and its environment;',
             'the statement that will run;',
             '**Why held**.']),
  ],
  pic=A + 'held-write.png',
  caption='A write to a made-up dev database, held on the task page.',
  notes='Sources: messages task.waiting.outbox, desk.outbox.what = "what", desk.outbox.system = "system", desk.outbox.zone = "Why held", '
        'desk.outbox.raw = "Raw command", desk.outbox.agent.wait; handler.py lines 395-411 (an outbox call gets a code and a card).'),

 dict(kicker='Step 6 · Approve it', title='Approve that one command',
  text=[
   ('steps', ['Press **View** and read the command.',
              'Click the code there: it fills the card’s box.',
              'Press **Approve**, or **Do not approve** and pick why.',
              'If the card offers **Tell the agent to run it**, press it; usually the agent was waiting and goes on.']),
   ('small', 'It runs once, exactly as written, within 10 minutes.'),
  ],
  pic='source/start-here/img/held-both.png',
  caption='A held write to a ticket, then approved (1.7.43; the same words in 1.7.45).',
  wide=True,
  notes='Sources: messages desk.outbox.view, desk.outbox.code_tip, desk.outbox.approve, desk.outbox.dismiss, desk.outbox.reason.*, '
        'desk.outbox.tell, desk.outbox.tell.hint, desk.outbox.told.wait (desk.js 1172-1187: no button when the agent\'s wait returned), desk.outbox.same_as, desk.outbox.asked; core/approvals.py DEFAULT_MINUTES = 10; '
        'docs/12-guardrails-and-gate.md "You decide when a call is held". Labels in the picture checked against messages.en.json 1.7.45.'),

 dict(kicker='Step 7 · Running a job', title='A job is yours to run',
  text=[
   'By default the agent may not run a job, such as a pipeline. It gives you the whole command and what it is for; '
   'the board may say **waits for your run**.',
   'Run it yourself, then bring the output back in the chat.',
   ('small', 'Your company’s rules may let you approve a job on its card instead.'),
  ],
  notes='Sources: core/systems.py DEFAULT_RULES exec: human; messages gate.external.human ("a person does it", task handoff run), '
        'task.waiting.run = "waits for your run", task.handoff.next.run; docs/04-reference.md task handoff run / task run record; '
        'docs/12-guardrails-and-gate.md table: "run a job: waits for you: you run it yourself, or, when its tool pack says so, approve it".'),

 dict(kicker='Step 8 · Open a connection', title='Open a connection for this task',
  text=[
   'A held write’s card may have **Open <connection> for this task**. It needs the code, like **Approve**. '
   'The card then says **Opened**; if it offers **Tell the agent to run it again**, press it.',
   'Or, in your own terminal:',
   ('code', 'harness task allow --conn orders-dev --on'),
   ('small', 'Prod is never opened. No such button: this call or this system cannot be opened.'),
  ],
  shot='The card of a held write after Open <connection> for this task was pressed: Opened, and the button Tell the agent to run it again',
  notes='Sources: messages desk.outbox.open = "Open {name} for this task", desk.outbox.open.tip.all, desk.outbox.opened, desk.outbox.opened.hint, '
        'desk.outbox.opened.tell; core/outbox.py offer_for (needs the held call\'s code); task/commands.py "allow" (--conn, --on/--off, person only); '
        'tasklife.py set_allow; handler.py _judge_one lines 288-292 (offer only for a held write whose type opens "all"); core/systems.py open scopes; '
        'sqlserver type "open": dev/ist all, qat/prod no; messages task.allow.no.'),

 dict(kicker='Step 9 · What opening means', title='Once open, the gate stops asking you',
  text=[
   'In this task, the agent’s writes and runs on that connection now pass with no approval, even a destroy its type allows (sample SQL Server type: a table drop on dev). '
   'Nobody checks them; they are only logged in **Records** › **Agent actions**.',
   'Open only a place you could repair.',
   ('small', 'A statement on none of its lists still waits.'),
  ],
  notes='Sources: messages task.allow.conn.on, desk.outbox.open.tip.all, desk.set.open.tip.conn; handler.py _judge_one line 282 '
        '(opened: task, outbox and human calls pass; a destroy only when its write list names it; "unjudged" zones still wait); '
        'messages gate.external.zone_ask; docs/12-guardrails-and-gate.md "What is still not covered" (WHERE id > 0 passes on an open connection; '
        'the account\'s rights are the limit); desk.tab.trace = "Agent actions", desk.group.records = "Records".'),

 dict(kicker='Step 10 · Close it again', title='Close it when you are done',
  text=[
   'At the head of the task page, **Open to the agent** names what is open. Click it, then press **Close** beside the connection.',
   'Or, in your own terminal:',
   ('code', 'harness task allow --conn orders-dev --off'),
   ('small', 'It also closes when the task closes. Close anything listed there that you did not open.'),
  ],
  shot='The task page head with Open to the agent clicked: the pop-up lists one open connection, orders-dev, with its Close button',
  notes='Sources: modules/task/web/desk.js envButton (lines 752-800): the "Open to the agent" button at the head, its list "Open in this task", '
        'a Close button per connection (task allow --conn <name> --off, no code); messages desk.set.open, desk.set.open.list, '
        'desk.set.open.conn.close, desk.set.open.cannot (paired browser, open task); task.allow.conn.off; tasklife.set_allow docstring '
        '("the switch ends with the task").'),

 dict(kicker='Step 11 · Ticket boards', title='A ticket board opens only linked tickets',
  text=[
   'A ticket board opens less. Its card offers **Open linked items of <connection> for this task**: '
   'writes to the tickets linked now then pass.',
   'A write to a ticket not linked is refused. A ticket the agent links, or a new one, still waits for you; '
   'one you add with **Link a ticket** while they are open is opened too.',
  ],
  notes='Sources: toolpacks/ado/types "open": "items"; handler.py _item_scope (unlinked refused, opened passes) and _judge_one lines 273-277; '
        'messages desk.outbox.open.items, desk.outbox.open.tip.items, gate.external.unlinked, desk.set.open.links.on.tip, desk.links.add = "Link a ticket"; '
        'tasklife._set_allow_links (the items linked when you opened them); tasklife.link by_person (a ticket the person links on the board while open is opened too; boardserve.py:791).'),
]

CLOSING = dict(title='Outside systems, in short',
  text=[
   ('list', ['By default a read runs, a write waits for you, a job is yours, a destroy is refused, prod is read only; tool packs and your company change this.',
             'Approve a held call on its card: View, the code, Approve.',
             'Open a connection only where you could repair the damage, and close it when you are done.']),
  ])
