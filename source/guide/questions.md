# Harness Guide: questions the agent must answer

The acceptance test for the Harness Guide agent: 50 questions, pinned to harness **1.8.3**. Each question has the key points a right answer must contain, the Guide files it should cite and the course or tutorial it should name. Answers are graded against these. This file is **not** a knowledge source of the agent: it stays outside `AI Exploration/2 Ask the Harness Guide/Knowledge/`.

The Guide helps people understand the harness; it is not a tutorial. Its questions come in four layers, from shallow to deep, plus two kinds of test:

- **Layer 1 · the harness:** what it is, what problem it solves.
- **Layer 2 · features:** its common features (task, board, approvals, checks, autorun, tool packs…).
- **Layer 3 · design:** how it is designed and built, where in the source, which test guarantees what, what changed in which version, known bugs.
- **Layer 4 · ideas:** the harness engineering knowledge behind it; the answer links the course on smarshu.com that teaches it.
- **Operate:** "how do I…". The right answer is short (a few sentences from the Guide), then names the harness tutorial that teaches it step by step, in `AI Exploration/3 Courses/Harness tutorials/`: `0 MUST READ`, `1 A day with the harness`, `2 A tour of the harness`, `3 When the agent is stopped`, `4 Independent checks`, `5 Outside systems and connections`, `6 Knowledge base`.
- **Not covered:** the right answer says "The Harness Guide does not cover this yet." and makes nothing up.

How to read each entry:

- **Layer · type · grain.** Type is one of `use` (what it does for me), `how` (how a feature works), `safety` (is it safe, can it be bypassed), `code` (where in the code, which test), `version` (what changed, which bug), `idea`, `operate`, `not-covered`. Grain is `broad` (the whole design) or `detail` (one mechanism).
- **Key points:** each one a fact checked against the harness code at tag `1.8.3` (`git -C ~/Developer/DE-agentic-harness show 1.8.3:<path>`), with its location as `path:lines`. The locations are for the grader: a right answer gives the Guide's own links for what it says; it need not repeat every location listed here. A right answer has every point; it may say them in other words.
- **Should cite:** the Guide files the answer should be built on, by their names. The knowledge is 23 files: 00 Harness at a glance · 01 Glossary · 11 Task · 12 The board · 13 Requirement and intake · 14 Plans and approvals · 15 The gate and guardrails · 16 Write-back · 17 Independent checks · 18 Knowledge base · 19 Tool packs, connections and MCP · 20 Autorun · 21 Super agent · 22 Cost and usage · 23 Skills · 24 Setup, doctor and upgrade · 31 How it is built · 32 Code map · 33 Test map and evals · 34 Version history · 35 Known limits · 36 Design decisions · 41 Ideas behind the harness. Citing another file that holds the same fact is not wrong. `21 Start a task and give it the requirement` is not knowledge: an answer that cites it, or sends the reader to it, is wrong.
- **Course:** the link the answer should give, when one fits. A Layer 4 answer always gives one. `AGENT.md` tells the agent to link the course of the file its answer is mostly built on, so any course listed in that file's front matter is also right.
- **Wrong if:** what makes an otherwise good answer wrong.
- Every answer must come from the Guide only. An answer that uses the asker's own work (their repository, mail, chats, files) to make an example is wrong, whatever else it gets right.
- The person signs off the expected answers of the `safety` questions: Q3, Q8, Q9, Q17, Q24, Q26, Q27, Q28, Q34, Q35, Q42. A `safety` answer that says more than the points allow ("the agent cannot do anything unsafe") or drops a limit the points name is wrong; no `safety` question may be answered wrong at acceptance.

History: the first pilot's P1–P15 are in git (commit 74cab51) and are not used. Q1–Q15 are the second pilot's questions, kept with their ids and their answers moved to 1.8.3. Q15 was "not covered" at 1.7.45; autorun now has its own file (20 Autorun), so Q15 is a Layer 2 question.

## The 50 questions

| # | Question | Layer | Type | Grain | Should cite |
|---|---|---|---|---|---|
| Q1 | What is this harness, and what problem does it solve? | 1 | use | broad | 00 |
| Q2 | Where does the harness run, and what does our team have to bring to it? | 1 | use | broad | 00, 24 |
| Q3 | Is the harness a sandbox? What does it protect against, and what not? | 1 | safety | broad | 00, 35 |
| Q16 | Why should my team use the harness instead of plain Copilot chat? What changes for us? | 1 | use | broad | 00, 11 |
| Q17 | Does any of our code or data leave our computers because of the harness? | 1 | safety | broad | 00, 15, 19 |
| Q18 | Which rules does code enforce, which are only asked of the model, and which are left to a person? | 1 | how | broad | 00 |
| Q19 | What does running the harness cost us? Does the harness itself spend tokens? | 1 | use | broad | 22, 00 |
| Q20 | What are the main parts of the harness, and who provides each? | 1 | how | broad | 00, 31 |
| Q4 | What is a task, and how is it different from a chat session? | 2 | use | broad | 11 |
| Q5 | What kinds of tasks are there, and how does each one end? | 2 | use | detail | 11, 00 |
| Q6 | What does the board show, and what does "waiting for you" mean? | 2 | use | detail | 11, 12 |
| Q15 | How does autorun work? Can a task run on its own overnight? | 2 | how | detail | 20 |
| Q21 | Our requirements come as Word and Excel files. How does the agent get them, and is AI used to read them? | 2 | how | detail | 13 |
| Q22 | What exactly does a person approve, and what makes an approval lapse? | 2 | how | detail | 14, 11 |
| Q23 | What are independent checks, and how is a pass counted? | 2 | how | detail | 17 |
| Q24 | When the work is written back, does the agent commit or push to our repository? | 2 | safety | detail | 16 |
| Q25 | What is the knowledge base, and how does the agent use it? | 2 | how | detail | 18 |
| Q26 | How does the agent reach systems like SQL Server or Azure DevOps, and who decides what it may do there? | 2 | safety | detail | 19 |
| Q27 | Can we connect an MCP server? Does the harness check its tools? | 2 | safety | detail | 19, 35 |
| Q28 | What is the super agent on the board, and can it do things on its own? | 2 | safety | detail | 21 |
| Q29 | How do I see what a task cost, and where do the numbers come from? | 2 | use | detail | 22 |
| Q30 | What skills come with the harness, and who may start them? | 2 | use | detail | 23 |
| Q31 | What does `harness doctor` check, and what happens when we upgrade the harness? | 2 | how | detail | 24 |
| Q32 | If the agent makes a mess in a task, can I go back? | 2 | use | detail | 11, 16 |
| Q7 | How does a task move from one stage to the next? Is that controlled by a skill or by code, and where in the code? | 3 | code | detail | 11 |
| Q8 | How does the gate block dangerous commands, and where are its rules? | 3 | safety | detail | 15, 00 |
| Q9 | How does the approval code work, and why can't the agent approve its own plan? | 3 | safety | detail | 14, 11 |
| Q33 | How do the hooks plug into Copilot? Which events, and which file is the entry point? | 3 | code | detail | 31, 32 |
| Q34 | What happens when the harness itself breaks, say a bug in the gate or a broken policy file? | 3 | safety | detail | 15, 31 |
| Q35 | Can the agent change the harness's own rules or code? | 3 | safety | detail | 15 |
| Q36 | Where in the code is the board, and how does it make sure only the person presses its buttons? | 3 | code | detail | 12, 32 |
| Q37 | Which test guarantees that the agent cannot run `approve-plan` itself? | 3 | code | detail | 33 |
| Q38 | How is the harness itself tested? What are the eval scenarios? | 3 | code | broad | 33 |
| Q39 | What changed in 1.8.0? | 3 | version | detail | 34, 20 |
| Q40 | What changed in 1.8.1, 1.8.2 and 1.8.3? | 3 | version | detail | 34, 21 |
| Q41 | I heard the agent could open a connection for itself with `task allow`. Is that a bug, and is it fixed? | 3 | version | detail | 34, 35, 19 |
| Q42 | What are the known ways round the harness in 1.8.3? | 3 | safety | broad | 35, 00 |
| Q43 | Why is so much worked out from files each time (the stage, the passes, the approvals) instead of being stored? | 3 | code | detail | 36 |
| Q10 | Why isn't a rule in the prompt or in `AGENTS.md` enough to keep the agent safe? | 4 | idea | broad | 41, 00 |
| Q11 | Why does the harness keep the work in tasks instead of in the chat? | 4 | idea | broad | 41, 11 |
| Q12 | What is the idea behind the approval gates, and where does a person hold the keys? | 4 | idea | detail | 41, 14, 00 |
| Q44 | Why does a separate reviewer check the work, instead of the agent checking itself? | 4 | idea | broad | 41, 17 |
| Q45 | Why does the harness use scripts for so much, instead of letting the model do it? | 4 | idea | broad | 41, 22 |
| Q46 | Why give a coding agent a knowledge base instead of letting it read the code? | 4 | idea | broad | 41, 18 |
| Q13 | I maintain a data pipeline repository. How do I start a task and give the agent my requirement documents? | operate | operate | detail | 00, 13 |
| Q14 | The agent says my command was refused. How do I get it run? | operate | operate | detail | 15, 00 |
| Q47 | How do I let the agent run queries on our SQL Server database? | operate | operate | detail | 19 |
| Q48 | How does the harness compare with Cursor or Claude Code? Should we switch? | none | not-covered | broad | none |
| Q49 | How many teams in our company use the harness, and how much time has it saved them? | none | not-covered | broad | none |
| Q50 | When is the next harness version coming, and what will it contain? | none | not-covered | detail | none |

Counts. By layer: Layer 1: 8; Layer 2: 16; Layer 3: 14; Layer 4: 6; operate: 3; not covered: 3. By type: use 10, how 8, safety 11, code 6, version 3, idea 6, operate 3, not-covered 3. By grain: broad 18, detail 32.

