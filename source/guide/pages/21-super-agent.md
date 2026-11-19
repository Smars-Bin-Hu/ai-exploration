---
title: Super agent
subject: Super agent
layer: concept
file: 21 Super agent
harness_tag: 1.8.3
course: The book · 2.4 Custom agents | https://smarshu.com/book/read/2-4-custom-agents.html
course: The book · 5.9 Who decides: code, a cheap model, the main model, a person | https://smarshu.com/book/read/5-9-who-decides.html
---
## Super agent: what it is

The Super agent view (1.8.3) is a third view of the board, next to Lobby and List: everything that waits for the person across all open tasks comes as short messages carrying the board's own buttons, so the person can answer, approve or ask without opening each task page {src:docs/07-release-notes.md#L13-L19}. Behind it is one Copilot chat a day with a custom agent called `super` (Claude Haiku 5.5, read and search tools only), which the board feeds a short digest of the tasks; it answers, sums up and proposes, but it never acts: every action is a button the person presses {src:.harness/engine/modules/task/superbrain.py#L1-L14} {src:.github/agents/super.agent.md#L1-L7}. It solves the person's attention problem when several tasks run at once: what needs them, in what order, without reading every chat.

The view is not the board's default: the board opens on Lobby or List as before, and the pick is not remembered. It exists only on a board served by `harness task board` {src:.harness/engine/modules/task/web/board.js#L558-L566}.

## Super agent: what the view shows

The Super agent view's messages are built by code from the rows the board already computes, with no model and no Credits. Each open task that waits for the person gives at most one message, in three groups: first what blocks running work (a question, a tool confirmation, a held outside call, a stopped autorun), then decisions (requirement, plan, write-back, checks, recovery, acceptance), then the rest (a commit, an agent that stopped); the longest wait first in each group. Closed and paused tasks give none {src:.harness/engine/modules/task/superview.py#L1-L9}. A message's buttons are the board's own, calling the same endpoints with the same code field for an approval; an answered message folds into one "✓" line {src:.harness/engine/modules/task/web/super.js#L1-L9}.

