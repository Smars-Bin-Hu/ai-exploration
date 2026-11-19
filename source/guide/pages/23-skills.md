---
title: Skills
subject: Skills
layer: concept
file: 23 Skills
harness_tag: 1.8.3
course: The book · 3.3 Instructions and skills, load only what you need | https://smarshu.com/book/read/3-3-instructions-and-skills.html
course: The book · 3.4 Turn your way of working into skills | https://smarshu.com/book/read/3-4-skills-and-workflows.html
---
## Skills: what they are and what problem they solve

A skill in GitHub Copilot is a folder `.github/skills/<name>/` holding a `SKILL.md` (front matter with `name` and `description`, then steps and gotchas) and optional `references/`, `templates/`, `scripts/`, `assets/`. Copilot reads only each skill's name and description at first, the whole `SKILL.md` when a request matches the description, and the other files when the body links to them; a person can load a skill by typing `/<name>` {src:.github/instructions/skills.instructions.md#L6-L12}. The harness ships 34 skills: 12 named `harness-*` and 22 named `generic-*` {src:.github/instructions/skills.instructions.md#L15-L31}. Skills solve a context problem: the know-how of every job cannot sit in every prompt, so only short core rules are always loaded and the how-to of a job is read when the job comes up {src:.github/instructions/skills.instructions.md#L6-L12}.

## Skills: how the harness uses skills next to code

In the harness, skills are instructions and code enforces. A skill gives the agent the order of work and the traps; the hook, the gate and the `harness` command line hold what must hold. Example: `harness-my-task` tells the agent to write `REQ.md`, then `PLAN.md`, then stop; the gate keeps `DEV/` closed to the task chat's edit tools until a person approves the plan {src:.github/skills/harness-my-task/SKILL.md#L75-L99} {src:.harness/engine/modules/gate/handler.py#L86-L90}. The rules for writing skills say a skill writes in the task folder only, never changes a target repository or the knowledge base, never switches on what only the person may, and stops where a step needs the person; each skill also names who starts it: `auto` (the agent, when it fits), `offer` (the agent asks first) or `user-only` {src:.github/instructions/skills.instructions.md#L34-L42}.

## Skills: the harness-* family

The `harness-*` skills are the harness's own: the meaning side of an engine module, or a flow for using the harness {src:.github/instructions/skills.instructions.md#L15-L31}.

- `harness-my-task`: open, go on with, switch or upgrade a task.
- `harness-task-fork`: start the next task from a finished one.
- `harness-task-archive`: move closed tasks to an archive folder.
- `harness-task-report` (user-only): where one task's time and usage went.
- `harness-agent-performance-review` (user-only): why a task's agent spent what it spent, and whose the waste was (see the file 22 Cost and usage).
- `harness-autorun` (user-only): get a task ready for autorun and set the scheduling rules.
- `harness-admin`: extend or debug the harness in admin mode, which the person switches on.
- `harness-reinstall`: carry tasks, runtime state and overrides to a new copy of the harness.
- `harness-vscode-updates` (user-only): advise what new VS Code releases mean for the harness.
- `harness-rookie-quick-start`: a newcomer's first lesson: a true story from request to branch, the chat and the board, and one practice task of kind `design`, which never touches a repository {src:.github/skills/harness-rookie-quick-start/SKILL.md#L13-L88}.
- `harness-rookie-wondering`: the deep course, 16 topics; the agent reads the harness's real files when its notes do not answer, and runs only read-only commands {src:.github/skills/harness-rookie-wondering/SKILL.md#L37-L73}.
- `harness-rookie-new-knowledgebase`: a wizard that builds a knowledge base from the team's code (see the file 18 Knowledge base).

