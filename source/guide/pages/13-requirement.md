---
title: Requirement and intake
subject: Requirement and intake
layer: concept
file: 13 Requirement and intake
harness_tag: 1.8.3
course: The book · 5.2 The agent writes the requirement, the person confirms it | https://smarshu.com/book/read/5-2-requirements.html
---
## Requirement and intake: what they are and what problem they solve

The requirement of a task is `REQ.md`, a page at the root of the task folder that the agent writes from what the person says and the documents they give, and that the person confirms. It has a "User confirmed" line and six sections: What to do; What not to do; Done when, as numbered items (`T1` shown by the task files, `R1` by a run the person does before the write-back, `A1` checked after deployment); Source; Not clear yet; Changes {src:.harness/contracts/templates/task/en/REQ.md#L1-L42}. Intake is how the person's documents get in: Word and Excel files are turned into Markdown and CSV by a program, with no AI, in the task's `REQ/` folder, which the agent reads and its edit tools cannot write {src:.harness/engine/modules/task/intake.py#L1-L11}. The problem solved: a request leaves things out, reads more than one way and changes over turns, so the plan, the work and the independent check go by one page the person has read, not by the chat {src:docs/05-design.md#L101-L109}.

## Requirement and intake: how the agent writes it, and the questions it asks

Writing `REQ.md` and asking are the agent's work, told by text; no code writes the requirement or judges what it says.

1. **Before the task**, the skill `harness-my-task` asks once, as numbered options: a new task or one to go on with; the kind; for `qa`, `rca`, `design` and `other`, whether a target repository changes. A look at a server or a small ticket chore is a `qa` task with no requirement {src:.github/skills/harness-my-task/SKILL.md#L20-L56}.
2. **Writing it.** From the `medium` tier on, `task new` makes `REQ.md` from the template and tells the agent to read `REQ/` and `REF/`, write the requirement as it understands it and ask the person to look {src:.harness/engine/core/messages.en.json#L14-L15}. What the person meant, nothing of the agent's own; what is unclear goes into "Not clear yet"; for kind `other`, "Done when" is asked first {src:.github/skills/harness-my-task/SKILL.md#L79-L110}.
3. **Asking until clear.** `generic-grill-me` looks facts up first and asks at most five questions a round, each with options and one recommended {src:.github/skills/generic-grill-me/SKILL.md#L24-L36}. With documents in `REQ/`, `generic-req-review` gives every item its source (file, section or sheet), checks the requirement against the knowledge base, and asks the five most blocking questions, numbered, only where documents contradict each other, are wrong, or do not match the knowledge base or the code {src:.github/skills/generic-req-review/SKILL.md#L24-L31}.
4. **Not finished.** While a line is still the template's `<...>`, the next-step text names the sections to finish, and the page shows "Requirement not finished" and no Confirm button {src:.harness/engine/modules/task/taskdesk.py#L538-L548}.

## Requirement and intake: where documents go, and what Intake does with them

The person gives documents on the **Intake** tab of the task page or with `harness task intake` in a terminal; both run the same code {src:.harness/engine/modules/task/commands.py#L318-L336}. The tab shows for an open task that has a `REQ.md` (tiers `medium` and `full`), and acts only for the paired browser {src:.harness/engine/modules/task/taskdesk.py#L509-L516}.

- **convert**: the original is kept untouched in `REQ/originals/`, its text is written beside it, and `<name>.convert.md` reports what was left out {src:.harness/engine/modules/task/intake.py#L278-L332}. A `.docx` becomes Markdown (headings, lists with Word's numbers as text, tables, footnotes, pictures in `REQ/media/`, tracked insertions, comments in a file of their own; headers, footers and contents dropped). An `.xlsx` becomes a CSV per sheet (hidden sheets, rows and columns skipped unless asked, merged cells repeated, formulas as last saved, colours counted, not kept) {src:.harness/engine/modules/task/intakeconvert.py#L1-L15}.
- **No AI**: a `.docx` or `.xlsx` is zipped XML read with Python's standard library, so it costs no tokens and changes no number. `.xls` and PDF need `xlrd` or `pypdf`, installed by the person; the harness never runs an install {src:.harness/policies/tools.json#L8-L11}.
- Text and pictures are kept as they are; `.doc`, `.pptx` and unknown types only as originals with a note; a file over 28 MB is refused on the Intake tab, over 60 MB by `task intake convert` in a terminal {src:.harness/engine/modules/task/intake.py#L37-L44} {src:.harness/engine/modules/task/taskdesk.py#L509-L516}.
- **paste** saves a copied table or text, the way out for a file too odd to convert; **init** makes `REQ/INTAKE.md`, a short goal (the kind of task, ask only what does not fit, "Human adds" for the person's lines, the knowledge base domain to scan) {src:.harness/contracts/templates/task/en/INTAKE.md#L1-L15}.
- On the tab the person trims a file (a CSV opens as a table), puts it back as converted, deletes, and copies a ready message that tells the agent to read `INTAKE.md` and the converted files and write `REQ.md` {src:.harness/engine/modules/task/intake.py#L1-L11}.

`REF/` holds reference material: files the person adds on the Files tab, an earlier task's conclusions copied by `task fork`, a hand edit kept by `task recover`; it is never written back {src:.harness/engine/modules/task/taskfork.py#L1-L10}. `INBOX/` holds results the person gives on the page (the file 11 Task). How the agent reads these is text: `INTAKE.md` first, the converted files, never the originals {src:.github/instructions/workspace.instructions.md#L13}. Code holds only this: for the chat that holds the task, the gate refuses the edit tools in `REQ/`, `REF/` and `INBOX/` {src:.harness/engine/modules/gate/handler.py#L64-L94}.

## Requirement and intake: how the person confirms the requirement

The person presses **Confirm requirement** on the task page or runs `harness task confirm-req` in their own terminal; the gate refuses it on the agent's command line {src:.harness/policies/gate.json#L131-L137}. The code to type comes from a sha256 of the whole `REQ.md`; the file is read again under the task's lock, a change meanwhile is refused, and the harness writes "confirmed" and the date into the line and keeps a digest in `.task/task.json` {src:.harness/engine/modules/task/task.py#L570-L612}. The digest covers only What to do, What not to do and Done when, so an answered question, a source or a line in Changes undoes nothing {src:.harness/engine/core/tasks.py#L117-L149}.

With a plan waiting, **Approve plan** (`task approve-plan --with-req`) confirms the requirement and approves the plan with one code over both files; the file 14 Plans and approvals explains that code.

What is only text: the code reads the confirmation line, not who wrote it, and the agent's edit tools may write `REQ.md` {src:.harness/engine/modules/task/taskreview.py#L88-L116}. A line the agent filled counts as confirmed only while no confirmation by the person is on record; after one, a change to the three sections counts as changed whatever the line says. At any time, deleting the line or `REQ.md` makes the state "none": nothing to confirm, and `approve-plan` approves the plan alone, with the person's code over `PLAN.md` only {src:.harness/engine/modules/task/task.py#L551-L567}. The agent is told never to touch the line {src:AGENTS.md#L51}.

## Requirement and intake: what happens when it changes after the plan was approved

The plan's approval keeps the digest of the requirement it was approved for, so a change to What to do, What not to do or Done when undoes it {src:.harness/engine/core/tasks.py#L152-L164}. Then, for the chat that holds the task, the gate refuses the edit tools under `DEV/`; the dry run and the write-back are refused; autorun stops; the stage falls back to the requirement {src:.harness/engine/modules/gate/handler.py#L64-L94}. `task approve-plan` alone is refused: the person reads both files and presses **Approve plan**, one code for both, or confirms and then approves {src:.harness/engine/modules/task/task.py#L443-L451}. The work in `DEV/` stays.

What is text: at every prompt of a task with a `REQ.md`, the hook tells the agent to change `REQ.md` first, with a line in Changes, when the person asks for something different, because an independent check goes by `REQ.md` only {src:.harness/engine/core/messages.en.json#L108}. A change said in the chat and never written into `REQ.md` undoes nothing.

## Requirement and intake: linked tickets

A task may name tickets of an outside tool (`ado:300100`), given in the New task window, on the task page, or by the agent with `task link add` for an id the person gave {src:.github/skills/harness-my-task/SKILL.md#L79-L110}. The harness keeps only the type and id; it copies nothing of the ticket into `REQ/` or `REQ.md` {src:.harness/engine/modules/task/tasklife.py#L612-L640}. Nothing tells the agent to read a linked ticket for the requirement; when the person names it, the tool pack's reads run without asking, and what the agent takes from it goes into `REQ.md` to be confirmed like any source {src:.harness/toolpacks/ado/skills/ado-workitem/SKILL.md#L14-L30}. Writes to tickets: the file 19.

## Requirement and intake: which tasks need a confirmed requirement

- **`light`** (`qa` by default): no `REQ.md`, no `REQ/`, no Intake tab {src:.harness/engine/modules/task/tasklife.py#L39-L45}.
- **`medium`** (`rca`, `design`, `other`): `REQ.md` and Intake are there and the page offers Confirm, but nothing waits for it and the agent is told not to ask {src:.harness/engine/modules/task/taskdesk.py#L533-L535} {src:.github/skills/harness-my-task/SKILL.md#L79-L110}.
- **`full`** (`dev`, `test`, `kb`, or a task raised to full): the board shows "the requirement waits for your confirmation" until it is confirmed or the plan approved {src:.harness/engine/modules/task/tasklife.py#L310-L315}.

The hard check is `task approve-plan`, in any tier: when `REQ.md` has a confirmation line, no plan is approved on a requirement unwritten, unconfirmed or changed {src:.harness/engine/modules/task/task.py#L443-L451}.

## Requirement and intake: what is enforced by code, and what is only an instruction

By code: the person's folders are closed to the task chat's edit tools; documents are converted by a fixed program; `confirm-req` and `approve-plan` need a person and a code, and the gate refuses them to the agent; a plan is refused on an unconfirmed or changed requirement when the line exists, and a change to the three sections undoes its approval {src:.harness/policies/gate.json#L131-L137} {src:.harness/engine/core/tasks.py#L152-L164}.

By instruction only: writing `REQ.md`, the questions, reading `INTAKE.md` and never the originals, changing `REQ.md` first, leaving the line alone {src:.github/skills/generic-req-review/SKILL.md#L24-L31}. Whether `REQ.md` says what the person meant only the person checks, by reading it.

## Requirement and intake: who decides what

The **person** chooses and trims the documents, writes "Human adds", answers, and confirms, again after each change. The **agent** writes `REQ.md` and picks the questions and sources. The **code** converts, closes the person's folders to the edit tools, fills the line, keeps the digest and refuses a plan on an unconfirmed or changed requirement {src:.harness/engine/modules/task/task.py#L570-L612}.

## Requirement and intake: why it is built this way, and what was tried before

**The agent writes, the person confirms.** The person's words are not kept as the requirement: a prompt leaves things out and the requirement changes over turns, so no single prompt is it {src:docs/05-design.md#L101-L109}.

**The confirmation grew into a gate.** At first the person edited the line by hand; then `confirm-req` filled it after a code (1.4.27). In 1.4.30 the plan was bound to three sections of the requirement, so a note in Changes undoes nothing {src:docs/07-release-notes.md#L2948-L2950}; in 1.5.30 a confirmed requirement became a condition of the plan, with one code for both {src:docs/07-release-notes.md#L2474}. Since 1.7.20 only `full` waits for it, because an analysis or a design goes from clues to result in one run {src:.harness/engine/modules/task/taskdesk.py#L533-L535}.

**Intake by a program (1.5.44).** A Word or Excel file is mostly layout; a model reading it spends tokens on that and may drop a part silently. So a program converts, keeps the original and says what it lost; the person, who knows which chapters matter, trims {src:docs/05-design.md#L204-L210}.

## Requirement and intake: where in the source

The templates in `.harness/contracts/templates/task/en/`; under `.harness/engine/`: `modules/task/task.py` (confirm, approve, `req_state`), `core/tasks.py` (the digest), `modules/task/taskreview.py` (the line), `modules/task/intake.py` and `intakeconvert.py` (Intake), `modules/task/taskdesk.py` (the tab, which tiers wait) {src:.harness/engine/modules/task/task.py#L570-L612}.

## Requirement and intake: common questions

**Q: Our requirements come as Word and Excel files. How does the agent get them, and is AI used to read them?** You drop them on the task's Intake tab: the original stays in `REQ/originals/`, a program writes Markdown or CSV beside it with a report of what it left out, and the agent reads those. No AI is used, so no tokens and no number changed {src:.harness/engine/modules/task/intakeconvert.py#L1-L15}.

**Q: How do I start a task and give the agent my requirement documents?** Start the board, say in one sentence what you want and where, let the agent ask and open the task, drop the documents on Intake, and confirm the `REQ.md` it writes with **Confirm requirement**. On screen: the harness tutorial "1 A day with the harness".

**Q: Can the agent confirm its own requirement?** Not with the command: the gate refuses it, and it asks a person for a code. But the code reads a text line of `REQ.md`, which the agent can write {src:.harness/engine/modules/task/taskreview.py#L88-L116}.

**Q: What if I change my mind after approving the plan?** Once `REQ.md` says so in its three sections, the plan's approval lapses: the task chat's edit tools are refused in `DEV/` (a terminal command is not checked there) and the write-back is refused until you approve both again with one code {src:.harness/engine/core/tasks.py#L152-L164}.

**Q: Does an RCA or design task need a confirmed requirement?** No: only a `full` task waits for it; a Q&A task has no `REQ.md` {src:.harness/engine/modules/task/taskdesk.py#L533-L535}.

## Requirement and intake: limits

- **The confirmation is a text line**: a line the agent filled counts only before the person's first confirmation; deleting the line or `REQ.md` at any time means nothing to confirm. The plan still needs the person's code {src:.harness/engine/modules/task/task.py#L551-L567}.
- **The person's folders are closed to the edit tools only.** `task intake` is not a person-only command, and the terminal checks do not cover `REQ/`, `REF/` or `INBOX/`, so a terminal copy or `harness task intake convert` run by the agent is not refused {src:.harness/engine/modules/gate/handler.py#L117-L139}.
- **Not reading the originals is an instruction**; nothing stops a read of `REQ/originals/` {src:.github/instructions/workspace.instructions.md#L13}.
- **The converter copies, it does not understand**: it cannot tell the important sheet, drops colours, and a number only in a picture is not read reliably {src:.harness/engine/modules/task/intakeconvert.py#L1-L15}.
- **A `medium` task does not wait for its requirement**: with no plan, a changed `REQ.md` stops nothing; with a `PLAN.md`, `approve-plan` holds it like any tier {src:.harness/engine/modules/task/taskdesk.py#L533-L535}.

## Requirement and intake: related files

The task, its tiers and folders: 11 Task. Approval codes and `--with-req`: 14 Plans and approvals. The gate: 15 The gate and guardrails. Checks against `REQ.md`: 17 Independent checks. The knowledge base: 18 Knowledge base. Tickets and connections: 19 Tool packs, connections and MCP. To do it step by step, see the harness tutorial "1 A day with the harness" in `3 Courses/Harness tutorials/` {src:.harness/engine/modules/task/intake.py#L1-L11}.
