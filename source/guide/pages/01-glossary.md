---
title: Glossary
subject: Glossary
layer: overview
file: 01 Glossary
harness_tag: 1.8.3
---
## Glossary: how to read these terms

The words the Harness Guide files use, for harness version 1.8.3, by area, then general AI words; each entry names the Guide file that explains it, with its code locations.

## Glossary: task terms

- **Accept and close** — the board button with which the person ends a task whose result stays in the folder (question, analysis, design, test), after the agent delivered it with `task deliver`. See: 11 Task.
- **DEV/** — the folder where the agent changes copies of repository files; the task chat's edit tools may write there only once the plan is approved, and only `DEV/<repository>/` is written back. See: 16 Write-back.
- **Fetch (`task fetch`)** — copies files of a target repository, as its base branch has them, into `DEV/`; it needs an approved plan. `task fetch --read` copies into `READ/`, to be read only, with no plan. See: 16 Write-back.
- **Intake** — how requirement documents enter a task: Word and Excel files are turned into Markdown and CSV in `REQ/` by a program, with no AI. See: 13 Requirement and intake.
- **Kind** — what a task is and what "done" means: `qa`, `rca` (root cause analysis), `design`, `dev`, `test`, `kb` (knowledge base update) or `other`. See: 11 Task.
- **Plan (`PLAN.md`)** — the agent's plan of the work, which the person approves with a code before the task chat may write in `DEV/`. See: 14 Plans and approvals.
- **REQ/, REF/, INBOX/** — the person's folders of a task (documents, reference material, results given on the task page); the task chat's edit tools are refused there. See: 13 Requirement and intake.
- **Requirement (`REQ.md`)** — the agent's account of what the person wants, which the person confirms with a code; its "User confirmed" line is text the agent could also write. See: 13 Requirement and intake.
- **Round** — one pass of a task up to its write-back; a written-back task opened again starts a new round with a new plan. One independent check is also called a round (`REVIEW/round-NNN/`). See: 11 Task.
- **Session** — one Copilot chat; it holds at most one task at a time, and the task outlives it. See: 11 Task.
- **Stage** — where a task stands (for `dev` and `kb`: requirement, plan, developing, write-back, done), worked out from the files each time, never set by the agent. See: 11 Task.
- **Task** — one piece of work kept as a folder under `.workspace/sandbox/tasks/<name>/`, with a handover note `TASK.md` any later chat reads first; the agent is told to open one, and code does not force it. See: 11 Task.
- **Task state file (`.task/task.json`)** — the task's record (status, round, approvals, history), written by harness code; the edit tools, and terminal commands that name it, are refused on it. See: 11 Task.
- **Tier** — which files a task has: `light` (`TASK.md`), `medium` (adds `REQ.md`, `REQ/`, `REF/`, `LOG.md`), `full` (adds `TODO.md`, the step list, `DEV/`, `TEST/`). See: 11 Task.
- **"Waiting for you"** — the board's state for a task whose next move is the person's while its agent is not mid-turn. See: 11 Task.

## Glossary: approval and write-back terms

- **Approval code** — the first six characters, in capitals, of a sha256 of what is approved, so a changed file gets a new code; held calls and git writes get a ticket for the exact command instead. See: 14 Plans and approvals.
- **`approve-command`** — the person's approval of one exact git write, once within 10 minutes, when target repositories are set up; `push`, `reset --hard` and any force are never approved. See: 16 Write-back.
- **Confirm requirement (`task confirm-req`)** — the person's code over `REQ.md`; `--with-req` (or **Approve plan**) confirms it and approves the plan with one code. See: 13 Requirement and intake.
- **Dry run (`task promote --dry-run`)** — builds the write-back plan, checks each repository, writes `PROMOTE-PLAN.diff` and writes nothing to a repository. See: 16 Write-back.
- **Held call** — a command to an outside system that must wait for the person (by default a write); once approved on its card or with `approve-action`, that exact command may run once within 10 minutes. See: 14 Plans and approvals.
- **Person-only command** — a harness command the gate refuses on the agent's command line, such as `task approve-plan`, `task autorun on`, `task allow`, `task close`, `admin on`. See: 14 Plans and approvals.
- **Recover the repository (`task recover`)** — the person's undo, with a code, of a write-back that stopped halfway. See: 16 Write-back.
- **Target repository** — a company code repository the harness may write back to, set up in **Get ready**; the agent's edit tools are refused in it. See: 16 Write-back.
- **Write-back (promote)** — `task promote`: the approved files from `DEV/` written to a new, uncommitted branch of each target repository (a registered knowledge base gets one commit); the approval binds a digest of branch, base commits and every file. See: 16 Write-back.

## Glossary: gate terms

- **Admin mode** — a switch on one chat, turned on only by the person with a code, that opens the guardrail files so the harness can be changed. See: 15 The gate and guardrails.
- **Allow, ask, refuse** — the gate's three answers; refuse wins over ask, ask over allow. An ask goes to Copilot's confirmation box; a refusal holds in every permission mode. See: 15 The gate and guardrails.
- **Ask list** — commands handed to Copilot's confirmation (deleting files, network, installs, git history rewrites); no box shows under Allow all, so it is a reminder. See: 15 The gate and guardrails.
- **Command-line-owned files** — `.task/`, `REVIEW/`, `OUTBOX/`, `READ/`, the `.diff` files and reports: only the `harness` command writes them. See: 15 The gate and guardrails.
- **Deny list** — commands always refused, such as `rm -rf` of the root or home folder, a download piped to a shell, `sudo`, `terraform apply`. See: 15 The gate and guardrails.
- **Edit tools** — the VS Code tools listed as edit or create tools in `tool_kinds.json`; an unlisted tool gets the kind `other` and no path check. See: 15 The gate and guardrails.
- **Fail closed** — when the guardrails cannot decide, every terminal command and file-changing tool is refused and reads go on; a hook that waits over 20 seconds for its lock gets the same answer ("the harness was busy"). See: 15 The gate and guardrails.
- **Gate** — the hook module that checks every tool call before it runs; it guards writes and commands, not reads, and reads the text of a call, so it is not a sandbox. See: 15 The gate and guardrails.
- **Guardrail files** — the files that hold the code rules (hooks, policies, engine, tool packs, `.harness/.env` and more), refused to the agent outside admin mode; `AGENTS.md`, instructions and skills are not among them. See: 15 The gate and guardrails.
- **Hook** — code VS Code runs at fixed events of a chat; the harness's one entry point runs the gate, task and observe modules, and only the event before a tool call decides whether it runs. See: 15 The gate and guardrails.
- **Integrity check** — while a guardrail file differs from the list the person accepted, the hook refuses every command and write. See: 24 Setup, doctor and upgrade.
- **Policy** — a JSON file in `.harness/policies/` with the lists and numbers the code reads, layered shipped, company, then the person's override. See: 31 How it is built.
- **Read-only turn** — the super agent chat (`/harness-super`) and a question to a task (`/harness-ask`), in which only reads and a few read-only harness commands pass. See: 15 The gate and guardrails.

## Glossary: board terms

- **Board** — the page `harness task board` (or **Start Harness**) serves on this computer only, with every task, what it waits for, and the buttons; only a person starts it. See: 12 The board.
- **Enter screen** — the board's first screen: five required lines must be green before **Enter** works. See: 12 The board.
- **Get ready** — the board's setup form; its choices go into the person's override files. See: 24 Setup, doctor and upgrade.
- **"Go on" message** — the fixed message the board sends the task's idle chat after an approval on the board; it starts a turn. See: 14 Plans and approvals.
- **Lobby, List, Super agent** — the board's three views: tasks as robots in zones, a table, and what waits across all tasks. See: 12 The board.
- **Pairing** — ties the buttons to the browser the person's terminal opened; an unpaired browser reads and can only pause and resume. See: 12 The board.
- **▶ Run and Terminal window** — run the person's own commands from the board server, which the gate does not see. See: 12 The board.
- **⚠ tag** — a health warning on an open task (stuck, repeat, idle, cost, context); it stops nothing. See: 12 The board.

## Glossary: agent and automation terms

- **Autorun** — a task mode (since 1.8.0) in which the agent works down `TODO.md` through the `worker` without a person at each step; only the person switches it on, code ends the run, the served board wakes the chat when it stops (the relay), and nothing is written back on the way. See: 20 Autorun.
- **Custom agent** — an agent file in `.github/agents/` with its own tools and model: `reviewer`, `mapper`, `worker`, `super`. See: 31 How it is built.
- **Independent check** — a review by the `reviewer` subagent, which sees the requirement, work and diff but never the author's reasoning; code counts the passes. See: 17 Independent checks.
- **Mapper** — the read-only subagent for parallel reading, only after the person types `/generic-mapreduce`, 4 calls in 60 minutes. See: 23 Skills.
- **Parked step** — an autorun step that cannot be settled, marked `[?]` with its question in `QUESTIONS.md`, asked once at the end. See: 20 Autorun.
- **Pass** — a `VERDICT: PASS`, counted in a row on the work as it is now; any change resets the count. See: 17 Independent checks.
- **Pit stop** — during autorun, the board ends the turn and compacts the chat at the compact percent (70 by default). See: 20 Autorun.
- **Proposal card** — the super agent's proposals as the board's own buttons; nothing happens until the person presses. See: 21 Super agent.
- **`[review]=n`** — the mark the person types to require n passes (0 off, at most 5); text a skill brings in does not count. See: 17 Independent checks.
- **Reviewer** — the subagent of the independent check, with no edit tool, called only in a task whose checks are on. See: 17 Independent checks.
- **Scheduler** — the task's own agent in autorun: it calls the worker per step and writes only `TODO.md`, `TASK.md`, `LOG.md`, `QUESTIONS.md`. See: 20 Autorun.
- **Skill** — a Copilot folder `.github/skills/<name>/SKILL.md`, read when a request matches or the person types `/<name>`; it is text, not enforcement. See: 23 Skills.
- **Stop reason** — the fact that ends an autorun run, such as `done`, `plan`, `budget`, `time`, `stalled`, `person`. See: 20 Autorun.
- **Super agent** — the board's view and one chat a day with the `super` custom agent, which only reads and proposes, within 50 Credits a day by default; it is not a subagent. See: 21 Super agent.
- **`/harness-ask`** — a marker, not a skill: the board sends the person's question to one task's chat as a read-only turn. See: 21 Super agent.
- **Text rules** — `AGENTS.md`, instructions, skills and the hook's prompt lines; they ask the model and block nothing. See: 23 Skills.
- **User-only skill** — a skill with `disable-model-invocation: true`, started only by the person or a board click; only text stops the agent reading it. See: 23 Skills.
- **Waive, extend, dismiss** — the person's choices, with a code, at the limit of checks: let this version through, give more checks, or drop a wrong one. See: 17 Independent checks.
- **Worker** — the subagent that does one `TODO.md` step in a fresh context, only while autorun is on. See: 20 Autorun.

## Glossary: knowledge base and outside system terms

- **Card** — the description of one object in a knowledge base domain, tied to its source's git blob so `kb stale` finds it when the source changes. See: 18 Knowledge base.
- **Connection** — one place an outside tool reaches (one database on DEV), with an environment and the person's sign-in in `.harness/.env`. See: 19 Tool packs, connections and MCP.
- **Domain** — one folder of a knowledge base for one business area, in a fixed form. See: 18 Knowledge base.
- **Knowledge base** — the team's Markdown and JSON notes about its code, in their own git repository, read before the code; the harness ships none. See: 18 Knowledge base.
- **Linked item** — a ticket named in a task (`ado:300100`); for `ado` and `demotracker`, a write to it is held until the person opens the linked items. See: 19 Tool packs, connections and MCP.
- **Open a connection (`task allow`)** — the person lets held writes on one connection pass in one task; `prod` never opens. See: 19 Tool packs, connections and MCP.
- **Tool pack** — a folder that teaches the agent one outside tool (database, ticket board, pipeline): the program, the gate's rules (`allow`, `task`, `outbox`, `human`, `deny` per verb) and skills. See: 19 Tool packs, connections and MCP.

## Glossary: cost terms

- **Agent Performance Review** — where a task's Credits and time went: free facts by code, and, when a person starts it, a model's verdict on whose each waste was. See: 22 Cost and usage.
- **Credits** — Copilot's AI Credits per model call, read from Copilot's own record, shown per prompt and stage on the report page; there is no total budget per task. See: 22 Cost and usage.
- **Spend limit** — the Credits an autorun run may add, picked by the person at each start. See: 20 Autorun.

## Glossary: general AI terms

- **Agent** — a model in a loop that asks for tool calls and gets their results; here, the Copilot agent in VS Code. Agent = Model + Harness. See: 41 Ideas behind the harness.
- **Allow all** — the chat permission under which Copilot's own confirmation box does not show; board-made chats start with it, and the gate's refusals still hold. See: 12 The board.
- **Compaction** — Copilot sums up a full chat (at about 80%) to free context; the task's files survive it. See: 11 Task.
- **Context** — everything the model reads at once, a shared budget; the harness loads core rules always and the rest on demand. See: 41 Ideas behind the harness.
- **Copilot Fusion** — Copilot picking a model per request; a task's chat does not start on it. See: 22 Cost and usage.
- **MCP server** — a program that gives the agent extra tools; in the harness it is off until the person allows it, and only a tool pack's named MCP tools are judged. See: 19 Tool packs, connections and MCP.
- **Prompt injection** — orders hidden in text the agent reads; the harness has no check for it and holds outside writes instead. See: 41 Ideas behind the harness.
- **Sandbox** — an operating-system boundary; the harness is not one, as the agent runs as the person's user. See: 00 Harness at a glance.
- **Subagent** — an agent the main agent calls for one job, with an empty context of its own; only `reviewer`, `mapper` and `worker` may run. See: 41 Ideas behind the harness.
- **Tool call** — one request of the model to run a tool; every one passes the hook first. See: 41 Ideas behind the harness.
