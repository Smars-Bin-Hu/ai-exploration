---
title: Start a task and give it the requirement
subject: Start a task
layer: how-to
file: 21 Start a task and give it the requirement
harness_tag: 1.7.45
course: The book · 5.2 The agent writes the requirement, the person confirms it | https://smarshu.com/book/read/5-2-requirements.html
course: The book · 5.1 Manage tasks, not chats | https://smarshu.com/book/read/5-1-tasks.html
---
## Start a task: before you start

To start a task you need four things ready. The harness is set up and `harness doctor` reports no error; VS Code is open on the harness folder with GitHub Copilot Chat; the board is running; and your browser is paired with the board {src:docs/01-quickstart.md#L56-L68}.

- **Start the board**: double-click `Start Harness.command` (macOS) or `Start Harness.cmd` (Windows), or run `harness task board` in your own terminal, and keep that window open. The board opens your browser, already paired {src:docs/01-quickstart.md#L20} {src:docs/01-quickstart.md#L87-L97}.
- **Use a paired browser**: Chrome, Edge or Firefox, opened from the link the board's terminal prints. A browser opened by hand is not paired: it can pause and resume a task, but every approval and every upload on the Intake tab is refused. The browser inside VS Code is never paired, because the agent can drive it {src:.harness/engine/core/messages.en.json#L1085-L1094} {src:.harness/engine/modules/task/boardserve.py#L2023-L2026}.
- **For a task that changes code**: the target repositories must be set up (on **Get ready**, or in `.harness/policies/target.override.json`); without them the agent cannot change your code {src:docs/01-quickstart.md#L99-L113}.

![The Enter screen of the board: the required block Harness & Local and the optional block From the company, both green, with the VS Code button beside Enter](img/enter.png)

You need no command and no path to start a task. One sentence is enough: what to do, and in which repository; add the scope and what "done" means for a better result {src:docs/01-quickstart.md#L144-L153}.

## Start a task: steps

### Step 1. Say what you want

Say in one sentence what you want done, in one of two places. In the Copilot chat in VS Code, type it to the default agent: "Add a field `region` to the orders table in `sales-etl`. Acceptance: the nightly load fills it." On the board, press **New task**: give a name, the kind, what to do in your own words, the model and the knowledge base domains; the board shows the first message before you send it, then makes a new chat in VS Code and sends it {src:.harness/engine/modules/task/chatnew.py#L1-L8} {src:.harness/engine/core/messages.en.json#L1995-L2022}.

A chat the board makes is set to Allow all permissions, so the agent's first command does not wait in VS Code; the harness gate still checks every tool call {src:.harness/engine/core/messages.en.json#L2013}. A plain question that touches no file and no server opens no task; a look at a server or at files opens a Q&A task without questions {src:.github/skills/harness-my-task/SKILL.md#L18-L22}.

### Step 2. Answer the agent's questions; it opens the task

The agent asks, all at once and with numbered options, what is not clear yet: a new task or one that exists, the kind of work, and, for a question, an analysis or a design, whether a repository must change or whether you will run code by hand {src:.github/skills/harness-my-task/SKILL.md#L35-L56}. Answer with the numbers. The agent then makes up a short task name and runs `harness task new <name> --kind <kind> --session-id <id>`, which makes the folder `.workspace/sandbox/tasks/<name>/` with the files of the tier {src:.harness/engine/modules/task/tasklife.py#L163-L174}.

| Kind | What "done" means | Default tier |
|---|---|---|
| `qa`: a question or a look at a server or files | the answer has a source | light: `TASK.md` |
| `rca`: root cause analysis | a chain of evidence | medium: adds `REQ.md`, `REQ/`, `REF/`, `LOG.md` |
| `design` | options and trade-offs | medium |
| `dev`: development | the changes match the approved plan | full: adds `TODO.md`, `DEV/`, `TEST/` |
| `test` | cases and results on disk | full |
| `kb`: knowledge base update | goes through a write-back | full |
| `other` | agreed with you, written in `REQ.md` | medium |

The table follows the harness's own lists: the kinds and their meaning of done from the skill, the tiers from the code {src:.github/skills/harness-my-task/SKILL.md#L42-L50} {src:.harness/engine/core/tasks.py#L21-L23} {src:.harness/engine/modules/task/tasklife.py#L39-L45}. A tier only goes up: when a question turns into a change of a repository, the agent runs `task upgrade` and only the missing files are added {src:.harness/engine/modules/task/tasklife.py#L196-L211}. The agent gives you the address of the task's page on the board.

### Step 3. Give the requirement documents on the Intake tab

When the requirement came as documents (a Word paper, an Excel mapping, emails), give them to the task on its **Intake** tab; you can skip this step when the conversation says it all. Open the task on the board, open **Intake**, and drop the files or press **Choose files** {src:.harness/engine/core/messages.en.json#L1300-L1303}.

![The Intake tab of a task page: drop files or choose them, paste a table, the six files the agent reads, and the message under Tell the agent with its Copy message button](img/task-intake.png)

What happens to each file, with no AI and no tokens {src:.harness/engine/modules/task/intake.py#L1-L10}:

- The original is kept untouched in `REQ/originals/`.
- Its text is written beside it in `REQ/`: Word becomes Markdown, each Excel sheet a CSV file.
- A report (`<name>.convert.md`) says what was left out: hidden sheets, comments, pictures, headers and footers. Read it: it is how you know what the agent will not see.

Then trim: click a file to cut what the agent does not need (a CSV opens as a table: search, pick rows, delete or keep them), and tick whole files to delete. A file that came out wrong can be replaced by a table or a text you paste in **Or paste a table, a Markdown document or a text**. Press **Create INTAKE.md**, choose the knowledge base domain the task is about, and add a line of your own if you want: `REQ/INTAKE.md` is the short goal the agent reads first {src:.harness/engine/core/messages.en.json#L1315-L1316}. Last, copy the message under **Tell the agent** into the chat, or send it with the reply panel {src:.harness/engine/core/messages.en.json#L1356-L1357}.

The same can be done in a terminal: `harness task intake convert <file> ... --task <task>`, `harness task intake paste`, and `harness task intake init` {src:.harness/engine/modules/task/commands.py#L318-L336}. The agent is told to read the converted files in `REQ/` and never the originals {src:.github/instructions/workspace.instructions.md#L13}. For the chat that holds the task, the gate refuses the agent's edit tools in `REQ/`; the `task intake` commands themselves have no check that a person runs them {src:.harness/engine/modules/gate/handler.py#L85-L87} {src:.harness/engine/modules/task/commands.py#L41-L51}.

### Step 4. Read and confirm the requirement

The agent writes the requirement as it understands it into `REQ.md`: what to do, what not to do, what counts as done, the source of each item, and what is not clear yet {src:.harness/contracts/templates/task/en/REQ.md#L1-L42}. Answer its open questions in the chat until `REQ.md` says what you mean. On the task page, open **Requirement** and read it. If a part still holds the template's text, the page says "Requirement not finished": ask the agent to finish it first {src:.harness/engine/core/messages.en.json#L3113}.

When it is right, press **Confirm requirement** at the top of the page and type the six-character code the page shows; in a terminal, the same is `harness task confirm-req --task <task>` {src:.harness/engine/core/messages.en.json#L649} {src:.harness/engine/modules/task/task.py#L570-L598}. The code belongs to this version of the file: if the agent changes `REQ.md` while you read, the confirmation is refused and you read it again. The harness then fills the "User confirmed" line with the date {src:.harness/engine/modules/task/task.py#L601-L612}. That line is what the code reads as the confirmation; it is plain text in `REQ.md`, which the agent is told to leave alone but can write {src:.harness/engine/modules/task/taskreview.py#L88-L110} {src:AGENTS.md#L51}.

A plan cannot be approved while `REQ.md` has a "User confirmed" line that is not filled in; a task with no `REQ.md`, or a `REQ.md` without that line, is not checked {src:.harness/engine/modules/task/task.py#L443-L451} {src:.harness/engine/modules/task/task.py#L551-L567}. **Approve plan** on the page offers to confirm the requirement and approve the plan with one code. The board marks a `full` tier task (`dev`, `test`, `kb`) as waiting for your confirmation {src:.harness/engine/modules/task/tasklife.py#L310-L315}. The skill tells the agent to ask you to look at `REQ.md` before it acts, and, for a task of kind `other`, to act only after you have read it {src:.github/skills/harness-my-task/SKILL.md#L77-L78}.

### Step 5. See the task on the board

Every open task is a row of the board's list, or a small robot in the board's lobby (the **Lobby / List** switch at the top). The list shows each task's state, how long it has waited, its stage dots, and a button for your next move; the tasks that wait for you come first {src:.harness/engine/modules/task/tasklife.py#L856-L870}.

![The board's list: six tasks waiting for you, each with its state, how long it waited and the button for the next move, such as Approve plan, Approve promote, Approve a call and Answer...](img/board-list.png)

**Waiting for you** at the top counts the tasks whose next move is yours and whose agent is not at work. The chip in the State column says why: "waits for you" means the agent ended its turn and stopped, and the task waits for your next message; "the plan waits for your approval", "the requirement waits for your confirmation", "to accept" and the others name the decision {src:.harness/engine/modules/task/tasklife.py#L840-L853} {src:.harness/engine/core/messages.en.json#L19}. Press the button in the **Do** column, or open the task: its page puts what waits for you first, as a card with the button for the answer and a link to the tab to read before you decide.

![A task page with the card at the top: the write-back waits for your approval, how long it has waited, and the buttons Approve promote and Read the promote plan](img/task-overview.png)

The section titled Start a task: what "waiting for you" means and what to do lists the reasons and what to do for each.

## Start a task: what "waiting for you" means and what to do

"Waiting for you" on the board means the task's next move is yours and its agent is not in the middle of a turn {src:.harness/engine/modules/task/tasklife.py#L840-L853}. What to do depends on the reason the board names {src:.harness/engine/modules/task/tasklife.py#L276-L336}:

- **the promote failed halfway and waits for you to recover**: press **Recover the repository** and type the code; then the agent runs the dry run again {src:.harness/engine/core/messages.en.json#L21}.
- **waits for you**: the agent stopped; read its last answer (the **Live** tab, or the chat) and reply. Your next message takes the mark away {src:.harness/engine/modules/task/handler.py#L398-L411}.
- **waits for your answer**: the agent asked a question; answer it on the page or in the chat.
- **the requirement waits for your confirmation**: read **Requirement**, then **Confirm requirement**.
- **the plan waits for your approval**: read **Plan**, then **Approve plan** and the code.
- **the promote (write-back repo) waits for your approval**: read **Changes**, then **Approve promote** and the code.
- **an outside call waits for your approval**: read the held call's card, then approve it or say why not.
- **waits for your run** or **waits for your test results**: run what the agent handed you and bring the output back on the page.
- **the checks are used up and wait for your decision**: **More checks** or **Waive checks**.
- **the plan is approved: tell the agent to go on** (and the like): the board could not tell the agent; press **Send to agent**, or say "approved" in the chat.
- **promoted: commit the files**: commit the new branch in the repository. The board closes such a task by itself once the agent has stopped and nothing else waits; the commit is still yours to make {src:.harness/engine/modules/task/accept.py#L186-L199}.
- **autorun stopped and waits for you**: read why it stopped, then reply or switch autorun on again {src:.harness/engine/core/messages.en.json#L132}.
- **cancelled, waits for you**: you stopped the agent's turn in VS Code; reply to let it go on {src:.harness/engine/core/messages.en.json#L131}.
- **to accept**: read the agent's summary, then **Accept and close**, or **Not yet** and say what is missing.

A paused task does not count as waiting; **Off work** pauses every open task that is not at work, so the night is not counted {src:.harness/engine/core/messages.en.json#L1617-L1618}.

## Start a task: when something goes wrong

- **The page says "This browser is not paired"** or a button is refused: press Enter in the terminal of `harness task board` and open the new link it prints, in Chrome, Edge or Firefox {src:.harness/engine/core/messages.en.json#L1085-L1087}.
- **The agent reports `There is no session <id>`**: it copied the session id wrongly; it should use the "current session id" from the rules at the top of its prompt {src:.harness/engine/core/messages.en.json#L7}.
- **`Task <name> exists already`**: a task has that name; say "go on with" and its name to pick it up, or ask for another name {src:.harness/engine/core/messages.en.json#L5}.
- **A task name is refused**: a name may not hold a space, a slash or a character a terminal reads as a command, a quote, a variable or a wildcard (`&`, `$`, `'`, `"`, `(`, `*` and the like), may not start with `-` or `.`, and may be at most 80 characters; letters, digits, `-`, `_` and `.` are safe {src:.harness/engine/modules/task/tasklife.py#L33-L69} {src:.harness/engine/core/messages.en.json#L1571}.
- **Confirm requirement says the file is not written or has no confirmation line**: the agent has not written `REQ.md` yet; ask it to {src:.harness/engine/core/messages.en.json#L639}.
- **"The requirement changed while you were confirming"**: the agent changed `REQ.md` after the page showed the code; read it again and confirm again {src:.harness/engine/modules/task/task.py#L590-L594}.
- **Approve plan is refused because the requirement is not confirmed**: use the one-code approval the page offers, which confirms the requirement and approves the plan together {src:.harness/engine/core/messages.en.json#L1810}.
- **The agent says it cannot run `task confirm-req` or `task approve-plan`**: that is by design; only you can, on the page or in your own terminal {src:.harness/engine/core/messages.en.json#L489}.
- **The board says the agent is at work** when you press a button: decide once it has stopped, or stop it first {src:.harness/engine/core/messages.en.json#L1643}.
- **An old Excel (`.xls`) or PDF file is not converted**: it needs a Python package (`xlrd`, `pypdf`); `harness task intake setup` prints the command to install it, which you run yourself {src:docs/09-intake.md#L91-L104}.

## Start a task: why it works this way

A chat is forgotten when it is compacted or closed, so the work lives in a task folder that any later chat can pick up; and the requirement is the agent's own writing in `REQ.md`, checked by you, because your confirmation is the real check and is easiest on a short, clean input {src:.harness/engine/core/tasks.py#L1-L8} {src:docs/09-intake.md#L17-L21}. Your documents are turned into text by a program, with no AI, so nothing in them is changed or paid for in tokens before you trim it {src:.harness/engine/modules/task/intake.py#L1-L10}. The file 11 Task explains how the task, its approvals and its stages work.
