---
title: Independent checks
subject: Independent checks
layer: concept
file: 17 Independent checks
harness_tag: 1.8.3
course: The book · 2.3 Use subagents sparingly | https://smarshu.com/book/read/2-3-subagents.html
course: The book · 5.4 Let the agent check its own work | https://smarshu.com/book/read/5-4-self-checks.html
course: The book · 5.5 Make a pass count | https://smarshu.com/book/read/5-5-counted-checks.html
course: The book · 5.6 Can a model check a model? | https://smarshu.com/book/read/5-6-model-checks-model.html
---
## Independent checks: what they are and what problem they solve

An independent check is a review of a task's work by the `reviewer`, a separate subagent with a context of its own, which sees only the requirement, the work and the diff, never the reasoning of the agent that wrote the work {src:.github/agents/reviewer.agent.md#L1-L13}. It answers two problems: an agent reading its own work reads what it meant, not what it wrote, so it tends to pass its own mistakes; and "I had it checked" in a chat proves nothing. So a second agent checks, and code counts the passes {src:docs/05-design.md#L111-L129}. Nothing is checked by default. The person sets a number n, and the task's work must then pass n checks in a row, each by a new reviewer, on the work as it is at the end, before the dry run of the write-back is let through {src:.harness/engine/modules/task/taskreview.py#L1-L22}.

## Independent checks: how they are switched on, and who sets the number

Only the person sets n: with `[review]=n` in a prompt of the task, or with the number under **Independent review** on the task page of the board (`harness task review set`). The hook reads the mark only in the words the person typed, not in the text a slash command's skill brings in (since 1.6.109, after a skill's example `[review]=1` switched checks on by itself); a mark typed in a chat with no task goes to the task that prompt opens {src:.harness/engine/modules/task/handler.py#L77-L113} {src:docs/07-release-notes.md#L852} {src:.harness/engine/modules/task/task.py#L191-L200}. n runs from 0 (off) to 5; a larger mark is cut to 5 {src:.harness/policies/task.json#L9-L13}. The agent cannot set it: the gate refuses `task review set` on the agent's command line, and the command checks for a person {src:.harness/policies/gate.json#L131-L137} {src:.harness/engine/modules/task/taskreview.py#L476-L568}.

## Independent checks: how one check runs, step by step

1. **Start.** When the work is written, the agent runs `harness task review start`. It is refused, with no check used, when checks are off, when there is nothing to check yet (for `dev` and `kb`, nothing under `DEV/`), when a run the person must do is not back, when the passes are already enough, or when the checks are used up. Otherwise it saves a snapshot of the work, writes `CHANGES.diff` for code fetched from a target repository, writes the review package `REVIEW/round-NNN/package.md` and opens the round {src:.harness/engine/modules/task/taskreview.py#L359-L436}.
2. **Call.** The agent calls the subagent `reviewer`. In a chat that holds a task, the task hook lets a subagent call through only for the reviewer of a task whose checks are on and whose round is open (besides the worker in autorun and the mapper after the person's `/generic-mapreduce`). When the reviewer starts, the hook gives it the path of its package {src:.harness/engine/modules/task/handler.py#L278-L344}.
3. **Answer.** When the reviewer's call ends, the hook takes its answer as it came back, writes it to `REVIEW/round-NNN/verdict.md`, reads the verdict, has a script check the findings of a FAIL, and closes the round {src:.harness/engine/modules/task/handler.py#L391-L420}.
4. **Next.** `harness task review status` says what comes next: fix and start again after a FAIL, start again for one more pass, go on, or stop at the limit. When the agent tries to end its turn with too few passes, the Stop hook sends it back once per prompt {src:.harness/engine/modules/task/taskreview.py#L1-L22} {src:.harness/engine/modules/task/handler.py#L391-L420}.

![The loop of one independent check: the person sets n, the agent starts a check, the reviewer answers, a hook saves the verdict, code counts the passes, and the work goes to the write-back or the person decides at the limit](fig/checks-loop.svg)

## Independent checks: what the review package holds

The review package is a Markdown file the `harness` command line writes for each check, and the reviewer reads it first {src:.harness/engine/modules/task/taskreview.py#L283-L317}. It says which check this is (from the second on: report only what affects correctness); where the requirement is (`REQ.md`, `PLAN.md`, `REQ/`), and that an empty "User confirmed" line is not a finding; how to judge numbered "Done when" items (`[T…]` on the task files, `[R…]` only by the person's saved runs, `[A…]` not at all); where `CHANGES.diff` is; the files to check, each with its size and the first 16 characters of its sha256 (the full sha256 is in the snapshot's manifest, not in the package); the saved runs the work cites, which the reviewer may run again as reads; after a FAIL, that verdict and the dropped findings; and how to answer {src:.harness/engine/core/messages.en.json#L45-L79}.

The files to check are the task's result files: the whole task folder except the harness's own folders, the person's material (`REQ/`, `REF/`, `INBOX/`) and the files that only say where the work stands (`TASK.md`, `TODO.md`, `LOG.md`, `QUESTIONS.md`, `COMMIT-MESSAGE.md`); `REQ.md` and `PLAN.md` are in {src:.harness/engine/modules/task/tasksnap.py#L28-L90}. The conversation and the agent's reasoning are not in the package. The agent is told its call message is one sentence, `Check the review package <path>`, with no reasoning and no conclusion {src:.github/skills/harness-my-task/SKILL.md#L115-L120}.

## Independent checks: what the reviewer may and may not do

The reviewer's agent file lists three tools, `read`, `search` and `execute` (the terminal), lists no subagents (`agents: []`) and keeps it out of the agent list {src:.github/agents/reviewer.agent.md#L1-L13}. That list names no edit tool, but nothing in it forbids a change either: `execute` is the terminal, so it is the text of the file that tells the reviewer not to change anything; only the gate's general terminal rules and its rule for `REVIEW/`, which apply to every session, hold in code. The file tells it: every check is a full check; first confirm whether the last findings are fixed; read the project's rules and knowledge base itself; confirm by command what a command can confirm, with read-only commands only; do not run a target repository's code. It must not change or create a file, write how to fix a finding (the next check would then check its own fix), redesign, call a subagent, or read `LOG.md` and `TODO.md` {src:.github/agents/reviewer.agent.md#L27-L57}.

The gate holds the reviewer at two places. On outside systems it may only read: a tool-pack call that needs the person's leave, and a tool pack's MCP tool that writes, are refused to any subagent, with nothing to approve {src:.harness/engine/modules/gate/handler.py#L326-L413}. And `REVIEW/` is a path only the command line writes, so an edit tool or a terminal command that names it is refused, for the reviewer and the agent alike {src:.harness/policies/gate.json#L24-L34}.

## Independent checks: the verdict, and the findings a script drops

The first line of the reviewer's answer must be `VERDICT: PASS` or `VERDICT: FAIL`; each finding is one line, `- <file>:<line> <what does not match> | basis: <where the requirement or rule says so>`; a PASS gives one line of evidence per requirement item; 20 lines at most {src:.github/agents/reviewer.agent.md#L59-L77}. Code looks for the verdict in the first three non-empty lines; an answer without it is recorded as `unknown`, which uses a check and is not a pass {src:.harness/engine/modules/task/taskreview.py#L69-L85}.

After a FAIL, a script drops each finding that names no `file:line`, whose file is found nowhere (the harness folder, the task folder, the target repositories), whose line is past the end of the file, or whose basis names only `[A…]` items. A FAIL with no finding left is invalid: the check is given back, at most 2 times in a round of the task (`review.free_invalid`), and the next package says why; after that it counts as a FAIL {src:.harness/engine/modules/task/reviewcheck.py#L93-L186} {src:.harness/engine/modules/task/taskreview.py#L359-L436}. The script checks the form only, never whether a finding is right {src:.harness/engine/modules/task/taskreview.py#L1-L22}. A check the person judges wrong is taken out of the count, as a check used and as a FAIL, with `task review dismiss` or **Dismiss check** on the board {src:.harness/engine/modules/task/taskreview.py#L476-L568}.

## Independent checks: how passes are counted, the limit, and the write-back

Passes are never stored as a number. Each time, code counts back from the latest check the PASSes in a row whose recorded digest equals the digest of the work now, skipping checks given back or dismissed {src:.harness/engine/modules/task/taskreview.py#L131-L167}. The digest is one sha256 over every result file, so any change to the work, to `REQ.md` or to `PLAN.md` sets the count to 0, and nobody has to reset it; `TASK.md`, `TODO.md`, `LOG.md`, `QUESTIONS.md`, `COMMIT-MESSAGE.md` and what a write-back puts into `DEV/` do not count {src:.harness/engine/modules/task/tasksnap.py#L28-L90}. A task opened again after a write-back starts a new round, and the count starts again.

The limit is n + 2 checks in a round of the task (`review.extra_checks`), plus what the person gives {src:.harness/policies/task.json#L9-L13}. At the limit, with too few passes, `task review start` is refused and tells the agent to stop and show the person where the last findings are. The person then chooses: `task review extend` for more checks; `task review waive` to let this version through without the passes, a waiver that ends when the work changes; or `task review dismiss` for a check judged wrong. Each asks for a typed code, in the person's terminal or behind the board's buttons (the board's extend gives 2) {src:.harness/engine/modules/task/taskreview.py#L476-L568} {src:.harness/engine/modules/task/boardserve.py#L151-L153}.

`task promote --dry-run` is refused while checks are on and the passes are too few, unless the person waived them. The write-back itself needs the person's approval of the dry run's plan digest, which covers every file, so work changed after the dry run needs a new dry run, and with it new passes {src:.harness/engine/modules/task/task.py#L921-L944}. A task written back or closed shows its checks as they stood on the last version checked; the gate always counts on the files as they are {src:.harness/engine/modules/task/taskreview.py#L240-L273}.

## Independent checks: which model the reviewer runs on

The reviewer's model is fixed in its agent file: Claude Sonnet 5.5 first, then Claude Haiku 5.5, then Claude Haiku 4.5 {src:.github/agents/reviewer.agent.md#L1-L13}. Copilot falls back down the list in order; `agents.json` lets the reviewer fall back across model series, and `harness doctor` checks that the other agents stay in one {src:docs/03-configure.md#L316-L323}. No rule makes the reviewer's model differ from the main agent's: `different_series` is empty, and the person picks the main model {src:.harness/policies/agents.json#L1-L20}. The docs warn that the platform may not run a subagent whose model is a class above the main model; a check that does not run gives no PASS.

## Independent checks: in autorun

Autorun cannot be switched on without checks: `task autorun on` needs n of at least 1 {src:.harness/engine/modules/task/autorun.py#L1-L23}. During a run, code works out the agent's next job in a fixed order: an open step of `TODO.md`, the open questions (asked together), the parked steps, the independent check, the write-back plan {src:.harness/engine/modules/task/autorun.py#L310-L368}. So in autorun the check comes after the questions are answered and before the dry run; `QUESTIONS.md` is outside the digest, so answering does not undo a pass. The skill tells the agent to send the findings to the worker and never fix them itself {src:.github/skills/harness-autorun/SKILL.md#L63-L70}. Checks used up without the passes end the run with the reason `review`; a run is done only when the checks passed and the write-back plan is made, and the write-back still waits for the person {src:.harness/engine/modules/task/autorun.py#L1-L23}. The file 20 Autorun has the rest.

## Independent checks: how they differ from self-checks

A self-check is the author checking its own work inside its loop: running a test, a build or a linter and reading the result. In the harness it is asked by text, for example of the worker of autorun, which runs the check its step names {src:.github/agents/worker.agent.md#L25}; no code counts it. An independent check is made by another agent that has not seen the reasoning, and code counts it. The data pipeline repositories the harness is built for cannot be run locally, so the reviewer checks by reading the work and the diff, not by running tests {src:docs/05-design.md#L202}.

## Independent checks: what is enforced by code, and what is only an instruction

**Code:** only the person sets n, extends, waives or dismisses; the reviewer is let through only with checks on and a round open; the package and the verdict are written by the command line and the hook, where the agent's edit tools cannot reach; code reads the verdict, drops findings with no real place, counts the passes, holds the limit, refuses the dry run without the passes, and in autorun requires checks {src:.harness/engine/modules/task/handler.py#L278-L344} {src:.harness/engine/modules/task/taskreview.py#L359-L436} {src:.harness/policies/gate.json#L131-L137}. The reviewer's tool list, without edit tools, is applied by Copilot, not by the harness, from `.github/agents/reviewer.agent.md`, a file the gate does not guard: a terminal write, or the edit tools of a chat with no task, can change it {src:.harness/policies/gate.json#L4-L19}.

**Text only:** that the call message holds only the package path (the hook adds the path but does not read the message); that the reviewer runs only read-only commands and writes no file through the terminal; that it does a full check, gives no fix, leaves `LOG.md` and `TODO.md` unread, and from the second check reports only what affects correctness; that the agent fixes the findings, checks after its last change, and stops at the limit {src:.github/skills/harness-my-task/SKILL.md#L115-L120} {src:.github/agents/reviewer.agent.md#L27-L57}.

## Independent checks: who decides what

The **person** sets the number of checks, gives more, waives them or dismisses one, and approves the write-back {src:AGENTS.md#L52-L53}. **Code** decides whether a check may start and the reviewer be called, what is in the package, what the verdict is, which findings stand, how many passes count, and whether the dry run may run. The **reviewer**, a model, judges whether the work meets the requirement. The **agent** chooses when to start a check and how to fix what was found.

## Independent checks: why they are built this way, and what was tried before

**One builder and one checker, not a team.** Version 1.0 had three levels. Its heavy level, L3, ran three role agents in a request folder: an orchestrator that planned and handed out work, a builder that changed files, a reviewer that checked them; the middle level had a separate verifier, switched on with `[verify]` {src:docs/07-release-notes.md#L3576-L3717}. On tasks with a clear requirement the three-role team was no better than one agent, at about 4.5 times the usage and 6 times the time {src:docs/05-design.md#L57-L65}. Version 1.1 removed the levels, the L3 flow, the orchestrator and builder agents and the verifier, and kept one role: the reviewer, switched on with `[review]=n` and counted by code {src:docs/07-release-notes.md#L3576-L3717}. The reviewer stayed because an independent point of view is one of the few things a second agent buys that one agent cannot get alone; that was reasoned, not measured on its own (the book's chapter "What I cut, and what the data says"). No dispatching agent was kept: the agent that holds the task moves it forward {src:docs/05-design.md#L111-L129}.

**Choices made on purpose.** The reviewer gets no author reasoning, because it would follow the same path and lose its independence. Agents do not message or debate each other: the reviewer's input is a file and its output a file a hook writes. The person, not the agent or the kind of task, switches checks on, because every check costs money. There is a limit, because a reviewer may keep finding fault {src:docs/05-design.md#L111-L129}. The 1.0 rule that builder and reviewer use different model series left with the builder; since the person picks the main model, the reviewer is not forced to differ {src:.harness/policies/agents.json#L1-L20}.

**What use added.** 1.5.31 brought the script that drops findings, the numbered "Done when" items and `dismiss`, after a reviewer failed a change twice because nobody had run the job yet; 1.5.29 stopped a write-back's own files from undoing the passes; 1.7.9 had the reviewer run the cited reads again {src:docs/07-release-notes.md#L2453-L2490}.

## Independent checks: where in the source

Under `.harness/engine/modules/task/` {src:.harness/engine/modules/task/taskreview.py#L1-L22}: `taskreview.py` (start, record, count, limit, the person's commands, the dry-run gate); `reviewcheck.py` (the script that drops findings); `tasksnap.py` (result files, digest); `handler.py` (the mark, the subagent rule, the verdict, the Stop reminder); `autorun.py`. Also `.github/agents/reviewer.agent.md`, the policies `task.json`, `agents.json`, `gate.json`, and the tests `test_taskreview.py`, `test_reviewcheck.py`.

## Independent checks: common questions

**Q: Can the agent switch checks on or off, or waive them?** No: the gate refuses `task review set`, `extend`, `waive` and `dismiss` on the agent's command line {src:.harness/policies/gate.json#L131-L137}.

**Q: Can the agent make the reviewer pass its work?** Its edit tools cannot write the package, the verdict file or the count; changing the work resets the count {src:.harness/policies/gate.json#L24-L34}. It could still put its reasoning into the call message, which only text forbids, or change the reviewer's agent file from the terminal, which no guardrail stops.

**Q: Why passes in a row, each by a new reviewer?** One PASS may be luck; two reviewers have been seen to give different verdicts on the same work. The docs advise n = 1 day to day and 2 for an important change {src:docs/02-features.md#L91-L106}.

**Q: What does a check cost?** One reviewer subagent call per check, up to n + 2 in a round plus what the person gives; each call is a model run on the reviewer's model {src:.harness/policies/task.json#L9-L13}.

**Q: Do checks hold back an analysis or a design task?** They run on any kind with something to check, but only the write-back's dry run is gated: `task deliver` does not look at the passes, and the Stop hook reminds the agent once per prompt {src:.harness/engine/modules/task/accept.py#L1-L11}.

**Q: What if the reviewer is wrong?** A FAIL pointing at nothing real is given back; one the person judges wrong is dismissed; a wrong PASS is caught only by more passes in a row and by the person reading the write-back {src:.harness/engine/modules/task/taskreview.py#L1-L22}.

## Independent checks: limits

- **Same model family, shared blind spots.** The reviewer is a Claude model, as the main agent often is, and nothing makes them differ; a PASS means a second reader found nothing, not that the work is right. Checks lower the risk and do not remove it, and how often the reviewer fails good work or passes bad work has not been measured {src:.harness/policies/agents.json#L1-L20} {src:docs/02-features.md#L91-L106}.
- **The script checks the form, not the judgment,** and only for a FAIL; a PASS's evidence lines are not checked {src:.harness/engine/modules/task/taskreview.py#L359-L436}.
- **The call message is not read by code,** and only text keeps the reviewer's terminal to read-only commands {src:.github/agents/reviewer.agent.md#L27-L57}.
- **Only the dry run of a write-back is gated.** For a task whose result stays in the folder, checks are a reminder {src:.harness/engine/modules/task/handler.py#L391-L420}.
- **The reviewer's agent file is not guarded.** Its tools, model list and instructions are not a guardrail path, not in the integrity list and not in the script check, so a terminal write can change them; only the person's review of the change would notice {src:.harness/engine/integrity.py#L23-L26} {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.
- **The record is files,** and a script the agent writes and runs can change what the gate does not see {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.
- **An answer without a verdict line uses a check,** and a reviewer whose model is a class above the main model may not run at all {src:.harness/engine/modules/task/taskreview.py#L69-L85} {src:docs/03-configure.md#L316-L323}.

## Independent checks: related files

- The typed codes behind extend, waive and dismiss, and every other approval: the file 14 Plans and approvals. The dry run and the write-back: the file 16 Write-back. Autorun: the file 20 Autorun. The task folder and its rounds: the file 11 Task. The idea of a second checker: the file 41 Ideas behind the harness.
- The code-level detail (the review state in `task.json`, the order of checks of the subagent rule, the package and its quotes, which hook saves the verdict, how passes are counted): the file 17b Independent checks internals.
- To do it step by step (switch checks on, read a verdict, extend, waive or dismiss), see the harness tutorial "4 Independent checks" in `3 Courses/Harness tutorials/` {src:AGENTS.md#L52-L53}.