There is no `harness-super` or `harness-ask` skill: those are markers the board writes so the gate makes a chat or turn read only {src:.harness/engine/modules/gate/superagent.py#L18-L20}.

## Skills: the generic-* family

The `generic-*` skills work for any domain {src:.github/instructions/skills.instructions.md#L15-L31}.

- **Requirement and plan:** `generic-grill-me` (ask until nothing is unclear), `generic-req-review` (write `REQ.md` from the intake files, list gaps), `generic-impact-analysis` (what a change touches across repositories and the knowledge base).
- **Doing and testing:** `generic-code-standards` (check code against the company's standards), `generic-evidence-run` (run a command on an environment, keep the output as evidence), `generic-test-guide` (a test guide for DEV, IST, UAT), `generic-capture-knowledge` (draft lessons; writes nothing into the knowledge base).
- **Long or wide work:** `generic-goal-driven` (user-only; goal and progress kept as files across sessions), `generic-mapreduce` (user-only; a big reading job split across read-only `mapper` subagents).
- **Knowledge base:** ten `generic-kb-*` skills, from `-toolkit-design` and `-toolkit-build` (user-only) to `-learn-batch`, `-refresh` and `-translate` (see the file 18 Knowledge base).
- **Skills and workflows:** `generic-workflow-design` (a routine done by hand becomes `WORKFLOW-DESIGN.md`), `generic-workflow-build` (user-only; builds it into skills and scripts with tests), `generic-build-new-skill` (make, check and test a skill, or repair its form) {src:.github/skills/generic-build-new-skill/SKILL.md#L34-L50}.

## Skills: who may start a skill, and how the board starts one

Eight skills carry `disable-model-invocation: true`: `harness-autorun`, `harness-agent-performance-review`, `harness-task-report`, `harness-vscode-updates`, `generic-goal-driven`, `generic-mapreduce`, `generic-workflow-build`, `generic-kb-toolkit-build`. Copilot does not load them for the agent; only the person's `/<name>` does. The agent could still open the `SKILL.md` with a read tool and follow it, since the gate never blocks a read; only text says not to. They spend much, change how a task runs, or are for the harness owner {src:.github/skills/harness-autorun/SKILL.md#L5} {src:.harness/engine/modules/task/skillsend.py#L26-L47} {src:.harness/policies/gate.json#L3}.

The board lists a skill in **Everything you can ask for** when its front matter has `board-opens`; the board keeps no list of its own, so a company skill appears the same way {src:.harness/engine/core/skillboard.py#L1-L12}. `board-opens` says what a click does:

- `chat`: a new chat whose first message is `/<name>` and the person's words, shown whole before **Start** {src:.harness/engine/modules/task/skillsend.py#L26-L47}.
- `reply`: a chip on a task page that puts `/<name>` in the reply box; the person presses Send {src:.harness/engine/modules/task/web/reply.js#L60-L72}.
- `task`: **New task** opens a task of the skill's kind. Since 1.8.2, for a user-only skill the first message only opens the task, and when that turn ends the board sends `/<name> <words>` to the same chat, once; for any other skill the first message says "Use the skill …" {src:.harness/engine/modules/task/chatnew.py#L91-L96} {src:.harness/engine/modules/task/vslink.py#L666-L700}.

So a board click counts as the person typing the command, and **Start autorun** likewise sends `/harness-autorun` itself after the person's choices and code.

## Skills: domain skills and company skills

A team's skills for one business domain live in the knowledge base, at `<knowledge base>/domains/<domain>/skills/<skill>/SKILL.md`, named `domain-<domain>-<name>`. Copilot does not see them, so they are not in the `/` menu and cost no context in other domains {src:.github/instructions/skills.instructions.md#L15-L31}. Once a task names its domains (`harness task set-domain`), the task hook adds a line to every prompt with those domains' skill names; the agent reads the `SKILL.md` and follows it, and `harness skill list --domain <d>` says when each is used {src:.harness/engine/modules/task/tasklife.py#L255-L263}.

A company's skills for every domain (a ticket tracker, a server) are `<skill_prefix>-<name>`, or `<skill_prefix>-<pack>-<name>` for a tool pack's, in `.github/skills/`; the company's word is `skill_prefix` in `company/company.json` in the knowledge base, and `harness company sync` copies by the word in the person's own `user.override.json`: when the company has skills or instruction files and the person's file has no word, or the two words differ (ignoring case), the sync stops before copying anything; when `company.json` has no word, the person's word alone is used. For `skill check`, `doctor` and the board's grouping the person's word wins and a difference is only a warning (the board's prefix button writes the word into the person's file; the file 23b Skills and text rules internals and the file 18b Knowledge base internals) {src:.harness/engine/core/company.py#L164-L174} {src:.harness/engine/core/skillcheck.py#L37-L57}. Written in the knowledge base's `company/skills/`, they are copied by `harness company sync`, which refuses a skill without the prefix or with a form error {src:.harness/engine/core/company.py#L165-L185}.

## Skills: AGENTS.md, instructions and skills

The harness keeps its text rules in four places, and one rule has one main source {src:AGENTS.md#L33-L40}: `AGENTS.md` (core rules and safety limits, in every chat); `.github/copilot-instructions.md` (what applies while running: after a refusal, approvals, git); `.github/instructions/*.instructions.md` (added when a file matching their `applyTo` is involved: `workspace`, `knowledgebase`, `skills`, `agents`); and skills (the how-to of one job, on demand). The task hook also adds lines to every prompt (session, language, the task's state and next step, domain skills), written from `messages.en.json` inside the engine {src:.harness/engine/modules/task/handler.py#L162-L177}. All of these ask the model; none blocks a call.

## Skills: how a team adds its own skill

A team asks the agent for a skill, and `generic-build-new-skill` writes it from the templates, runs `harness skill check <name>`, fixes every error, and tests that it loads and changes what the agent does, by running the same job with and without it; a company skill gets the prefix, and a domain skill is moved by the person from the task folder into the knowledge base {src:.github/skills/generic-build-new-skill/SKILL.md#L34-L50}. `board-*` keys put it on the board. `skill check` and `doctor` check form only, and `doctor` only warns {src:.harness/engine/core/skillcheck.py#L132-L202} {src:.harness/engine/doctor.py#L575-L589}.

## Skills: what is enforced by code, and what is only an instruction

**Copilot** keeps a `disable-model-invocation` skill from the agent. The harness adds its own check only for `generic-mapreduce`: the hook reads the person's prompt, and only a prompt that carries the skill gives the session a number of `mapper` calls (4 within 60 minutes, by the policy `task.json`); every other `mapper` call is refused {src:.harness/engine/modules/task/mapreduce.py#L1-L12}. For `harness-autorun` the gate guards the action: `task autorun on` is refused on the agent's command line {src:.harness/policies/gate.json#L131-L137}.

**Harness code, around skills:** a skill's own text never counts as the person's words, so a `[review]=1` or `[ZH]` in a skill's example does not switch checks or language (since 1.6.109) {src:.harness/engine/adapters/copilot_vscode.py#L71-L85}; the super agent chat and a `/harness-ask` turn cannot load skills, since the gate allows them only read, search and meta tools {src:.harness/engine/modules/gate/superagent.py#L18-L20}.

**Protection of skill files.** `.github/skills/`, `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/` and `.github/agents/` are not guardrail paths and not in the integrity list {src:.harness/policies/gate.json#L4-L19} {src:.harness/engine/integrity.py#L23-L26}. What the code does: the edit tools of a chat that holds an open task cannot write them, because they are outside its task folder; a chat with no task, admin or not, can write them with its edit tools; a terminal write to them is refused in no chat {src:.harness/engine/modules/gate/handler.py#L50-L139}. Domain skills and the `company/skills/` sources differ: in a knowledge base registered as a target repository (the usual setup), every chat is refused an edit-tool write there, and a terminal write that names the repository's full path, so through the harness they change by a task's approved write-back (any task kind; that it is a `kb` task is only an instruction); a terminal write by a relative path, a script or a path made at run time is not refused; only an unregistered `knowledge-base/` folder is open to the edit tools {src:.harness/engine/modules/gate/handler.py#L50-L139} {src:.harness/engine/modules/gate/policy.py#L149-L156} {src:.harness/engine/core/targets.py#L196-L242}. `generic-build-new-skill`'s repair flow counts on this and runs only in a chat with no task {src:.github/skills/generic-build-new-skill/references/repair.md#L7}. The lines the hook adds come from the engine, which is guarded.

**Only an instruction:** `auto` or `offer`, asking before a costly skill, every step and gotcha of every skill, and not following a user-only domain skill {src:.harness/engine/core/messages.en.json#L1155}.

## Skills: who decides what

The **person** starts every user-only skill and approves what a skill drafts; the **agent** picks `auto` and `offer` skills from their descriptions; **code** decides what the board lists, which `mapper` calls pass and what `company sync` copies {src:.harness/engine/core/skillboard.py#L1-L12}.

## Skills: why it is built this way, and what was tried before

**Text first, code where it matters.** A rule starts as text and moves into code when it is broken again and again, when breaking it cannot be undone, or when it breaks another part's premise. `generic-mapreduce` is the case where the skill flag was not trusted alone {src:.harness/engine/modules/task/mapreduce.py#L1-L12}.

**Changes.** 1.6.86 added the board's window of skills and retired the setup skill `harness-rookie-get-me-ready`, since a form now does setup with no agent {src:docs/07-release-notes.md#L1145-L1146}. 1.8.2 made user-only skills that open a task work from their button; before, the button told the agent to use a skill it could not load {src:docs/07-release-notes.md#L42-L46}.

## Skills: where in the source

Under `.harness/engine/` {src:.harness/engine/core/skillboard.py#L1-L12}: `core/skillcheck.py`, `core/skillboard.py`, `core/domainskills.py`, `modules/task/skillsend.py`, `chatnew.py`, `vslink.py`, `mapreduce.py`, `adapters/copilot_vscode.py`, `core/company.py`; the skills in `.github/skills/`, their rules in `.github/instructions/skills.instructions.md`.

## Skills: common questions

**Q: What skills come with the harness, and who may start them?** 34: 12 `harness-*`, 22 `generic-*`. The agent may load 26 when they fit; eight are user-only: Copilot loads them only from the person's `/<name>` or a board button {src:.github/skills/harness-autorun/SKILL.md#L5}.

**Q: Can the agent change a skill or AGENTS.md?** A skill in `.github/skills/` and `AGENTS.md`, yes: from a chat with no task, or by a terminal command from any chat, since they are not guardrail files; a chat holding a task cannot change them with its edit tools. A domain skill in a registered knowledge base, not by the edit tools or a terminal command that names its full path: through the harness it changes by a task's approved write-back, but a terminal write by a relative path is not refused (see 18 Knowledge base) {src:.harness/policies/gate.json#L4-L19} {src:.harness/engine/modules/gate/handler.py#L50-L139} {src:.harness/engine/modules/gate/policy.py#L149-L156}.

**Q: Where do our own business rules go?** One domain's rules go in the knowledge base as domain skills, named to the agent once a task names the domain; company-wide SOPs go in `company/skills/` with the company prefix {src:.github/instructions/skills.instructions.md#L15-L31}.

**Q: What do the two rookie skills cost?** Each is an ordinary Copilot chat and spends Credits like one; from the board it runs on Copilot Fusion at Standard when Copilot lists it. {src:.harness/engine/modules/task/boardserve.py#L1223-L1233}.

## Skills: limits

- **Skill files in `.github/skills/` and the text rules are unguarded** (domain skills in a registered knowledge base are guarded, except against a terminal write by a relative path): only the edit tools of a chat that holds a task are kept off them; a chat with no task, or a terminal command from any chat, can change them, and the harness does not notice {src:.harness/policies/gate.json#L4-L19}.
- **Copilot does not keep a user-only domain skill from the agent**: the agent reads it as a file, and only the prompt text says not to follow it {src:.harness/engine/core/messages.en.json#L1155}.
- **The 1.8.2 follow-up lives in the board's memory**: a board restart before the first turn ends loses it; after an hour it is dropped with a note on the task {src:.harness/engine/modules/task/vslink.py#L188}.
- **Six of the eight user-only skills rest on Copilot's flag alone**, which stops the skill from being loaded, not its file from being read and followed; `harness task performance`, which Agent Performance Review uses, is not person-only {src:.harness/policies/gate.json#L131-L137}.

## Skills: related files

00 Harness at a glance, 15 The gate and guardrails, 18 Knowledge base, 20 Autorun, 21 Super agent, 22 Cost and usage. For the code-level detail (text-layer files, what the hook injects, prefixes, `skillcheck.py`, the `board-*` keys, domain skills, language tables), see 23b Skills and text rules internals. How a person starts a skill from the board: the section "Skills: who may start a skill, and how the board starts one" of this file; the knowledge base skills in the order they are used: the file 18 Knowledge base {src:.harness/engine/core/skillboard.py#L1-L12}.
