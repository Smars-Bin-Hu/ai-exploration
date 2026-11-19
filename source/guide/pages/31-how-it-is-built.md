---
title: How it is built
subject: Architecture
layer: concept
file: 31 How it is built
harness_tag: 1.8.3
course: The book · 0.2 A minimal harness in 30 minutes | https://smarshu.com/book/read/0-2-minimal-harness.html
course: The book · 2.2 Hooks, the point every call passes through | https://smarshu.com/book/read/2-2-hooks.html
course: The book · 4.4 Build the enforcement layer like software | https://smarshu.com/book/read/4-4-enforcement-design.html
---
## Architecture: what the harness is made of

The harness is a set of files Copilot already reads, plus Python code that VS Code runs at every hook event of a Copilot chat. Text (`AGENTS.md`, instructions, skills, agent files) tells the model how to work; code (the hooks and the `harness` command) enforces what must hold; JSON policies hold the numbers and lists the code reads; the work and its state are files on the person's computer {src:docs/05-design.md#L28-L53}. There is no harness server: the board is a local web server on 127.0.0.1, and the model runs in GitHub Copilot's service {src:.harness/engine/modules/task/boardserve.py#L1-L17}. The file 32 Code map lists every file, and the file 33 Test map and evals every test.

## Architecture: the parts, who provides each, and the layers

![The harness architecture: the person and the text layer on the left, the Copilot agent and the hook path through launch.py, hook.py, the modules and the core library, then the harness command and the board server, and on the right the policies, session state, task folders and outside folders](fig/architecture.svg)

Who provides each part {src:AGENTS.md#L7-L15} {src:docs/05-design.md#L11-L26}: **GitHub** the Copilot agent in VS Code, its tools and the model (only chats whose session target is Copilot are supported; Local sessions and `copilot -p` are not {src:docs/05-design.md#L155-L161}); **the harness** the hook configuration, the engine under `.harness/engine/`, the `harness` command, the board, the default policies, the task templates, four custom agents and 34 skills {src:.harness/registry.json#L9-L23}; **the team** the knowledge base (`knowledge-base/` ships empty) with its domain skills, the target repositories, tool packs, connections and override files.

The layers, from what changes most to least: text (read by the model, which may ignore it); policies and templates (read by code); the enforcing code (hook path and command line); the adapter (the only code that knows Copilot's payloads); and the evidence (tests, eval scenarios, logs, `doctor`) {src:docs/05-design.md#L28-L53}.

## Architecture: how one tool call flows from the Copilot agent to an answer

Every hook event of a Copilot chat runs one command, and one Python process answers it:

1. **VS Code runs the hook.** `.github/hooks/harness.json` registers one command, `python3 .harness/engine/launch.py` (`python` on Windows), for nine events: `SessionStart`, `UserPromptSubmit`, `userPromptTransformed`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `SubagentStart`, `SubagentStop`, `Stop`, each with a 30-second limit; `.vscode/settings.json` turns hooks, `AGENTS.md` and instruction files on {src:.github/hooks/harness.json#L1-L113} {src:.vscode/settings.json#L1-L5}.
2. **`launch.py` loads `hook.py`**, and answers in its place when it cannot be loaded {src:.harness/engine/launch.py#L2-L5}.
3. **The integrity check.** For a tool call, a prompt or a session start, `hook.py` first checks that the guardrail files are as the person accepted them {src:.harness/engine/hook.py#L312-L326}.
4. **The adapter** turns the payload into one `HookEvent` (event, session, tool name and kind, paths, command, prompt, subagent); `tool_kinds.json` sorts tool names into kinds, and an unknown tool is `other` {src:.harness/engine/core/events.py#L27-L93}.
5. **The session state** `.harness/runtime/state/vscode/<session>.json` is locked and read; the new session of a subagent inherits the task its parent holds {src:.harness/engine/hook.py#L90-L117}.
6. **The registry** `.harness/registry.json` names the modules that subscribe to the event and are switched on, listed in registry order by `modules_for`, only for the events in the module's `events` list (a `PreToolUse` call gets `task`, then `gate`; `evalcheck` has an empty list, so the hook never calls it) {src:.harness/engine/core/registry.py#L128-L134}; `run_modules` in `hook.py` then calls each one in that order {src:.harness/engine/hook.py#L58-L87}.
7. **The modules decide; the answers are merged.** Each returns allow, ask or deny, text for the model, a Stop block, or nothing; deny wins over ask over allow, texts are joined, one block blocks {src:.harness/engine/core/events.py#L27-L93}.
8. **The breaker and the state.** The same refusal a third time in one prompt has its reason replaced by an instruction to stop; the state is written back {src:.harness/engine/core/breaker.py#L1-L5}.
9. **The answer and the record.** The adapter writes the JSON Copilot reads (`permissionDecision`, `additionalContext`); Copilot runs the call, asks the person, or refuses it. The observe module writes one line to `.harness/runtime/logs/vscode/<session>.jsonl`; a failure of the log never changes the answer {src:.harness/engine/hook.py#L118-L164}.

A call record keeps the event, the tool, the decision, who decided and why. The paths and command are kept only for a call refused or sent to the person; a call that went through keeps a short hash of its terminal command, the paths a finished call touched, the knowledge base files it read (names only), and for an outside system its system, environment, verb and target {src:.harness/engine/core/callrecord.py#L1-L10}. An ask shows Copilot's confirmation box; under Allow all, which every chat the board makes uses, an ask passes (file 15 The gate and guardrails) {src:.harness/engine/modules/task/chatnew.py#L1-L26}.

## Architecture: fail closed, and the locks of the system

The hook fails closed for the guardrails: when it cannot decide, a call that may run a command or change a file is refused, while reads, the question tool and subagent calls pass {src:.harness/engine/hook.py#L2-L16}. That happens when the engine cannot load (a syntax error, a conflict marker, a missing file: `launch.py` or `hook.py` answers with the standard library alone); when the gate raises on a `PreToolUse` call; when the session state or the registry cannot be read; and when a guardrail file is not as accepted, outside admin mode. When the task module raises, only subagent calls are refused, the only calls it judges {src:.harness/engine/hook.py#L51-L87} {src:.harness/engine/launch.py#L2-L5}. When the gate's own policy cannot be read, the gate runs on a built-in copy of the shipped rules and refuses writes outside the task folder and git writes, and a call to a program of an unreadable tool pack is refused {src:.harness/engine/modules/gate/fallback.py#L1-L14} {src:.harness/engine/modules/gate/failclosed.py#L1-L7}. Only helpers may fail without stopping work: the log, reminders, what the board shows {src:AGENTS.md#L42-L59}. Two cases are Copilot's: when Python cannot start, Copilot counts the hook as a refusal; when the hook runs past 30 seconds, Copilot lets the call through with no notice (measured by the harness's authors) {src:docs/05-design.md#L163-L174}.

The locks: a hook holds the session's lock while every module decides. Since 1.8.1 the locks of session and task state are locks of the operating system, on lock files in the system's temp folder: the system frees a lock when its process ends, a slow holder is never taken over, and a call waits up to 20 seconds before it is refused as "the harness was busy" {src:.harness/engine/core/state.py#L28-L34} {src:.harness/engine/core/state.py#L129-L227}. Every state file is written to a temporary file and renamed, so no reader sees half a file {src:.harness/engine/core/state.py#L129-L227}.

## Architecture: the modules and the registry

A module is one ability, called with `handle(event, ctx)`, answering a decision or nothing; its code is in `.harness/engine/modules/<name>/`, its settings in `.harness/policies/<name>.json`. Its registry entry holds `status` (experimental to retired), `enabled`, the `events` it gets, `enforcement` letters, its `files` (checked by `doctor`) and `retire_when`, the Copilot feature that would make it unneeded {src:.harness/engine/core/registry.py#L13-L46}. The four modules at 1.8.3 {src:.harness/registry.json#L91-L322}:

| Module | Hook events | Letters | What it does |
|---|---|---|---|
| `task` | SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, SubagentStart, SubagentStop, Stop | S C H | the lines added to every prompt, which subagent may run, Stop reminders and blocks; as commands: tasks, write-back, checks, autorun, the board, the super agent |
| `gate` | PreToolUse, UserPromptSubmit, SessionStart, PostToolUse, PostToolUseFailure | S H | guards writes and commands; of reads it refuses only `.harness/.env`, secrets in the environment and requests to the board {src:.harness/engine/modules/gate/handler.py#L633-L650}; admin mode; git and outside-call approvals |
| `observe` | PostToolUseFailure | V | the call log (the hook hands it every record), statistics, the `kb` commands |
| `evalcheck` | none | V | judges fixed scenarios after a run; command line only |

The letters are the enforcement ladder: **S** text the model reads, **C** the `harness` command doing the work and checking preconditions, **H** a hook refusal or block, **V** a check after the fact {src:.github/skills/harness-rookie-wondering/references/14-internals.md#L86-L95}. Only modules marked H count as guardrails when they fail, which is `task` and `gate`: when the gate raises on a `PreToolUse` call the whole call is refused, and when the task module raises only subagent calls are refused, because they are the only calls it judges; on other events a failing guard refuses nothing {src:.harness/engine/hook.py#L55-L87}. The task module is the largest (78 of the engine's 191 Python files). Modules import only the core library, never each other, and each keeps its own part of the session state; a shared field has one writer: `active_task` the task command, `admin` the gate's command {src:.harness/engine/core/state.py#L1-L10}.

## Architecture: the core library, and how it differs from a module

The core library, `.harness/engine/core/` (70 files), is what every module, the hook entry and the command line build on; it has no entry in the registry, and the hook uses it on every event (state, subagent tracking, merge). A module owns hook behaviour, a policy and commands; core holds what several of them need, so removing one module does not break another {src:.github/skills/harness-rookie-wondering/references/14-internals.md#L23-L35}. Its groups: hook plumbing (`events.py`, `state.py`, `registry.py`, `config.py`, `breaker.py`, `logs.py`, `callrecord.py`); tasks and approvals (`tasks.py`; `approval.py`, a person at a terminal and a typed code bound to a sha256, behind every approval {src:.harness/engine/core/approval.py#L1-L43}); reading Copilot (`copilot_events.py`, Copilot's own record `~/.copilot/session-state/<id>/events.jsonl`, read for times and usage {src:.harness/engine/core/copilot_events.py#L1-L12}; `ahp.py`, the board's client of VS Code); the knowledge base (`kb*.py`, used by the `harness kb` commands); outside systems (`toolpacks.py`, `connections.py`, `systems.py`, `outbox.py`); words and paths (`messages.py`, `paths.py`, `guardrails.py`).

## Architecture: policies, override files, and what a team may configure

The policies in `.harness/policies/` hold what the code reads: `gate.json` (guardrails, terminal rules, git), `task.json` (checks, autorun, board, health), `target.json`, `tools.json` (outside systems), `observe.json`, `agents.json`, `user.json` (name, language), `cli.json`, `connections.json`, `computer.json` {src:.harness/INDEX.md#L58-L109}. Each is read in three layers: the shipped `<name>.json`, then `<name>.company.json` (copied in by `harness company sync`), then `<name>.override.json` (the person's), which wins; a key ending in `+` appends to a list {src:.harness/engine/core/config.py#L1-L50}. A team configures by adding files next to the defaults, so an upgrade does not overwrite its settings {src:docs/03-configure.md#L26-L47}.

A team may set target repositories, language, outside systems and their rules, check and autorun limits, board thresholds, more guardrail paths and the gate's terminal rules, and it brings tool packs, connections, the knowledge base and domain skills. It cannot drop the core guardrail paths (hooks, policies, engine, `bin`, registry, runtime, `.vscode/settings.json`): the gate adds them back and `doctor` reports an error {src:.harness/engine/core/guardrails.py#L9-L23}. The override files are under `.harness/policies/**`, a guardrail path, so outside admin mode the agent's edit tools, and terminal writes that name them, are refused; they are not in the integrity list, so a person's change does not stop the hook {src:.harness/engine/integrity.py#L1-L29}.

## Architecture: contracts, templates and message tables

`.harness/contracts/` holds the forms code and agent share: the task file templates (`TASK.md`, `REQ.md`, `TODO.md`, `LOG.md`, `INTAKE.md`) in `templates/task/en/` and `zh/`, which `task new` copies by tier and language; the knowledge base standard and the repository map contract in `kb/`; the tool pack protocol in `toolpack/` {src:.harness/INDEX.md#L58-L109}. Every text the engine prints is a named entry in `core/messages.en.json` and `core/messages.zh.json`, with the same names and placeholders; `language` in `user.json` picks one. The docs, rules and skills exist once, in English {src:docs/05-design.md#L147-L153}.

## Architecture: the harness command line

`harness` is a short launcher (`.harness/bin/harness`, or `harness.cmd` on Windows) that finds `.harness/engine/cli.py` from the current folder and runs it {src:.harness/bin/harness#L1-L40}. `cli.py` is the one command entry for people and agents; each module registers its commands: the task module `task` (new, open, fetch, promote, review, deliver, close, autorun, board and more) and `target`; the gate module `admin`, `approve-command`, `approve-action`, `tools`, `as`, `wait`; the observe module `stats`, `kb`, `logs`; the evalcheck module `eval`; and `cli.py` itself `doctor`, `user`, `skill`, `company`, `toolpack`, `reinstall` {src:.harness/engine/cli.py#L2-L19}. A result is text on a terminal and JSON on a pipe. The commands only a person may run (approvals, admin mode, autorun on, checks, pause) are refused on the agent's command line by the gate, and most also need a terminal with a keyboard and a typed code; the board's buttons run the same functions {src:.harness/policies/gate.json#L131-L144}.

## Architecture: the board server and how it reaches VS Code

The board is a web server inside the task module, started by the person with `harness task board` (what Start Harness runs); it serves the harness's own pages in `modules/task/web/`. It listens on 127.0.0.1 only and answers only to that Host and Origin; approval buttons need the paired browser, which traded a one-time code for a cookie, and run the terminal command's function with the code the person types; the gate refuses an agent's request to the board {src:.harness/engine/modules/task/boardserve.py#L1-L17}.

The link to VS Code: one background thread (`vslink.py`) reads the address and token of VS Code's agent host (`code agent endpoints`), connects with a WebSocket over a local socket or named pipe carrying JSON-RPC (`core/ahp.py`), and keeps a cache of the chats that pages read. A send, steer, stop, allow or answer is a job that thread runs after it looked at the chat again; it refuses rather than guess {src:.harness/engine/modules/task/vslink.py#L1-L16}. `chatlink.py` binds a chat to a task only when sure (a chat the board made, or Copilot's session id found in it) {src:.harness/engine/modules/task/chatlink.py#L1-L15}. **New task** makes a chat through the host with a fixed first message built by `chatnew.py`, and that chat opens the task itself {src:.harness/engine/modules/task/chatnew.py#L1-L26}. The super agent view opens one chat a day with the `super` agent and sends it a digest written by code. The files 12 The board and 21 Super agent explain them.

## Architecture: the agents and the skills

The person talks to Copilot's default agent, which holds the task. The four custom agents in `.github/agents/` cannot be picked in the chat {src:docs/05-design.md#L101-L119}: `reviewer` (the independent checker; read, search, execute; file 17 Independent checks) {src:.github/agents/reviewer.agent.md#L1-L8}; `mapper` (a read-only reader for `/generic-mapreduce`; tools read, search) {src:.github/agents/mapper.agent.md#L1-L8}; `worker` (one step of `TODO.md` in autorun, in a fresh context; its agent file has no `tools` line, so no tool list is written there, and what it may write is set by the gate's autorun write split and by the file's own text; file 20 Autorun) {src:.github/agents/worker.agent.md#L1-L7}; and `super` (the board's talker about tasks; the gate makes its chat read-only; file 21 Super agent) {src:.harness/engine/modules/gate/superagent.py#L1-L5}. The task hook refuses any subagent other than the reviewer, the mapper and the worker, each only in its own case {src:.harness/engine/modules/task/handler.py#L278-L300}. The 34 skills in `.github/skills/` are text: 12 `harness-*` (the task flow, autorun, admin, the courses) and 22 `generic-*` (requirement review, impact analysis, knowledge base building, mapreduce, workflows); domain skills live in the team's knowledge base {src:.harness/INDEX.md#L23-L56}. The file 23 Skills explains them.

## Architecture: where state lives

State is kept in files, never only in a chat {src:docs/05-design.md#L101-L119}:

- **The session:** `.harness/runtime/state/vscode/<session>.json` (its task, admin mode, subagents, each module's part), the hook log `.harness/runtime/logs/vscode/<session>.jsonl`, and `hook-errors.jsonl` {src:.harness/engine/core/logs.py#L1-L5}.
- **The rest of `.harness/runtime/`:** the board's port, the super agent's day, git approvals, the knowledge base map cache. It is ignored by git and stays closed to the agent's edit tools even in admin mode, because a session that could write it could make itself admin or forge an approval {src:.harness/engine/core/guardrails.py#L9-L23}.
- **The task:** `.workspace/sandbox/tasks/<task>/` with `.task/task.json`, written by harness code; the agent's edit tools and a terminal command that names it are refused, but a script the agent runs is not checked for it; reports in `.workspace/reports/`; none of it in git (file 11 Task) {src:.harness/policies/gate.json#L4-L34}.
- **Outside the folder:** the integrity list in `~/.copilot-harness/integrity/`, lock files in the temp folder, Copilot's own record in `~/.copilot/session-state/`, and the target repositories: their files are written by the harness through `task promote` after the person approves; besides, `task fetch` and every dry run first `git fetch` and fast-forward the local base branch (a `git merge --ff-only` when it is checked out and clean) {src:.harness/engine/modules/task/promote_target.py#L1-L14} {src:.harness/engine/modules/task/basesync.py#L1-L15}.

## Architecture: integrity checks and doctor

The integrity list holds the size, time and SHA-256 of every file of `.harness/engine/`, `.harness/bin/`, `.github/hooks/`, `.harness/toolpacks/`, `registry.json` and the shipped policies (not the override and company files), in the person's home {src:.harness/engine/integrity.py#L1-L29}. It is made at the first start of the board, at the first start after an upgrade, by `harness doctor --accept` at the person's terminal, by the board's paired button, and when admin mode ends {src:.harness/engine/integrity.py#L200-L210}. Before every tool call the hook compares the files with it; a changed, new or missing file refuses commands and writes until the person accepts or restores it. Nothing is checked before the first list exists, nor in an admin session {src:.harness/engine/hook.py#L312-L326}.

`harness doctor` checks that the parts agree: Python, the hook configuration and that the hook starts, the registry and each module's files, policies and overrides, message tables, agent models, knowledge base, skills, tool packs, VS Code settings, target repositories, the integrity list, and how close recent gate times come to the hook limit {src:.harness/engine/doctor.py#L120-L160}. The file 24 Setup, doctor and upgrade explains it.

## Architecture: tests, evals and dependencies

The harness has 142 test files with 3910 test methods in `.harness/tests/`, plain `unittest`, run with `python3 -m unittest discover -s .harness/tests`; the helpers in `support.py` start `hook.py` and `cli.py` as real processes with `HARNESS_ROOT` set to a temporary root, with hook input recorded from real Copilot sessions; many tests also import engine code and call its functions in-process {src:.harness/INDEX.md#L58-L109} {src:.harness/tests/support.py#L1}. The evals are four fixed scenarios that a person runs once in a real chat and `harness eval check` judges from the log and files, with no model scoring. The file 33 Test map and evals lists them all.

Dependencies: Python 3.9 or later and its standard library only; no third-party import appears in the engine, the board's WebSocket client included {src:.harness/engine/doctor.py#L65-L71} {src:.harness/engine/core/ahp.py#L1}. Two optional packages, `xlrd` (old `.xls`) and `pypdf` (PDF text), extend `task intake convert`; the harness never installs them {src:.harness/policies/tools.json#L3-L11}. Outside the harness: VS Code with GitHub Copilot, `git`, and the `code` program for the board's link.

## Architecture: what is enforced by code, and what is only an instruction

By code: every decision on the hook path (the gate's refusals and asks, the task module's subagent rules and Stop blocks, the integrity check, failing closed), the preconditions the `harness` command checks before it acts (an approved plan, a code typed at a terminal, enough passes), and that the agent's edit tools and terminal commands that name them cannot write the state files {src:.harness/engine/hook.py#L2-L16}. Only text: when to open a task, the order of work, how to call the reviewer, how to read the knowledge base, in `AGENTS.md`, instructions and skills, which the model may ignore {src:AGENTS.md#L42-L59}. The lines the task hook adds to each prompt are written by code but are text to the model {src:.harness/engine/modules/task/handler.py#L93-L126}. The tool lists of the custom agents are applied by Copilot; the harness adds limits on subagents only as the files 15, 17, 20 and 21 describe. The text files, `.github/agents/` included, are not guardrail paths {src:.harness/policies/gate.json#L4-L34}. The file 00 Harness at a glance gives this split area by area.

## Architecture: who decides what

- **The person** starts the board, types every approval code (requirement, plan, write-back, git writes, held outside calls), switches checks, autorun and admin mode on, accepts integrity changes, writes override files, accepts or closes tasks, and commits {src:.harness/policies/gate.json#L131-L144}.
- **The code** decides each tool call, counts check passes, works out a task's stage from its files, and refuses when it cannot decide {src:.harness/engine/modules/task/taskstages.py#L1-L15}.
- **The agent** decides the rest: what to read, what to write in the task folder, which tool to call, how to word the requirement and the plan {src:docs/05-design.md#L133-L137}.

## Architecture: design principles, and what was tried before

These principles come from the harness's design notes and `docs/05-design.md`, stated only where the code at 1.8.3 still does them:

- **Code for what must hold, text for judgement.** What is certain (dangerous commands, writes out of bounds, a write-back without passes) is enforced by hooks and the command line; what is not (is the requirement right, is the work good) is text, then checked by an independent reviewer {src:docs/05-design.md#L133-L137}.
- **The person holds the keys.** Approvals need a typed code bound to what is approved, not a confirmation box, because "Allow in this Session" switches a box off {src:docs/05-design.md#L176-L182}.
- **The enforcement ladder.** A rule starts as text and moves to the command line or a hook when it is broken again and again, cannot be undone, or other parts depend on it; the command line is preferred because it holds in every runtime; each refusal says why and what to do next {src:.github/skills/harness-rookie-wondering/references/14-internals.md#L86-L95}.
- **The harness and the company never edit the same file**, so an upgrade does not conflict; after a model upgrade the text and numbers change, not the code {src:docs/03-configure.md#L26-L47}.
- **Build each module to be removed:** `retire_when` names the Copilot feature that would replace it; the guardrails and the task's write scope never retire {src:.harness/registry.json#L285}.
- **One entry for every event:** the platform does not filter hook commands by matcher, so one dispatching entry starts one process, not one per module {src:.github/skills/harness-rookie-wondering/references/14-internals.md#L113-L114}.

What was tried before: until 1.1.0 work was split into levels L1 to L3 with a multi-agent flow; only L2 was used, and L3 cost about 4.5 times as much for no better result {src:docs/05-design.md#L57-L65}. An admin agent existed until 1.5.32; admin rights now come from a switch on the session {src:docs/05-design.md#L194-L198}. Until 1.7.38 the hook failed open, and a broken engine or policy let every call through; 1.7.38 made the guardrails fail closed and added `launch.py` and the integrity list {src:docs/07-release-notes.md#L254-L259}. Until 1.8.1 a lock older than 5 seconds was removed, so two writers could get in {src:docs/07-release-notes.md#L54}.

## Architecture: where in the source

`.github/hooks/harness.json`; `.harness/engine/launch.py` and `hook.py` (entry, merge, fail-closed, integrity); `adapters/`; `core/`; `modules/{task,gate,observe,evalcheck}/`, the board in `modules/task/boardserve.py` and `web/`; `cli.py`, `doctor.py`, `integrity.py`, `.harness/bin/`; `.harness/registry.json`, `policies/`, `contracts/`; `.harness/tests/`, `.harness/eval/` {src:.harness/INDEX.md#L58-L109}. The file 32 Code map lists every file with one line.

## Architecture: common questions

**Q: Where does the harness plug into Copilot?** At `.github/hooks/harness.json`, read when the VS Code window starts: nine events, one command, `launch.py`. The rest is text Copilot already reads: `AGENTS.md`, `.github/instructions/`, `.github/skills/`, `.github/agents/` {src:.github/hooks/harness.json#L1-L113}.

**Q: What happens when the harness itself is broken?** For the guardrails it fails closed: commands and writes are refused, reads go on, and the agent is told to report it; the person repairs it and checks with `harness doctor` {src:.harness/engine/hook.py#L2-L16}. Only helpers may fail without stopping work.

**Q: Can we add our own module or switch one off?** The registry has a switch per module; a new one is registered switched off, then gets its policy, code and tests. The agent may change the engine and the registry only in admin mode, which only the person switches on; a change made outside it must be accepted with `harness doctor --accept` {src:.github/skills/harness-rookie-wondering/references/14-internals.md#L113-L114}. Switching off the gate or the task module removes the guardrails.

**Q: Does it need a server, a database or packages, and does it slow the agent?** No server and no database: files and local processes, standard library only. Each event starts one Python process; the design target is well under 300 milliseconds, and `doctor` warns when recent gate times come close to the 30-second limit {src:.github/skills/harness-rookie-wondering/references/14-internals.md#L23-L35} {src:.harness/engine/doctor.py#L120-L160}.

## Architecture: limits

- **Not a sandbox.** The agent runs as the person's user and the gate reads the text of a call; a write the text does not show is not stopped (file 15 The gate and guardrails) {src:.harness/engine/modules/gate/terminal.py#L1-L5}.
- **A hook past 30 seconds lets the call through,** by Copilot's rule, with no notice {src:docs/05-design.md#L163-L174}.
- **The text layer is not protected:** `AGENTS.md`, instructions, skills and agent files are neither guardrail paths nor in the integrity list {src:.harness/engine/integrity.py#L1-L29}.
- **The integrity list holds only against slips:** not checked before the first board start or in admin mode, and a process of the same user can rewrite it {src:.harness/engine/integrity.py#L1-L29}.
- **Only Copilot sessions in VS Code** get any protection, and the adapter follows Copilot's undocumented payloads, which an update can change {src:.harness/engine/adapters/copilot_vscode.py#L1-L8}.
- **Some text still says "fail open":** comments in `modules/task/handler.py`, `core/failopen.py` and the gate's `handle`, and `docs/05-design.md`, describe the behaviour before 1.7.38; the code refuses {src:.harness/engine/modules/task/handler.py#L23} {src:.harness/engine/modules/gate/handler.py#L723} {src:docs/05-design.md#L163-L174}.

## Architecture: related files

- The four layers as the design document names them, the registry fields and how the hook uses them, why modules import only `core/`, the adapter, the session state and its locks, how the tests run the hook, the replay, the eval scenarios, the red-team, docs and old-Python tests and the `evalrecord` whitelist: the file 31c Engine and tests internals.
- The subagents in code (the order of the subagent rule, the mapper grant, the worker's checks, the refused question tool, how the core links a subagent session to its parent): the file 31b Subagents internals.
- Every file: the file 32 Code map. Every test: the file 33 Test map and evals. Changes by version: the file 34 Version history.
- The gate: the file 15 The gate and guardrails. Tasks: the file 11 Task. The board: the file 12 The board. Setup and `doctor`: the file 24 Setup, doctor and upgrade. The ideas: the file 41 Ideas behind the harness; the decisions: the file 36 Design decisions.
- Extending the harness is guided by the skill `harness-admin`, used in admin mode {src:.harness/INDEX.md#L23-L56}; there is no harness tutorial for it in `3 Courses/Harness tutorials/`.
