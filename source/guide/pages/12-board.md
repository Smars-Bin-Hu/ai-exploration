---
title: The board
subject: Board
layer: concept
file: 12 The board
harness_tag: 1.8.3
course: The book · 5.1 Manage tasks, not chats | https://smarshu.com/book/read/5-1-tasks.html
course: The book · 5.3 Two gates: where a person approves | https://smarshu.com/book/read/5-3-two-approvals.html
course: The book · 6.1 Record what happened, not what the agent said | https://smarshu.com/book/read/6-1-observe.html
---
## Board: what it is and what problem it solves

The board is a small web server on the person's own computer, started by `harness task board` (or a double-click on **Start Harness**) in the person's own terminal and kept running until Ctrl+C. In the browser it shows every task, what each waits for and since when, a page per task, and buttons that act: approve with a typed code, accept, close, pause, start a task, talk to the task's Copilot chat {src:.harness/engine/modules/task/boardserve.py#L1-L33}. It solves the problem of a person running many tasks in many chats: which one waits, what to approve, what the agent does.

## Board: where it runs, which port, and who can reach it

The board server listens on `127.0.0.1` only, on port 8765 unless `board.port` in the task policy or `--port` says otherwise, so no other computer can reach it {src:.harness/engine/modules/task/boardserve.py#L119-L122}. Only a person at a terminal starts it: the command checks for a keyboard and a screen, and the gate refuses `task board` on the agent's command line, except `--once`, which writes a static page with no buttons {src:.harness/policies/gate.json#L131-L137}. A copy has one board; a second start opens the running one, whose port is in `.harness/runtime/board-serve.json` {src:.harness/engine/modules/task/boardserve.py#L2254-L2312}.

Three rings keep it the person's. Every request must name the host `127.0.0.1:<port>` or `localhost:<port>`, and every POST must carry the header `X-Harness-Board` and no foreign `Origin`, so a page of another web site cannot press a button {src:.harness/engine/modules/task/boardserve.py#L1672-L1707}. Any program on the computer can send those headers, so every action but Pause, Resume, Off work and Back to work also needs the pairing cookie. And while the board runs, the gate refuses any agent tool call, terminal or other, whose text names the board's address with its port (a tool that only shows a question to the person is exempt) {src:.harness/engine/modules/gate/handler.py#L580-L584}.

## Board: pairing, and what an unpaired browser can and cannot do

Pairing ties the buttons to the browser the person's own terminal opened. At start the server makes a random code kept in memory only, opens the default browser at `http://127.0.0.1:<port>/#pair=<code>`, and the page trades the code once for a session cookie (HttpOnly, SameSite=Strict). Enter in the board's terminal prints a new link and voids the old code; when the server stops, the pairings are gone, except through **Restart board** {src:.harness/engine/modules/task/boardserve.py#L11-L16}. The browser inside VS Code (its user agent names Electron) is never paired, because the agent can drive it with its browser tools (since 1.7.14) {src:.harness/engine/modules/task/boardserve.py#L1709-L1721}. Pairing is needed because the agent can reach `127.0.0.1` too: knowing the address must not be enough to press a person's button.

An unpaired browser can read the board, the task pages, the Files and Live tabs, the report pages and the Super agent messages, save a page, and press **Pause**, **Resume**, **Off work** and **Back to work**, which guard nothing. It cannot approve, confirm, accept, close, archive, send to or answer a chat, make a task, use **▶ Run** or the Terminal window, start or stop autorun, give or edit files, or change settings: each answers "This browser is not paired" {src:.harness/engine/core/messages.en.json#L1119-L1126}.

## Board: the Enter screen

The Enter screen is the first thing a browser tab shows: a check, asked every 3 seconds, that what the board needs is in place. **Harness & Local** is required, five lines: This copy is set up, Browser paired, `harness doctor` has no error, VS Code is open for this copy, Copilot is connected; **Enter** works only when all five are green. **From the company** (knowledge base, instructions, company skills, code standards, tool packs, connections, code repositories) never blocks; what is missing links to the place that mends it {src:.harness/engine/modules/task/ready.py#L1-L17}.

![The board's Enter screen: the READY list with the required block Harness & Local (5 of 5) and the optional block From the company, the Restart VS Code button and Enter; shot on 1.7.43, labels unchanged at 1.8.3](img/enter.png)

The screen shows once per browser tab session, and the page offers no way past it until the five lines are green. It is drawn by the page: the server checks the pairing cookie and, for approvals, the code, not whether Enter was pressed {src:.harness/engine/modules/task/web/enter.js#L1-L11}.

## Board: the three views and the task page

The board shows the same rows, read again every 3 seconds, in three views picked at the top right {src:.harness/engine/modules/task/web/board.js#L555-L575}: **Lobby**, the first screen, where each task that is not closed is a small robot in the zone of what it does (at work, waiting for you, left alone, resting); **List**, a table with totals, filters, search and sort; and **Super agent** (1.8.3), what waits across all tasks as messages with the board's own buttons, plus a chat that only reads (see the file 21 Super agent).

A task page shows the task's wait with the button that answers it, the stage ribbon, marks (Independent review, Open to the agent, VS Code linked, Paired) and tabs in five groups {src:.harness/engine/modules/task/web/desk.js#L15-L22}: **Live** (the latest items of the chat, redacted); **Overview** (Overview, Requirement with **Confirm requirement**, Intake, Plan with **Approve plan**, TODO); **Results** (Changes, Test, RCA, Design, Evidence, **Review** for the independent checks); **Records** (Log, Task Record, and **Agent actions**, the Trace of each tool call and gate decision of the task and its subagents, from the hook log, which holds no reply and no thinking) {src:.harness/engine/modules/task/tasktrace.py#L1-L4}; and **Files**. Beside them sit the autorun **run card** (see the file 20 Autorun), the **report page** with the task's time, Credits and every call the gate blocked, where the person judges each block and can export wrong ones as test samples {src:.harness/engine/modules/task/gatereview.py#L1-L9}, and the **Terminal window** (`>_`).

## Board: "waiting for you", and the ⚠ tag

"Waiting for you" means the next move is the person's and the agent is not in the middle of a turn. Each task has one state from facts, first that holds: new, closed, paused, working, waiting, quiet (held by a session, nothing to do), no session {src:.harness/engine/modules/task/tasklife.py#L842-L855}. The kinds of wait, from a question or a plan to approve to "the agent stopped", are explained in the file 11 Task {src:.harness/engine/modules/task/tasklife.py#L276-L338}. The board adds two it reads from VS Code, which come first: Copilot asks to run a command (**Allow · deny**), or the agent asks a question (**Answer...**) {src:.harness/engine/modules/task/chatask.py#L1-L9}.

The ⚠ tag is a health warning on an open task, read from the hook log and Copilot's own session record, never the conversation. While the agent works: stuck (no tool call for 10 minutes), repeat (the same command 3 times), idle (4 model turns with no file change). On any open task: cost (Credits at 2 times the median of closed tasks of the same kind, with at least 3 of them) and context (the chat over 70% full). The limits are `health` in the task policy {src:.harness/engine/modules/task/health.py#L188-L212}; the file 22 Cost and usage explains the cost rule.

## Board: what a person can do there

Each button runs the same function as the terminal command; `board.actions` in the task policy names which act on the page, and the others run their command in the Terminal window.

- **Approve with a code**: Confirm requirement, Approve plan (alone or with the requirement under one code), Approve promote, Approve a call (a held outside call, or several with one code), More checks, Waive checks, Dismiss check, Recover the repository. The preview shows what the terminal would show and the code; the act runs the function with the code typed {src:.harness/engine/modules/task/boardserve.py#L746-L859}. See the file 14 Plans and approvals.
- **No code, paired**: Set the checks, Open to the agent (closing a connection; opening needs a held call's code), Link a ticket, Choose who runs a test; **Accept and close**, **Close**, **Archive** (one way) {src:.harness/engine/modules/task/boardserve.py#L697-L711}.
- **New task**: name, kind, a task to fork from, what to do, model, reply language, knowledge base domains, tickets, files, a skill; the board makes a Copilot chat whose agent opens the task {src:.harness/engine/modules/task/chatnew.py#L1-L8}.
- **Pause, Resume, Off work, Back to work**: set a task aside so the time is not counted as waiting; the next message resumes it. Pause does not stop the agent; **Stop** does {src:.harness/engine/modules/task/tasklife.py#L684-L695}.
- **Reply**: Say something, Steer, Stop, Answer, Allow · deny, Go on in a new chat, Compact.
- **Save as HTML**: the task page as one file with its pictures and files, no buttons, nothing that calls a server {src:.harness/engine/modules/task/boardserve.py#L623-L638}.

Every decision but the settings is refused while the agent is in the middle of a turn, unless VS Code says the chat is idle, waits for input or ended in error {src:.harness/engine/modules/task/boardserve.py#L685-L695}.

## Board: what it does by itself, and what it never does

While it runs, the board acts without a click in these cases. After the person confirms the requirement, approves the plan or approves the write-back, it sends the task's idle chat the fixed "go on" message, which starts a turn (since 1.7.38); Approve plan offers "I will switch autorun on next: do not wake the agent". After a decision on a held call whose agent's turn has ended, it wakes the agent {src:.harness/engine/modules/task/boardserve.py#L842-L851}. While autorun is on, it wakes the agent when its chat stops and compacts the chat {src:.harness/engine/modules/task/autorun_relay.py#L1-L14}. It closes a written-back development or knowledge base task once the agent has stopped and nothing else waits {src:.harness/engine/modules/task/accept.py#L184-L218}. At start it puts the company content in place, accepts the guardrail files at the first start or after an upgrade, and runs `harness doctor`. The Super agent view asks for a summary on the day's first open.

It never by itself confirms or approves (each needs the person's code), writes back, commits, starts autorun (that needs the Start form), allows a command or answers a question in VS Code, runs a code block or Terminal command, archives, or closes any other task {src:.harness/engine/modules/task/boardserve.py#L11-L16}.

## Board: how it talks to VS Code and Copilot, and which buttons spend Credits

A background thread of the board connects to VS Code's local agent host (`code agent endpoints` gives a socket, a named pipe on Windows, and a token kept in memory only). It lists the chats and binds each task to its chat, never by a guess: the chat the board made for it, or the chat whose Copilot session id is the task's; when unsure, the task stays unbound {src:.harness/engine/modules/task/chatlink.py#L1-L16}. A send, and an answer to VS Code's own waits, is a job for the thread, which checks the binding and the chat again and refuses rather than guess; a refused send gives the text to copy {src:.harness/engine/modules/task/vslink.py#L1-L24}. When VS Code closes, a tab already past the Enter screen still shows tasks and takes approvals, but nothing is sent; a new tab waits at the Enter screen.

Buttons that start or continue a Copilot turn spend Credits: **New task**, **Go on in a new chat**, a one-click skill, Send to agent, Answer, Allow · deny, Steer, **Ask agent** on a code block, Compact, the automatic "go on" after an approval, autorun, and the Super agent chat {src:.harness/engine/modules/task/chatsend.py#L1-L12}. Approving, pausing, accepting, closing, archiving, Save as HTML, **▶ Run** and the Terminal window start no turn.

Every chat the board makes (New task, a one-click skill, Go on in a new chat) starts in mode Interactive with the permission Allow all, the only one the board offers: Copilot's own confirmation of commands on the gate's ask list does not show there, while the gate's refusals hold. The person can change a task chat's permission later on the task page {src:.harness/engine/modules/task/chatnew.py#L23-L26}.

## Board: ▶ Run and the Terminal window, and what the gate checks there

**▶ Run** and the Terminal window run the person's own commands from the board server, so the gate does not see them: no deny list, guardrail paths, git or outside-system rules apply. Only the paired browser may use them; the person's reading is the only check, also of a command an agent wrote {src:.harness/engine/modules/task/taskrun.py#L1-L8} {src:.harness/engine/modules/task/boardterm.py#L1-L9}.

- **▶ Run** is on each shell code block of a task page. Its dialog shows the whole command and says "The gate does not check this. Read the whole command first, above all if an agent wrote it." It runs in the task folder as the person, with no input, and saves the output in `INBOX/BOARD/<time>/` for the agent to read {src:.harness/engine/core/messages.en.json#L2005-L2014}. **Ask agent** beside it sends the command to the chat instead: the gate holds, and it costs Credits.
- **The Terminal window** (`>_`) runs one line per command, any shell command by default (`board.terminal_any_command: false` leaves `harness` commands only), with no input. A `harness` command typed there gets a one-time code that vouches for the person, so person-only commands that ask no code run (`task pause`, `task review set`, `task allow`, `doctor --accept`); one that asks for a typed code is refused, since there is no keyboard. **▶ Run** gets no such code {src:.harness/engine/core/boardperson.py#L1-L10}.

## Board: what is enforced by code, and who decides what

**Code** enforces the `127.0.0.1` server with its Host, Origin and header checks; the gate's refusal of the agent's `task board` and of calls naming the board's address; the paired cookie for every action but Pause, Resume, Off work and Back to work; the typed code bound to a digest for approvals; no pairing in VS Code's browser; decisions held while the agent works; a fresh binding check before each send {src:.harness/engine/modules/task/boardserve.py#L1-L33}. **Not enforced**: what **▶ Run** and the Terminal window run, and Copilot's ask confirmations in Allow all chats. **Text only**: the agent is told to stop and ask the person to approve on the task page {src:.github/skills/harness-my-task/SKILL.md#L113-L114}.

**The person** starts the board, pairs a browser, types every code and presses every button. **Code** decides each task's state and wait, which chat is the task's, whether a button may act now, and the ⚠ rules. **The agent** decides nothing on the board: it cannot start it, reach it through the gate, or pair a browser.

## Board: how it is built, and where in the source

The board is Python's standard `http.server` in one process: Python computes every row and decision, and the pages in `web/` only draw them. Labels are keys of `core/messages.en.json` (and `messages.zh.json`, by the `language` setting); a message that names a button writes `{@name}`, so text and screen use the same words {src:.harness/engine/core/messages.py#L1-L8}. Under `.harness/engine/modules/task/`: `boardserve.py` (server, pairing, endpoints, buttons), `ready.py` (Enter screen), `taskboard.py` and `tasklife.py` (rows, waits), `taskdesk.py` (task page), `health.py` (⚠), `tasktrace.py`, `gatereview.py` (Agent actions, verdicts), `vslink.py`, `chatlink.py`, `chatsend.py`, `chatnew.py` and `core/ahp.py` (VS Code), `taskrun.py`, `boardterm.py` with `core/boardperson.py` (**▶ Run**, Terminal), and `web/` (`board.js`, `lobby.js`, `desk.js`, `enter.js`, `super.js`, `run.js`, `term.js`, the HTML and styles). Settings: `board` and `health` in `.harness/policies/task.json`.

## Board: why it is built this way, and what was tried before

- **A local page, not a service.** The board began in 1.4.4 as a served page with pause, resume and the two approvals, on the person's computer, so it needs pairing, not a login {src:docs/07-release-notes.md#L3333-L3343}. Each button calls the terminal command's own function, so there is no second way to approve.
- **Linked to Copilot, never guessing.** In 1.6 the board learned to talk to VS Code's chats, because a person with a dozen tasks had to find the waiting window and paste a message after each approval; every send follows a person's press, and none goes to an uncertain chat. An approval first left a button to send "go on"; since 1.7.38 it wakes the agent by itself {src:.harness/engine/modules/task/boardserve.py#L842-L851}.
- **One permission for new chats.** Three were planned; Allow all was kept because with another the agent's first command waited in VS Code before the task was on the board to show it {src:.harness/engine/modules/task/chatnew.py#L23-L26}.
- **Run, two ways.** The first Run prototype sent the command to the agent; the board ships both, **Ask agent** under the gate and **▶ Run** outside it. The Terminal window took only `harness` commands at first (1.6.92), any command from 1.6.94 {src:.harness/engine/modules/task/boardterm.py#L1-L9}.

## Board: common questions

**Q: Is the board a server my team shares?** No. It runs on your computer, listens on `127.0.0.1` only, and shows your copy's tasks {src:.harness/engine/modules/task/boardserve.py#L119-L122}.

**Q: Can the agent press the board's buttons, or approve through it?** Not by the ways the harness gives it: the gate refuses its start of the board and its calls to the board's address, actions need the paired cookie, VS Code's browser is never paired, and approvals need your typed code {src:.harness/policies/gate.json#L131-L137} {src:.harness/engine/modules/task/boardserve.py#L1709-L1721}.

**Q: Why must my browser be paired?** So only the browser your own terminal opened can act. Unpaired, you can read and pause or resume; press Enter in the board's terminal for a new link {src:.harness/engine/core/messages.en.json#L1126}.

**Q: Does a board button cost Credits?** Only one that starts or continues a Copilot turn: New task, Go on in a new chat, sends, Ask agent, Compact, the automatic "go on" after an approval, autorun, the Super agent chat {src:.harness/engine/modules/task/chatsend.py#L1-L12}.

**Q: Is ▶ Run checked by the gate?** No. It and the Terminal window run as you, from the board server; the dialog says so {src:.harness/engine/modules/task/taskrun.py#L1-L8}.

**Q: Can I use the board with VS Code closed?** A new browser tab stops at the Enter screen, whose VS Code and Copilot lines stay red. A tab already past it still reads, approves, accepts and closes; nothing is sent to a chat {src:.harness/engine/modules/task/ready.py#L1-L17}.

## Board: limits

- **▶ Run and the Terminal window bypass the gate,** also for a command the agent wrote {src:.harness/engine/modules/task/taskrun.py#L1-L8}.
- **Reads and pause need no pairing.** Any program on the computer that sends the right host can read the pages, files and Live items and press pause or resume; the gate refuses only an agent call whose text names the address with the port, so a script that builds the address at run time is not seen {src:.harness/engine/modules/gate/handler.py#L580-L584}.
- **The embedded browser is known by its user agent** (Electron); another browser tool is kept out only by having no cookie. **Board-made chats start with Allow all,** so the ask list's confirmations do not show there {src:.harness/engine/modules/task/boardserve.py#L1709-L1721} {src:.harness/engine/modules/task/chatnew.py#L23-L26}.
- **An approval starts a turn by itself,** unless the no-wake box of Approve plan is ticked {src:.harness/engine/modules/task/boardserve.py#L842-L851}.
- **Accept, Close, Archive and the settings need pairing but no code,** though the task policy's description says the other buttons ask for one {src:.harness/policies/task.json#L3}.
- **With no board, no relay:** autorun's wake-ups, the close of written-back tasks and the wakes after approvals happen only while the board runs; **▶ Run** and Terminal commands stop with it {src:.harness/engine/modules/task/autorun_relay.py#L1-L14}.

## Board: related files

- The task and its waits: 11 Task. Approvals and codes: 14 Plans and approvals. The gate: 15 The gate and guardrails. Checks: 17 Independent checks. Autorun and the run card: 20 Autorun. The Super agent view: 21 Super agent. Credits and the cost rule: 22 Cost and usage. Every code location: 32 Code map {src:.harness/engine/modules/task/boardserve.py#L1-L33}.
- To do this step by step, see the tutorials "1 A day with the harness" and "2 A tour of the harness" in `3 Courses/Harness tutorials/`; they show the board of 1.7.45, before the Super agent view and the autorun Start form.
