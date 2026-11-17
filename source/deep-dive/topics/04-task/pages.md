---
title: Task — design and lifecycle
number: 04
short: Task
series: Harness Deep Dive
file: 04 Task — design and lifecycle
harness_tag: 1.7.41
---
=== split
part: pattern
fig: fig/idea.svg
caption: One piece of work, two chats days apart, and the task both read and write.

A piece of work outlives the chats that do it, so the harness gives it its own home: the task. A chat in VS Code is compacted as its context fills {src:.harness/policies/task.json#L3}; its record is Copilot's file; the harness saves the chat's rounds (prompts and replies) into the task at close {src:.harness/engine/modules/task/chatrounds.py#L1-L10}. A chat's confirmation cannot hold an approval: it can be allowed for the whole session {src:.harness/engine/core/approval.py#L1-L8}.

A task is a folder in the workspace: a handover note, the requirement, the plan, the results and a state file {src:.harness/engine/core/tasks.py#L1-L37}. Any later chat opens it and goes on; it stays open until the person accepts it {src:.harness/engine/modules/task/accept.py#L1-L11}.

=== figure
part: pattern
fig: fig/pattern.svg
caption: Above: the parts and who calls whom (dashed: control, solid: data). Below: the lifecycle of a task at a glance.

Five parts and the person do the work. The task hook tells the agent at every prompt where its task stands {src:.harness/engine/modules/task/handler.py#L157-L172}; for a session that holds a task, the gate keeps the edit tools in its folder {src:.harness/engine/modules/gate/handler.py#L64-L88}. The edit tools cannot write the task's state; a terminal command that writes it by name is refused {src:.harness/policies/gate.json#L24-L86} {src:.harness/engine/modules/gate/handler.py#L100-L102}. So are the person-only commands {src:.harness/policies/gate.json#L130-L143}.

=== split
part: pattern
fig: fig/guarantee.svg
caption: How an approval of the plan is given, recorded and enforced, and what undoes it.

The guarantee that matters most: code is written back to a repository only in a version the person approved {src:.harness/engine/modules/task/task.py#L898-L901}. The person, at a keyboard or on the board page paired to it, types a code computed from the files, so no click in a chat can approve {src:.harness/engine/core/approval.py#L1-L58}. The commands re-check the files before recording the approval {src:.harness/engine/modules/task/task.py#L458-L469}; for the session that holds the task, the gate compares that record with the files before each edit-tool write to the code folder {src:.harness/engine/modules/gate/handler.py#L64-L88} {src:.harness/engine/core/tasks.py#L117-L159}.

A change to the plan, or to what the requirement asks, makes the approval stale {src:.harness/engine/core/tasks.py#L117-L159}. The gate refuses the approval commands to the agent {src:.harness/policies/gate.json#L130-L143}.

=== figure
part: depth
fig: fig/arch.svg
caption: The parts in code: every component with its path. Solid arrows carry data, dashed arrows carry control. Opens up: the parts.

In code, each part has its own files, and the task folder is the only place the work lives. The commands write `task.json` under a lock {src:.harness/engine/modules/task/task.py#L80-L96}, and so do the hook and the board for their own marks {src:.harness/engine/modules/task/tasklife.py#L458-L470}. The hook engine runs each module on the events it subscribes to {src:.harness/engine/hook.py#L1-L15}; the board calls the same functions as the terminal {src:.harness/engine/modules/task/boardserve.py#L140-L153}.

=== split
part: depth
fig: fig/task-vs-session.svg
caption: What lives with the session and what lives with the task, and the pointer each keeps to the other. Opens up: agent and task.

A session and a task point at each other, the session's `active_task` at the task and the task's `session_id` at its latest session, so either can end or change without the other. `attach` sets the session's `active_task`, and a task the session leaves stays open {src:.harness/engine/modules/task/task.py#L138-L216}. The task records every pick-up in `sessions[]`, so its report can add up time across chats {src:.harness/engine/modules/task/task.py#L182-L184}. A subagent's session inherits its parent's task {src:.harness/engine/core/state.py#L252-L303}; a subagent or an admin session cannot open one {src:.harness/engine/modules/task/tasklife.py#L126-L135}. Tests: another session picks a task up; the gate follows the task a session holds {src:.harness/tests/test_tasklife.py#L151-L215}.

=== split
part: depth
fig: fig/task-files.svg
caption: The files of a task folder by tier, what each holds, and who may write it. Opens up: the task.

A task's memory is a set of files fixed by tier, each with one main writer. `task new` makes the tier's files from templates {src:.harness/engine/modules/task/tasklife.py#L39-L123}. `TASK.md` is the handover a new session reads first {src:.harness/contracts/templates/task/en/TASK.md}. For a session that holds the task, the gate refuses the edit tools `REQ/`, `REF/` and `INBOX/` always, and `DEV/` until the plan is approved {src:.harness/engine/modules/gate/handler.py#L64-L88}; it refuses every path the harness owns to any session {src:.harness/policies/gate.json#L24-L33}.

`task list` reads `task.json`, not the Markdown: a status typed into `TASK.md` changes nothing {src:.harness/tests/test_tasklife.py#L592-L596}. The hook keeps no prompt while the task runs {src:.harness/tests/test_tasklife.py#L618-L625}; at close the chat's rounds are copied in {src:.harness/engine/modules/task/task.py#L384-L389}.

=== split
part: depth
fig: fig/pickup.svg
caption: A new chat picks up an existing task, then works until it stops. Opens up: any later chat may open it again.

A new session resumes a task by name, from the files alone. A session without a task is told which tasks are open {src:.harness/engine/modules/task/handler.py#L124-L172}. The agent runs `task open`; `attach` refuses an unknown session, a subagent, admin mode and a promote stopped halfway {src:.harness/engine/modules/task/task.py#L138-L181}, and its answer names `TASK.md` as the file to read first {src:.harness/engine/modules/task/tasklife.py#L155-L160}.

Each later prompt carries the kind, round, next step and write scope {src:.harness/engine/modules/task/handler.py#L88-L121}. At Stop, a prompt that wrote task files but not `TASK.md` is sent back once, as are unpassed checks and a few other loose ends {src:.harness/engine/modules/task/handler.py#L454-L475}; otherwise the task is marked as waiting {src:.harness/engine/modules/task/handler.py#L398-L411}.

=== figure
part: depth
fig: fig/lifecycle.svg
caption: The two state machines kept in task.json; each arrow names the event, then the code that fires it. Opens up: the lifecycle.

A task's life is two stored values: `status`, open or closed, and for the write-back (`task promote`), `promote.state` {src:.harness/engine/modules/task/task.py#L138-L216}. The agent opens tasks and runs a write-back; only a person approves or recovers one {src:.harness/engine/modules/task/task.py#L868-L1017}. The person closes a task, or the board does once a write-back is done and nothing waits {src:.harness/engine/modules/task/accept.py#L167-L218}.

=== split
part: depth
fig: fig/gates.svg
caption: Each move, who may make it, and what is checked first. Opens up: the guarantee.

Every move re-checks, when it runs, the facts it depends on. The approvals of the requirement, the plan and the write-back name the files, ask for the first six characters of the sha256 of what is approved, and check again under the task's lock that nothing changed {src:.harness/engine/core/approval.py#L17-L58} {src:.harness/engine/modules/task/task.py#L458-L469}. The plan approval keeps two digests, of `PLAN.md` and of the three sections of `REQ.md` that say what is asked; a change to either closes `DEV/` again {src:.harness/engine/core/tasks.py#L117-L159}.

The gate refuses the agent the person-only commands and `task close` {src:.harness/policies/gate.json#L130-L143}. The board runs the same functions with the code typed on the page {src:.harness/engine/modules/task/boardserve.py#L1-L17}.

=== split
part: depth
fig: fig/derived.svg
caption: Above: how the one board state of a task is chosen. Below: the stages of each kind and the fact that ends each. Opens up: where the task stands.

What the board shows is derived each time and never stored. `state_of` takes the first test that holds {src:.harness/engine/modules/task/tasklife.py#L840-L853}; working is read from the session's `active_task`, the age of its hook log and running subagents {src:.harness/engine/modules/task/tasklife.py#L774-L803}. The reasons to wait are ordered by how much they block {src:.harness/engine/modules/task/tasklife.py#L276-L336}. `unheld` means the session that last opened the task no longer holds it.

The ribbon is computed from files and state, so a task whose requirement changed, or that starts a new round, falls back to the right step by itself {src:.harness/engine/modules/task/taskstages.py#L1-L15}.

=== split
part: depth
fig: fig/decisions.svg
caption: Designs the git history replaced, by release: the earlier design, then what replaced it.

Each of these designs was replaced, five of them after a release, and the code still shows the seams. A session state from before 1.1.0 is upgraded by deleting the Levels' fields {src:.harness/engine/core/state.py#L110-L119}.

Alternatives taken on purpose: approvals bound to a digest instead of a dialog {src:.harness/engine/core/approval.py#L1-L8}; stages derived instead of stored {src:.harness/engine/modules/task/taskstages.py#L1-L4}; a closed task reopened in place; for a kind with no write-back rounds, a changed requirement is pointed to `task fork` {src:.harness/engine/modules/task/tasklife.py#L189-L192}. The cost of state in files: every reader parses `task.json`, and writers queue on a lock directory {src:.harness/engine/core/state.py#L123-L176}.

=== text
part: depth

**Limits.**

- Stop checks that `TASK.md` was written, not that it is right {src:.harness/engine/modules/task/handler.py#L335-L347}.
- `attach` trusts the given session id if its state file exists, and does not release an earlier session holding the task {src:.harness/engine/modules/task/task.py#L148-L207}.
- Edit tools are confined only in a session holding an open task. Terminal writes are refused by named path, or when a script they run writes a guardrail file {src:.harness/engine/modules/gate/handler.py#L64-L146}.
- After plan approval, outside calls marked `task`, and writes on a connection opened by `task allow`, need no approval of the code {src:.harness/engine/modules/gate/handler.py#L266-L291}.
- The `REQ.md` confirmation is a text line the agent can write; without it, the plan is approved alone {src:.harness/engine/modules/task/taskreview.py#L88-L110}.
- Working is read from the hook log's age (300 s): a longer tool call looks idle {src:.harness/engine/modules/task/tasklife.py#L774-L803}.

=== text
part: depth

**Code map**, under `.harness/engine/`.

- `core/tasks.py`: task paths, kinds, tiers, digests
- `core/state.py`: session state, lock, subagent claim
- `core/approval.py`: the typed approval
- `modules/task/tasklife.py`: new, open, list, waiting, pause
- `modules/task/task.py`: attach, approvals, fetch, promote, close
- `modules/task/accept.py`: deliver, accept, sweep
- `modules/task/taskstages.py`: stage ribbon
- `modules/task/handler.py`: prompt context, Stop marks
- `modules/gate/handler.py`: write scope
- `modules/task/boardserve.py`: the board and its actions
- `modules/task/promote_target.py`: write-back to repositories
- `modules/task/commands.py`: the task commands
- `../contracts/templates/task/<lang>/`: templates
- `../policies/task.json`, `../policies/gate.json`: policies
