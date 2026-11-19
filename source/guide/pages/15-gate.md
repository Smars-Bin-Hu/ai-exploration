---
title: The gate and guardrails
subject: Gate
layer: concept
file: 15 The gate and guardrails
harness_tag: 1.8.3
course: The book · 2.2 Hooks, the point every call passes through | https://smarshu.com/book/read/2-2-hooks.html
course: The book · 4.3 Guard the files that hold the rules | https://smarshu.com/book/read/4-3-guardrails.html
course: The book · 4.4 Build the enforcement layer like software | https://smarshu.com/book/read/4-4-enforcement-design.html
course: The book · 4.5 Some things you never hand over | https://smarshu.com/book/read/4-5-least-privilege.html
---
## Gate: what it is and what problem it solves

The gate is the harness code that checks every tool call of the Copilot agent before it runs and answers allow, ask or refuse. It is a module of the one hook that VS Code runs before each tool call {src:.harness/engine/modules/gate/handler.py#L1-L14}. It exists because a rule in `AGENTS.md` or a skill is text the model may ignore, and Copilot's own confirmation box does not show when the chat's permission is Allow all; a refusal from the hook holds in every permission mode {src:docs/02-features.md#L50-L61}. The gate guards writes and commands, not reads: the files that hold the harness's rules (the guardrail files), the files only the `harness` command line writes, `.git` folders, target repositories, the task folder, dangerous commands and the commands only a person may run {src:.harness/policies/gate.json#L3}. It is not a sandbox: it reads the text of a call, and the agent has the person's rights {src:docs/02-features.md#L50-L61}.

## Gate: which hooks run and when they fire

`.github/hooks/harness.json` starts `.harness/engine/launch.py` for nine Copilot events: session start, each prompt (`UserPromptSubmit`, `userPromptTransformed`), before a tool call (`PreToolUse`), after it (`PostToolUse`, `PostToolUseFailure`), subagent start and stop, and when the agent stops; each with a 30-second timeout {src:.github/hooks/harness.json#L1-L113}. `launch.py` loads `hook.py`, which reads the event, locks the session's state, runs the modules `.harness/registry.json` subscribes to that event, and merges their answers {src:.harness/engine/hook.py#L1-L15}. The gate runs at session start, each prompt, and before and after a tool call; the task module also at subagent start and stop and at stop {src:.harness/registry.json#L92-L285}.

Only `PreToolUse` decides whether a call runs. On the other events the gate only adds text for the agent (connections, approved outside calls) and sets or clears the read-only marks {src:.harness/engine/modules/gate/handler.py#L758-L812}. On `PreToolUse` the task module judges only subagent calls {src:.harness/engine/modules/task/handler.py#L278-L300}. A subagent's own tool calls go through the same hook, in a session linked to its parent that holds the parent's task {src:.harness/engine/hook.py#L90-L133}.

## Gate: how one tool call is decided (allow, ask, refuse)

The gate looks at a `PreToolUse` call in this order {src:.harness/engine/modules/gate/handler.py#L758-L812}:

1. In the super agent's chat or a question turn, anything but a read is refused.
2. A tool that is not the terminal and whose input names the board's local port is refused. An MCP tool a tool pack names: a read passes, a write or run asks, a destroy is refused {src:.harness/engine/modules/gate/handler.py#L317-L333}.
3. For every tool: reading `.harness/.env`, printing a variable that holds a sign-in, or dumping the environment is refused {src:.harness/engine/modules/gate/handler.py#L633-L650}.
4. Only edit, create and terminal calls go further; every other call passes. They are checked against `.harness/policies/gate.json`, with the company's `gate.company.json` and the person's `gate.override.json` merged on top; the core guardrail paths are added whatever a layer says {src:.harness/engine/core/guardrails.py#L9-L23}.

Across modules a refusal wins over an ask and an ask over an allow {src:.harness/engine/hook.py#L1-L15}. An ask hands the call to Copilot's confirmation box. A refusal tells the agent why and what to do instead; the third identical one in a prompt orders it to stop retrying {src:.harness/policies/gate.json#L146-L189}.

## Gate: what it checks on the edit tools

The gate knows a tool by its name in `.harness/engine/adapters/tool_kinds.json`: `create_file`, `replace_string_in_file`, `apply_patch`, `Write`, `Edit` and a few more are edit tools {src:.harness/engine/adapters/tool_kinds.json#L1-L39}. An edit tool whose target path cannot be read is refused {src:.harness/engine/modules/gate/handler.py#L773-L836}.

For every chat, an edit is refused inside a `.git` folder, inside the integrity-list folder (`~/.copilot-harness`, or `HARNESS_INTEGRITY_DIR`), inside a target repository and on a path only the command line writes; and, outside admin mode, on a guardrail path (in admin mode only `.harness/runtime/**` and the policy's `admin_locked_paths` stay closed) {src:.harness/engine/modules/gate/handler.py#L38-L109} {src:.harness/engine/core/guardrails.py#L9-L23}. The guardrail paths are the hooks, the policies, the engine, `.harness/bin`, the tool packs, `.harness/.env`, the start files, `registry.json`, `.harness/runtime/**`, `.vscode/settings.json`, `.vscode/mcp.json`, `LICENSE` and `NOTICE`; the command line alone writes a task's `.task/`, `REVIEW/`, `SNAPSHOT/`, `OUTBOX/`, `READ/`, its `.diff` files and `.workspace/reports/` {src:.harness/policies/gate.json#L4-L34}. For a chat that holds an open task, edits stay inside that task's folder; `REQ/`, `REF/` and `INBOX/` are refused, and `DEV/` until the plan is approved. A chat with no open task is not kept to a folder {src:.harness/engine/modules/gate/handler.py#L38-L109}.

## Gate: what it checks on a terminal command

A terminal command is read as text before it runs {src:.harness/engine/modules/gate/handler.py#L117-L167}:

- **A write to a protected path** (redirect, `tee`, `rm`, `mv`, `cp`, `sed -i`, `git checkout`…) naming a guardrail path, a command-line-owned path or `.git` is refused, also by a relative path after a `cd` in the same line {src:.harness/policies/gate.json#L35-L130} {src:.harness/engine/modules/gate/terminal.py#L1-L5}. One naming a target repository is refused only when it spells the repository's full path (also after a `cd` to that full path): the rule is built from absolute paths, so a relative path into the repository, or a `cd` to a relative folder, passes {src:.harness/engine/modules/gate/policy.py#L149-L156}.
- **Git, when target repositories are set up:** `push`, `clean` (but a dry run), `filter-branch`, `filter-repo`, `update-ref`, `prune`, `reset --hard`, `gc --prune`, `reflog expire` and `reflog delete`, `branch -D`, `gh pr`, and any force are never approved, and a line that mixes one of them with another write is never approved as a whole (the file 16 Write-back); another git write waits until the person approves that exact command with `harness approve-command`, for one run within 10 minutes {src:.harness/engine/modules/gate/gitcmd.py#L1-L9}.
- **Person-only commands:** `task confirm-req`, `approve-plan`, `approve-promote`, `recover`, `review set`, `extend`, `waive`, `dismiss`, `test runner`, `pause`, `resume`, `offwork`, `onwork`, `autorun on`, `task allow` (every spelling), `task board` (except `--once`), `task close`, `approve-command`, `approve-action`, `admin on`, `doctor --accept`. The line is read as the shell reads it, so a quote, a variable or `python3 -m cli` hides nothing; a harness call whose words cannot be read is refused {src:.harness/policies/gate.json#L131-L144} {src:.harness/engine/modules/gate/harnesscmd.py#L1-L8}.
- **A script the line runs** (`python3 x.py`, `node -e`, a here-document) is read, best effort, and refused when it writes to a guardrail path {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.
- **The deny list:** `rm -rf` of the root, home or current folder, a download piped to a shell, formatting a disk, `sudo` and the like, `chmod -R`, `docker rm`, `kubectl delete`, `terraform apply`/`destroy`, also inside `bash -c` {src:.harness/policies/gate.json#L35-L130}.
- **The board's port** is refused; **an outside system** is judged by its tool pack's rules (the file 19 Tool packs, connections and MCP).
- **The ask list:** deleting files, rewriting git history, the network, installing packages, pruning logs {src:.harness/policies/gate.json#L146-L189}.

A command that matches none of these passes {src:.harness/engine/modules/gate/terminal.py#L1-L5}.

## Gate: what "fail closed" means, and when the harness is busy

Fail closed means: when the guardrails cannot decide, every terminal command and every tool that may change a file is refused, and reads go on, until the person repairs the fault. It applies when `hook.py` cannot be loaded (`launch.py` answers in its place), the engine cannot be imported, the gate raises on a call, or the session state or registry cannot be read {src:.harness/engine/hook.py#L1-L15} {src:.harness/engine/launch.py#L1-L5}. The emergency answer passes only a fixed list of reads, searches, the question to the person and subagent calls; a terminal tool, a tool with a `command`, an edit tool and an unknown tool are refused {src:.harness/engine/hook.py#L169-L180} {src:.harness/engine/hook.py#L261-L309}. When `gate.json` or a layer cannot be read, the gate runs on a built-in copy of the shipped rules and also refuses edits outside the open task's folder, git writes and shell writes outside that folder {src:.harness/engine/modules/gate/fallback.py#L1-L13}.

When the task module fails (it raises on a call), the harness does not fail closed: only subagent calls are refused, and every other command and write of the session goes on, judged by the gate as usual. The registry marks both the gate and the task module as guardrails (`H`), but the hook names the task module in `GUARDS_FOR`, so its failure refuses only the calls it judges, which are subagent calls; the agent is told that no subagent can start now and that the person checks it with `harness doctor` {src:.harness/registry.json#L104-L108} {src:.harness/registry.json#L232-L235} {src:.harness/engine/hook.py#L55} {src:.harness/engine/hook.py#L76-L83} {src:.harness/engine/core/messages.en.json#L3896}.

The harness is busy when a hook call cannot get its session's lock. Since 1.8.1 the lock is held by the operating system for the process (a file in the system's temp folder): it is freed when the process ends, a slow holder is never taken over, and a call waits up to 20 seconds, under the hook's 30-second timeout {src:.harness/engine/core/state.py#L29-L34} {src:.harness/engine/core/state.py#L172-L217}. A call that waits longer gets the fail-closed answer with "the harness was busy … run the same call again" {src:.harness/engine/hook.py#L169-L180}. Before 1.8.1 a lock older than 5 seconds was removed, so two calls could write at once {src:docs/07-release-notes.md#L13-L89}.

## Gate: admin mode

Admin mode is a switch on one chat session that lets it change the guardrail files, to extend or debug the harness. Only a person switches it on: `harness admin on --session-id <id>` in their own terminal, with a typed code; the gate refuses `admin on` on the agent's command line, and the command refuses a subagent's session and one that holds an open task {src:.harness/engine/modules/gate/commands.py#L84-L136}.

It opens the guardrail paths to the edit tools, terminal writes and scripts {src:.harness/engine/core/guardrails.py#L9-L23}. It leaves closed `.harness/runtime/**` (the session state and the approvals, so an admin chat cannot make itself admin or forge an approval) with the policy's `admin_locked_paths`, the integrity-list folder, command-line-owned files, `.git`, target repositories and the person-only commands {src:.harness/engine/core/guardrails.py#L9-L23} {src:.harness/engine/core/messages.en.json#L513-L516}. An admin session calls no subagent and opens no task {src:.harness/engine/modules/task/handler.py#L278-L300}. Its integrity check is skipped, and `admin off` (anyone may run it) accepts the guardrail files as they are then {src:.harness/engine/hook.py#L312-L360}.

## Gate: read-only turns (super agent chat and questions to a task)

Since 1.8.3 the gate keeps two kinds of turn to reading {src:docs/07-release-notes.md#L13-L89}. A session in which a person's prompt starts with `/harness-super` (the board's super agent chat) stays read only; a turn whose prompt starts with `/harness-ask` (a question the person asks a task through the board) is read only until the next normal prompt. Only a person's prompt sets or clears a mark. While marked, only read, search and meta tools pass, plus a terminal line that is exactly one of `task list`, `task status`, `task queue`, `task autorun status`, `task review status`, `target list`, `target show`; all else is refused, subagent and MCP calls included, and so is any call when the mark cannot be read {src:.harness/engine/modules/gate/superagent.py#L18-L89} {src:.harness/engine/modules/gate/askturn.py#L21-L53}.

## Gate: the autorun write split

While a task's autorun is on (since 1.8.0), the task's own chat, which only schedules, may write only `TODO.md`, `TASK.md`, `LOG.md` and `QUESTIONS.md` at the folder's root; the `worker` subagent may write anything else the rules allow, but not those four {src:.harness/engine/modules/gate/handler.py#L38-L109}. A worker call the gate holds, or refuses for a reason the person can decide, goes into `QUESTIONS.md` as a held line and the run goes on; a write outside what the worker may write (outside the folder, into the four files, or with no path) is only counted; an outside call that needs a person is refused, since nobody is there to approve it {src:.harness/engine/modules/gate/handler.py#L736-L755} {src:docs/07-release-notes.md#L13-L89}. See the file 20 Autorun.

## Gate: the integrity check of the guardrail files

The hook compares the guardrail files with a list the person accepted: size, time and SHA-256 of everything under `.harness/engine`, `.harness/bin`, `.github/hooks` and `.harness/toolpacks`, of `registry.json` and of the shipped policies (not the `*.override.json` and `*.company.json` layers). The list lives in `~/.copilot-harness/integrity/`, made when the person accepts: the board's first start (also after an upgrade), `harness doctor --accept`, `admin off` {src:.harness/engine/integrity.py#L1-L9}. Before each tool call, prompt and session start the hook compares; while a file differs, every command and write is refused and the agent is told which files {src:.harness/engine/hook.py#L312-L360}.

## Gate: what is enforced by code, what is asked by text, and who decides

**Code**, in the hook before the call runs: every refusal and ask above, the fail-closed answer, the integrity check, the read-only marks and the autorun split {src:.harness/engine/modules/gate/handler.py#L758-L812}. **Code** in the `harness` command line: the approvals (requirement, plan, write-back, recover, `autorun on`, `extend`, `waive`, `dismiss`, `admin on`, held calls and git writes) check for a person at a terminal (or the board's Terminal window) and ask for a typed code; the settings (`review set`, `task allow`, `test runner`, `pause`, `resume`, `offwork`, `onwork`, `board --serve`, `doctor --accept`) check for a person and ask no code; `task close` has no person check of its own, only the gate's refusal {src:.harness/engine/core/approval.py#L28-L58} {src:.harness/engine/modules/task/commands.py#L123-L133}.

**Text** only: do not change guardrail files, tell the person instead; when the guardrails cannot decide, tell the person and do not go round it; each refusal says not to retry another way {src:AGENTS.md#L55-L64}.

**Who decides:** the person switches admin mode on, accepts the guardrail files, approves held calls, answers the ask box, picks the chat's permission, and runs a refused command themselves when needed; the company adds paths and rules but cannot remove the core guardrail paths; the code refuses or asks {src:.harness/policies/gate.json#L131-L144} {src:.harness/engine/core/guardrails.py#L9-L23}.

## Gate: why it is built this way, and what was tried before

**Ask is not a limit; refusals teach.** Each refusal says why and what to do instead, so the agent changes course. Copilot's confirmation box is skipped under Allow all and after "Allow in this Session", while a hook's refusal holds in every mode. So what must hold is a refusal, and key approvals are a code typed in a terminal, not a pop-up; administrator rights, recursive permission changes and deleting infrastructure moved from the ask list to the deny list {src:docs/02-features.md#L50-L61} {src:docs/05-design.md#L133-L198}.

**Guard writes, not reads.** The gate sorts work by what a mistake costs. A read changes nothing, so it is not stopped: the design document puts read-only work in the row "Not stopped" of its table {src:docs/05-design.md#L69-L74}, and says, about a hook that fails itself, that hurting normal work costs more than missing a stop {src:docs/05-design.md#L165}. The harness has no sentence of its own that gives the reason for reads; this is the Guide's reading of those two passages. The gate refuses no read but the secrets file `.harness/.env`, printing a secret variable or the whole environment, and the board's port; since 1.8.3 the super agent chat and a question turn are also kept to reads {src:.harness/policies/gate.json#L3} {src:.harness/engine/modules/gate/handler.py#L633-L650}.

**From fail open to fail closed.** Until 1.7.38 an error of the hook counted as "no opinion" and the call passed, on the ground that hurting normal work costs more than missing a stop; a red-team round showed calls passing because the gate had failed. Since 1.7.38 a guardrail that cannot decide does not pass, `launch.py` answers for a broken `hook.py`, the guardrail files are checked against an accepted list, and person-only commands are read as the shell reads them. In 1.8.0 every spelling of `task allow` became the person's {src:docs/07-release-notes.md#L229-L259} {src:docs/07-release-notes.md#L13-L89}.

**Rights follow the session, not the agent.** A hook does not see which main agent is talking, so choosing an agent cannot open the guardrails; the admin agent was retired in 1.5.32 for a switch on the session {src:docs/05-design.md#L133-L198}.

**No sandbox of its own.** Isolation by the operating system (a container, an account with fewer rights) is left to the company {src:docs/02-features.md#L50-L61}. The registry says the gate may retire once Copilot itself limits writes by path and refuses dangerous commands {src:.harness/registry.json#L92-L285}.

## Gate: where it is in the source

Under `.harness/` {src:.harness/engine/modules/gate/handler.py#L1-L14}: `policies/gate.json` (the rules); `engine/launch.py` and `engine/hook.py` (entry, merge, fail-closed answer, integrity check); `engine/modules/gate/` (`handler.py` the order of checks; `terminal.py`, `harnesscmd.py`, `scriptcheck.py`, `gitcmd.py` command lines; `superagent.py`, `askturn.py` read-only turns; `failclosed.py`, `fallback.py` failures; `commands.py` admin mode and held-call approvals); `engine/core/guardrails.py`, `engine/integrity.py`, `engine/core/state.py`; `engine/adapters/tool_kinds.json`.

## Gate: common questions

**Q: Is the gate a sandbox?** No. It reads the text of each call and the agent runs as the person, so a write the text does not show is not stopped (see "Gate: limits") {src:docs/02-features.md#L50-L61}. For an agent you do not trust, use a container or an account with fewer rights.

**Q: Can the agent switch the gate off or change its rules?** Not by edits or terminal writes that name the files, outside admin mode; a changed hook, policy or engine file makes the hook refuse every command and write until the person accepts or restores it {src:.harness/engine/hook.py#L312-L360}. A process of the same user that builds the path at run time can still change them, the accepted list included {src:.harness/engine/integrity.py#L1-L9}.

**Q: Can the agent run an approval command itself?** The gate refuses the person-only commands on its command line, however spelled, and most of them also check for a person at a terminal; `task close` relies on the gate alone {src:.harness/engine/modules/gate/harnesscmd.py#L1-L8} {src:.harness/engine/core/approval.py#L28-L58}. The code is printed in the question: it proves someone read and typed; it is not a secret. A script file the agent writes and runs is read only for writes to guardrail paths {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.

**Q: What happens when the harness itself breaks, or is busy?** Commands and writes are refused and reads go on until the person repairs it (`harness doctor`); "busy" means another call of the session held the lock 20 seconds, and the call is run again {src:.harness/engine/hook.py#L169-L180}.

## Gate: limits

- **The gate reads text.** A terminal write into a target repository by a relative path, a path built from variables, a script that writes a command-line-owned file (the approval records in `.task/` among them), or a program that chooses where to write is not seen {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11} {src:docs/02-features.md#L50-L61}.
- **Unknown tools are not checked.** A tool not in `tool_kinds.json` gets kind `other`: no path check and no terminal rules, only the tool-pack MCP check, the board-port check and the secrets check. That covers a file-writing MCP server no tool pack names, and an edit or terminal tool under a new name {src:.harness/engine/modules/gate/handler.py#L773-L836}.
- **The ask rules are only a reminder.** Under Allow all no box shows; every chat the board makes starts with Allow all, and **Start autorun** sets it on the task's chat {src:.harness/engine/modules/task/chatnew.py#L25-L26} {src:.harness/engine/modules/task/autorun_start.py#L1-L6}.
- **▶ Run and the board's Terminal window bypass the gate.** Both run the command from the board server as the person. Only the paired browser may use them, and the Run dialog warns that the gate does not check the command, also one the agent wrote {src:.harness/engine/modules/task/boardterm.py#L1-L9} {src:.harness/engine/core/messages.en.json#L2005-L2009}.
- **The task folder binds only a chat that holds an open task, and only its edit tools;** the terminal is not kept to it {src:.harness/engine/modules/gate/handler.py#L38-L109}.
- **Git writes are checked only when target repositories are set up;** without them only the ask list looks at git {src:.harness/engine/modules/gate/handler.py#L773-L836}.
- **A hook that times out lets the call through.** Measured in a Copilot session: the platform passes the call with no notice; the timeout is 30 seconds {src:docs/05-design.md#L133-L198}.
- **The text rules are not guarded.** `AGENTS.md`, instructions, skills and agent files are not guardrail paths for the edit tools and are not in the integrity list {src:.harness/policies/gate.json#L4-L34} {src:.harness/engine/integrity.py#L1-L9}.

## Gate: related files

- The whole harness and its guarantees: the file 00 Harness at a glance. The task folder and the plan approval that opens `DEV/`: the file 11 Task.
- Calls to databases, ticket boards and pipelines: the file 19 Tool packs, connections and MCP. Autorun: the file 20 Autorun. The super agent: the file 21 Super agent.
- The code-level detail behind this file (hook events and modules, the path of one call, merging, failure answers, how command lines are read): the file 15b The gate and guardrails internals.
- What a refused or held call looks like on the board: the harness tutorial "3 When the agent is stopped", in `3 Courses/Harness tutorials/`.

The gate's entry in the registry lists its files {src:.harness/registry.json#L222-L285}.
