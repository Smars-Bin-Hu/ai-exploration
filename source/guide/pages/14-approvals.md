---
title: Plans and approvals
subject: Plans and approvals
layer: concept
file: 14 Plans and approvals
harness_tag: 1.8.3
course: The book · 5.3 Two gates: where a person approves | https://smarshu.com/book/read/5-3-two-approvals.html
course: The book · 5.9 Who decides: code, a cheap model, the main model, a person | https://smarshu.com/book/read/5-9-who-decides.html
course: The book · 4.2 Asking is not a limit | https://smarshu.com/book/read/4-2-ask-vs-refuse.html
---
## Plans and approvals: what they are and what problem they solve

Plans and approvals are the points of a task where a person, not the agent, decides. A task that changes a code repository (`dev`, `kb`) passes two approvals: the plan (`PLAN.md`), before the edit tools of the task's chat may write in its `DEV/` folder and before anything in `DEV/` can be written back, and the write-back (promote), before the harness writes any file to the repository {src:.harness/engine/modules/gate/handler.py#L64-L94} {src:.harness/engine/modules/task/task.py#L911-L944}. Each approval is a six-capital code the person types, made from a sha256 of what they read, so it holds only for that version {src:.harness/engine/core/approval.py#L1-L25}. The problem solved: a confirmation box in the chat can be switched off (Allow all, "Allow in this Session"), so the decisions that cannot be taken back need a step the agent cannot take for the person {src:docs/05-design.md#L176-L182}.

## Plans and approvals: everything a person approves