- **Avatars.** One round avatar per open task: green dashed ring when it works, amber with a count when it waits for the person, grey when idle. A click shows only that task's messages {src:.harness/engine/modules/task/web/super.js#L100-L118}.
- **The robot.** A small robot rests in the top right corner and flies to a task's avatar when a message comes (a right click changes its skin). One click shows the next thing that waits, a second opens that task, a double click asks for the day's summary. Its moves cost nothing; only the summary spends Credits {src:.harness/engine/modules/task/web/pet.js#L1-L5} {src:.harness/engine/modules/task/web/super.js#L594-L645}.

## Super agent: how the chat works

The super agent chat is one Copilot chat a local day, made and owned by the board {src:.harness/engine/modules/task/superbrain.py#L1-L14}. A turn runs in these steps:

1. **The person asks**: types a question (at most 1,000 characters), presses **What's next?** or **Sum up today**, or double-clicks the robot. The first time the view is opened in a day, when something waits and nobody has talked to the agent yet, the view asks for the summary by itself {src:.harness/engine/modules/task/web/super.js#L902-L908}. Only the paired browser may send a turn {src:.harness/engine/modules/task/boardserve.py#L2082-L2088}.
2. **Code checks** that VS Code is linked to the board, that today's spend is under the limit and that no turn runs; otherwise the turn is refused {src:.harness/engine/modules/task/superbrain.py#L415-L433}.
3. **Code writes the digest**: a head line (open tasks, how many wait, work, idle), one line per open task (name, kind, state, what it waits for and how long, the waiting ones first), and the closed tasks the board still shows; at most 2,000 characters (the rest is cut), built from the board's rows and holding no file content; the agent's own read and search tools are not limited to it by code (see "Super agent: limits") {src:.harness/engine/modules/task/superbrain.py#L124-L145}.
4. **The board sends** `/harness-super`, the digest and the person's words to the day's chat, made on the first turn with the agent file `.github/agents/super.agent.md`, Claude Haiku 5.5 and Allow all (Copilot's own confirmations do not show) {src:.harness/engine/modules/task/superbrain.py#L415-L474}.
5. **The gate marks the session** from the `/harness-super` and keeps it to reading (see "Super agent: what is enforced by code, and what is only asked by text").
6. **The board reads the answer back**, cuts out the proposal block, checks each proposal against the board, and shows the answer with a ◇ whose tip says it is the agent's judgment, not a fact read by the board {src:.harness/engine/modules/task/superbrain.py#L295-L327} {src:.harness/engine/core/messages.en.json#L1787}.

The agent file asks for at most 100 words, most urgent first, never claiming that anything was done {src:.github/agents/super.agent.md#L12-L42}. 

## Super agent: the daily Credits limit

The super agent chat spends at most `super.daily_credits` Credits a local day, set in `.harness/policies/task.json`; the default is 50, and `0` switches the chat off {src:.harness/policies/task.json#L25-L27} {src:docs/07-release-notes.md#L13-L38}. The spend is read from Copilot's own records: the usage of the turns that ended or the chat's events file, whichever is more {src:.harness/engine/modules/task/superbrain.py#L1-L14}. At the limit the board sends the chat no new turn until the next day; the messages and their buttons go on working. A battery in the view's header shows what is left; pointing at it gives the Credits spent, the limit and what is left {src:.harness/engine/modules/task/web/super.js#L720-L725} {src:.harness/engine/core/messages.en.json#L1685}.

## Super agent: history and the pop-out

**History per day.** When a new day starts, the conversation of the day before (what was said, the questions asked to tasks, what the day spent) is kept as one file per day, named `<day>.json` (for example `2026-11-18.json`), in the folder `.harness/runtime/super-history/`, and today's record starts again. The clock button in the header lists earlier days to read, archive or delete for good; only the paired browser may archive or delete. Today cannot be deleted, because its record holds the day's spend and a delete would undo the limit {src:.harness/engine/modules/task/superbrain.py#L1-L14} {src:.harness/engine/modules/task/boardserve.py#L2100-L2119}.

**The pop-out.** The ⇱ button opens a small window that stays on top of other windows, so the person can work in VS Code and still answer what waits: Chrome and Edge only (Document Picture-in-Picture). Its buttons are the view's own; a window that needs a code (an approval, a new task) opens in the board page, and the pop-out says so {src:.harness/engine/modules/task/web/companion.js#L1-L7}.

## Super agent: working with a task from the view

- **Answering a task's question.** When a task stopped with a question in text, its message has a reply box; the words go to the task's chat and the message folds as answered {src:.harness/engine/modules/task/web/super.js#L389-L415}.
- **Saying something instead of picking an answer.** When the agent waits on its own question tool, the box says "Or just say something: it skips the question": the board skips the question and puts the words into the running turn, and the agent goes on from them. Not for a command confirmation, which is answered only with its buttons {src:.harness/engine/modules/task/boardserve.py#L1288-L1295} {src:docs/07-release-notes.md#L13-L38}.
- **Asking a task a question.** With one task's avatar filter on, the input asks that task; with "All", a message starting `@name` does. The board sends `/harness-ask` and the question to the task's own chat, with the task's model: at once when idle, after the running turn when it works, never steered into it. The answer shows under the question, about 12 lines with **Show more**, and is kept in the day's history; a paused task, a task with no reachable chat, or one waiting on its own question is refused {src:.harness/engine/modules/task/superroute.py#L1-L8} {src:.harness/engine/modules/task/superroute.py#L75-L128}. The turn is read only and the task keeps what it waited for.
- **Previews before approving.** A plan approval shows the plan's numbered steps, a write-back approval the files it would change with added and removed lines, at most 12 lines each; the full plan and diff stay on the task page (the file 14 Plans and approvals) {src:.harness/engine/modules/task/superpreview.py#L1-L6}.
- **Steer and Stop from an avatar.** A right click on a working task's avatar gives **Steer…** (one line into the running turn) and **Stop**, through the board's own endpoints, which only the paired browser may call {src:.harness/engine/modules/task/web/super.js#L120-L170} {src:.harness/engine/modules/task/boardserve.py#L1899-L1901}.

## Super agent: proposal cards

The person may ask the super agent for anything; it does nothing itself and may end its answer with a block of at most 8 proposals, which the board turns into a card headed "The agent proposes. Nothing happens until you press." {src:.github/agents/super.agent.md#L21-L36} {src:.harness/engine/core/messages.en.json#L1822}. Three kinds:

- **action**: any button the board offers for that task at that moment (archive, pause, resume, close, accept, approve plan or write-back, confirm requirement, recover, more or waived checks, approve a held call, autorun on), plus set checks (the card takes 0 to 9, but the board's own setting then refuses more than the policy's cap, 5 by default), steer and stop. {src:.harness/engine/modules/task/superact.py#L23-L25} {src:.harness/engine/modules/task/superact.py#L96}. The card shows the board's own button, so a code or a dialog is asked as on the board;
- **send**: a message to the task that owns the work, in an editable box with **Send**, sent as a normal message;
- **new**: the board's New task window, filled in; the person still creates the task {src:.harness/engine/modules/task/web/super.js#L235-L311}.

Each proposal is checked by code against the board as it is at that moment, again at every refresh: an action only when the board offers it for that task now (checks: an open task; steer and stop: a working task), a send only to an open task that is not paused, a new task only with a free, valid name. A proposal that fails shows its reason and no button, so nothing the agent writes makes a button appear that the board would not offer {src:.harness/engine/modules/task/superact.py#L1-L8}. Two or more of the same simple action (archive, pause, resume, close, checks) get **Do all**, which runs them in turn and stops at the first refusal {src:.harness/engine/modules/task/web/super.js#L235-L311}.

## Super agent: what is enforced by code, and what is only asked by text

Enforced by code:

- **The super agent chat only reads.** A session is marked when a person's prompt starts with `/harness-super`; a subagent's message, a Stop hook's feedback and a subagent's session never set it, and the mark stays for the session. In a marked session the gate, before any other check, refuses every call except read, search and meta tools (tool search, `task_complete`) and a terminal line that is exactly one of `harness task list`, `task status`, `task queue`, `task autorun status`, `task review status`, `target list`, `target show` with their listed options and no shell syntax. Edits, other commands, web fetches, MCP tools, skills and subagent calls are refused, and so is any call when the mark cannot be read {src:.harness/engine/modules/gate/superagent.py#L18-L89} {src:.harness/engine/modules/gate/handler.py#L758-L765}.
- **Copilot gives it no write tool.** The agent file lists only `read` and `search` and no subagents: a first layer held by Copilot; the gate is the second {src:.harness/engine/modules/gate/superagent.py#L1-L5}.
- **A question to a task is a read-only turn.** A person's prompt starting with `/harness-ask` marks that turn, and the next person's prompt without it clears the mark; while marked, the gate allows only what the super agent chat may do {src:.harness/engine/modules/gate/askturn.py#L1-L53}. The task hook leaves the task as it was: the prompt clears no wait and no delivery, and at the turn's end the task waits for what it waited for before {src:.harness/engine/modules/task/handler.py#L221-L244} {src:.harness/engine/modules/task/handler.py#L605-L607}.
- **Proposals are checked, and only the person presses.** A card's button calls the board's endpoints like any board button, with the same pairing and the same typed code for an approval {src:.harness/engine/modules/task/superact.py#L1-L8}.
- **The digest, the daily limit and when a turn is sent** are code {src:.harness/engine/modules/task/superbrain.py#L415-L433}.

Asked by text only: use the digest as the only view of the tasks, answer in at most 100 words, never do the work or say it was done, never name a task the digest does not show {src:.github/agents/super.agent.md#L12-L42}; for a task's agent in a `/harness-ask` turn, answer in at most 150 words and write no file {src:.github/instructions/agents.instructions.md#L44-L46}. What the answer says, its order and its advice are the model's judgment; no code checks them.

## Super agent: who decides what

- **Code** decides what waits and in what order, what the agent is told (the digest), whether a turn may go, and whether each proposal is something the board offers now {src:.harness/engine/modules/task/superview.py#L1-L9} {src:.harness/engine/modules/task/superact.py#L1-L8}.
- **The super agent** decides the words of its answer, what it finds most urgent, and what to propose {src:.github/agents/super.agent.md#L12-L42}.
- **The person** decides everything that happens: each button, each code, each message sent, each task created, and the daily limit {src:.harness/policies/task.json#L25-L27}.

## Super agent: why it is built this way

The design keeps a router that only talks apart from the tasks that do the work, and makes "it does not work" a rule of the system, not of the prompt: a model told only to route, in one chat with subagents, often did the work itself. So the super agent can only read and propose {src:.harness/engine/modules/gate/superagent.py#L1-L5}.

- **Notices by code, the model on demand.** What waits is computed by the board for free and keeps coming when VS Code is closed; the model is called only when the person asks or presses, or once on the day's first open {src:.harness/engine/modules/task/web/super.js#L902-L908}.
- **Facts apart from judgment.** Messages are facts read by the board; the agent's words carry a mark that they can be wrong. The buttons act on what the board reads from the files, never on the agent's retelling, so a summary cannot lead the person to approve something else {src:.harness/engine/core/messages.en.json#L1787}.
- **Cheap by construction.** The cheapest Claude model that ordered tasks well in tests, a 2,000-character digest instead of task files, no subagents, a new chat each day, a daily cap the person set at 50 {src:.harness/engine/modules/task/superbrain.py#L33-L45}.
- **A marker in the prompt.** The hook cannot see which custom agent a main chat uses, so the chat is known by the `/harness-super` at the start of the board's message, kept in the session state every hook already loads {src:.harness/engine/modules/gate/superagent.py#L1-L5}.

**Version.** All of this was released in 1.8.3 {src:docs/07-release-notes.md#L13-L38}. Some code comments and the `task.json` description label parts "1.8.1" or "1.8.2" (the say-instead code "1.8.4"): those are the branches they were built on; the released 1.8.1 and 1.8.2 hold none of it {src:.harness/engine/modules/gate/askturn.py#L1} {src:docs/07-release-notes.md#L40-L57}.

## Super agent: where it is in the source

Under `.harness/engine/` {src:.harness/engine/modules/task/superbrain.py#L1-L14}:

- `modules/task/superview.py`: what waits across tasks and in what order; `superbrain.py`: the chat, digest, spend, limit, history; `superroute.py`: a question to one task; `superact.py`: proposals and their check; `superpreview.py`: plan and changes previews.
- `modules/gate/superagent.py`: the read-only super agent chat; `modules/gate/askturn.py` and `core/askmark.py`: the read-only question turn; `modules/task/handler.py`: the task left as it was in that turn.
- `modules/task/boardserve.py`: the `/api/super*` endpoints and the say-instead send; `modules/task/web/super.js`, `superhist.js`, `companion.js`, `pet.js`: the view, history, pop-out and robot.
- `.github/agents/super.agent.md` (the agent) and `.harness/policies/task.json` (`super.daily_credits`); tests in `.harness/tests/test_gate_super.py` and `test_super*.py`.

## Super agent: common questions

**Q: Can the super agent approve a plan or change a task by itself?** No. Its chat may only read, the gate refuses everything else, and its proposals are the board's own buttons that do nothing until the person presses them; an approval still needs the typed code {src:.harness/engine/modules/gate/superagent.py#L18-L89} {src:.harness/engine/modules/task/superact.py#L1-L8}.

**Q: Is the super agent a subagent?** No. It is a custom agent in its own main chat, opened by the board once a day; the subagents are only the reviewer, the worker and the mapper {src:.github/instructions/agents.instructions.md#L44-L46} {src:AGENTS.md#L53}.

**Q: What does it cost, and how do I cap it?** About 0.2 Credits a summary, at most `super.daily_credits` a day (50 by default; `0` switches it off), shown as a battery. Messages, robot and buttons cost nothing {src:.harness/policies/task.json#L25-L27} {src:.harness/engine/core/messages.en.json#L1685}.

**Q: When I ask a task a question from the view, can it change files while it answers?** No. That turn is read only until the next normal message, and the task keeps what it waited for {src:.harness/engine/modules/gate/askturn.py#L1-L53}.

**Q: What does the super agent know about my tasks?** A digest of at most 2,000 characters written by code: names, kinds, states, what each waits for and how long, and closed tasks not yet archived; the digest holds no file content, but the agent's read and search tools are not held to it by code {src:.harness/engine/modules/task/superbrain.py#L124-L145}.

**Q: Does the view work with VS Code closed?** In a board tab already past the Enter screen, the messages and buttons do; the chat sleeps, and questions to tasks are refused until VS Code is linked. A new board tab cannot pass Enter while VS Code is closed {src:.harness/engine/modules/task/web/enter.js#L5} {src:.harness/engine/modules/task/superroute.py#L75-L128}.

## Super agent: limits

- **Any person's prompt starting with `/harness-super` sets the mark, not only the first,** and it lasts for the session: typed in a task's own chat, it makes that chat read only for good. The release notes say "first prompt" {src:.harness/engine/modules/gate/superagent.py#L18-L89} {src:docs/07-release-notes.md#L13-L38}.
- **The gate does not limit what is read.** Read and search tools pass anywhere they reach, under the gate's other checks; keeping to the digest is only asked by text {src:.github/agents/super.agent.md#L12-L42}.
- **The limit is checked before a turn,** so the turn that crosses it is still spent. `0` shows as "today's limit is used", not as switched off {src:.harness/engine/modules/task/superbrain.py#L415-L433}.
- **Questions to tasks are outside the daily limit.** They run in each task's chat with its model, spend that chat's Credits, and are not refused at the limit {src:.harness/engine/modules/task/superroute.py#L75-L128}.
- **A proposal that passes is offered, not judged wise;** a state that changes before the press is refused by the board's own button {src:.harness/engine/modules/task/superact.py#L1-L8}.
- **The pop-out is Chrome and Edge only,** without proposal cards or history; a deleted day is gone for good {src:.harness/engine/modules/task/web/companion.js#L1-L7} {src:.harness/engine/modules/task/boardserve.py#L2100-L2119}.

## Super agent: related files

- The harness: the file 00 Harness at a glance. "Waiting for you" and the question turn: the file 11 Task. Approvals and previews: the file 14 Plans and approvals. The read-only turns among the gate's checks: the file 15 The gate and guardrails. Autorun: the file 20 Autorun. Versions: the file 34 Version history.
- The code level of this file (the marker, the digest lines, the order of the limit checks, the proposal checks, the question turn, the previews): the file 21b Super agent internals.
- No harness tutorial shows this view yet: the tour "2 A tour of the harness", in the OneDrive folder `3 Courses/Harness tutorials/`, is for 1.7.45 and has no Super agent view; "1 A day with the harness" and "3 When the agent is stopped" show the same waits and buttons on the task page {src:docs/07-release-notes.md#L13-L19}.