## Layer 1 · the harness

### Q1. What is this harness, and what problem does it solve?

Layer 1 · use · broad.

- A set of files and Python code that wraps the GitHub Copilot agent in VS Code so that a team can let it work on real code under rules; version 1.8.3 (`.harness/registry.json:3`).
- The problem: rules written only for the model ask it, and it can ignore them; the harness turns the rules that must hold into code and leaves what cannot be taken back to a person (`AGENTS.md:42-58`; `.harness/engine/modules/task/handler.py:93-126`).
- Three things. A hook checks every tool call of the agent before it runs (`.github/hooks/harness.json:4-100`; `.harness/engine/hook.py:2-9`). Work is done in tasks, folders with the requirement, the plan, the results and a state file; opening one is asked of the agent by text, not forced (`.harness/engine/core/tasks.py:1-8`; `AGENTS.md:46-47`). A person approves the plan and every write-back to a code repository with a typed code, and confirms the requirement the same way, though that confirmation is a text line the agent can write (`.harness/engine/core/approval.py:1-8`; `.harness/engine/modules/task/taskreview.py:88-110`).
- It is not a sandbox: it guards against an agent's mistakes, not against an agent set on getting round it (`.harness/engine/modules/gate/terminal.py:1-5`).

Should cite: 00 Harness at a glance ("Harness: what it is", "Harness: the parts and how a piece of work flows through them", "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person"). Course: The book · 0.1 What is Harness Engineering? (https://smarshu.com/book/read/0-1-the-gap-and-the-map.html).

Wrong if: it calls the harness a sandbox or a security boundary; it names a version other than 1.8.3.

### Q2. Where does the harness run, and what does our team have to bring to it?

Layer 1 · use · broad.

- The harness has no server of its own: the board, its only web server, runs on the person's computer and listens on 127.0.0.1 only (`.harness/engine/modules/task/boardserve.py:8-9`). It needs Python 3.9 or later and no required package (`.harness/engine/doctor.py:65-71`; `.harness/engine/doctor.py:627-628`).
- The model runs in GitHub Copilot's service: the harness's agents name Copilot models (`.github/agents/reviewer.agent.md:5`; `.github/agents/super.agent.md:6`).
- The harness carries no business knowledge. The team plugs in its own knowledge base, skills and target repositories, the company repositories the agent may change, set in `target.override.json` (`AGENTS.md:11-15`; `.harness/engine/core/targets.py:1-6`). A company may bring tool packs, which let the agent call an outside system under the gate's rules (`.harness/engine/core/toolpacks.py:1-3`).
- The person brings the decisions: confirming the requirement, approving the plan and the write-back, committing the branch (`.harness/policies/gate.json:131-137`; `.harness/engine/modules/task/promote_target.py:5-6`).

Should cite: 00 Harness at a glance; 24 Setup, doctor and upgrade. Course: The book · 0.1 What is Harness Engineering?

Wrong if: it says the harness sends code or data to a server of its own; it makes up install steps.

### Q3. Is the harness a sandbox? What does it protect against, and what not?

Layer 1 · safety · broad.

- No. The gate reads the text of a command, so the harness guards against an agent's mistakes, not against an agent set on getting round it; the agent's commands run as the person's own user (`.harness/engine/modules/gate/terminal.py:1-5`; `.harness/engine/integrity.py:8`).
- What it protects most: the harness writes a target repository only through `task promote`, in the version the person approved (one plan digest over branch, base commit of each repository and sha256 of every file), to a new branch, never committed; a registered knowledge base gets one commit on its base branch (`.harness/engine/modules/task/task.py:941-944`; `.harness/engine/modules/task/promote_target.py:1-10`; `.harness/engine/modules/task/promote_target.py:112-116`). A git command the person approves with `approve-command` can also write there (`.harness/engine/modules/gate/handler.py:154-162`).
- Also: approvals need a person and a typed code, and the gate refuses every person-only command on the agent's command line, `task allow` included since 1.8.0 (`.harness/policies/gate.json:131-137`; `.harness/engine/core/approval.py:17-58`); guardrail files are refused and, once accepted, checked against the accepted list before every call, except in an admin chat (`.harness/policies/gate.json:4-19`; `.harness/engine/hook.py:312-326`); when the engine cannot decide, commands and writes are refused and reads stay allowed (`.harness/engine/hook.py:11-15`).
- What not, at least three of: the terminal is not confined to the task folder (`.harness/engine/modules/gate/handler.py:117-139`); a script or a path made at run time is not seen (`.harness/engine/modules/gate/scriptcheck.py:1-11`); a tool not recorded in `tool_kinds.json` gets no write check (`.harness/engine/adapters/tool_kinds.json:3`; `.harness/engine/modules/gate/handler.py:778-781`); the ask rules are only Copilot's confirmation, absent under Allow all, which every board-made chat starts with (`.harness/engine/modules/task/chatnew.py:25`); the board's **▶ Run** and Terminal window run the person's commands without the gate (`.harness/engine/modules/task/taskrun.py:1-8`); admin mode opens the guardrails (`.harness/engine/core/guardrails.py:21-23`).

Should cite: 00 Harness at a glance ("Harness: the main safety guarantees and their exact scope", "Harness: known limits"); 35 Known limits. Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can (https://smarshu.com/writing/basic-06-prompt-cannot-stop).

Wrong if: it reassures beyond the Guide ("the agent cannot do anything unsafe"); it drops the limits; it still says `task allow --conn` is not refused (that was 1.7.38 to 1.7.46).

### Q16. Why should my team use the harness instead of plain Copilot chat? What changes for us?

Layer 1 · use · broad. A leader's question.

- The work outlives the chat: each piece of work is a task folder with requirement, plan, results and state, and any later chat goes on from it (`.harness/engine/core/tasks.py:1-8`; `.harness/engine/modules/task/task.py:174-209`).
- One board lists every task, what it waits for and since when (`.harness/engine/modules/task/tasklife.py:276-338`; `.harness/engine/modules/task/boardserve.py:1-9`).
- Nothing reaches a code repository before a person approves the plan and then the exact write-back, each with a typed code (`.harness/engine/modules/gate/handler.py:86-90`; `.harness/engine/modules/task/task.py:941-944`).
- A hook checks every tool call: dangerous commands are refused and git writes wait for the person (`.harness/policies/gate.json:88-130`; `.harness/engine/modules/gate/gitcmd.py:30-37`).
- "Done" comes with evidence: independent checks by a separate reviewer, counted by code, and a report per task written from the logs (`.harness/engine/modules/task/taskreview.py:1-4`; `.harness/engine/modules/task/task_report.py:1-5`).

Should cite: 00 Harness at a glance; 11 Task. Course: The book · 0.1 What is Harness Engineering?, or Basic 01 · Stop using AI the 2024 way (https://smarshu.com/writing/basic-01-stop-using-ai-the-2024-way).

Wrong if: it promises results the Guide does not measure (time saved, fewer bugs).

### Q17. Does any of our code or data leave our computers because of the harness?

Layer 1 · safety · broad.

- The harness runs no server of its own; the board listens on 127.0.0.1 only and answers only to the Host and Origin of that address (`.harness/engine/modules/task/boardserve.py:8-9`; `.harness/engine/modules/task/boardserve.py:1673`).
- The model is Copilot's: what the agent reads goes to GitHub Copilot's service as it does without the harness; the harness names Copilot models for its agents (`.github/agents/super.agent.md:6`; `.github/agents/worker.agent.md:6`).
- Identities for outside systems are kept in `.harness/.env` on the person's computer, never in git, a log, a page or the knowledge base, and the gate refuses the agent a read of that file or a print of a secret variable (`.harness/engine/core/connections.py:10-11`; `.harness/engine/modules/gate/handler.py:633-650`).
- The call log keeps no tool arguments, except the paths and command of a call that was refused or sent to a person (with passwords and tokens masked) and the paths a finished call touched (`.harness/engine/core/callrecord.py:1-9`; `.harness/engine/modules/observe/handler.py:50-60`). Copilot's own record is read for numbers only (`.harness/engine/core/copilot_events.py:7-11`).

Should cite: 00 Harness at a glance; 15 The gate and guardrails; 19 Tool packs, connections and MCP. Course: The book · 4.5 Some things you never hand over (https://smarshu.com/book/read/4-5-least-privilege.html).

Wrong if: it says nothing leaves the computer at all (the model is a cloud service); it says the harness sends anything to a server of its own.

### Q18. Which rules does code enforce, which are only asked of the model, and which are left to a person?

Layer 1 · how · broad.

- Code (the hooks and the command line) enforces what must hold: for the chat that holds a task, `DEV/` stays closed to the edit tools until the plan is approved; the write-back needs a dry run and an approval of the same digest; guardrail files and dangerous commands are refused (`.harness/engine/modules/gate/handler.py:64-94`; `.harness/engine/modules/task/task.py:941-944`; `.harness/policies/gate.json:4-19`).
- Text asks the model, which can ignore it: `AGENTS.md`, `.github/instructions/`, skills and the lines the hook adds to every prompt; example: opening a task before producing files is text only (`AGENTS.md:46-47`; `.harness/engine/core/messages.en.json:14-15`).
- A person decides what cannot be taken back: confirm the requirement, approve the plan and the write-back, approve git writes and held outside calls, switch autorun on, commit, accept or close (`.harness/policies/gate.json:131-144`; `.harness/engine/core/approval.py:28-58`).
- The exception to name: the requirement's confirmation is a text line in `REQ.md` that the agent can write (`.harness/engine/modules/task/taskreview.py:88-110`).

Should cite: 00 Harness at a glance ("Harness: what is enforced by code, what is asked of the model by text, and what is left to a person"). Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can.

Wrong if: it says everything is enforced by code, or drops the requirement exception.

### Q19. What does running the harness cost us? Does the harness itself spend tokens?

Layer 1 · use · broad. A leader's question.

- The harness itself is local Python with no required package; its hooks, task commands and checks call no model: document conversion, the knowledge base checks and autorun's stop rules are code (`.harness/engine/doctor.py:65-71`; `.harness/engine/modules/task/intakeconvert.py:3-4`; `.harness/engine/core/kbstd.py:10-11`; `.harness/engine/modules/task/autorun.py:7`).
- What costs Copilot Credits is model use. Three features spend more, each switched on by the person and capped: independent checks (n + 2 checks, then the person decides) (`.harness/policies/task.json:9-13`; `.harness/engine/modules/task/taskreview.py:19-20`); autorun (a spend limit picked at Start, recommended 500, 1000 or 2000 Credits by the number of steps) (`.harness/engine/modules/task/autorun.py:86-89`; `.harness/engine/modules/task/autorun.py:148-168`); the super agent chat (50 Credits a day by default) (`.harness/policies/task.json:25-27`).
- The report and the board read the Credits and premium requests from Copilot's own session record, not from the agent's word (`.harness/engine/core/copilot_events.py:1-11`; `.harness/policies/task.json:21-24`).

Should cite: 22 Cost and usage; 00 Harness at a glance. Course: The book · 1.1 Don't pick a model by token price alone (https://smarshu.com/book/read/1-1-models-and-cost.html).

Wrong if: it gives money figures or Copilot licence prices (the Guide has none).

### Q20. What are the main parts of the harness, and who provides each?

Layer 1 · how · broad.

- Hooks: `.github/hooks/harness.json` makes VS Code run one Python entry point at nine events, from session start to stop (`.github/hooks/harness.json:4-100`; `.harness/engine/launch.py:2-5`).
- Modules registered in `registry.json`: `task`, `gate`, `observe`, `evalcheck`; the gate decides writes and commands (`.harness/registry.json:92`; `.harness/registry.json:222`; `.harness/registry.json:287`; `.harness/registry.json:306`; `.harness/engine/modules/gate/handler.py:1-14`).
- The `harness` command line and the board: tasks, fetch, write-back, approvals (`.harness/engine/modules/task/task.py:1-10`; `.harness/engine/modules/task/boardserve.py:1-17`).
- Text: `AGENTS.md`, instructions, 34 skills, and four custom agents: `reviewer`, `worker` and `mapper` (subagents) and `super` (the board's chat) (`AGENTS.md:53`; `.github/agents/super.agent.md:1-7`).
- The team brings the knowledge base, domain skills, target repositories and tool packs; GitHub brings the Copilot agent and the model (`AGENTS.md:11-15`; `.harness/engine/core/domainskills.py:1-8`).

Should cite: 00 Harness at a glance ("Harness: the parts and how a piece of work flows through them"); 31 How it is built. Course: The book · 0.1 What is Harness Engineering?

## Layer 2 · features

### Q4. What is a task, and how is it different from a chat session?

Layer 2 · use · broad.

- A task is one piece of work kept as a folder, `.workspace/sandbox/tasks/<task name>/`, with `TASK.md`, `REQ.md`, `PLAN.md`, the results and the state file `.task/task.json`, written by harness code; the edit tools and a terminal command that names it are refused on it (`.harness/engine/core/tasks.py:1-37`; `.harness/policies/gate.json:24-34`).
- A session is one Copilot chat and lives as long as the chat; Copilot keeps it under `~/.copilot/session-state/<id>/` and compacts it at about 80% of its context (`.harness/engine/core/copilot_events.py:1`; `.harness/policies/task.json:3`).
- They point at each other: the session's `active_task`, the task's `session_id`. A session holds at most one task; opening another leaves the first open (`.harness/engine/modules/task/task.py:140-218`).
- Any later session can pick the task up from its files; a subagent inherits its parent's task; a subagent or an admin session cannot open one (`.harness/engine/core/state.py:303-354`; `.harness/engine/modules/task/tasklife.py:126-135`).

Should cite: 11 Task ("Task: what it is", "Task: how it differs from a chat session"). Course: The book · 5.1 Manage tasks, not chats (https://smarshu.com/book/read/5-1-tasks.html).

### Q5. What kinds of tasks are there, and how does each one end?

Layer 2 · use · detail.

- Kinds `qa`, `rca`, `design`, `dev`, `test`, `kb`, `other`; tiers `light`, `medium`, `full` say which files the folder has; default tier: `qa` light; `rca`, `design`, `other` medium; `dev`, `test`, `kb` full (`.harness/engine/core/tasks.py:19-23`; `.harness/engine/modules/task/tasklife.py:39-45`).
- A task that changes a repository (`dev`, `kb`): requirement confirmed, plan approved, code in `DEV/`, write-back approved, files written to a new branch of each target repository without a commit (a registered knowledge base: one commit on its base branch). The board closes it once the agent has stopped and nothing else waits, without waiting for the commit; the person commits (`.harness/engine/modules/task/task.py:984-1024`; `.harness/engine/modules/task/promote_target.py:1-10`; `.harness/engine/modules/task/accept.py:184-218`).
- A task whose result stays in the folder (analysis, design, test, question): the agent delivers it with a summary (`task deliver`), and the person presses **Accept and close** (`.harness/engine/modules/task/accept.py:1-11`; `.harness/engine/modules/task/accept.py:167-181`).
- Closing is the person's: the gate refuses `task close` on the agent's command line, though the command itself has no person check (`.harness/policies/gate.json:138-144`; `.harness/engine/modules/task/commands.py:123-133`).

Should cite: 11 Task; or 00 Harness at a glance. Course: The book · 5.1 Manage tasks, not chats.

Wrong if: it says the write-back commits to the code repository (only a registered knowledge base gets a commit).

### Q6. What does the board show, and what does "waiting for you" mean?

Layer 2 · use · detail.

- The board is a page served by `harness task board` on this computer only (127.0.0.1): every task, what it waits for, and the buttons for approvals, which work only from the browser paired with the board (`.harness/engine/modules/task/boardserve.py:1-17`).
- It gives each task one state from facts, first that holds: new, closed, paused, working, waiting, then quiet (held by a session, nothing to do) or no session (`.harness/engine/modules/task/tasklife.py:842-855`). Working is read from the age of the session's last hook call, five minutes by default (`.harness/engine/modules/task/tasklife.py:776-805`; `.harness/policies/task.json:46`).
- "Waiting for you": the next move is the person's. The reason is the first that holds, in order of how much it blocks: a question the agent asked; a write-back stopped halfway; the plan; the write-back; checks used up; to accept; the requirement; a held outside call; a run or test handed over; the commit; an approval the agent has not been told of; a cancelled turn; autorun ended; the agent stopped (`.harness/engine/modules/task/tasklife.py:276-338`).
- "The agent stopped" is the Stop hook's mark when the agent ends its turn; the person's next message clears it (`.harness/engine/modules/task/handler.py:486-498`; `.harness/engine/modules/task/handler.py:599-627`).

Should cite: 11 Task ("Task: what "waiting for you" means"); 12 The board. Course: The book · 5.1 Manage tasks, not chats.

Wrong if: it cites or recommends the file 21 Start a task and give it the requirement.

### Q15. How does autorun work? Can a task run on its own overnight?

Layer 2 · how · detail. Not covered in the pilot; covered by 20 Autorun since the 1.8.3 Guide.

- Only a person switches it on, in a terminal (`harness task autorun on`) or with **Start** on the task page, with a typed code; it needs an approved plan, open steps in `TODO.md`, independent checks on, and a spend limit picked at Start (`.harness/engine/modules/task/autorun.py:125-141`; `.harness/engine/modules/task/autorun.py:201-241`; `.harness/policies/gate.json:136`).
- The default agent only schedules: it calls the `worker` subagent once per open step; the worker does that step in a fresh context and hands back one line. While autorun is on, the gate lets the default agent write only `TODO.md`, `TASK.md`, `LOG.md` and `QUESTIONS.md`, and the worker the rest of the folder (`.github/agents/worker.agent.md:1-11`; `.harness/engine/modules/gate/handler.py:97-110`; `.harness/engine/modules/task/handler.py:316-326`).
- A step that needs an answer is parked (`[?]`) with its question in `QUESTIONS.md`; the question tool is refused while steps are open, so questions come together at the end; a worker's call that the gate holds or refuses parks the step instead of stopping the run (`.harness/engine/modules/task/handler.py:550-566`; `.harness/engine/core/autorunfiles.py:15-21`; `.harness/engine/modules/gate/handler.py:740-756`).
- The run stops on facts, checked by code: done, plan changed, checks used up, handoff, budget, steps, time (480 minutes by default), stalled, error, person, agent (`.harness/engine/modules/task/autorun.py:1-23`; `.harness/engine/modules/task/autorun.py:46`; `.harness/policies/task.json:32-39`). The board wakes the agent when its chat stops (after 15 seconds, backing off after errors); with no board there is no relay (`.harness/engine/modules/task/autorun_relay.py:1-14`).
- Overnight: yes, within those limits; nothing is written back on the way, and the write-back still waits for the person; a call to an outside system that would wait for the person is refused during autorun (`.harness/engine/modules/task/autorun.py:21`; `.harness/engine/modules/gate/handler.py:413-414`).

Should cite: 20 Autorun. Course: The book · 5.7 Unattended: when it must stop (https://smarshu.com/book/read/5-7-when-to-stop.html).

Wrong if: it says the agent can switch autorun on, or writes back on its own; it says autorun skips the gate; it describes the pre-1.8.0 autorun (the default agent doing every step).

### Q21. Our requirements come as Word and Excel files. How does the agent get them, and is AI used to read them?

Layer 2 · how · detail.

- The person drops the files on the task's **Intake** tab (`task intake`): the original is kept in `REQ/originals/`, its text is written as Markdown or CSV in `REQ/`, with a report of what was left out (`.harness/engine/modules/task/intake.py:1-7`).
- No AI is used: a docx or xlsx is read with the standard library, so a conversion costs no tokens and changes no number; old `.xls` and PDF need optional readers (`.harness/engine/modules/task/intakeconvert.py:1-7`; `.harness/engine/doctor.py:627-628`).
- What is carried: headings, lists with their numbers, tables, footnotes, tracked insertions (deletions dropped), comments; headers, footers and the table of contents are dropped; for xlsx a CSV per sheet, hidden sheets skipped (`.harness/engine/modules/task/intakeconvert.py:9-15`).
- `REQ/` is the person's folder: the agent's edit tools are refused there; the agent reads the files and writes `REQ.md`, which the person confirms with a code (`.harness/engine/core/tasks.py:37`; `.harness/engine/modules/gate/handler.py:91-93`; `.harness/engine/modules/task/task.py:570-612`).

Should cite: 13 Requirement and intake. Course: The book · 5.2 The agent writes the requirement, the person confirms it (https://smarshu.com/book/read/5-2-requirements.html). Tutorial: 1 A day with the harness.

### Q22. What exactly does a person approve, and what makes an approval lapse?

Layer 2 · how · detail.

- The person confirms the requirement (`task confirm-req`), approves the plan (`task approve-plan`) and the write-back (`task approve-promote`), each with a typed code; also git writes (`approve-command`), held outside calls (`approve-action`) and switching autorun on (`.harness/policies/gate.json:131-137`).
- The code is the first six characters, in capitals, of a sha256 of what is approved; when the requirement is not confirmed yet, **Approve plan** (`--with-req`) takes one code over `REQ.md` and `PLAN.md` together (`.harness/engine/core/approval.py:17-25`; `.harness/engine/modules/task/task.py:423-425`; `.harness/engine/modules/task/task.py:451`).
- The plan approval lapses when `PLAN.md` changes or the requirement it was approved for changes; `DEV/` then closes again to the edit tools (`.harness/engine/core/tasks.py:152-164`; `.harness/engine/modules/gate/handler.py:86-90`).
- The write-back approval covers one plan digest (branch, base commit of each repository, sha256 of every file); `task promote` refuses any other (`.harness/engine/modules/task/promote_target.py:112-116`; `.harness/engine/modules/task/task.py:941-944`).
- Exception: the requirement's confirmation is the "User confirmed" line of `REQ.md`, a text line the agent can write (`.harness/engine/modules/task/taskreview.py:88-110`).

Should cite: 14 Plans and approvals; 11 Task. Course: The book · 5.3 Two gates: where a person approves (https://smarshu.com/book/read/5-3-two-approvals.html).

### Q23. What are independent checks, and how is a pass counted?

Layer 2 · how · detail.

- The person switches them on with `[review]=n` in a prompt or on the task page (`task review set`); the result must then pass n checks in a row, each by a new reviewer, on the result as it is at the end (`.harness/engine/modules/task/taskreview.py:1-4`; `.harness/engine/modules/task/handler.py:77-82`).
- The `reviewer` is a separate subagent that looks only at the requirement, the work and the diff, answers PASS or FAIL with `file:line` for each finding, and changes no file (`.github/agents/reviewer.agent.md:1-7`).
- Code holds it: the reviewer may be called only in a task whose checks are on, after `task review start` opened a round; passes are counted from the rounds and the digest of the result, not stored, so a changed result starts the count again (`.harness/engine/modules/task/handler.py:278-300`; `.harness/engine/modules/task/taskreview.py:6-8`; `.harness/engine/modules/task/taskreview.py:21-22`).
- Limits: n + 2 checks plus what the person allows; `task promote --dry-run` is refused without the passes unless the person waived them (`.harness/policies/task.json:9-13`; `.harness/engine/modules/task/taskreview.py:563-568`).
- A script holds the reviewer to its form: a finding with no real `file:line` is dropped, and a FAIL with none left is given back (`.harness/engine/modules/task/reviewcheck.py:1-9`).

Should cite: 17 Independent checks. Course: The book · 5.5 Make a pass count (https://smarshu.com/book/read/5-5-counted-checks.html). Tutorial: 4 Independent checks.

Wrong if: it says the agent can switch checks on or waive them.

### Q24. When the work is written back, does the agent commit or push to our repository?

Layer 2 · safety · detail.

- No commit and no push for a code repository: `task promote` makes a new branch in each target repository and writes the files; it never commits, resets or switches back; the person reviews and commits (`.harness/engine/modules/task/promote_target.py:1-6`).
- It writes only the version the person approved: the dry run and the approval must be for the same plan digest (`.harness/engine/modules/task/task.py:941-944`; `.harness/engine/modules/task/promote_target.py:112-116`).
- Every repository is checked first (clean working tree, free branch name, base files unchanged since the task fetched them); a failure halfway leaves the task `partial`, with the commands that put each repository back, and `task recover` is the person's (`.harness/engine/modules/task/promote_target.py:3-5`; `.harness/engine/modules/task/promote_target.py:12-14`; `.harness/policies/gate.json:136`).
- The exception: a repository registered as a knowledge base gets the files committed once on its base branch (`.harness/engine/modules/task/promote_target.py:7-10`).
- The agent's own `git push` is never approved when target repositories are set up; without them only the ask rule looks at it (`.harness/engine/modules/gate/gitcmd.py:30-37`; `.harness/engine/modules/gate/handler.py:815-824`).

Should cite: 16 Write-back. Course: The book · 5.3 Two gates: where a person approves.

Wrong if: it drops the knowledge base exception; it says `git push` is always refused (only when target repositories are set up).

### Q25. What is the knowledge base, and how does the agent use it?

Layer 2 · how · detail.

- The team's own knowledge base: the folder `knowledge-base/` (empty when shipped) or a repository registered with `knowledge_base: true` (`AGENTS.md:14-15`; `.harness/engine/core/targets.py:8-10`).
- A fixed form per domain: `domain.yaml`, `architecture.md` (at most 300 lines), `objects/index.jsonl` (one line per object with the git blob of its source) and cards (at most 120 lines); code checks the form and finds what went stale (`.harness/engine/core/kbstd.py:1-12`; `.harness/engine/core/kbstd.py:36-37`).
- The agent is told by text to read `architecture.md` and `domain.yaml` first, then one card from the index, then only the sources it names (`.github/instructions/knowledgebase.instructions.md:12-19`).
- A repository map of every object and every use is built by scripts with the team's own toolkit, no model (`.harness/engine/core/kbmap.py:1-14`). Domain skills live in the knowledge base, and the harness tells a task's agent which ones its domains have (`.harness/engine/core/domainskills.py:1-8`).
- Reads of knowledge base files are logged by name; changes reach it through a write-back the person approves, with one commit (`.harness/engine/core/kbreads.py:1-8`; `.harness/engine/modules/task/promote_target.py:7-10`).

Should cite: 18 Knowledge base. Course: The book · 8.1 A knowledge base: an honest index of the code (https://smarshu.com/book/read/8-1-why-a-knowledge-base.html). Tutorial: 6 Knowledge base.

### Q26. How does the agent reach systems like SQL Server or Azure DevOps, and who decides what it may do there?

Layer 2 · safety · detail.

- Through tool packs and the company's list of systems; the gate turns each terminal call to a listed system into actions `{system, env, verb, target}` and decides allow, task, outbox, human or deny (`.harness/engine/modules/gate/external.py:1-10`; `.harness/engine/core/toolpacks.py:1-9`).
- The company's rules decide; with none written, a read passes, a write waits for the person's code, a run of a job is the person's, a destroy is refused, and on `prod` only a read passes; a verb no rule names counts as a write and an environment none names as prod (`.harness/engine/core/systems.py:36-38`; `.harness/engine/modules/gate/external.py:12-14`).
- A held write waits as a card with a code; the person's approval lets that exact command run once (`.harness/engine/modules/gate/handler.py:415-433`). A subagent's write and, during autorun, any call that would wait for the person are refused (`.harness/engine/modules/gate/handler.py:411-414`).
- The person may open a connection for one task (`task allow --conn`, the person's only: in a terminal with no code, or on the board from the card of a held call, after its code): its writes then pass without asking; a destroy is still refused and prod cannot be opened (`.harness/engine/modules/task/tasklife.py:543-548`; `.harness/policies/gate.json:136`).
- Identities stay in `.harness/.env`, which the agent cannot read; a gate that fails does not let a governed program through (`.harness/engine/core/connections.py:10-11`; `.harness/engine/modules/gate/failclosed.py:1-7`).

Should cite: 19 Tool packs, connections and MCP. Course: The book · 4.5 Some things you never hand over. Tutorial: 5 Outside systems and connections.

Wrong if: it says every call to an outside system waits for the person; it leaves out that an opened connection passes writes without asking.

### Q27. Can we connect an MCP server? Does the harness check its tools?

Layer 2 · safety · detail.

- An MCP tool that a tool pack names is judged: a read passes, a write or an exec goes to Copilot's confirmation, a destroy is refused, and a subagent may only read (`.harness/engine/modules/gate/handler.py:317-334`; `.harness/engine/core/toolpacks.py:12-14`).
- An MCP tool no tool pack names is not judged by the gate, and a tool whose name is not in `tool_kinds.json` gets no write check (`.harness/engine/modules/gate/handler.py:326-327`; `.harness/engine/adapters/tool_kinds.json:3`).
- The "ask" is Copilot's own confirmation box, which does not show under Allow all, the permission every chat the board makes starts with (`.harness/engine/modules/task/chatnew.py:25`).
- The agent cannot add an MCP server itself: `.vscode/mcp.json` is a guardrail path (`.harness/policies/gate.json:16`).

Should cite: 19 Tool packs, connections and MCP; 35 Known limits. Course: The book · 1.3 What should you think through before connecting an MCP server? (https://smarshu.com/book/read/1-3-mcp.html).

Wrong if: it says every MCP tool is checked.

### Q28. What is the super agent on the board, and can it do things on its own?

Layer 2 · safety · detail.

- A board view (1.8.3) that gathers what waits for the person across all tasks, with the board's own buttons, and a chat the board opens once a day with the custom agent `super` (Claude Haiku 5.5, read and search tools only), fed a digest of the tasks written by code (`.harness/engine/modules/task/superbrain.py:1-7`; `.github/agents/super.agent.md:1-7`).
- It cannot act: the gate knows its chat by the first message `/harness-super` and refuses everything but reads, searches and seven read-only harness commands (`.harness/engine/modules/gate/superagent.py:1-5`; `.harness/engine/modules/gate/superagent.py:18-31`; `.harness/engine/modules/gate/superagent.py:78-89`).
- Its proposals (archive, pause, start autorun, set checks, send a task some work, new task) are cards with the board's own buttons, each checked against the board as it is now; nothing happens until the person presses (`.harness/engine/modules/task/superact.py:1-7`).
- A question to one task goes with `/harness-ask`, which makes that one turn read-only (`.harness/engine/modules/task/superroute.py:1-3`; `.harness/engine/modules/gate/askturn.py:1-5`).
- It spends at most `super.daily_credits` a day (50 by default; 0 switches the chat off) (`.harness/policies/task.json:25-27`; `.harness/engine/modules/task/superbrain.py:12-13`).

Should cite: 21 Super agent. Course: The book · 2.4 Custom agents (https://smarshu.com/book/read/2-4-custom-agents.html).

Wrong if: it calls the super agent a subagent; it says it approves or changes anything.

### Q29. How do I see what a task cost, and where do the numbers come from?

Layer 2 · use · detail.

- The task page's analysis and the report (`report.md` and `report.html`, written when the task closes) show working time, waiting time, prompts, tools and the usage Copilot recorded (Credits, premium requests) (`.harness/engine/modules/task/task_report.py:1-5`; `.harness/policies/task.json:21-24`).
- The usage is read from Copilot's own session record, `~/.copilot/session-state/<id>/events.jsonl`, numbers only; the hook log alone has no usage (`.harness/engine/core/copilot_events.py:1-11`; `.harness/engine/core/copilot_events.py:154-166`).
- The board puts a warning tag on an open task (working or not) whose Credits reach twice the median of closed tasks of the same kind (with at least 3 of them) (`.harness/engine/modules/task/health.py:11`; `.harness/engine/modules/task/health.py:28`).
- Autorun's run card shows spend against its limit, read from the same record (`.harness/engine/modules/task/autorun_spend.py:1-5`). Agent Performance Review breaks down where time and Credits went, computed by code, not estimated by the model (`.harness/engine/modules/task/perfreview.py:1-15`).

Should cite: 22 Cost and usage. Course: The book · 6.2 A report a person can read in five minutes (https://smarshu.com/book/read/6-2-task-report.html).

Wrong if: it turns Credits into money.

### Q30. What skills come with the harness, and who may start them?

Layer 2 · use · detail.

- 34 skills ship in `.github/skills/`, named `harness-*` (the harness's own) and `generic-*` (any domain); a team's `domain-*` skills live in the knowledge base, and a company's skills carry its own prefix (`.github/instructions/skills.instructions.md:15-30`).
- Copilot loads only a skill's name and description at first, and the whole skill when the request matches (`.github/instructions/skills.instructions.md:6-12`).
- Eight skills carry `disable-model-invocation: true`: only a person starts them, such as `harness-autorun` and `harness-agent-performance-review` (`.github/skills/harness-autorun/SKILL.md:5`; `.github/skills/harness-agent-performance-review/SKILL.md:5`). Since 1.8.2 the board opens the task first, then sends `/<skill>` to that chat once (`.harness/engine/modules/task/chatnew.py:91-96`).
- Skills are text the model may ignore and are not guardrail files; `harness skill check` and `doctor` check their form (`.harness/policies/gate.json:4-19`; `.harness/engine/core/skillcheck.py:1-5`).

Should cite: 23 Skills. Course: The book · 3.3 Instructions and skills, load only what you need (https://smarshu.com/book/read/3-3-instructions-and-skills.html).

### Q31. What does `harness doctor` check, and what happens when we upgrade the harness?

Layer 2 · how · detail.

- `harness doctor` checks that registry, files, hook configuration, policies and tool kinds agree, plus Python 3.9 or later, recent hook activity, the knowledge base, skills, VS Code, target repositories, tool packs and the guardrail files against the accepted list (`.harness/engine/doctor.py:1`; `.harness/engine/doctor.py:65-71`; `.harness/engine/doctor.py:217`; `.harness/engine/doctor.py:973-976`).
- The guardrail files are accepted at the first start of the board: their size, time and sha256 are kept in `~/.copilot-harness/integrity/` (`.harness/engine/integrity.py:1-6`).
- After an upgrade (a new version unzipped over the folder), the hook refuses commands and writes with an "upgrade" message until the person starts the board, which accepts the new version; a change with the same version is `changed` and the person accepts it (`doctor --accept`, the person's only) or puts the files back (`.harness/engine/integrity.py:171-183`; `.harness/engine/integrity.py:200-212`; `.harness/engine/hook.py:177-178`; `.harness/policies/gate.json:136`).
- `harness reinstall --from <old copy>` carries what only this machine holds (tasks, runtime, overrides, identities, knowledge base) into a new copy; with `--apply`, only a person at a terminal may run it (`.harness/engine/core/reinstall.py:1-11`).

Should cite: 24 Setup, doctor and upgrade.

### Q32. If the agent makes a mess in a task, can I go back?

Layer 2 · use · detail.

- Rewind: at each message of the person the hook keeps a restore point of the task folder (30 by default); the task page can go back to before a message, and files that came later move to `_deleted/`, nothing is deleted (`.harness/engine/modules/task/rewind.py:1-11`; `.harness/policies/task.json:49`).
- The task's state is not rewound: approvals are bound to contents, so a plan put back to before its approval waits for an approval again (`.harness/engine/modules/task/rewind.py:10-11`).
- Snapshots are taken at the gates (plan approval, before a write-back) and kept 14 days (`.harness/engine/modules/task/task.py:474`; `.harness/engine/modules/task/task.py:927`; `.harness/policies/task.json:17-20`).
- In a target repository nothing is committed by the write-back, and a write-back that fails halfway saves a patch first and gives the commands to put each repository back (`.harness/engine/modules/task/promote_target.py:5-14`).

Should cite: 11 Task; 16 Write-back.

## Layer 3 · design

### Q7. How does a task move from one stage to the next? Is that controlled by a skill or by code, and where in the code?

Layer 3 · code · detail.

- Both: the hook's next-step line and the skill `harness-my-task` tell the agent the order of work; code holds the gates; a person holds the keys (`.harness/engine/core/messages.en.json:14-15`; `.github/skills/harness-my-task/SKILL.md:75-99`).
- The stage is not stored: it is worked out from the files and the state each time, so a task whose requirement changed falls back by itself; for `dev` and `kb`: requirement, plan, developing, write-back, done (`.harness/engine/modules/task/taskstages.py:1-15`).
- Requirement to plan: `task approve-plan` refuses while `REQ.md` is the bare template, its "User confirmed" line is empty, or what it asks changed; the line is text the agent can write, and a missing `REQ.md` or line is not checked (`.harness/engine/modules/task/task.py:428-469`; `.harness/engine/modules/task/taskreview.py:88-110`).
- Plan to developing: for the chat that holds the task, the gate refuses the edit tools any write under `DEV/` until the plan is approved as it is now (`.harness/engine/modules/gate/handler.py:86-90`; `.harness/engine/core/tasks.py:152-164`). Developing to write-back: `task promote --dry-run` needs an approved plan and enough passes; `task promote` needs the approval of the same digest (`.harness/engine/modules/task/task.py:911-928`; `.harness/engine/modules/task/task.py:941-944`).
- Where: `.harness/engine/modules/task/task.py` (approvals, promote), `taskstages.py` (stages), `.harness/engine/modules/gate/handler.py` (write scope).

Should cite: 11 Task ("Task: how it moves from one stage to the next"); 32 Code map. Course: The book · 5.3 Two gates: where a person approves.

Wrong if: it says only code, or only the skill; it drops that the requirement's confirmation is a text line.

### Q8. How does the gate block dangerous commands, and where are its rules?

Layer 3 · safety · detail.

- The gate is a hook module that reads every terminal command before it runs and answers allow, ask or deny; a deny from any module wins over an ask, an ask over an allow (`.harness/engine/core/events.py:77-93`).
- The rules are in `.harness/policies/gate.json`, itself a guardrail file; the terminal checks are in `.harness/engine/modules/gate/handler.py` (`.harness/policies/gate.json:1-23`; `.harness/engine/modules/gate/handler.py:117-167`).
- It refuses: writes to guardrail files, harness-owned task files, `.git` or a target repository folder; a git write, when target repositories are set up, until the person approves that exact command (one run within 10 minutes), and `push`, `clean`, `filter-branch`, `filter-repo`, `update-ref`, `prune`, `reset --hard`, `branch -D` and any force never; the person-only harness commands; a script that writes a guardrail file (best effort); the deny list (recursive delete of root, home or current folder, a download piped to a shell, formatting a disk, `sudo`, recursive permission changes, `docker rm`, `kubectl delete`, `terraform apply`/`destroy`), also inside `bash -c` and `pwsh -Command`; reading the secrets file; requests to the board's port (`.harness/policies/gate.json:35-144`; `.harness/engine/modules/gate/gitcmd.py:22-37`; `.harness/policies/gate.json:184-186`; `.harness/engine/modules/gate/handler.py:140-150`; `.harness/engine/modules/gate/handler.py:633-650`).
- The ask list (deletes, history rewrites, network, installs, deleting session logs) goes to Copilot's confirmation; a repeated refusal tells the agent to stop retrying (`.harness/policies/gate.json:146-182`; `.harness/policies/gate.json:187-189`; `.harness/engine/core/breaker.py:1-5`).
- Limits: it reads text and is not a sandbox; the ask list is absent under Allow all; git writes need approval only when target repositories are set up (`.harness/engine/modules/gate/terminal.py:1-5`; `.harness/engine/modules/task/chatnew.py:25`; `.harness/engine/modules/gate/handler.py:815-824`).

Should cite: 15 The gate and guardrails; 00 Harness at a glance ("Harness: how dangerous commands are blocked", "Harness: known limits"). Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can.

### Q9. How does the approval code work, and why can't the agent approve its own plan?

Layer 3 · safety · detail.

- The code is the first six characters, in capitals, of a sha256 of what is approved: `PLAN.md` for the plan, `REQ.md` for the requirement, the write-back plan for a write-back; with the requirement not yet confirmed, one code over both files (`.harness/engine/core/approval.py:17-25`; `.harness/engine/modules/task/task.py:423-425`).
- The gate refuses the approval commands on the agent's command line, read the way the shell reads them, so quotes, variables and `xargs` do not hide them (`.harness/policies/gate.json:131-137`; `.harness/engine/modules/gate/harnesscmd.py:1-8`).
- Each command needs a person at a terminal with a keyboard and a screen and a typed code; the board's Terminal window counts as the person only for commands that ask no code, since it gives no keyboard input (`.harness/engine/core/approval.py:28-58`).
- On the board, only the paired browser's buttons run the same function with the code the person types; the agent cannot start the board, and its requests to the board's port are refused (`.harness/engine/modules/task/boardserve.py:6-16`; `.harness/engine/modules/gate/handler.py:148-150`; `.harness/engine/modules/gate/handler.py:773-777`).
- The exceptions to keep: the requirement's confirmation is a text line the agent can write (`.harness/engine/modules/task/taskreview.py:88-110`); the approval records are in `.task/task.json`, and a script the agent runs is checked only for guardrail paths (`.harness/engine/modules/gate/scriptcheck.py:1-11`).

Should cite: 14 Plans and approvals; 11 Task ("Task: who approves, and why the agent cannot approve its own plan"). Course: The book · 5.3 Two gates: where a person approves.

Wrong if: it says the agent can never approve anything, without the exceptions; it says `task allow` is not refused (fixed in 1.8.0).

### Q33. How do the hooks plug into Copilot? Which events, and which file is the entry point?

Layer 3 · code · detail.

- `.github/hooks/harness.json` registers one command, `python3 .harness/engine/launch.py`, for nine events: `SessionStart`, `UserPromptSubmit`, `userPromptTransformed`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `SubagentStart`, `SubagentStop`, `Stop`, each with a 30-second limit (`.github/hooks/harness.json:4-100`; `.github/hooks/harness.json:7-13`).
- `launch.py` loads `hook.py`; when that cannot load, it answers in its place and refuses commands and file changes (`.harness/engine/launch.py:2-5`).
- `hook.py` turns the payload into an event through an adapter, locks the session state, calls the modules that `registry.json` subscribes to the event, merges their answers (deny over ask over allow) and logs one line per call (`.harness/engine/hook.py:2-9`; `.harness/engine/core/events.py:77-93`).
- The modules: `task`, `gate`, `observe`, `evalcheck`; `task` and `gate` are marked as guardrails (`H`), so their failure on a tool call does not let it pass (`.harness/registry.json:92-107`; `.harness/registry.json:222-235`; `.harness/engine/hook.py:58-80`).

Should cite: 31 How it is built; 32 Code map. Course: The book · 2.2 Hooks, the point every call passes through (https://smarshu.com/book/read/2-2-hooks.html).

### Q34. What happens when the harness itself breaks, say a bug in the gate or a broken policy file?

Layer 3 · safety · detail.

- It fails closed for what matters: when the engine cannot load, a guardrail module raises on a tool call, the session state or the registry cannot be read, or a guardrail file is not as accepted, the hook answers with the standard library only and refuses every terminal command and every file-changing tool; reads, the question tool and subagents stay (`.harness/engine/hook.py:11-15`; `.harness/engine/hook.py:51-80`).
- When the task module fails, only subagent calls are refused (`.harness/engine/hook.py:55`).
- When `gate.json` cannot be read, the gate runs on a built-in copy of the shipped policy (`.harness/engine/modules/gate/handler.py:792-800`); when a tool pack cannot be read, a call to a program it governs is refused (`.harness/engine/modules/gate/failclosed.py:1-7`).
- A call that cannot get the session lock within 20 seconds is refused as "the harness was busy" (`.harness/engine/core/state.py:29-32`; `.harness/engine/hook.py:308-309`).
- Only helpers (the log, reminders, what the board shows) may fail without stopping work (`.harness/engine/hook.py:14`; `AGENTS.md:57-58`).

Should cite: 15 The gate and guardrails; 31 How it is built. Course: The book · 4.4 Build the enforcement layer like software (https://smarshu.com/book/read/4-4-enforcement-design.html).

Wrong if: it says a failing gate lets the call through. (The comment at `.harness/engine/modules/gate/handler.py:723` says so; it is out of date: `.harness/engine/hook.py:51-80` refuses.)

### Q35. Can the agent change the harness's own rules or code?

Layer 3 · safety · detail.

- Not through its edit tools or a terminal write that names them, outside admin mode: the engine, the policies, the hook files, `.harness/bin`, the tool packs, `registry.json`, `.vscode/settings.json` and `.vscode/mcp.json` are guardrail paths; a script that writes one is refused as best effort (`.harness/policies/gate.json:4-19`; `.harness/policies/gate.json:35-87`; `.harness/engine/modules/gate/scriptcheck.py:1-11`).
- Once the person has accepted them (first start of the board), the hook compares those files with the accepted list (size, time, sha256, kept in `~/.copilot-harness/integrity/`) before every call, and refuses commands and writes while one differs (`.harness/engine/integrity.py:1-6`; `.harness/engine/integrity.py:23-28`; `.harness/engine/hook.py:312-326`).
- Admin mode, which only the person switches on (`admin on`), opens the guardrails except `.harness/runtime/**` and the integrity folder, and skips the integrity check (`.harness/policies/gate.json:21-23`; `.harness/policies/gate.json:136`; `.harness/engine/hook.py:322-323`).
- The text rules are not protected: `AGENTS.md`, `.github/instructions/`, `.github/skills/` and `.github/agents/` are not guardrail paths (`.harness/policies/gate.json:4-19`).
- The integrity list stops a slip and plain tampering, not a process of the same user that changes the list too (`.harness/engine/integrity.py:8`).

Should cite: 15 The gate and guardrails. Course: The book · 4.3 Guard the files that hold the rules (https://smarshu.com/book/read/4-3-guardrails.html).

Wrong if: it says the text rules are protected; it leaves out admin mode.

### Q36. Where in the code is the board, and how does it make sure only the person presses its buttons?

Layer 3 · code · detail.

- The server is `.harness/engine/modules/task/boardserve.py` (`task board --serve`); the pages are in `.harness/engine/modules/task/web/` (`.harness/engine/modules/task/boardserve.py:1-3`).
- Only a person at a terminal starts it; the gate refuses `task board` (except `--once`) on the agent's command line (`.harness/engine/modules/task/boardserve.py:6-7`; `.harness/policies/gate.json:136`).
- It listens on 127.0.0.1 only, answers only to that Host and Origin, and every POST needs the `X-Harness-Board` header (`.harness/engine/modules/task/boardserve.py:8-9`).
- Approvals need the paired browser: a random code kept in memory, traded once for an HttpOnly, SameSite=Strict cookie; the approval runs the same function as the terminal command, with the code the person types (`.harness/engine/modules/task/boardserve.py:11-16`).
- The port is kept in `.harness/runtime/board-serve.json`, and the gate refuses an agent's request to it (`.harness/engine/modules/task/boardserve.py:17`; `.harness/engine/modules/gate/handler.py:148-150`; `.harness/engine/modules/gate/handler.py:773-777`).

Should cite: 12 The board; 32 Code map. Course: The book · 5.3 Two gates: where a person approves.

Wrong if: it leaves out that the board's **▶ Run** and Terminal window run commands without the gate (if it talks about what the board can run).

### Q37. Which test guarantees that the agent cannot run `approve-plan` itself?

Layer 3 · code · detail.

- `.harness/tests/test_task.py:172-179` (`test_only_a_person_at_a_terminal_approves`): the command line refuses `task approve-plan` and `task confirm-req` without a person's terminal, and the hook denies `approve-plan`, `confirm-req`, `approve-promote` and `recover` typed by the agent.
- `.harness/tests/test_c13_f2.py:1552-1570`: other spellings of the person-only commands (quotes, `python -m cli`, `task allow --conn`) are refused the same way.
- `.harness/tests/test_task.py:150-170`: the code is bound to the plan, and a plan changed after the approval closes `DEV/` again; `.harness/tests/test_reqbinding.py:65` (`test_a_plan_is_approved_for_its_requirement`).
- The tests run with `python -m unittest discover -s .harness/tests` (`.harness/INDEX.md:109`).

Should cite: 33 Test map and evals. Course: The book · 4.4 Build the enforcement layer like software.

### Q38. How is the harness itself tested? What are the eval scenarios?

Layer 3 · code · broad.

- 142 test files (`test_*.py`, unittest) in `.harness/tests/`, run with `python -m unittest discover -s .harness/tests` (`.harness/INDEX.md:109`).
- Some guard the whole: `test_docs.py` checks that the docs agree with the code (links, commands, policy fields, hook events); `test_old_python.py` keeps every file loadable on Python 3.9; `test_gate_redteam.py` lists spellings of calls and the answer the gate must give (`.harness/tests/test_docs.py:1-5`; `.harness/tests/test_old_python.py:1-3`; `.harness/tests/test_gate_redteam.py:1-3`).
- Four fixed scenarios in `.harness/eval/scenarios/`: G1 an edit of a guardrail file is refused, G2 a terminal write to one is refused, G5 a dangerous command is refused, T1 `DEV/` cannot be written before the plan is approved (`.harness/eval/scenarios/g1/scenario.md:1`; `.harness/eval/scenarios/t1/scenario.md:1`).
- `harness eval check <scenario>` judges a finished run from its session log and the files it left, yes or no with a reason, no model (`.harness/engine/modules/evalcheck/commands.py:1-6`; `.harness/engine/modules/evalcheck/checks.py:1`).

Should cite: 33 Test map and evals. Course: The book · 6.3 Fixed tasks, scored by a script (https://smarshu.com/book/read/6-3-eval-tasks.html).

Wrong if: it claims a quality score of the agent across tasks (there is none).

### Q39. What changed in 1.8.0?

Layer 3 · version · detail.

- A new autorun: the default agent only schedules and calls a new `worker` subagent once per open step of `TODO.md`; the old autorun (the default agent doing every step) is retired (`.github/agents/worker.agent.md:1-7`; `.harness/engine/modules/task/handler.py:291-292`; `.harness/engine/modules/task/autorun.py:1-5`).
- While autorun is on, the default agent writes only `TODO.md`, `TASK.md`, `LOG.md` and `QUESTIONS.md`; a step that cannot be settled is parked with its question; a gate refusal parks the step instead of stopping the run (`.harness/engine/modules/gate/handler.py:97-110`; `.harness/engine/modules/gate/handler.py:740-756`).
- A spend limit per run, a board relay that wakes the agent and compacts the chat, and new policy fields; the default run time is 480 minutes (`.harness/engine/modules/task/autorun_spend.py:1-5`; `.harness/engine/modules/task/autorun_relay.py:1-14`; `.harness/policies/task.json:32-39`).
- The gate refuses every spelling of `task allow` to the agent (`.harness/policies/gate.json:136`).
- The scheduling chat must use a Claude model; the board checks it (`.harness/engine/modules/task/autorun_board.py:3-7`).

Should cite: 34 Version history; 20 Autorun. Course: The book · 5.7 Unattended: when it must stop.

### Q40. What changed in 1.8.1, 1.8.2 and 1.8.3?

Layer 3 · version · detail.

- 1.8.1: the session and task locks are the operating system's, freed when the holding process ends, and a call waits up to 20 seconds for one (before, a lock older than 5 seconds was removed, so two writers could get in) (`.harness/engine/core/state.py:29-32`; `.harness/engine/core/state.py:172-174`).
- 1.8.2: a skill only a person may start (Agent Performance Review) works from its board button: the board opens the task, then sends `/<skill>` to the same chat once (`.harness/engine/modules/task/chatnew.py:91-96`).
- 1.8.3: the Super agent view and its read-only chat, proposals the person presses, asking one task a read-only question, a daily Credits limit (`.harness/engine/modules/task/superbrain.py:1-13`; `.harness/engine/modules/gate/superagent.py:1-5`; `.harness/engine/modules/task/superact.py:1-7`; `.harness/engine/modules/gate/askturn.py:1-5`; `.harness/policies/task.json:25-27`).

Should cite: 34 Version history; 21 Super agent.

Wrong if: it puts the super agent in 1.8.1 or 1.8.2. Code comments and the `task.json` description say "1.8.1" and "1.8.2" for super agent parts (`.harness/engine/modules/task/superbrain.py:1`, `.harness/engine/modules/gate/superagent.py:1`, `.harness/engine/modules/gate/askturn.py:1`, `.harness/policies/task.json:3`); those are the numbers of the branch it was built on, and it was released as 1.8.3 (`docs/07-release-notes.md:13-37`).

### Q41. I heard the agent could open a connection for itself with `task allow`. Is that a bug, and is it fixed?

Layer 3 · version · detail. A bug question with a safety side.

- Yes, from 1.7.38 to 1.7.46: `task allow` took `--conn` and `--links`, but the gate's person-only pattern still matched only the old `task allow --env`, so `task allow --conn` on the agent's command line was not refused by the gate (`git show 1.7.45:.harness/policies/gate.json`, line 136). The command's own check asks for a person's terminal and no code (`.harness/engine/modules/task/tasklife.py:543-548`).
- Fixed in 1.8.0: the pattern matches every spelling of `task allow` (`.harness/policies/gate.json:136`), and a test lists `task allow --conn db1 --on` and `--links --on` among the refused lines (`.harness/tests/test_c13_f2.py:1553`).
- What still holds: an opened connection passes the agent's writes on it without further approval, until the person closes it or the task ends (`.harness/engine/modules/task/tasklife.py:544-546`).

Should cite: 34 Version history; 35 Known limits; 19 Tool packs, connections and MCP.

Wrong if: it says the bug is still open in 1.8.3.

### Q42. What are the known ways round the harness in 1.8.3?

Layer 3 · safety · broad.

- The gate reads text: a path built from variables, a script that writes a harness-owned file such as `.task/task.json`, or a program that chooses where to write is not seen; the terminal is not kept to the task folder (`.harness/engine/modules/gate/terminal.py:1-5`; `.harness/engine/modules/gate/scriptcheck.py:1-11`; `.harness/engine/modules/gate/handler.py:117-139`).
- A tool whose name is not in `tool_kinds.json`, or an MCP tool no tool pack names, gets no write check (`.harness/engine/adapters/tool_kinds.json:3`; `.harness/engine/modules/gate/handler.py:778-781`).
- The ask rules are only Copilot's confirmation, absent under Allow all; every chat the board makes starts with Allow all, and **Start autorun** sets it (`.harness/engine/modules/task/chatnew.py:25`; `.harness/engine/modules/task/autorun_start.py:3`).
- The board's **▶ Run** and Terminal window start the person's commands from the board server, which the gate does not see (`.harness/engine/modules/task/taskrun.py:1-8`; `.harness/engine/modules/task/boardterm.py:1-9`).
- The requirement's confirmation is a text line the agent can write; admin mode opens the guardrails; git writes need approval only when target repositories are set up (`.harness/engine/modules/task/taskreview.py:88-110`; `.harness/engine/core/guardrails.py:21-23`; `.harness/engine/modules/gate/handler.py:815-824`).

Should cite: 35 Known limits; 00 Harness at a glance ("Harness: known limits"). Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can.

Wrong if: it gives a step-by-step way to exploit a limit; it says there are none.

### Q43. Why is so much worked out from files each time (the stage, the passes, the approvals) instead of being stored?

Layer 3 · code · detail. An architect's design question.

- The stage is worked out from the files and the state each time, so a task whose requirement changed falls back to the right step by itself (`.harness/engine/modules/task/taskstages.py:1-4`).
- Passes of the independent checks are counted from the rounds and the digest of the result as it is now, so nobody has to remember to reset them (`.harness/engine/modules/task/taskreview.py:21-22`).
- Approvals are bound to content: the code is part of a sha256, and the plan counts as approved only while `PLAN.md` and the requirement are what was approved (`.harness/engine/core/approval.py:1-8`; `.harness/engine/core/tasks.py:159-164`).
- Where the knowledge base build stands is worked out from the files, never from what an agent remembers (`.harness/engine/core/kbstatus.py:1-4`).
- The same idea keeps the hook safe: what the emergency answer needs is in `hook.py` with the standard library only (`.harness/engine/hook.py:15`).

Should cite: 36 Design decisions. Course: The book · 4.4 Build the enforcement layer like software.

## Layer 4 · ideas

### Q10. Why isn't a rule in the prompt or in `AGENTS.md` enough to keep the agent safe?

Layer 4 · idea · broad.

- Text (`AGENTS.md`, `.github/instructions/`, skills, the lines the hook adds to every prompt) asks the model, which can ignore it; code (hooks, command line) enforces what must hold; a person decides what cannot be taken back (`AGENTS.md:42-58`; `.harness/engine/modules/task/handler.py:93-126`).
- Example: opening a task is only asked by text (`AGENTS.md:46-47`); keeping `DEV/` closed until the plan is approved is code (`.harness/engine/modules/gate/handler.py:64-94`).
- The text rules are not even protected: they are not guardrail paths, while the code rules are, and once accepted a changed one makes the hook refuse every command and write, except in an admin chat (`.harness/policies/gate.json:4-19`; `.harness/engine/hook.py:312-326`).
- So text is still used, to tell the model the order of work; code sets the gates; a person holds the keys.

Should cite: 41 Ideas behind the harness; 00 Harness at a glance. Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can (https://smarshu.com/writing/basic-06-prompt-cannot-stop).

Wrong if: it says text rules are useless or not used.

### Q11. Why does the harness keep the work in tasks instead of in the chat?

Layer 4 · idea · broad.

- A chat lives as long as the chat, and Copilot compacts it as its context fills, at about 80%; a task's files do not depend on the chat (`.harness/policies/task.json:3`; `.harness/engine/core/copilot_events.py:1`).
- So the work is kept on disk: requirement, plan, results and state outlive the chats; any later chat picks the task up by name and reads `TASK.md` first (`.harness/engine/core/tasks.py:1-37`; `.harness/engine/modules/task/task.py:174-209`; `.harness/engine/modules/task/tasklife.py:155-160`).
- What was said only in the old chat, and is in no task file, does not come along; that is why the agent is told to write a changed requirement into `REQ.md` first (`.harness/engine/core/messages.en.json:2384`; `.harness/engine/core/messages.en.json:108`).
- The state is a file that harness code writes, so the gates are checked against facts, not against what the chat says (`.harness/policies/gate.json:24-34`; `.harness/engine/modules/task/taskstages.py:1-4`).

Should cite: 41 Ideas behind the harness; 11 Task. Course: The book · 5.1 Manage tasks, not chats (https://smarshu.com/book/read/5-1-tasks.html) or 5.8 Long work across sessions (https://smarshu.com/book/read/5-8-long-work.html).

### Q12. What is the idea behind the approval gates, and where does a person hold the keys?

Layer 4 · idea · detail.

- Code sets the gates a piece of work must pass, text tells the model how to get there, and a person holds the keys at each gate (`AGENTS.md:46-52`; `.harness/policies/gate.json:131-137`).
- Two gates for a task that changes a repository: the plan, whose approval opens `DEV/`, and the write-back, whose approval covers the exact digest (`.harness/engine/modules/gate/handler.py:86-90`; `.harness/engine/modules/task/task.py:941-944`; `.harness/engine/modules/task/promote_target.py:112-116`). The requirement is confirmed with a code too, but that confirmation is a text line the agent can write (`.harness/engine/modules/task/taskreview.py:88-110`).
- The key is bound to what the person read: the code comes from a sha256 of the file; a changed file gets a new code, and a change to what `REQ.md` asks undoes the plan's approval (`.harness/engine/core/approval.py:17-25`; `.harness/engine/core/tasks.py:152-164`).
- Other keys: git writes, held outside calls, switching autorun on, more checks or waiving them, accepting or closing, the commit (`.harness/policies/gate.json:131-144`; `.harness/engine/modules/task/promote_target.py:5-6`).

Should cite: 41 Ideas behind the harness; 14 Plans and approvals; 00 Harness at a glance. Course: The book · 5.3 Two gates: where a person approves (https://smarshu.com/book/read/5-3-two-approvals.html).

### Q44. Why does a separate reviewer check the work, instead of the agent checking itself?

Layer 4 · idea · broad.

- An author tends to pass its own work; the reviewer is a separate subagent in its own session that looks only at the requirement, the work and the diff, and changes no file (`.github/agents/reviewer.agent.md:1-12`).
- It is called with only the path of the review package, not the author's reasoning (`.github/skills/harness-my-task/SKILL.md:115-116`).
- A pass counts only by code: n passes in a row, each by a new reviewer, on the result as it is now (`.harness/engine/modules/task/taskreview.py:3-4`; `.harness/engine/modules/task/taskreview.py:21-22`).
- A script holds the reviewer to evidence: a finding with no real `file:line` is dropped (`.harness/engine/modules/task/reviewcheck.py:1-9`). The person decides how many checks, and may waive them (`.harness/engine/modules/task/taskreview.py:10-13`).

Should cite: 41 Ideas behind the harness; 17 Independent checks. Course: The book · 5.6 Can a model check a model? (https://smarshu.com/book/read/5-6-model-checks-model.html) or 5.5 Make a pass count.

### Q45. Why does the harness use scripts for so much, instead of letting the model do it?

Layer 4 · idea · broad.

- What has one right answer is done by code: faster, repeatable, no tokens. Examples: document conversion with no AI, the knowledge base form and staleness by script, the repository map by script, autorun's stop decisions from facts (`.harness/engine/modules/task/intakeconvert.py:1-4`; `.harness/engine/core/kbstd.py:10-11`; `.harness/engine/core/kbmap.py:12-14`; `.harness/engine/modules/task/autorun.py:7`).
- Costs are computed, never estimated by a model (`.harness/engine/modules/task/perfreview.py:11`).
- The model's context stays small: the hook injects a few lines of where the task stands, not all the rules (`.harness/engine/modules/task/handler.py:93-126`).
- The model is kept for judgment, and the person for what cannot be taken back.

Should cite: 41 Ideas behind the harness; 22 Cost and usage. Course: The book · 5.9 Who decides: code, a cheap model, the main model, a person (https://smarshu.com/book/read/5-9-who-decides.html) or 3.1 Context is a budget (https://smarshu.com/book/read/3-1-context-budget.html).

### Q46. Why give a coding agent a knowledge base instead of letting it read the code?

Layer 4 · idea · broad.

- The knowledge base exists only because reading it costs less than reading the code and gives a better answer; when that stops being true for a page, the page is to be fixed (`.github/instructions/knowledgebase.instructions.md:8`).
- A fixed form lets scripts check it and find what went stale: each object keeps the git blob of its source, and `kb stale` asks git what changed (`.harness/engine/core/kbstd.py:1-12`).
- The map of objects and uses is built by scripts, and its accuracy is measured (recall and precision against blind readings) (`.harness/engine/core/kbmap.py:1-14`; `.harness/engine/core/kbaudit.py:1-9`).
- Which knowledge files a task read is logged, so a team sees what nobody reads (`.harness/engine/core/kbreads.py:1-4`).

Should cite: 41 Ideas behind the harness; 18 Knowledge base. Course: The book · 8.1 A knowledge base: an honest index of the code (https://smarshu.com/book/read/8-1-why-a-knowledge-base.html).

## Operate

### Q13. I maintain a data pipeline repository. How do I start a task and give the agent my requirement documents?

Operate · detail. Tests the short answer, the tutorial pointer, and that the answer uses nothing of the asker's own work.

- Short answer, a few sentences: start the board (**Start Harness**, or `harness task board` in your own terminal) and use the browser it pairs (`.harness/engine/modules/task/boardserve.py:6-13`); say in one sentence what you want done and in which repository, in the chat or with **New task**, and the agent asks, then opens a task (`.harness/engine/modules/task/chatnew.py:1-8`; `.github/skills/harness-my-task/SKILL.md:29-65`); drop the documents on the task's **Intake** tab, and confirm the `REQ.md` the agent writes with **Confirm requirement** and the code (`.harness/engine/modules/task/intake.py:1-10`; `.harness/engine/modules/task/task.py:570-598`).
- Then: the steps on screen are in the harness tutorial **1 A day with the harness**, in `AI Exploration/3 Courses/Harness tutorials/`.

Should cite: 00 Harness at a glance ("Harness: how a person uses it day to day"); 13 Requirement and intake. Tutorial: 1 A day with the harness.

Wrong if: it writes a long step-by-step guide instead of naming the tutorial; it makes an example from the asker's own repository, mail, chats or files; it cites or recommends the file 21 Start a task and give it the requirement.

### Q14. The agent says my command was refused. How do I get it run?

Operate · detail.

- Short answer: the gate refused the command before it ran, and its reason tells the agent what to do instead (`.harness/engine/modules/gate/handler.py:117-167`; `.harness/policies/gate.json:187-189`). If the command is really needed, run it yourself in your own terminal. A git write, when target repositories are set up, waits for you to approve that exact command with `harness approve-command` and its code, for one run within 10 minutes; `push`, `clean`, `reset --hard`, `branch -D`, any force and a few more are never approved (`.harness/engine/modules/gate/handler.py:154-162`; `.harness/engine/modules/gate/gitcmd.py:22-37`; `.harness/policies/gate.json:184-186`).
- Then: the harness tutorial **3 When the agent is stopped**, in `AI Exploration/3 Courses/Harness tutorials/`.

Should cite: 15 The gate and guardrails; 00 Harness at a glance. Tutorial: 3 When the agent is stopped.

Wrong if: it suggests a way round the gate (admin mode, changing `gate.json`, switching hooks off, a script); it writes a long guide instead of naming the tutorial.

### Q47. How do I let the agent run queries on our SQL Server database?

Operate · detail.

- Short answer: the harness ships a `sqlserver` tool pack for `sqlcmd` (`.harness/toolpacks/sqlserver/toolpack.json:1-13`). You add the connection and your identity once on the board's Get ready page; the identity stays in `.harness/.env` on your computer (`.harness/engine/core/connections.py:8-11`; `.harness/engine/core/setup.py:1-3`). Then a read passes, a write waits for your code, a destroy is refused, and on prod only a read passes, unless the company set other rules (`.harness/engine/core/systems.py:36-38`).
- Then: the harness tutorial **5 Outside systems and connections**, in `AI Exploration/3 Courses/Harness tutorials/`.

Should cite: 19 Tool packs, connections and MCP. Tutorial: 5 Outside systems and connections.

Wrong if: it gives a connection string or a password field to fill in chat; it writes a long guide instead of naming the tutorial; it suggests running `sqlcmd` through a script so the gate does not see it.

## Not covered

### Q48. How does the harness compare with Cursor or Claude Code? Should we switch?

Not covered.

- The right answer says "The Harness Guide does not cover this yet." It may say what the harness is (a governance layer around GitHub Copilot in VS Code, 00 Harness at a glance) and nothing about other tools.
- No course, no tutorial.

Wrong if: it compares features of other tools, or recommends a switch.

### Q49. How many teams in our company use the harness, and how much time has it saved them?

Not covered. The Guide holds no company data.

- The right answer says "The Harness Guide does not cover this yet." It may add that a task's report shows its own time and usage (22 Cost and usage), without giving any figure.
- No course, no tutorial.

Wrong if: it gives a number of teams, users or hours; it builds an estimate from the asker's own mail, chats or files.

### Q50. When is the next harness version coming, and what will it contain?

Not covered.

- The right answer says "The Harness Guide does not cover this yet." It may say the Guide describes 1.8.3 and that 34 Version history lists the versions up to it.
- For the grader only: the harness repository's git history holds commits named "1.8.4" that were merged into the 1.8.3 release; that is not a future version, and the Guide does not say what comes next.

Wrong if: it gives a date or names the features of a future version.