Besides the plan and the write-back, a person decides the things below. The gate refuses each command of the list on the agent's command line; each runs in the person's own terminal or from a board button in the paired browser {src:.harness/policies/gate.json#L131-L144} {src:.harness/engine/modules/task/boardserve.py#L5-L16}.

| Decision | Terminal | Board | The code is made from |
|---|---|---|---|
| Confirm the requirement | `task confirm-req` | **Confirm requirement** | all of `REQ.md` |
| Approve the plan | `task approve-plan` | **Approve plan** | `PLAN.md`; with the requirement not confirmed, `REQ.md` and `PLAN.md` together (`--with-req`) |
| Approve the write-back | `task approve-promote` | **Approve promote** | the write-back plan: branch, base commit of each repository, path, action and sha256 of each file |
| Switch autorun on | `task autorun on` | the Start form | the task, its round, the plan and the steps of `TODO.md` |
| Number of independent checks | `[review]=n` in a message, `task review set` | check chips | no code |
| More checks, waive, dismiss one | `task review extend`, `waive`, `dismiss` | Review tab | the task's results |
| A held call to an outside system | `approve-action` | **Approve** on its card | a ticket for that exact command |
| A git write, once target repositories are set up | `approve-command` | none | a ticket for that exact command |
| Open a connection for one task | `task allow` | on a held card | no code; the board asks the held call's code |
| Accept and close, or close | `task close` | **Accept and close**, **Close** | no code |

The digests come from `task.py`, `promote_target.py` and `autorun.py`; a held call's ticket from `approvals.py` {src:.harness/engine/modules/task/task.py#L423-L471} {src:.harness/engine/modules/task/promote_target.py#L112-L116} {src:.harness/engine/modules/task/autorun.py#L125-L145} {src:.harness/engine/core/approvals.py#L50-L94}. The number of checks comes only from the person's own words, never the text of a skill, or the person's command {src:.harness/engine/modules/task/handler.py#L77-L81}. `task close` has no person check of its own, only the gate's refusal (see the file 11 Task).

## Plans and approvals: how an approval works

The approvals of the requirement, the plan, the write-back, autorun, more checks and a waiver each run one function, the same in the terminal and on the board, in four steps {src:.harness/engine/core/approval.py#L28-L58}:

1. **A person is checked for:** a terminal with a keyboard and a screen, or the board's Terminal window, which vouches for a command with a one-time code. A pipe or a script is refused.
2. **The screen names the file to read in the editor**, never its content, and says what the approval opens.
3. **The code is asked for.** It is the first six characters, in capitals, of the sha256 of what is approved, and the question shows it ("To approve this plan, type CC845C"); anything else cancels. The code is not a secret: it proves a person read and typed, and binds the yes to one version.
4. **The file is read again under the task's lock** before the approval is kept, so a plan or requirement changed while the person read is refused {src:.harness/engine/modules/task/task.py#L423-L471}. The write-back approval looks again only when the code came more than three seconds after the screen (1.7.43); `task promote` compares again before it writes {src:.harness/engine/modules/task/task.py#L984-L1024}.

Where the code is typed: in the person's own terminal, or in the window the board opens for an approval button. The board runs the same function in two steps, `preview` (the screen and the code) and `act` (with the code typed); a file changed between them has another code and is refused {src:.harness/engine/modules/task/boardserve.py#L5-L16}. The board's Terminal window has no keyboard behind it, so a command that asks for a code is refused there; it runs the person-only commands that ask for none, such as `task pause` or `task allow` {src:.harness/engine/core/boardperson.py#L1-L10}.

The records are kept in `.task/task.json`: the plan's digest with the digest of the requirement it was approved for, the confirmed requirement's digest (the harness also fills the "User confirmed" line of `REQ.md`), and the approved write-back plan {src:.harness/engine/modules/task/task.py#L551-L612}.

## Plans and approvals: why the agent cannot approve its own plan

The agent cannot approve its own plan by the ways the harness gives it (the file 11 Task has the detail). The gate refuses the person-only commands on its command line, read the way the shell reads them, so quotes, variables and `xargs` do not hide them {src:.harness/engine/modules/gate/harnesscmd.py#L1-L8}. Each approval command checks for a person at a terminal and asks for a typed code. The board acts only for its paired browser, and the gate refuses the agent's requests to the board's port {src:.harness/engine/modules/gate/handler.py#L580-L585}. The board's super agent approves nothing: its proposals are cards with the board's own buttons, which act only when the person presses them {src:.harness/engine/modules/task/superact.py#L1-L7}. The exceptions are in the section "Plans and approvals: limits".

## Plans and approvals: what happens when the plan or the requirement changes

An approval belongs to the version the person read; a change after it undoes the approval by itself, because each check compares the kept digest with the file as it is now {src:.harness/engine/core/tasks.py#L117-L164}.

- **`PLAN.md` changes.** The plan counts as not approved. For the chat that holds the task, the gate refuses the edit tools' writes under `DEV/` again; the dry run, the write-back approval and the write-back are refused; a running autorun stops with the reason `plan` {src:.harness/engine/modules/task/autorun.py#L308-L314}. The work in `DEV/` stays; the person approves the new plan with its new code.
- **What `REQ.md` asks changes.** The digest covers three sections: What to do, What not to do, Done when (blank lines and line breaks ignored). A change there makes the plan not approved and the requirement not confirmed; `task approve-plan` alone is refused, and the person confirms the requirement and approves the plan with one code (**Approve plan**, or `--with-req`) {src:.harness/engine/modules/task/task.py#L423-L471}. A change to the confirmation line, the sources, the open questions or the change record undoes nothing. A `REQ.md` with none of the three sections counts as a whole, but for the confirmation line.
- **The files to write back change.** A new dry run whose plan differs drops the write-back approval; the same plan keeps it. `task promote` writes only when the dry run and the approval are for the plan as it is now {src:.harness/engine/modules/task/task.py#L911-L944}.

The code sees only files: a change said in the chat and never written into `REQ.md` undoes nothing. The agent is told by text to change `REQ.md` first {src:.github/skills/harness-my-task/SKILL.md#L106-L114}.

## Plans and approvals: previews, and the approve-plan window on the board

**Previews in the Super agent view (1.8.3).** A plan approval waiting in the view shows the plan's steps, and a write-back approval the files it changes with their added and removed lines, unfolded with a click {src:docs/07-release-notes.md#L26}. The preview only reads: the numbered steps of `PLAN.md` (else its headings and top-level bullets), or the changed files, at most 12 lines of at most 160 characters, leaving out files the person runs by hand {src:.harness/engine/modules/task/superpreview.py#L1-L20}. A preview is a short look, not what is approved: the code binds the whole file, and the full plan and diff stay on the task page. The code window opens in the board page, also from the view's pop-out.

**"I will switch autorun on next: do not wake the agent" (1.8.0).** Since 1.7.38 the board sends the agent its "go on" message at once after the person confirms the requirement, approves the plan or approves the write-back there. The **Approve plan** window has a box for the person who will start autorun next: when ticked, the plan is approved, the board sends nothing, and the task's history notes it, so the approval does not start a turn before the Start form does {src:.harness/engine/modules/task/boardserve.py#L842-L852} {src:.harness/engine/modules/task/web/serve.js#L292-L324}. An approval typed in the terminal never wakes the agent; the board then shows that the agent has not been told.

When the requirement is not confirmed, the same **Approve plan** window says so, names the sections of `REQ.md` that are not finished, and its one code does both {src:.harness/engine/modules/task/web/serve.js#L292-L324}.

## Plans and approvals: held calls and Copilot's own asks

A held call is a command to an outside system (a database, a ticket board, a pipeline) that the company's rules say must wait for the person, by default a write. The gate refuses it once, records it with a code, and in a session that holds a task writes a draft into the task's `OUTBOX/` {src:.harness/engine/core/outbox.py#L1-L8}. The task page shows a card with the exact command; the person presses **View**, types the code and presses **Approve**, or **Do not approve**.

The approval lets that exact command, from the same session, run once within 10 minutes; the files it names are pinned as the person viewed them, and one changed since is asked about again. A request waits 24 hours {src:.harness/engine/core/approvals.py#L50-L94} {src:.harness/engine/core/outbox.py#L269-L302}. Unlike a plan's code, a held call's code is a ticket made from the session, the command and the time. Several calls of a task can be approved with one code for exactly the calls ticked. The agent waits in the same turn with `harness wait --approval <code>`. A subagent's held write, and any call that would wait for the person while autorun is on, is refused instead: nobody is there to approve it {src:.harness/engine/modules/gate/handler.py#L412-L433}. With target repositories set up, a git write is held the same way and approved with `approve-command`; without them only the ask list looks at git (see the file 15 The gate and guardrails).

Copilot's own ask is another thing: VS Code's box for a command on the gate's ask list (deleting files, network, installs), answered in VS Code or with Allow and Deny on the task page, with no code {src:.harness/engine/modules/task/chatask.py#L1-L8}. Under Allow all no box shows; every chat the board makes starts with Allow all, and **Start autorun** sets it, so an ask is a reminder, not a limit {src:.harness/engine/modules/task/chatnew.py#L25-L26}.

## Plans and approvals: what is enforced by code, and what is only an instruction

Enforced by code: the gate's refusal of the person-only commands (every spelling of `task allow` since 1.8.0); the person check of each command, and for the approvals a typed code bound to a digest; the board's paired browser; the lapse of a changed plan or requirement, which closes `DEV/` to the edit tools of the task's chat (not to its terminal) and blocks the dry run and the write-back; `task approve-plan` refusing while the "User confirmed" line of `REQ.md` is not filled in or the requirement changed since, when `REQ.md` has that line; `task promote` writing only the approved plan; autorun needing an approved plan, open steps and checks on; a held call running once, as approved {src:.harness/policies/gate.json#L131-L144} {src:.harness/engine/modules/task/task.py#L423-L471} {src:.harness/engine/modules/task/autorun.py#L125-L145}.

Only an instruction to the agent, text it can ignore {src:AGENTS.md#L48-L52} {src:.github/skills/harness-my-task/SKILL.md#L106-L114}:

- Leave the "User confirmed" line of `REQ.md` alone; only the person changes it. The line itself is plain text: the code reads it and does not check who wrote it {src:.harness/engine/modules/task/taskreview.py#L88-L117}.
- Write `PLAN.md`, stop, and ask the person to approve it on the task page; with the requirement not confirmed, ask for **Approve plan**, which does both.
- Change `REQ.md` first when the person changes their mind.

## Plans and approvals: who decides what

The person makes every decision in the table of the section "Plans and approvals: everything a person approves", answers Copilot's asks and commits the branch. Code decides whether an approval still holds and refuses what was not approved. The agent writes `REQ.md` and `PLAN.md`, runs the dry run, asks and waits; once approved, it writes `DEV/` and runs `task promote` {src:.harness/policies/gate.json#L131-L144} {src:.harness/engine/core/tasks.py#L117-L164}.

## Plans and approvals: why it is built this way, and what was tried before

**Asking is not a limit.** VS Code's confirmation box is skipped under Allow all and after "Allow in this Session", while a hook's refusal holds in every mode; so the approvals that matter are a code a person types, and the agent is refused the commands {src:docs/05-design.md#L176-L182}.

**Bind the key to what was read.** The code comes from the sha256 of the approved file, so a change after the person read it needs a new look; the screen names the file and never prints it, because a plan or a diff is read in the editor {src:.harness/engine/core/approval.py#L1-L25}. Since 1.5.30 a plan stands on a confirmed requirement, and the plan's approval now also keeps the requirement it was approved for {src:.harness/engine/modules/task/task.py#L423-L471}.

**The agent writes the requirement; the person confirms it.** An early build kept the person's own prompts as the requirement and was dropped the same day: a prompt leaves things out, and people change their mind over several turns. So `REQ.md` holds what the agent understood, the person's documents stay in `REQ/`, and the confirmation is a line in the file the agent writes {src:.harness/contracts/templates/task/en/REQ.md#L1-L6}.

**From the terminal to the board.** Since 1.4.4 the served board's buttons run the same function for the paired browser {src:docs/07-release-notes.md#L3341}. In 1.7.38 the codes of the requirement, the plan and the write-back became six capitals like a held call's (the requirement's had been eight small characters), the agent names the button instead of a command, and an approval on the board wakes the agent {src:docs/07-release-notes.md#L283}. 1.7.39 let the board's Terminal window count as the person for commands that ask no code, 1.8.0 added the "do not wake" box, 1.8.3 the previews.

**Held calls wait a day.** Since 1.7.9 a request waits 24 hours (ten minutes lost calls while the person looked elsewhere), and an approval is good for ten minutes, so a stale yes never fires {src:docs/07-release-notes.md#L686}.

## Plans and approvals: where in the source

Under `.harness/engine/` {src:.harness/engine/core/approval.py#L1-L25}: `core/approval.py` (person check, code); `core/tasks.py` (digests, whether the plan is approved now); `modules/task/task.py` (`approve-plan`, `confirm-req`, `approve-promote`, `promote`, `recover`); `modules/task/taskreview.py` (the confirmation line, the check counts); `modules/task/promote_target.py` (the write-back plan's digest); `modules/task/autorun.py` (switching autorun on); `core/approvals.py` and `core/outbox.py` (held calls and git writes); `modules/task/boardserve.py` and `web/serve.js` (the approval windows, the "do not wake" box); `modules/task/superpreview.py` (the previews). The person-only commands are in `.harness/policies/gate.json`.

## Plans and approvals: common questions

**Q: How is the code made, and can the agent read it?** The first six capitals of a sha256 of what is approved, shown with the question. Reading it does not help the agent: it cannot run the command or reach the board {src:.harness/engine/core/approval.py#L1-L25}.

**Q: Can the agent approve its own plan?** Not by the ways the harness gives it. Two exceptions remain: the requirement's confirmation line is text the agent can write, and the approval records are files a script could change {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.

**Q: I approved the plan, then the requirement changed. What now?** When what `REQ.md` asks changed, the approval lapses and `DEV/` closes to the edit tools of the task's chat; read both files and press **Approve plan**, which confirms the requirement and approves the plan with one code {src:.harness/engine/modules/task/task.py#L423-L471}.

**Q: Why did the agent not start after I approved the plan?** The code was typed in a terminal, which does not wake the agent; or the box "I will switch autorun on next" was ticked; or the board could not reach the chat. Send the "go on" message from the task page, or start autorun {src:.harness/engine/modules/task/boardserve.py#L842-L852}.

**Q: What is the difference between a held call and Copilot's ask?** A held call is refused by the gate and waits for the person's code; Copilot's ask is VS Code's own box, answered without a code and not shown under Allow all. The harness tutorial "3 When the agent is stopped" shows both.

## Plans and approvals: limits

- **The requirement's confirmation is a line of text.** The agent's edit tools may write the "User confirmed" line of `REQ.md`, and a line it fills counts as confirmed; a missing `REQ.md`, or one with no such line, counts as nothing to confirm, so the plan is approved alone {src:.harness/engine/modules/task/taskreview.py#L88-L117} {src:.harness/engine/modules/task/task.py#L551-L612}.
- **The approval records are files.** They are in `.task/task.json`; the edit tools and a terminal command that names it are refused, but a script the agent writes and runs is checked only for guardrail paths {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11}.
- **`DEV/` is closed only to the edit tools of the chat that holds the task.** Its terminal commands, and a chat with no task, are not kept out of `DEV/` before the plan is approved; what code guarantees is that nothing in `DEV/` is written back without an approved plan and an approved write-back {src:.harness/engine/modules/gate/handler.py#L64-L94} {src:.harness/engine/modules/task/task.py#L911-L944}.
- **The write-back is not the only way into a repository.** The harness itself writes a target repository only through `task promote`, and the gate refuses the edit tools and terminal commands that name a target repository; but the gate reads text, so a script, or a path built at run time, is not seen, and a git write the person approves with `approve-command` changes a repository without a write-back (see the file 15 The gate and guardrails, limits) {src:.harness/engine/modules/gate/scriptcheck.py#L1-L11} {src:.harness/engine/modules/gate/handler.py#L153-L162}.
- **Some decisions ask for no code.** `task review set`, `task allow`, `task test runner`, `task pause` and `task resume` check for a person but ask no typed code, because the harness counts them as changes that can be undone; accepting and closing are kept from the agent by the gate and the paired board, not by a person check in `task close` {src:.harness/engine/modules/task/taskreview.py#L476-L480} {src:.harness/engine/modules/task/tasklife.py#L543-L548}.
- **After the plan is approved, some outside calls need no further approval:** a call the company's rules mark `task`, and a write on a connection the person opened for the task {src:.harness/engine/modules/gate/handler.py#L287-L308}.
- **The board refuses a decision while the agent is in the middle of a turn,** except the settings (`review set`, `task allow`, `task link`, `test runner`); a task that waits for the person is not at work {src:.harness/engine/modules/task/boardserve.py#L685-L695}.

## Plans and approvals: related files

- The task and its stages: the file 11 Task. The whole harness: the file 00 Harness at a glance. The requirement: the file 13 Requirement and intake. The write-back: the file 16 Write-back.
- Held calls and connections: the file 19 Tool packs, connections and MCP. Git writes and person-only commands: the file 15 The gate and guardrails. Checks: the file 17 Independent checks. Autorun: the file 20 Autorun. The Super agent view: the file 21 Super agent.
- To do it step by step, see the harness tutorials in `3 Courses/Harness tutorials/`: "1 A day with the harness", "3 When the agent is stopped", "4 Independent checks", "5 Outside systems and connections".

The gate's person-only rules name every terminal command of the table {src:.harness/policies/gate.json#L131-L144}.
