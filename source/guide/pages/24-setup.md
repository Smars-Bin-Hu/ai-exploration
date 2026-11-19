---
title: Setup, doctor and upgrade
subject: Setup
layer: concept
file: 24 Setup, doctor and upgrade
harness_tag: 1.8.3
course: The book · 0.2 A minimal harness in 30 minutes | https://smarshu.com/book/read/0-2-minimal-harness.html
---
## Setup: what it is and what problem it solves

The harness has no server and no installer: it is a copy of its repository on each person's computer, opened as the VS Code workspace, so VS Code loads its hooks and instructions from that folder {src:.github/hooks/harness.json#L1-L15}. This file explains setup; to install step by step, see the guide "Install the harness" in the OneDrive folder `AI Exploration/4 Install the harness/`.

## Setup: what a computer needs, and where things are kept

Required: **Python 3.9 or later**, standard library only, run as `python3` (macOS, Linux) or `python` (Windows): the hooks start that name, and a hook that cannot start makes Copilot refuse every tool call {src:.harness/engine/doctor.py#L65-L93}; **VS Code with GitHub Copilot Chat**, signed in, with the chat's Session Target set to Copilot, the only session kind the harness is sure to work in; **the short command `harness` on PATH**, since every command the agent is told to run starts with it {src:.harness/engine/doctor.py#L173-L190}; a browser for the board. **git** is needed for target repositories and the knowledge base. Optional: the `code` command on PATH, `xlrd` and `pypdf` for old Excel and PDF intake files {src:.harness/engine/doctor.py#L601-L644}, and the programs of a tool pack the company turns on (`az`, `sqlcmd`).

What git ignores in the copy is the person's, and an upgrade leaves it {src:.gitignore#L1-L35}: tasks, reports and goals under `.workspace/`; `.harness/runtime/` (which chat holds which task, session logs, map cache); four of the settings files, `target`, `user`, `cli` and `tools` as `.harness/policies/<name>.override.json` (other override files are not ignored); identities in `.harness/.env` and the CA bundle in `.harness/certs/`. The knowledge base `knowledge-base/` has its own `.git`; the harness ships none. Outside the copy, `~/.copilot-harness/integrity/` keeps the list of accepted guardrail files, one per copy, and the gate refuses the agent's writes there, in admin mode too {src:.harness/engine/integrity.py#L33-L48} {src:.harness/engine/modules/gate/handler.py#L44-L46}.

## Setup: Start Harness, the harness command and Get ready

`harness` is a script in `.harness/bin/` (`harness.cmd` on Windows). Like git, it works on the copy that holds the current folder, so one PATH entry serves every copy {src:.harness/bin/harness#L1-L36}. **Start Harness** (`.command` on macOS, `.cmd` on Windows) runs `harness task board` and stays open while the board runs. Only a person starts the board: the gate refuses the agent's `task board` (except `--once`) {src:.harness/policies/gate.json#L131-L137}. The board opens the browser paired (see the file 12 The board).

**Get ready** is a form on the board: no agent runs and only the paired browser may use it. Its four cards: **1 The short command** (required; **Set it up** copies `harness.cmd` to `%USERPROFILE%\bin` and adds it to the user Path on Windows, or on macOS and Linux links the script into `~/bin` or `~/.local/bin` when one is on PATH and otherwise adds `~/bin` in `~/.zshrc` or `~/.bashrc`, and **Test it** runs `harness --version` as a new terminal would {src:.harness/engine/core/shortcmd.py#L56-L109}); **2 You** (required: name and language); **3 From the company** (the only card marked optional: the knowledge base to keep or take from a package or folder, a checklist of what it brought, and the code repositories; without a knowledge base the agent does local work only {src:.harness/engine/core/readyitems.py#L1-L19}); **4 Local** (a checklist of the programs the packs need, the CA bundle and MCP, and under "More" the Python install command and the paths the agent must not touch). The checklists in cards 3 and 4 only show facts and open the Servers and Local windows: Get ready writes no connection, sign-in, MCP setting or CA bundle. What Finish writes into the person's own override files is the name, language and skill prefix (`user`), the code repositories and their paths to keep out (`target`), and the Python install command and the Python that runs the board, pinned so that a package installed for the harness is found by every terminal (`tools`); the exact keys are in the file 24b {src:.harness/engine/core/setup.py#L391-L454}.

**Finish setup** runs seven steps in order and stops at the first that fails: the three override writes, then the knowledge base in place, a git repository made of it, the copy of the company's content, and `harness doctor`; an error stops it, and the person fixes it and presses Finish again {src:.harness/engine/modules/task/setupjob.py#L88-L137}. The first three steps write only the override files; the last four also write `knowledge-base/` and the copies under `.github/` and `.harness/policies/`. The Enter screen then needs five green lines: copy set up, browser paired, `doctor` without error, VS Code open, Copilot connected; the company's items never block {src:.harness/engine/modules/task/ready.py#L1-L8}.

## Setup: what harness doctor checks

`harness doctor` prints one line per check: `[OK]`, `[WARN]` (a reminder that stops nothing) or `[ERROR]` (fix first), then `{"errors": N}`; it exits 1 when N is not 0 {src:.harness/engine/doctor.py#L1017-L1112}.

- **Errors**: Python too old or not running; no `harness` on PATH; registry or engine files missing; a wrong hook configuration; `launch.py` or `hook.py` that does not compile; a policy or override that cannot be read or merged, a faulty tool pack or connection file; a target repository without its base branch; guardrail files not as accepted {src:.harness/engine/doctor.py#L193-L269} {src:.harness/engine/doctor.py#L973-L998}.
- **Warnings**: no hook call for 7 days; a Local session; a gate near the hook timeout; knowledge base, skill and company-copy gaps; a pack's program missing; a pack name no pack has; an outside system not reached; `code` not found; optional packages; a long or synced Windows path; no integrity list {src:.harness/engine/doctor.py#L120-L155}.

## Setup: the accepted guardrail files and doctor --accept

The guardrail files (all of `.harness/engine`, `.harness/bin`, `.github/hooks`, `.harness/toolpacks`, `registry.json` and the shipped policies) are listed with size, time and sha256 when the person accepts them: at the board's first start, at its first start after the version in `registry.json` changed, by `harness doctor --accept`, by the board's Accept button in a paired browser, and when admin mode ends {src:.harness/engine/integrity.py#L1-L9}. At every tool call, prompt and session start the hook compares, except in a session the person switched to admin mode; while a file is changed, new or missing it refuses every terminal command and every tool that may change a file, and reads still pass. Its message says: after an upgrade, start the board; else accept or restore the files {src:.harness/engine/hook.py#L312-L360}.

`doctor --accept` is the person's: the gate refuses it on the agent's command line, and the command needs a terminal with keyboard and screen; it prints which files it takes in {src:.harness/policies/gate.json#L131-L137} {src:.harness/engine/doctor.py#L1017-L1112}.

## Setup: upgrading to a new version

**Same folder**: stop the board, put the new version over the copy (unzip, or check out the new tag), start the board; what git ignores stays. Shipped files (`AGENTS.md`, instructions, the harness's skills and policies) are replaced, so a person's own change to one must be backed up first; the company's copies come back because the board puts the company's content in place at each start {src:.harness/engine/modules/task/boardserve.py#L2283-L2296}. Until the board has started once, the hook refuses the agent's commands and writes with an "upgrade" message; that start accepts the new guardrail files {src:.harness/engine/integrity.py#L171-L210}.

**New folder**: `harness reinstall --from <old copy>` carries tasks, reports, goals, `runtime/` (not its debug capture or old port), override files, `.env`, `certs/`, the knowledge base (only into an empty one) and shipped files the company changed. It never overwrites, refuses a newer old copy, and ends with `company sync` and `doctor` {src:.harness/engine/core/reinstall.py#L1-L13}. Without `--apply` it only lists, and the agent may run that; `--apply` needs a person at a terminal, or **Coming from an older copy?** in Get ready {src:.harness/engine/core/reinstall.py#L300-L331}. The skill `harness-reinstall` guides it.

The skill `harness-vscode-updates` upgrades nothing: it turns VS Code release notes into advice for maintainers.

## Setup: what stays on the computer

The harness has no server of its own; the board listens on 127.0.0.1 only. What the agent reads and writes goes to GitHub Copilot's service, as without the harness. The harness's own code reaches the network for: `git fetch` of a target repository's base branch at the first fetch of a round and at every write-back dry run, which also fast-forwards the local base branch (offline, the local branch is used) {src:.harness/engine/modules/task/basesync.py#L1-L14}; one TLS connection, through the proxy, to read a certificate chain when the person presses **Make** for the CA bundle {src:.harness/engine/core/launchenv.py#L676-L690}; connection probes of the company's systems: from the board, with the person's identity, when the person presses Test, when it opens VS Code or when the Enter screen needs a fresh answer; and from the hook at the start of a chat, in VS Code's own identity, only for identities that exist in VS Code's window alone (`harness doctor` reports what the probes found and writes nothing there) {src:.harness/engine/modules/task/reachcheck.py#L1-L11} {src:.harness/engine/core/reach.py#L1-L10} {src:.harness/engine/modules/gate/commands.py#L162-L180}; a knowledge base update by `git fetch` from a folder the person names.

Setup keeps the person's identities (accounts, passwords, tokens of the connections) on the computer in `.harness/.env`, which git ignores; by design they never go into git, a log, a page or the knowledge base, and `harness reinstall` carries the file to a new copy {src:.harness/engine/core/connections.py#L1-L11} {src:.gitignore#L16-L18}. The gate refuses the agent a read of `.harness/.env`, a print of a variable that carries an identity, and a dump of the environment; this is a net, not a wall, with the gaps the files Gate and Tool packs list {src:.harness/engine/modules/gate/handler.py#L633-L650}. The hook's log of each call keeps no tool arguments, except the paths and the command of a call that was refused or held for the person, and there what looks like a password or token is masked, best effort; a call that went through leaves at most the paths it touched and a short hash of its terminal command {src:.harness/engine/core/callrecord.py#L1-L9} {src:.harness/engine/modules/observe/handler.py#L50-L61}.

## Setup: what is enforced by code, and who decides

**Code**: `doctor`'s checks and Finish setup's stop on an error; the hook's refusal while guardrail files are not as accepted (outside admin mode) {src:.harness/engine/hook.py#L312-L360}; the gate's refusal of the agent's `doctor --accept` and `task board`; Get ready only from the paired browser; `reinstall` never overwriting. **Text**: the steps of the skill `harness-reinstall` and the install guide. **The person**: installs programs, presses **Set it up** (only then is PATH changed), fills Get ready, starts the board after an upgrade, accepts or restores guardrail files, runs `reinstall --apply`.

## Setup: design, and what came before

- **A form, not a chat.** Before 1.6, setup was a skill in the Copilot chat plus override files by hand; Get ready needs no agent, so it spends no request and does not rely on the model {src:.harness/engine/core/setup.py#L1-L4}.
- **Fail closed, and a list outside the workspace** (1.7.38). Before, a hook whose engine could not load let every call pass; now `launch.py` refuses commands and writes. The list lives in the home folder: one the agent could rewrite would accept anything {src:docs/07-release-notes.md#L254-L255}.
- **Reinstall is a command** (1.5.8): hand copies lost `runtime/`, and with it which chat held which task {src:.harness/engine/core/reinstall.py#L1-L13}.

## Setup: common questions

**Q: Where does the harness run, and what does our team bring?** On each person's computer, as a copy opened in VS Code; the model is Copilot's. The person brings the decisions: confirming the requirement, approving the plan and the write-back with a code, and committing (see 00 Harness at a glance). The team brings the knowledge base, company skills, tool packs and target repositories, all optional at setup {src:.harness/engine/core/readyitems.py#L1-L19}.

**Q: What does `harness doctor` check, and what happens when we upgrade?** That the parts agree, plus Python, PATH, hook activity, repositories, knowledge base, packs and guardrail files. After an upgrade the agent's commands and writes are refused until the board starts once {src:.harness/engine/integrity.py#L171-L210}.

**Q: Does the harness send our code anywhere?** Not to a server of its own; it has none. The agent's work goes to GitHub Copilot as without the harness; the harness itself runs `git fetch` (and fast-forwards the local base branch), connection probes (also automatic) and the CA bundle check.


## Setup: limits

- **The integrity list stops slips and plain tampering, not a process that runs as the same user**, which can rewrite the list; without a list (before the board's first start) nothing is checked and `doctor` only warns {src:.harness/engine/integrity.py#L1-L9} {src:.harness/engine/doctor.py#L973-L998}.
- **A version change is accepted whole**: the first board start after it accepts every watched file as it then is, without listing what differs {src:.harness/engine/integrity.py#L171-L210}.
- **A hook that times out lets the call through**, and `doctor` cannot prove the hook runs: it reads the session logs {src:.harness/engine/doctor.py#L120-L155}.
- **`reinstall --apply` has no gate rule**, unlike `doctor --accept`; only its terminal test stands for the person {src:.harness/engine/core/reinstall.py#L300-L331}.
- **The Enter screen guards the board only**: the hook does not read whether Get ready was finished {src:.harness/engine/hook.py#L312-L360}.

## Setup: related files

The board, pairing and the Enter screen: 12 The board. Guardrail files and admin mode: 15 The gate and guardrails. Knowledge base: 18 Knowledge base. Packs, connections, sign-ins, MCP: 19 Tool packs, connections and MCP. Releases: 34 Version history. The code-level detail (launcher, Get ready's files and keys, policy layers, the checks in order, `doctor --accept`, the pinned Python, upgrade acceptance, what `reinstall` carries, how the board opens VS Code with the environment, why no install is run or guessed, supported session types): 24b Setup, doctor and upgrade internals. Code: `doctor.py`, `integrity.py`, `core/setup.py`, `modules/task/setupjob.py`, `core/reinstall.py` {src:.harness/engine/doctor.py#L1017-L1112}. To install step by step: the guide "Install the harness" in `AI Exploration/4 Install the harness/`.
