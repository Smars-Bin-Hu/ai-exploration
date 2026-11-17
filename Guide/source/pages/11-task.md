---
title: Task
subject: Task
layer: concept
file: 11 Task
harness_tag: 1.7.41
course: The book · 5.1 Manage tasks, not chats | https://smarshu.com/book/read/5-1-tasks.html
course: The book · 5.3 Two gates: where a person approves | https://smarshu.com/book/read/5-3-two-approvals.html
---
## Task: what it is

A task is one piece of work kept as a folder on disk, so that it outlives the chats that do it. The folder `.workspace/sandbox/tasks/<task name>/` holds a handover note (`TASK.md`), the requirement (`REQ.md`), the plan (`PLAN.md`), the results, and a state file `.task/task.json` that harness code writes; the agent's edit tools, and a terminal command that names the file, are refused on it {src:.harness/engine/core/tasks.py#L1-L36} {src:.harness/policies/gate.json#L24-L33}. The agent is told to open a task before it produces or changes files; the code does not force it to {src:AGENTS.md#L46-L47}. Any later chat can open the task and go on from the files. A task stays open until the person accepts or closes it, or, for a written-back development or knowledge base task, until the board closes it once nothing waits; `task close` itself has no check that a person runs it, only the gate's refusal on the agent's command line {src:.harness/engine/modules/task/tasklife.py#L177-L193} {src:.harness/engine/modules/task/accept.py#L1-L11} {src:.harness/engine/modules/task/accept.py#L184-L218} {src:.harness/engine/modules/task/commands.py#L123-L133}.

Every task has a kind and a tier. The kind says what "done" means: `qa` (a question or a look at a server or files), `rca` (root cause analysis), `design`, `dev` (development), `test`, `kb` (knowledge base update) or `other`. The tier says which files the folder has: `light` has `TASK.md`; `medium` adds `REQ.md`, `REQ/`, `REF/` and `LOG.md`; `full` adds `TODO.md`, `DEV/` and `TEST/`. Each kind has a default tier: `qa` light; `rca`, `design` and `other` medium; `dev`, `test` and `kb` full {src:.harness/engine/core/tasks.py#L19-L23} {src:.harness/engine/modules/task/tasklife.py#L39-L45}.

## Task: how it works

Five parts and the person do the work of a task, and the figure shows who calls whom and the life of a task.

![The parts of a task and who calls whom, above, and the life of a task from opened to closed, below](fig/pattern.svg)

The parts, as the figure draws them:

- The **agent** is a chat in VS Code and holds one task at a time {src:.harness/engine/core/state.py#L1-L10}.
- The **task hook** tells the agent at session start and at every prompt where its task stands: kind, tier, round, the next step, the write scope and the checks {src:.harness/engine/modules/task/handler.py#L88-L121} {src:.harness/engine/modules/task/handler.py#L157-L172}.
- The **gate** keeps the edit tools of a chat that holds an open task inside its folder; a chat with no task is not bound {src:.harness/engine/modules/gate/handler.py#L64-L88}.
- The **task** is the folder: handover note, requirement, plan, code, state. Its state file is written by harness code; the agent's edit tools are refused on it {src:.harness/policies/gate.json#L24-L33}.
- The **task commands** (`harness task ...`) open, approve, write back and close, and each checks the facts it depends on before it acts {src:.harness/engine/modules/task/task.py#L1-L10}.
- The **person** asks, approves and accepts. The agent opens tasks, delivers results and writes back.

The life of a task has two paths. A task that changes a repository (`dev`, `kb`) is opened; its requirement is confirmed; its plan is approved; the agent writes code in `DEV/`; the write-back is approved; the files are written back; then the board closes the task once the agent has stopped and nothing else waits, without waiting for the commit {src:.harness/engine/modules/task/task.py#L568-L610} {src:.harness/engine/modules/task/task.py#L426-L473} {src:.harness/engine/modules/task/task.py#L941-L980} {src:.harness/engine/modules/task/accept.py#L184-L218}. A task whose result stays in the folder (analysis, design, test, question) is opened; the result is written in the folder (an analysis or a design at its root, test results in `TEST/` and run records in `RUNS/`, a Q&A answer in `TASK.md`); the agent delivers it with a summary (`task deliver`), and the person accepts it with **Accept and close** {src:.harness/engine/modules/task/taskstages.py#L122-L139} {src:.github/instructions/workspace.instructions.md#L15-L17} {src:.github/skills/harness-my-task/SKILL.md#L82} {src:.harness/engine/modules/task/accept.py#L45-L68} {src:.harness/engine/modules/task/accept.py#L167-L181}. Confirming the requirement, approving the plan and the write-back, and accepting are the person's moves; closing a written-back task is the board's. The requirement's confirmation line in `REQ.md` is also plain text the agent can write (see the section "Task: limits"). Any later chat may open a task again, closed or not {src:.harness/engine/modules/task/tasklife.py#L177-L193}.

## Task: how it moves from one stage to the next

A task's stage is not a value the agent sets: it is worked out each time from the files and the state, so a task whose requirement changed falls back to the right stage by itself {src:.harness/engine/modules/task/taskstages.py#L1-L15}. For `dev` and `kb` the stages are requirement, plan, developing, write-back, done; for `rca`, `design` and `other`, doing and done; for `test`, the guide and one stage per environment; `qa` has none {src:.harness/engine/modules/task/taskstages.py#L56-L67}.

What moves the work forward is the agent, told by text; what stops it at each gate is code. The text: the hook's next-step line, the skill `harness-my-task` and the workspace instructions tell the agent to write `REQ.md`, ask the person to look at it, write `PLAN.md`, stop and give the link {src:.harness/engine/core/messages.en.json#L14-L15} {src:.github/skills/harness-my-task/SKILL.md#L73-L97}. The code at each gate:

- **Requirement to plan.** `task approve-plan` refuses a plan while `REQ.md` is still the bare template (the template's opening placeholder is still there), or its "User confirmed" line is not filled in, or what it asks changed since it was confirmed; `--with-req` confirms the requirement and approves the plan with one code {src:.harness/engine/modules/task/task.py#L426-L467} {src:.harness/engine/modules/task/task.py#L479} {src:.harness/engine/modules/task/task.py#L549-L565}. The confirmation is read from that text line, which the agent can write, and a missing `REQ.md` or line is not checked at all {src:.harness/engine/modules/task/taskreview.py#L88-L110}.
- **Plan to developing.** For the chat that holds the task, the gate refuses the edit tools any write under `DEV/` until the plan is approved as it is now, for the requirement as it is now; a chat with no task is not bound, but nothing reaches a repository without the write-back approval {src:.harness/engine/modules/gate/handler.py#L80-L84} {src:.harness/engine/core/tasks.py#L147-L159}.
- **Developing to write-back.** `task promote --dry-run` needs an approved plan and, when the person switched checks on, enough passes of the independent check {src:.harness/engine/modules/task/task.py#L868-L885} {src:.harness/engine/modules/task/taskreview.py#L563-L568}. `task promote` needs the person's approval of the same plan digest {src:.harness/engine/modules/task/task.py#L898-L901}.
- **Done.** Closing is the person's: the gate refuses `task close` on the agent's command line, and the agent is told never to close a task; the command itself has no person check, so a script the agent runs is not stopped {src:.harness/policies/gate.json#L137-L143} {src:.harness/engine/modules/task/commands.py#L123-L133}.

So the answer to "is the workflow a skill or code" is both: the skill says the order, the code holds the gates, and a person holds the keys of the gates.

## Task: how it differs from a chat session

A session is one Copilot chat and lives as long as that chat; a task outlives its sessions. The two point at each other, so either can end or change without the other: the session's state names the one task it holds (`active_task`), and the task's state names its latest session (`session_id`) {src:.harness/engine/modules/task/task.py#L138-L216}.

![What lives with the session and what lives with the task, and the pointer each keeps to the other](fig/task-vs-session.svg)

What lives with the session: the Copilot chat with its context and transcript, kept by Copilot under `~/.copilot/session-state/<id>/` {src:.harness/engine/core/copilot_events.py#L1}; the harness's session state `.harness/runtime/state/<surface>/<session>.json`, with `session_id`, `active_task` (the one task it holds), `parent_session_id` (set for a subagent's session), `admin` (admin mode, which holds no task), the running subagents (reviewer, mapper) and `modules.task` (per-prompt counters), written by `core/state.py` under a lock {src:.harness/engine/core/state.py#L1-L10} {src:.harness/engine/core/paths.py#L86-L87}; and the hook log `.harness/runtime/logs/<surface>/<session>.jsonl` {src:.harness/engine/core/logs.py#L35-L36}.

What lives with the task: the task files (`TASK.md`, `REQ.md`, `PLAN.md`, `TODO.md`, `LOG.md`, `DEV/`, `REQ/`, `REF/`), which any session reads by path, and `.task/task.json`, written by harness code (the command line, the hook and the board), under a lock, and replaced whole at each write {src:.harness/engine/modules/task/task.py#L80-L96} {src:.harness/engine/core/state.py#L123-L141}. Its fields are listed in the section "Task: where its record is kept, and what is in it".

The rules between them: one session holds at most one task, and opening another leaves the first open {src:.harness/engine/modules/task/task.py#L138-L158}. Any later session may open the task again: a new holder, the same state. A subagent's session inherits its parent's task; a subagent or an admin session cannot open one {src:.harness/engine/core/state.py#L252-L303} {src:.harness/engine/modules/task/tasklife.py#L126-L135}. Copilot compacts a chat as its context fills, at about 80%; the task's files do not depend on the chat {src:.harness/policies/task.json#L3}.

## Task: where its record is kept, and what is in it

A task's record is its folder, `.workspace/sandbox/tasks/<task name>/`, on the person's computer; the folder is ignored by git {src:.harness/engine/core/tasks.py#L19-L36} {src:.gitignore#L27-L30}. The files, by tier {src:.harness/engine/modules/task/tasklife.py#L39-L45}:

- `TASK.md`: the handover note a new session reads first: kind, tier, status, what is being done, the next step, the decisions, the open questions {src:.harness/contracts/templates/task/en/TASK.md#L1-L23}.
- `REQ.md`: the requirement as the agent understands it, with the "User confirmed" line and the sections What to do, What not to do, Done when, Source, Not clear yet, Changes {src:.harness/contracts/templates/task/en/REQ.md#L1-L42}.
- `REQ/`, `REF/`, `INBOX/`: what the person gave (documents, reference files, results given on the task page); for the chat that holds the task, the gate refuses the agent's edit tools there {src:.harness/engine/core/tasks.py#L36} {src:.harness/engine/modules/gate/handler.py#L85-L87}.
- `PLAN.md`, `TODO.md`, `LOG.md`; `DEV/` for code that goes back to a repository; `TEST/` for test results; results that stay in the task (`RCA.md`, `DESIGN.md`) at the root.
- Files only the command line writes: `.task/` (state and the base versions of fetched files), `REVIEW/` (each independent check and its verdict), `SNAPSHOT/`, `OUTBOX/`, `CHANGES.diff`, `PROMOTE-PLAN.diff` {src:.harness/policies/gate.json#L24-L33}.

The state file `.task/task.json` holds: the task's path, name, kind and tier; `status` (open or closed); `round` (one more each time a written-back task is opened again); `session_id` (the latest holder) and `sessions[]` (every pick-up, the last 100); `req` (the digest of the confirmed requirement); `plan` (the approved plan's digest and the requirement digest it was approved for); `promote` (none, dry_run, done or partial, with the approved digest); `waiting` and `paused`; `deliver` and `handoff`; `review`, `allow_conn` and `links`; `events[]` (the history, the last 200); `rounds[]` (earlier write-backs); and `chat` (the bound VS Code chat) {src:.harness/engine/modules/task/task.py#L36-L39} {src:.harness/engine/modules/task/task.py#L163-L188} {src:.harness/engine/modules/task/task.py#L232-L249} {src:.harness/engine/modules/task/task.py#L467}.

When a task closes, the chat's rounds (prompts, the agent's text, tool names, times, credits; no thinking and no tool results) are copied into `.task/transcript.jsonl`, and a report is written to `.workspace/reports/tasks/<task name>/report.md` {src:.harness/engine/modules/task/task.py#L384-L396} {src:.harness/engine/modules/task/chatrounds.py#L1-L10}. Closing changes only the state: the folder stays where it is {src:.harness/engine/modules/task/tasklife.py#L10-L11}.

## Task: how a new chat continues the same task

A new chat continues a task from its files, by name. A session that holds no task is told at every prompt which tasks are open (the newest five) and to run `harness task open <task name>` when the person means one of them {src:.harness/engine/modules/task/handler.py#L124-L137} {src:.harness/engine/core/messages.en.json#L107}. So the person says "go on with" and the task's name, and the agent, following the skill `harness-my-task`, runs `task open` {src:.github/skills/harness-my-task/SKILL.md#L58-L65}. On the board, **Go on in a new chat** on the task page starts a new chat in VS Code that picks the task up; what was said only in the old chat, and is in no task file, does not come along {src:.harness/engine/core/messages.en.json#L2139-L2140}.

`task open` makes the new session the task's holder: it records the pick-up in `sessions[]`, sets `session_id`, clears the waiting mark and a pause, and sets the session's `active_task` {src:.harness/engine/modules/task/task.py#L172-L207}. It refuses an unknown session, a subagent, an admin session and a write-back stopped halfway {src:.harness/engine/modules/task/task.py#L138-L175}. Its answer tells the agent to read `TASK.md` first, then `REQ.md`, `REQ/` and `REF/` {src:.harness/engine/modules/task/tasklife.py#L155-L160} {src:.harness/engine/core/messages.en.json#L14-L15}. A closed task is opened again as it was; a written-back task opened again starts a new round, with the old `DEV/` and plan moved aside and a new plan to approve {src:.harness/engine/modules/task/task.py#L172-L181} {src:.harness/engine/modules/task/task.py#L232-L249}.

## Task: who approves, and why the agent cannot approve its own plan

The agent cannot approve its own plan by the ways the harness gives it. Three things stand in the way. First, the gate refuses, on the agent's command line, `task confirm-req`, `task approve-plan`, `task approve-promote`, `task recover`, `task review set`, `extend`, `waive` and `dismiss`, `task test runner`, `task pause`, `resume`, `offwork` and `onwork`, `task autorun on`, `task board` (except `--once`), `approve-command`, `approve-action`, `admin on` and `doctor --accept`, and reads them the way the shell does, so a quote, a variable or `xargs` does not hide them {src:.harness/policies/gate.json#L130-L136} {src:.harness/engine/modules/gate/harnesscmd.py#L1-L8}. It does not refuse `task allow --conn` or `task allow --links`: its pattern lists only the retired `task allow --env`, so only that command's own terminal check, with no code, stands in the way {src:.harness/engine/modules/task/tasklife.py#L541-L546} {src:.harness/engine/modules/task/commands.py#L357-L365}. Second, each approval command needs a person at their own terminal, with a keyboard and a screen, and a typed code; the board's Terminal window gives no keyboard input, so an approval cannot be typed there {src:.harness/engine/core/approval.py#L28-L58} {src:docs/04-reference.md#L9}. Third, on the board an approval goes through the buttons of the browser paired with the board server, which runs the same function with the code the person types {src:.harness/engine/modules/task/boardserve.py#L11-L16} {src:.harness/engine/modules/task/boardserve.py#L812-L823}; the agent cannot start the server (the gate refuses it), and its requests to the board's port are refused {src:.harness/engine/modules/task/boardserve.py#L1-L17} {src:.harness/engine/modules/gate/handler.py#L559-L564}.

The code the person types is the first six characters, in capitals, of a sha256 of what is approved: `PLAN.md` for the plan, `REQ.md` for the requirement, the write-back plan for a write-back {src:.harness/engine/core/approval.py#L17-L25}. The command checks the file again under the task's lock before it records the approval, so a plan changed while the person read it is refused {src:.harness/engine/modules/task/task.py#L458-L469}. The record (`plan.approved_sha256` and the requirement digest) is compared with the files before each edit-tool write to `DEV/`; a plan changed after the approval is not approved {src:.harness/engine/core/tasks.py#L154-L159}.

Two exceptions narrow this. The requirement's confirmation is the "User confirmed" line of `REQ.md`, a text line the agent can write {src:.harness/engine/modules/task/taskreview.py#L88-L110}. The approval records live in `.task/task.json`; a terminal command that names it is refused, but a script the agent runs is checked only for guardrail paths {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.

## Task: what happens when the requirement changes after the plan was approved

When what `REQ.md` asks for changes after the plan was approved, the approval lapses and, for the chat that holds the task, `DEV/` closes again to the edit tools. The plan's approval keeps the digest of the three sections of `REQ.md` that say what is wanted (What to do, What not to do, Done when); a change there makes the plan count as not approved {src:.harness/engine/core/tasks.py#L112-L159}. A change to the confirmation line, the sources, the open questions or the change record does not undo the approval {src:.harness/engine/core/tasks.py#L117-L121}.

What follows, in code: for the chat that holds the task, the gate refuses the agent's edit-tool writes to `DEV/` and tells it to check the plan, stop, and ask the person to confirm the requirement and approve the plan again {src:.harness/engine/modules/gate/handler.py#L80-L84} {src:.harness/engine/core/messages.en.json#L397}. `task approve-plan` alone is refused; the person confirms the changed requirement and approves the plan with one code (`--with-req`, or **Approve plan** on the task page) {src:.harness/engine/modules/task/task.py#L442-L467}. The dry run, the write-back approval and the write-back all need the plan approved as it is now {src:.harness/engine/modules/task/task.py#L872} {src:.harness/engine/modules/task/task.py#L950}. The work already in `DEV/` stays.

What is asked by text: the hook tells the agent at every prompt to change `REQ.md` first, with a line in its change record, whenever the person asks for something different {src:.harness/engine/core/messages.en.json#L108}. The code sees only the file: a change said in the chat and never written into `REQ.md` does not undo the approval.

In an open task of any kind, a changed requirement is written into `REQ.md` and the work goes on in the same task {src:.harness/engine/core/messages.en.json#L108}. After a write-back is done, the same goal goes on as a new round of the same task: `task open` moves the old `DEV/` and plan aside and asks for a new plan {src:.harness/engine/modules/task/task.py#L172-L181} {src:.harness/engine/modules/task/task.py#L232-L249}. When a closed task of a kind with no write-back (`rca`, `design`, `test`, `other`, `qa`) is opened again, the agent is told that it has no new round and that a changed requirement is a new task forked from it {src:.harness/engine/modules/task/tasklife.py#L189-L192} {src:.harness/engine/core/messages.en.json#L17}.

## Task: what the agent may write

For a chat that holds an open task, the edit tools write only inside that task's folder. The edit tools are the VS Code tools the harness lists as edit or create tools (`create_file`, `replace_string_in_file` and the like); a tool it does not list, such as a file-writing MCP server a team adds that no tool pack names, gets no path check {src:.harness/engine/adapters/tool_kinds.json#L1-L10} {src:.harness/engine/modules/gate/handler.py#L724-L734}. Inside the folder, `REQ/`, `REF/` and `INBOX/` are refused always and `DEV/` until the plan is approved {src:.harness/engine/modules/gate/handler.py#L64-L88}. For every chat, task or not, the edit tools are refused on files only the command line writes (`.task/`, `REVIEW/` and the others), inside any `.git` folder, and inside a target repository's working tree; they are refused on guardrail files too, except in a chat the person switched to admin mode, where only `.harness/runtime/**`, the policy's `admin_locked_paths` and the integrity-list folder (`~/.copilot-harness`, or `HARNESS_INTEGRITY_DIR`) stay closed {src:.harness/engine/modules/gate/handler.py#L38-L61} {src:.harness/engine/core/guardrails.py#L21-L61}.

The terminal is not confined to the task folder. A terminal command is refused when it names a guardrail file, a command-line-owned file, a `.git` path or a target repository folder as a write target, in full or by a relative path after a `cd` in the same command line (the terminal's real working folder is not used), or when a script it runs is found, as best effort, to write a guardrail file; other writes pass {src:.harness/engine/modules/gate/handler.py#L96-L118} {src:.harness/engine/modules/gate/terminal.py#L65-L117} {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}. A session that holds no task, or whose task is closed, is not kept to any folder by the edit-tool check {src:.harness/engine/modules/gate/handler.py#L67-L72}. The agent is told by text to work in a task and write only in its folder {src:.harness/engine/core/messages.en.json#L41} {src:.harness/engine/core/messages.en.json#L43}. The harness itself writes a target repository only through `task promote`, after the person's approval; a git command the person approves with `approve-command` can also write there, and a write the text checks cannot see (a script, a path made at run time) is not stopped {src:.harness/engine/modules/task/task.py#L898-L914} {src:.harness/engine/modules/gate/handler.py#L132-L141} {src:.harness/engine/modules/gate/terminal.py#L1-L5}.

## Task: what "waiting for you" means

"Waiting for you" on the board means the task's next move is the person's and its agent is not in the middle of a turn. The board picks one state per task from facts, first that holds: closed, paused, working, waiting, quiet (held by a session, nothing to do), no session {src:.harness/engine/modules/task/tasklife.py#L840-L853}. Working is read from the age of the session's hook log (five minutes by default) and running subagents {src:.harness/engine/modules/task/tasklife.py#L774-L803}.

The reason a task waits is told from facts, in order of how much it blocks {src:.harness/engine/modules/task/tasklife.py#L276-L336}:

- the agent asks a question and waits for the answer;
- a write-back stopped halfway and waits for **Recover the repository**;
- the plan waits for your approval;
- the write-back waits for your approval;
- the independent checks are used up and wait for your decision;
- the task was delivered and waits **to accept**;
- the requirement waits for your confirmation (`full` tier only);
- a call to an outside system waits for your approval;
- the agent handed you a run or a test to do;
- the files were written back and wait for your commit;
- you approved something and the agent has not been told yet;
- autorun stopped;
- the agent stopped: the Stop hook marks the task "waits for you" when the agent ends its turn, and your next message takes the mark away {src:.harness/engine/modules/task/handler.py#L398-L411} {src:.harness/engine/modules/task/handler.py#L210-L211}.
- you cancelled the agent's turn in VS Code: "cancelled, waits for you" {src:.harness/engine/core/messages.en.json#L131}.

The task page shows the reason at the top with a button for the answer; the file 21 Start a task and give it the requirement shows it on screen.

## Task: what is enforced by code, and what is not

Enforced by code:

- The state file is written by harness code; the edit tools are refused on it, and a terminal command that names it as a write target is refused (a script the agent runs is not checked for it) {src:.harness/policies/gate.json#L24-L33} {src:.harness/engine/modules/gate/handler.py#L100-L102}.
- For the chat that holds an open task, the edit tools stay inside its folder (a chat with no task is not bound); `REQ/`, `REF/`, `INBOX/` are refused, `DEV/` until the plan is approved {src:.harness/engine/modules/gate/handler.py#L64-L88}.
- The approvals of the plan and the write-back need a person and a typed code bound to a digest; the gate refuses the approval commands and `task close` on the agent's command line {src:.harness/engine/core/approval.py#L17-L58} {src:.harness/policies/gate.json#L130-L143}; `task close` itself has no person check {src:.harness/engine/modules/task/commands.py#L123-L133}.
- A plan cannot be approved while the "User confirmed" line of `REQ.md` is not filled in, when `REQ.md` has that line; the line is text the agent can write; a changed requirement or plan undoes the approval {src:.harness/engine/modules/task/task.py#L441-L449} {src:.harness/engine/core/tasks.py#L147-L159}.
- A write-back writes exactly the approved files to a new branch, uncommitted; a registered knowledge base gets one commit on its base branch instead {src:.harness/engine/modules/task/task.py#L898-L901} {src:.harness/engine/modules/task/promote_target.py#L1-L14}.
- The reviewer is called only in a task whose checks are on, and its passes are counted by code {src:.harness/engine/modules/task/handler.py#L226-L246}.
- A session holds one task at a time; a subagent or admin session cannot open one {src:.harness/engine/modules/task/tasklife.py#L126-L135}.

Asked of the model by text: open a task before producing files; read `TASK.md` first; write the requirement into `REQ.md` and change it first when the person changes their mind; leave the confirmation line alone; write the plan and stop; update `TASK.md` before stopping (the Stop hook reminds it once); deliver and never ask "close the task?" {src:.github/skills/harness-my-task/SKILL.md#L73-L111} {src:AGENTS.md#L46-L51}.

Left to a person: confirming the requirement, approving the plan and the write-back, giving more checks or waiving them, recovering a failed write-back, accepting or closing the task, committing the branch {src:.harness/policies/gate.json#L130-L136}.

## Task: common questions

**Q: What is a task, and how is it different from a chat session?** A task is a folder that holds one piece of work and its state; a session is one Copilot chat. A session holds one task at a time, and any later session can pick the task up from its files {src:.harness/engine/modules/task/task.py#L138-L216}.

**Q: Can the agent approve its own plan?** Not by the ways the harness gives it: the gate refuses the approval commands on the agent's command line, the commands need a person at their own terminal or the paired board's buttons, and the code is bound to the plan's sha256 {src:.harness/policies/gate.json#L130-L136} {src:.harness/engine/core/approval.py#L17-L58}. The requirement's confirmation line is the exception: it is text the agent can write.

**Q: I closed VS Code yesterday. Can a new chat continue the same task?** Yes. Say "go on with" and the task's name in a new chat; the agent runs `harness task open <task name>` and reads `TASK.md` first. Or press **Go on in a new chat** on the task page {src:.harness/engine/modules/task/tasklife.py#L155-L160} {src:.harness/engine/core/messages.en.json#L2139-L2140}.

**Q: Where is a task's record kept?** In `.workspace/sandbox/tasks/<task name>/` on your computer: the Markdown files, and the state in `.task/task.json` with its history; at close also the chat's rounds and a report in `.workspace/reports/tasks/<task name>/` {src:.harness/engine/core/tasks.py#L19-L36} {src:.harness/engine/modules/task/task.py#L384-L396}.

**Q: What happens if the requirement changes after I approved the plan?** When what `REQ.md` asks changes, the approval lapses, `DEV/` closes to the edit tools of the chat that holds the task, and you confirm the requirement and approve the plan again with one code {src:.harness/engine/core/tasks.py#L147-L159} {src:.harness/engine/modules/task/task.py#L442-L467}.

**Q: Can the agent write files outside its task folder?** Its VS Code edit tools cannot, while its chat holds an open task; a chat with no task is not bound, and a tool the harness does not list as an edit tool is not path-checked. Its terminal commands are not confined to the folder: only writes that name a guardrail file, a harness-owned file, `.git` or a target repository, in full or after a `cd` in the same line, are refused {src:.harness/engine/modules/gate/handler.py#L64-L118} {src:.harness/engine/modules/gate/terminal.py#L65-L117}. Guardrail files are open in a chat the person switched to admin mode.

**Q: Is the workflow controlled by a skill or by code?** The skill and the hook's text tell the agent the order; code holds the gates between stages {src:.harness/engine/modules/gate/handler.py#L80-L84} {src:.harness/engine/modules/task/task.py#L898-L901}.

**Q: Who closes a task?** The person, with **Accept and close** or **Close** on the board, or `task close` in their own terminal; the board closes a written-back development or knowledge base task once the agent stopped and nothing waits, without waiting for the commit. The gate refuses `task close` on the agent's command line, though the command itself has no person check {src:.harness/engine/modules/task/accept.py#L167-L218} {src:.harness/policies/gate.json#L137-L143}.

## Task: limits

- **The confirmation of the requirement is a text line.** The code reads the "User confirmed" line of `REQ.md`, which the agent's edit tools may write; a missing `REQ.md`, or one with no such line, counts as nothing to confirm, and the plan is then approved alone {src:.harness/engine/modules/task/taskreview.py#L88-L110} {src:.harness/engine/modules/task/task.py#L549-L565} {src:.harness/engine/modules/task/task.py#L443-L447}.
- **Admin mode opens the guardrails.** In a chat the person switched to admin mode, only `.harness/runtime/**`, the policy's `admin_locked_paths` and the integrity-list folder stay closed; the integrity check is skipped, and ending admin mode accepts the guardrail files as they are then. An admin chat cannot open a task {src:.harness/engine/core/guardrails.py#L21-L61} {src:.harness/engine/hook.py#L312-L323} {src:.harness/engine/integrity.py#L1-L5} {src:.harness/engine/modules/task/tasklife.py#L126-L135}.
- **The folder binds only a chat that holds an open task,** and only its recorded edit tools. Terminal writes are refused only when they name a protected path in full or after a `cd` in the same line, or when a script they run is found, as best effort, to write a guardrail file {src:.harness/engine/modules/gate/handler.py#L64-L118} {src:.harness/engine/modules/gate/terminal.py#L65-L117}.
- **The approval records are files.** They live in `.task/task.json`; a terminal command that names the file is refused, but a script the agent writes and runs is checked only for guardrail paths {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.
- **After the plan is approved, some outside calls need no further approval.** Calls the company's policy marks `task`, and writes on a connection opened with `task allow`, pass without an approval of the code {src:.harness/engine/modules/gate/handler.py#L266-L287}.
- **`task allow` is not refused by the gate.** The gate's person-only pattern lists only the retired `task allow --env`, so `task allow --conn` and `task allow --links` on the agent's command line meet only the command's own terminal check, with no code; a connection opened this way passes the agent's writes and runs with no further approval {src:.harness/policies/gate.json#L135} {src:.harness/engine/modules/task/tasklife.py#L541-L546} {src:.harness/engine/modules/gate/handler.py#L266-L287}.
- **Opening a task does not release an earlier session that still holds it.** `task open` changes only the opening session's state; an earlier session whose `active_task` still names the task keeps it {src:.harness/engine/modules/task/task.py#L152-L207}.
- **The Stop reminder checks that `TASK.md` was written, not that it is right** {src:.harness/engine/modules/task/handler.py#L335-L347}.
- **Working is read from the age of the hook log** (300 seconds): a tool call longer than that looks idle {src:.harness/engine/modules/task/tasklife.py#L774-L803}.

## Task: related files

- The whole harness, its parts and its safety guarantees: the file 00 Harness at a glance.
- How a person starts a task, gives the requirement documents and reads the board: the file 21 Start a task and give it the requirement.

Code map, under `.harness/engine/` {src:.harness/engine/modules/task/tasklife.py#L1-L13}:

- `core/tasks.py`: task paths, kinds, tiers, digests.
- `core/state.py`: session state, lock, subagent claim.
- `core/approval.py`: the typed approval.
- `modules/task/tasklife.py`: new, open, list, waiting, pause.
- `modules/task/task.py`: attach, approvals, fetch, promote, close.
- `modules/task/accept.py`: deliver, accept, the board's close of written-back tasks.
- `modules/task/taskstages.py`: the stages.
- `modules/task/handler.py`: the task hook (prompt context, Stop marks, subagent calls).
- `modules/gate/handler.py`: the write scope.
- `modules/task/boardserve.py`: the board and its buttons.
- `modules/task/promote_target.py`: the write-back to repositories.
