---
title: Code map
subject: Code map
layer: reference
file: 32 Code map
harness_tag: 1.8.3
---

## Code map: what this file holds

The code map lists every file of the harness engine at version 1.8.3, and the hook configuration, the policies, the contracts, the agents, the skills and the text rules, each with one or two sentences taken from the file itself (a Python module's docstring, a policy's `description`, a skill's `description`) and its code location. It answers "where in the code is X" and "what does file Y do". The engine has 191 Python files under `.harness/engine/`; 0 of them have no module docstring and are listed by path only. Each entry starts with the file's code location (its path and the lines of its docstring), then what the file says it does. The engine's own index of its parts is `.harness/INDEX.md` {src:.harness/INDEX.md#L101}.

## Code map: how the parts fit

Every hook event of a Copilot chat runs one command, `launch.py`, which loads and runs `hook.py` {src:.harness/engine/launch.py#L2-L5}: the adapter turns the event into the harness's own form, the modules listed in `registry.json` for that event decide, and the answers are merged (deny over ask over allow) {src:.harness/engine/hook.py#L2-L16}. The gate module guards writes; the task module keeps tasks, the board and autorun; the observe module writes the log; the evalcheck module judges fixed scenarios. A person and the agent reach the same code through the `harness` command (`cli.py`) {src:.harness/engine/cli.py#L2-L20}. The policies in `.harness/policies/` hold the settings and lists the code reads; an override goes in the `.override.json` file of the same name {src:.harness/INDEX.md#L64}.

## Code map: entry points (hook, launcher, CLI, doctor, integrity)

- {src:.harness/engine/cli.py#L2-L20} Command line entry for agents and people: \<python\> .harness/engine/cli.py \<command\> (python on Windows …
- {src:.harness/engine/doctor.py#L1} `cli.py doctor`: check that registry, files, hook config, policies and tool kinds agree.
- {src:.harness/engine/hook.py#L2-L16} The only hook entry point. One process per hook event.
- {src:.harness/engine/integrity.py#L1-L10} The integrity list of the guardrail files (1.7.38).
- {src:.harness/engine/launch.py#L2-L5} The one file `.github/hooks/harness.json` starts (1.7.38).

## Code map: adapters (Copilot payloads in and out)

- {src:.harness/engine/adapters/__init__.py#L1} Runtime adapters: raw hook payload \<-\> HookEvent / Decision.
- {src:.harness/engine/adapters/common.py#L1} Shared adapter helpers: tool\_kinds.json, tool input parsing, HookEvent construction.
- {src:.harness/engine/adapters/copilot_vscode.py#L1-L9} VS Code, Copilot (SDK) sessions: the `@github/copilot` engine. Fixtures: eval/fixtures/hooks/copilot-sdk/.

Data file of the adapters: `tool_kinds.json` {src:.harness/engine/adapters/tool_kinds.json}.

## Code map: engine core: knowledge base

- {src:.harness/engine/core/kbatlas.py#L1-L5} The map of the domains: which domain uses which, for a person.
- {src:.harness/engine/core/kbaudit.py#L1-L10} How right is the map? A measured answer, not a feeling.
- {src:.harness/engine/core/kbdetail.py#L1-L5} What the knowledge base window shows beside `kb status` (1.6.86): the stale cards, the form errors, when a …
- {src:.harness/engine/core/kbextract.py#L1-L6} Running the extractors of a toolkit: one file in, its objects out.
- {src:.harness/engine/core/kbgraph.py#L1-L10} Questions on the repository map: the objects and uses `kb map` cached, read back as one graph.
- {src:.harness/engine/core/kblearn.py#L1-L11} Learning a domain from the map: the structure is done by script, the words by the model.
- {src:.harness/engine/core/kbmap.py#L1-L15} Building the repository map (layer one of learning a code base): every object and every use, by script.
- {src:.harness/engine/core/kbmigrate.py#L1-L13} `kb migrate`: a domain of before the standard (v0) into the standard form v1, by code.
- {src:.harness/engine/core/kbreads.py#L1-L9} Which knowledge base files a tool call read.
- {src:.harness/engine/core/kbstatus.py#L1-L8} Where building the knowledge base stands, worked out from the files, never from what an agent remembers.
- {src:.harness/engine/core/kbstd.py#L1-L13} The knowledge base standard, v1: a fixed form, so that scripts can check it and find what went stale.

## Code map: engine core

- {src:.harness/engine/core/__init__.py#L1} Engine core: config, session state, events, fail-open, logs. Modules only import from here.
- {src:.harness/engine/core/ahp.py#L1-L13} A small client for the Agent Host Protocol of VS Code (1.6). Python standard library only.
- {src:.harness/engine/core/approval.py#L1-L8} A person's approval at a terminal or the paired board, with a typed code: behind confirm-req, approve-plan, approve-promote, recover, review extend, waive and dismiss, autorun on and admin on. Git writes and held outside calls get their codes from `core/approvals.py` instead.
- {src:.harness/engine/core/approvals.py#L1-L6} A person's approval of one command: a git write (A5, `approve-command`) or a call to an outside system (M43-4 …
- {src:.harness/engine/core/askmark.py#L1-L2} The mark of a question to a task through the board (1.8.2): a message that starts with `/harness-ask`.
- {src:.harness/engine/core/autorunfiles.py#L1-L3} The files of a task in autorun that the gate and the task module both read and write (1.8): TODO.md steps …
- {src:.harness/engine/core/boardperson.py#L1-L10} A command typed in the board's Terminal window is the person's (1.7.39).
- {src:.harness/engine/core/breaker.py#L1-L6} Deny circuit breaker: the same deny, again and again, ends with a plain stop instruction.
- {src:.harness/engine/core/callrecord.py#L1-L10} The record of one hook call, as it goes into the session log (observe module).
- {src:.harness/engine/core/calls.py#L1-L6} The calls to outside systems that went through, noted by the gate for the task that was open (1.7.9) …
- {src:.harness/engine/core/clip.py#L1} A text cut to a length for a person (1.7.38): between words, with an ellipsis, never inside a word.
- {src:.harness/engine/core/company.py#L1-L18} The company's own content: `<knowledge base>/company/`, kept apart from the harness so that a copy of the …
- {src:.harness/engine/core/config.py#L1-L6} Policy loading.
- {src:.harness/engine/core/connections.py#L1-L17} Connections and the person's identities for them (1.7.10, named so in 1.7.17).
- {src:.harness/engine/core/connlayers.py#L1-L14} Which step of a connection broke (1.7.38): program, sign-in, account access, address.
- {src:.harness/engine/core/context.py#L1} What a module gets besides the event: the session state and policies.
- {src:.harness/engine/core/copilot_events.py#L1-L12} Copilot's own record of a session: `~/.copilot/session-state/<session id>/events.jsonl`.
- {src:.harness/engine/core/domainskills.py#L1-L9} Domain skills: skills of one business domain live in the knowledge base, not in `.github/skills/`.
- {src:.harness/engine/core/evalrecord.py#L1-L17} The eval record of a task: what may be kept about a closed task, and nothing else.
- {src:.harness/engine/core/events.py#L1} HookEvent (what a hook received) and Decision (what a module wants), independent of the runtime.
- {src:.harness/engine/core/failopen.py#L1} Fail-open: a broken module or hook must never block normal work (AGENTS.md).
- {src:.harness/engine/core/gitread.py#L1-L6} Running git, once for the whole engine: the same environment, timeout and error for every call.
- {src:.harness/engine/core/govern.py#L1-L4} The programs a tool pack or the tools policy governs, read as plain text (1.7.38).
- {src:.harness/engine/core/guardrails.py#L1} The guardrail files every Level must protect. Core knows them so the gate and promote share one floor.
- {src:.harness/engine/core/inputfiles.py#L1-L8} The files and the text a call reads its statements from (1.7.38).
- {src:.harness/engine/core/launchenv.py#L1-L14} What VS Code needs at its start so that the agent's commands reach the tools of this computer (1.7.11).
- {src:.harness/engine/core/logs.py#L1-L5} JSONL logs under .harness/runtime/logs/. Logging must never raise.
- {src:.harness/engine/core/messages.py#L1-L8} The message table: what the engine says to people and agents, by name.
- {src:.harness/engine/core/miniyaml.py#L1-L6} The part of YAML a knowledge base uses, read and written with the standard library only.
- {src:.harness/engine/core/netonly.py#L1-L6} Start a process with network credentials only, as `runas /netonly` does, without a prompt (1.7.10).
- {src:.harness/engine/core/outbox.py#L1-L8} The outbox: a call to an outside system the policy marks `outbox` waits for a person.
- {src:.harness/engine/core/output.py#L1} How the CLI prints: the `cli` policy. Reading it never fails: a missing or broken policy means the default.
- {src:.harness/engine/core/paths.py#L1} Repository paths. HARNESS\_ROOT overrides the root (used by tests).
- {src:.harness/engine/core/pinfiles.py#L1-L10} The files a held call reads, pinned when the person approves it (1.7.38).
- {src:.harness/engine/core/pinpython.py#L1-L9} The Python the harness runs on, pinned (1.5.46).
- {src:.harness/engine/core/procrun.py#L1-L5} A program run with a time limit that holds (1.7.45). `subprocess.run(timeout=)` on Windows kills only the …
- {src:.harness/engine/core/reach.py#L1-L19} Can the agent reach each environment from VS Code? (1.7.9)
- {src:.harness/engine/core/readyitems.py#L1-L18} What the company brings, and what is still missing (1.7.38, block B): the Optional block of the Enter screen …
- {src:.harness/engine/core/redact.py#L1-L5} Take what looks like a secret out of a text before it leaves the machine's logs (a sample kept for eval).
- {src:.harness/engine/core/registry.py#L1} Module registry: .harness/registry.json. Decides which modules get which events.
- {src:.harness/engine/core/reinstall.py#L1-L14} `harness reinstall --from <old copy>`: carry what only this machine holds from an older copy of the harness to …
- {src:.harness/engine/core/render.py#L1-L5} A command result as text a person reads at a terminal. The CLI prints JSON on a pipe and this on a terminal.
- {src:.harness/engine/core/repo_paths.py#L1-L4} Path handling for the gate: one spelling for relative, absolute, `..`, Windows `\` and any letter case.
- {src:.harness/engine/core/schema.py#L1-L5} Minimal JSON schema check: type, required, enum, properties, items, minimum, and a few size and shape limits.
- {src:.harness/engine/core/setup.py#L1-L4} Get ready (1.6.57): what the page `/setup` shows and writes. No agent, no premium request.
- {src:.harness/engine/core/shortcmd.py#L1-L4} The short command `harness`: the one line a person runs once, and whether a new terminal finds it (1.6.57).
- {src:.harness/engine/core/skillboard.py#L1-L12} What skills show on the board (1.6.62).
- {src:.harness/engine/core/skillcheck.py#L1-L5} Is a skill well formed? The checks a person would do by hand before putting a skill into `.github/skills/`.
- {src:.harness/engine/core/skillgroups.py#L1-L9} Which of three groups a skill belongs to, by its name alone (1.7.32).
- {src:.harness/engine/core/standards.py#L1-L5} The company's code standards, written by the company, read by the skill `generic-code-standards` …
- {src:.harness/engine/core/starticon.py#L1-L6} The icon of Start Harness (1.6.83): the robot, on this computer, from the first start on.
- {src:.harness/engine/core/state.py#L1-L10} Per-session state: lock, atomic write, shared fields, subagent tracking.
- {src:.harness/engine/core/statements.py#L1-L15} Free text cut into statements (1.7.38, C12: pass, refuse, ask).
- {src:.harness/engine/core/systems.py#L1-L11} The outside systems a company lists (`systems` in tools.json, its company and override layers): what the list …
- {src:.harness/engine/core/targets.py#L1-L13} Target repositories: git repositories outside the harness folder that a task reads from and promotes into.
- {src:.harness/engine/core/tasks.py#L1-L8} A task: where its files live and what its state says.
- {src:.harness/engine/core/toolpacks.py#L1-L28} Tool packs (1.7.12): what lets the agent work with one outside tool (a ticket board, a pipeline service), as …
- {src:.harness/engine/core/unseen.py#L1-L4} Tool calls the harness has not seen: a tool name it does not know, or a shape it cannot read.
- {src:.harness/engine/core/user.py#L1} Who uses this copy of the harness: the `user` policy. An agent asks for the name with `harness user`.

Data files of the engine core: `messages.en.json` {src:.harness/engine/core/messages.en.json}, `messages.zh.json` {src:.harness/engine/core/messages.zh.json}. `messages.en.json` and `messages.zh.json` hold every sentence the hooks and the CLI say, in English and Chinese.

## Code map: gate module

- {src:.harness/engine/modules/gate/__init__.py#L1} Gate: guardrail files, the write scope of a task and dangerous terminal commands.
- {src:.harness/engine/modules/gate/approvals.py#L1} The approvals live in core (1.7.7: the task module reads them for the board); this name stays for the gate and …
- {src:.harness/engine/modules/gate/askturn.py#L1-L5} 1.8.2: a question to a task through the board.
- {src:.harness/engine/modules/gate/buildtools.py#L1-L11} Build tools: programs that run what a file of the project says (1.7.38).
- {src:.harness/engine/modules/gate/builtin.py#L1-L8} A built-in copy of the shipped gate policy (1.7.38).
- {src:.harness/engine/modules/gate/commands.py#L1-L9} CLI commands of the gate module.
- {src:.harness/engine/modules/gate/external.py#L1-L24} External actions: the protocol for a call that reaches a system outside this repository (a cloud, a database …
- {src:.harness/engine/modules/gate/failclosed.py#L1-L8} A gate that fails does not let a governed program through (1.7.38).
- {src:.harness/engine/modules/gate/fallback.py#L1-L14} The gate when its own policy cannot be read (1.7.38).
- {src:.harness/engine/modules/gate/gitcmd.py#L1-L9} git commands in a terminal call: what only reads, what needs a person's approval, what is never approved.
- {src:.harness/engine/modules/gate/handler.py#L1-L14} gate hook handler. PreToolUse only. It guards writes and never blocks a read.
- {src:.harness/engine/modules/gate/harnesscmd.py#L1-L8} The harness commands only a person may run, read as the shell reads them (1.7.38).
- {src:.harness/engine/modules/gate/outbox.py#L1} The outbox lives in core (1.7.7: the task module reads it for the board); this name stays for the gate and the …
- {src:.harness/engine/modules/gate/pin.py#L1-L15} Which connection does a call reach? (1.7.38)
- {src:.harness/engine/modules/gate/policy.py#L1} gate.json: schema, validation and the compiled form the handler uses.
- {src:.harness/engine/modules/gate/rules.py#L1-L5} Texts the model sees when the gate refuses a call. Each says why it was refused and what to do next.
- {src:.harness/engine/modules/gate/scriptcheck.py#L1-L12} The run of a script is judged (1.7.38, narrowed in FR2 3).
- {src:.harness/engine/modules/gate/shellwords.py#L1-L9} How the gate reads the words of a shell line and the wrappers in it (1.7.38). Standard library only.
- {src:.harness/engine/modules/gate/superagent.py#L1-L5} The super agent chat (1.8.1): a Copilot chat the board opens to talk about the tasks.
- {src:.harness/engine/modules/gate/targetfault.py#L1-L13} A `target.json` that cannot be read (1.7.38).
- {src:.harness/engine/modules/gate/terminal.py#L1-L6} Terminal commands: what writes a guardrail file, what is denied, what needs a person to confirm.
- {src:.harness/engine/modules/gate/wait.py#L1-L19} `harness wait` (1.7.5): wait for an outside system to reach a state, in one terminal call, so the agent does …

## Code map: task module: autorun

- {src:.harness/engine/modules/task/autorun.py#L1-L23} autorun (beta): the default agent only schedules; a worker does one TODO step at a time, and a fact says when …
- {src:.harness/engine/modules/task/autorun_board.py#L1-L8} autorun on the board (1.8, step 9): what the Start form offers, the checks of a Start request, and the run …
- {src:.harness/engine/modules/task/autorun_relay.py#L1-L15} autorun, the third layer and the pit stop (1.8, steps 7 and 8): the board wakes the agent, and ends a turn to …
- {src:.harness/engine/modules/task/autorun_spend.py#L1-L6} autorun spend limit (1.8.0, step 4): the Credits a run has spent, read from the events file of the session …
- {src:.harness/engine/modules/task/autorun_start.py#L1-L11} autorun, the Start order of the board (1.8, step 9; design §9).

## Code map: task module: super agent

- {src:.harness/engine/modules/task/superact.py#L1-L8} Proposals of the super agent (1.8.3): the agent never does anything; it may end an answer with one block and …
- {src:.harness/engine/modules/task/superbrain.py#L1-L14} The super agent chat (1.8.1, steps 5 and 7): one Copilot chat that the board opens and owns.
- {src:.harness/engine/modules/task/superpreview.py#L1-L6} A short look at a task's plan or changes for the super agent view (1.8.2, step 6): `/api/super/preview` …
- {src:.harness/engine/modules/task/superroute.py#L1-L8} Asking a task from the super agent view (1.8.2, step 3): the person's question goes to one task's chat with …
- {src:.harness/engine/modules/task/superview.py#L1-L9} The super agent view (1.8.1): what waits for the person across all open tasks, as a list of short items, from …

## Code map: task module: link to VS Code chats

- {src:.harness/engine/modules/task/chatask.py#L1-L9} What waits for a person in a chat of VS Code, and how the board answers it (1.6).
- {src:.harness/engine/modules/task/chatctx.py#L1-L12} How full the context of a chat is (1.6).
- {src:.harness/engine/modules/task/chatlink.py#L1-L16} Which chat of VS Code belongs to which task (1.6). Never a guess: when it is not sure, the task is unbound.
- {src:.harness/engine/modules/task/chatlive.py#L1-L9} What the Live tab shows of a chat (1.6): the latest few items of the cached state, small, redacted and cut.
- {src:.harness/engine/modules/task/chatnew.py#L1-L9} Making a task from the board (1.6): what the dialog sends is checked here, and the first message is made here.
- {src:.harness/engine/modules/task/chatrounds.py#L1-L10} The rounds of a task's chat (1.6.55): each prompt of the person, with all the text the agent wrote for it, for …
- {src:.harness/engine/modules/task/chatsend.py#L1-L13} What the board says to the chat of a task, and what it keeps of it (1.6).
- {src:.harness/engine/modules/task/tasksub.py#L1-L8} The line under a task name on the board, and the "recent" bar of a task page (1.6): what the agent did last.
- {src:.harness/engine/modules/task/vslink.py#L1-L20} The link from the board to the VS Code that runs the chats (1.6).
- {src:.harness/engine/modules/task/vsrestart.py#L1-L7} Restart VS Code from the board (1.7.38, block B): ask it to quit the normal way, wait until it has gone, open …

## Code map: task module: board server and pages

- {src:.harness/engine/modules/task/boardserve.py#L1-L38} `task board --serve`: the board as a page on this computer only, with buttons that act.
- {src:.harness/engine/modules/task/boardterm.py#L1-L10} The Terminal window of the board (1.6.92): a person types a command on the page and reads its output, in tabs.
- {src:.harness/engine/modules/task/cmdview.py#L1-L6} How a command is laid out for a person (1.7.7): the program on the first line, each option on its own line …
- {src:.harness/engine/modules/task/companyview.py#L1-L5} The Company tab of the knowledge base window (1.7.32): what this company's agent can do, from the files that …
- {src:.harness/engine/modules/task/gatereview.py#L1-L10} Gate blocks of one task, the person's verdict on each, and the samples made from the wrong ones (1.6).
- {src:.harness/engine/modules/task/health.py#L1-L15} Health rules of a task on the board (1.6): a warning tag, only when a rule fires.
- {src:.harness/engine/modules/task/kbview.py#L1-L4} The knowledge base window of the board (1.6.63).
- {src:.harness/engine/modules/task/mdtree.py#L1-L11} Markdown into a tree of blocks for the task page: Python reads, the page draws with textContent only.
- {src:.harness/engine/modules/task/outview.py#L1-L12} How the output of a run is laid out for a person (1.7.9).
- {src:.harness/engine/modules/task/perfreview.py#L1-L18} Agent Performance Review (1.7.41): the command an rca task uses to review how the agent of another task …
- {src:.harness/engine/modules/task/ready.py#L1-L17} What the Enter screen of the board asks (`/api/ready`, 1.6 B86): is everything the board needs in place?
- {src:.harness/engine/modules/task/reviewcheck.py#L1-L10} What a script can hold the reviewer to (1.5.31).
- {src:.harness/engine/modules/task/rewind.py#L1-L12} Rewind (1.6.109): a restore point of the task folder at each message of the person, so the task can go back to …
- {src:.harness/engine/modules/task/setupjob.py#L1-L4} Get ready: the part of Finish that can take long (1.6.58).
- {src:.harness/engine/modules/task/skillsend.py#L1-L5} One-click skills of the board (1.6.61): a new chat in VS Code whose first message calls a skill.
- {src:.harness/engine/modules/task/stmtview.py#L1-L9} The statements of a held call, one by one, for its card (1.7.38): a statement, which system it is on, and how …
- {src:.harness/engine/modules/task/taskboard.py#L1-L10} The task board: which task waits for the person, and for how long. Code only, no agent, no token.
- {src:.harness/engine/modules/task/taskdesk.py#L1-L6} One task in the browser: its documents, its TODO progress, its history, what it changes, and what the person …
- {src:.harness/engine/modules/task/taskfileedit.py#L1-L7} The person changes the files of a task from its Files tab (1.6.100): edit a text file, add a file or a folder …
- {src:.harness/engine/modules/task/taskfiles.py#L1-L9} The "Files" tab of the task page (1.5.41): what the person put in `REQ/` and `REF/`, the files the agent …
- {src:.harness/engine/modules/task/taskhtml.py#L1-L37} The two pages a person opens in a browser: one task's time and usage, and the board of all tasks.
- {src:.harness/engine/modules/task/taskinbox.py#L1-L11} `INBOX/` (1.5.42): what the person gives the task on its page, saved by the board server, read by the agent.
- {src:.harness/engine/modules/task/taskinsight.py#L1-L13} Where a task's time and usage went: the numbers behind `task report` and the board.
- {src:.harness/engine/modules/task/taskreview.py#L1-L23} Independent checks of a task: `[review]=n`.
- {src:.harness/engine/modules/task/taskrun.py#L1-L9} Commands the person runs from the task page (1.6.50): the Run button of a code block.
- {src:.harness/engine/modules/task/tasksize.py#L1-L6} How much room the task folders take (1.6.109): the served board measures `.workspace/sandbox/tasks/` once an …
- {src:.harness/engine/modules/task/tasktrace.py#L1-L15} The Trace tab of a task page (1.6): a timeline of the tool calls and the gate decisions of the task's session.
- {src:.harness/engine/modules/task/wallpaper.py#L1-L11} The wallpaper of the board (1.6.19): the pictures of one folder the person chose, read only.

## Code map: task module: checks, records and reports

- {src:.harness/engine/modules/task/evidence.py#L1-L5} Evidence (1.7.3): every run saved in a task has one number, `E<n>`, whichever way it came: a run the person …
- {src:.harness/engine/modules/task/perfdata.py#L1-L22} Agent Performance Review, layer 1 (1.7.41): the accounts and the facts of how the agent of one task worked.
- {src:.harness/engine/modules/task/perfroll.py#L1-L9} Agent Performance Review across tasks (`harness task performance --all`): what keeps coming back, and what it …
- {src:.harness/engine/modules/task/runrecord.py#L1-L10} `harness task run record` (1.5.42): the result of a run the person did before the write-back, written by a …
- {src:.harness/engine/modules/task/task_report.py#L1-L6} `task report`: one Markdown page about a task, from task.json, PLAN.md, DEV/ and the hook log of its session.
- {src:.harness/engine/modules/task/testdefects.py#L1-L7} The defects of a test task (`TEST/defects.md`) and their status, kept by a script, not by hand (1.5.27).
- {src:.harness/engine/modules/task/testrecord.py#L1-L13} `harness task test record`: the results of a test environment are written by a script, not by hand (1.5.28).

## Code map: task module: task life, commands and write-back

- {src:.harness/engine/modules/task/__init__.py#L1} Task: the task folder, its life, its two approvals, its independent checks, and what every prompt is told.
- {src:.harness/engine/modules/task/accept.py#L1-L11} Closing is the person's acceptance (1.7.38, C12 Q14; C13: the agent closes nothing).
- {src:.harness/engine/modules/task/basesync.py#L1-L15} Bring the base branch of a target repository up to its remote before files are read from it (1.5.39).
- {src:.harness/engine/modules/task/commands.py#L1-L16} CLI commands of the task module.
- {src:.harness/engine/modules/task/commitmsg.py#L1-L13} The commit message of a write-back (1.5.29): the agent writes it, the page shows it with the contributor line …
- {src:.harness/engine/modules/task/common.py#L1-L4} What the task commands share: the refusal a command raises, clean paths, file copies, the target repositories.
- {src:.harness/engine/modules/task/handler.py#L1-L24} task hook behavior: what every prompt is told, which subagent may be called, and the two reminders at Stop.
- {src:.harness/engine/modules/task/intake.py#L1-L11} `task intake` (1.5.44): the documents a business gave, as files the agent can read, in `REQ/` of a task.
- {src:.harness/engine/modules/task/intakeconvert.py#L1-L16} Business documents as text the agent can read (1.5.44): docx to Markdown, xlsx to CSV, with a report of what …
- {src:.harness/engine/modules/task/kbsetup.py#L1-L5} `target init-kb`: make `knowledge-base/` a git repository, so that a task can update it.
- {src:.harness/engine/modules/task/mapreduce.py#L1-L13} `/generic-mapreduce`: the one way a session may call subagents that are not the reviewer.
- {src:.harness/engine/modules/task/policy.py#L1} task.json: how many files a fetch may copy, the contributor line of the commit message, the TASK.md reminder …
- {src:.harness/engine/modules/task/promote_target.py#L1-L15} promote to target repositories: the result of a task goes onto a new branch of each repository.
- {src:.harness/engine/modules/task/reachcheck.py#L1-L12} The board checks the outside connections itself (1.7.19), in the background, so the Enter screen does not wait …
- {src:.harness/engine/modules/task/refs.py#L1-L6} `target refs`: where are these names used? One search over every target repository and the knowledge base.
- {src:.harness/engine/modules/task/steps.py#L1-L20} A run the agent did as steps (1.7.9): one step per command, each with its title, what it shows, the command …
- {src:.harness/engine/modules/task/task.py#L1-L15} A task: one agent, a task folder, and two approvals by the person (the plan, the promote).
- {src:.harness/engine/modules/task/taskarchive.py#L1-L14} `task archive`: move closed tasks out of `.workspace/sandbox/tasks/` into a folder of the person's choosing.
- {src:.harness/engine/modules/task/taskfork.py#L1-L10} `task fork` (1.5.37): a task is done, the next one starts from what it found.
- {src:.harness/engine/modules/task/tasklife.py#L1-L13} A task's life, apart from a session: make it, pick it up, give it more files, list them all.
- {src:.harness/engine/modules/task/taskqueue.py#L1-L10} The promote queue: several tasks, one branch each, written into the same repositories one after the other.
- {src:.harness/engine/modules/task/tasksnap.py#L1-L7} Snapshots of a task at its gates: what the results were when the plan was approved, before each check, before …
- {src:.harness/engine/modules/task/taskstages.py#L1-L15} The stage ribbon of a task: the steps its kind has, which are done, which is the one now, and the reviewer's …

## Code map: observe module (logs and statistics)

- {src:.harness/engine/modules/observe/__init__.py#L1} Observe: one log file per session, and the numbers read from them. Policy: .harness/policies/observe.json.
- {src:.harness/engine/modules/observe/commands.py#L1-L11} CLI commands of the observe module.
- {src:.harness/engine/modules/observe/handler.py#L1-L6} observe: writes the call log. hook.py calls `record_call` after the decision is merged, so the record has the …
- {src:.harness/engine/modules/observe/kbstats.py#L1-L6} `kb reads`: which knowledge base files the tasks read, and which nobody read.
- {src:.harness/engine/modules/observe/policy.py#L1-L2} observe.json: how long a recorded text may be, the capture switch, when doctor says the logs are many, whether …
- {src:.harness/engine/modules/observe/prune.py#L1} `cli logs prune`: delete session logs not written to for N days. Nothing is deleted automatically.
- {src:.harness/engine/modules/observe/stats.py#L1} `cli stats`: counts and times from the session logs.

## Code map: evalcheck module (fixed scenarios)

- {src:.harness/engine/modules/evalcheck/__init__.py#L1} Eval: fixed scenarios and `cli eval check`, which judges a finished run from its session log and the files it …
- {src:.harness/engine/modules/evalcheck/checks.py#L1} Run the checks of one scenario against one finished run. Reads only; every answer is yes or no with a reason.
- {src:.harness/engine/modules/evalcheck/commands.py#L1-L6} CLI commands of the evalcheck module.
- {src:.harness/engine/modules/evalcheck/handler.py#L1} evalcheck subscribes to no event: it only reads what other modules wrote. `doctor` checks the scenario files.
- {src:.harness/engine/modules/evalcheck/scenario.py#L1-L12} A scenario is a folder `.harness/eval/scenarios/<id>/` with `scenario.md` (what to run, what a person checks) …

## Code map: modules package

- {src:.harness/engine/modules/__init__.py#L1} Pluggable modules. Each one exposes handle(event, ctx) -\> Decision \| None and imports only core/.

## Code map: board pages (`modules/task/web/`)

The board's pages are served by `task board --serve` (`modules/task/boardserve.py`) on 127.0.0.1 only {src:.harness/engine/modules/task/boardserve.py#L1-L38}. The scripts and pages, each with the first sentence of its own header comment:

Pages: `board.html` {src:.harness/engine/modules/task/web/board.html}; `desk.html` {src:.harness/engine/modules/task/web/desk.html}; `perfpage.html` {src:.harness/engine/modules/task/web/perfpage.html}; `setup.html` {src:.harness/engine/modules/task/web/setup.html}; `task.html` {src:.harness/engine/modules/task/web/task.html}.

Scripts: `autorun.js`: Autorun on the board (1.8, step 9): the Start dialog (models, spend limit, the typed code) and the run card of … {src:.harness/engine/modules/task/web/autorun.js#L1-L2}; `batch.js`: A box over the cards when two held calls or more of a task wait at once (1.7.38): one row for each call (its … {src:.harness/engine/modules/task/web/batch.js#L1-L4}; `board.js`: The board: every task, what it waits for, its time and usage {src:.harness/engine/modules/task/web/board.js#L1-L8}; `bot3d.js`: The robot of the Enter screen in 3D (1.6.76): one canvas, one fragment shader that draws the robot of enter.js … {src:.harness/engine/modules/task/web/bot3d.js#L1-L2}; `chat.js`: Talking to the chat of a task from a served page (1.6): the send panel, "steer" and "stop"; the "New task" … {src:.harness/engine/modules/task/web/chat.js#L1-L2}; `common.js`: Shared by the task page and the board. No library, no network {src:.harness/engine/modules/task/web/common.js#L1-L3}; `companion.js`: The pop-out of the super agent view (1.8.1, "the companion"): a small window that stays on top of every other … {src:.harness/engine/modules/task/web/companion.js#L1-L8}; `companytab.js`: The Company tab of the knowledge base window (1.7.32): what this company's agent can do, from the files in … {src:.harness/engine/modules/task/web/companytab.js#L1-L3}; `desk.js`: One task in the browser: its documents, TODO progress, history, changes, and what the person can do now {src:.harness/engine/modules/task/web/desk.js#L1-L5}; `diffview.js`: The code compare of the Changes tab, as in VS Code: old code on the left, new code on the right (or one … {src:.harness/engine/modules/task/web/diffview.js#L1-L5}; `dock.js`: The buttons at the bottom right (1.6.61): the question mark and the one-click chats {src:.harness/engine/modules/task/web/dock.js#L1-L2}; `enter.js`: The Enter screen of a served page (1.6 B86): the wordmark HARNESS, the robot floating over its middle (in 3D … {src:.harness/engine/modules/task/web/enter.js#L1-L14}; `highlight.js`: Colours for code, by the type of the file or the language of a fenced block: SQL, Bash, PowerShell, Python … {src:.harness/engine/modules/task/web/highlight.js#L1-L4}; `kbatlas.js`: The map of the domains, in the knowledge base window (core/kbatlas.py) {src:.harness/engine/modules/task/web/kbatlas.js#L1-L4}; `live.js`: The Live tab of a task page (1.6.17): the latest items of the agent's chat, as they come {src:.harness/engine/modules/task/web/live.js#L1-L7}; `lobby.js`: The lobby: the first screen of the board {src:.harness/engine/modules/task/web/lobby.js#L1-L7}; `machine.js`: Local (1.7.11) and Tool packs (1.7.13), two of the three windows of tools.js (the third is Connections & … {src:.harness/engine/modules/task/web/machine.js#L1-L3}; `perf.js`: The small part of the Agent Performance Review on a task's report page (1.7.41) {src:.harness/engine/modules/task/web/perf.js#L1-L3}; `perfpage.js`: The Agent Performance Review page of a task (`/tasks/<task>/performance`, 1.7.41) {src:.harness/engine/modules/task/web/perfpage.js#L1-L4}; `pet.js`: The pet of the super agent view (1.8.1): a small robot in a headset that hovers over the view, turns to face … {src:.harness/engine/modules/task/web/pet.js#L1-L5}; `readybar.js`: The blocks at the top of the board after Enter (1.7.38, block B): what is still missing, from the same answer … {src:.harness/engine/modules/task/web/readybar.js#L1-L7}; `readyui.js`: Shared by the Enter screen (enter.js) and the block of the board after Enter (readybar.js) (1.7.38, block B) … {src:.harness/engine/modules/task/web/readyui.js#L1-L9}; `reply.js`: The reply panel of a task page (1.6.17): one small pill fixed at the bottom centre ("Say something", key R, a … {src:.harness/engine/modules/task/web/reply.js#L1-L10}; `rounds.js`: The earlier rounds of a task's chat, at the top of the Live tab (1.6.55): one line for each prompt of the … {src:.harness/engine/modules/task/web/rounds.js#L1-L7}; `run.js`: The two buttons of a shell code block on the task page (1.6.50), and the panel of a running command {src:.harness/engine/modules/task/web/run.js#L1-L3}; `serve.js`: Only in the page `task board --serve` sends (never in the files on disk): the buttons that act, and the … {src:.harness/engine/modules/task/web/serve.js#L1-L4}; `servers.js`: Connections & sign-ins (1.7.10, one window since 1.7.38): the connections of the company and the person's own … {src:.harness/engine/modules/task/web/servers.js#L1-L3}; `setup.js`: Get ready (1.6.57): one command, then one form. No agent runs {src:.harness/engine/modules/task/web/setup.js#L1-L2}; `shell.js`: The controls fixed to the browser window of the board and the task page: the search pill (top right) and the … {src:.harness/engine/modules/task/web/shell.js#L1-L8}; `space.js`: The 3D space behind the page (1.6.19): the stage (\#sp) with the picture far back, two layers of dust nearer … {src:.harness/engine/modules/task/web/space.js#L1-L6}; `status.js`: The small status marks of a task (1.6.14): one row of up to five marks, in this order: model, context, run … {src:.harness/engine/modules/task/web/status.js#L1-L9}; `stmts.js`: The statements of a held call on its card (1.7.38): numbered, each with the system it is on and how its type … {src:.harness/engine/modules/task/web/stmts.js#L1-L4}; `super.js`: The super agent view of the board (1.8.1): one window like a messenger {src:.harness/engine/modules/task/web/super.js#L1-L9}; `superhist.js`: The history of the super agent chat (1.8.1): a panel over the messages of the super view with the earlier days … {src:.harness/engine/modules/task/web/superhist.js#L1-L3}; `task.js`: One task: where its time and usage went. DATA.info is what taskinsight.build returns {src:.harness/engine/modules/task/web/task.js#L1-L4}; `term.js`: The Terminal window (1.6.92): a small window at the top right of a served page, with tabs {src:.harness/engine/modules/task/web/term.js#L1-L5}; `theme.js`: Sets data-theme on \<html\> before the page is drawn: the person's choice (localStorage "harness.theme": light … {src:.harness/engine/modules/task/web/theme.js#L1-L4}; `tools.js`: Tools (1.7.38): three windows, each opened on its own: Tool packs, Connections & sign-ins, and Local {src:.harness/engine/modules/task/web/tools.js#L1-L4}; `wall.js`: The wallpaper of a served page (1.6.19): the pictures of the one folder the person chose, shown behind the … {src:.harness/engine/modules/task/web/wall.js#L1-L9}.

Style sheets and pictures of the board: `autorun.css`, `batch.css`, `companion.css`, `company.css`, `desk.css`, `diffview.css`, `dock.css`, `enter.css`, `highlight.css`, `icon.png`, `kbatlas.css`, `list.css`, `live.css`, `lobby.css`, `page.css`, `perf.css`, `perfpage.css`, `readybar.css`, `rounds.css`, `run.css`, `setup.css`, `shell.css`, `space.css`, `status.css`, `stmts.css`, `super.css`, `tokens.css`, `ui.css`, `wall.css`.

## Code map: hooks and the module registry

The hook configuration `.github/hooks/harness.json` subscribes the harness to 9 events of a Copilot chat, and every one runs the same command, `python3 .harness/engine/launch.py` (`python .harness/engine/launch.py` on Windows): `SessionStart` {src:.github/hooks/harness.json#L4}, `UserPromptSubmit` {src:.github/hooks/harness.json#L16}, `userPromptTransformed` {src:.github/hooks/harness.json#L28}, `PreToolUse` {src:.github/hooks/harness.json#L40}, `PostToolUse` {src:.github/hooks/harness.json#L52}, `PostToolUseFailure` {src:.github/hooks/harness.json#L64}, `SubagentStart` {src:.github/hooks/harness.json#L76}, `SubagentStop` {src:.github/hooks/harness.json#L88}, `Stop` {src:.github/hooks/harness.json#L100}.

- Module `task` (active, on): hook events `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`; 106 files and folders belong to it {src:.harness/registry.json#L92}.
- Module `gate` (active, on): hook events `PreToolUse`, `UserPromptSubmit`, `SessionStart`, `PostToolUse`, `PostToolUseFailure`; 44 files and folders belong to it {src:.harness/registry.json#L222}.
- Module `observe` (active, on): hook events `PostToolUseFailure`; 3 files and folders belong to it {src:.harness/registry.json#L287}.
- Module `evalcheck` (active, on): hook events no hook event (command line only); 3 files and folders belong to it {src:.harness/registry.json#L306}.

The registry also lists the files of the engine itself, which an upgrade replaces as a whole {src:.harness/registry.json#L9}.

## Code map: the `harness` command and the start files

- `.harness/bin/harness`: Short command for people and agents (macOS/Linux): harness \<command\> ... Like git, it works on the harness … {src:.harness/bin/harness#L2-L5}
- `.harness/bin/harness.cmd`: Short command for people and agents (Windows): harness \<command\> ... Like git, it works on the harness … {src:.harness/bin/harness.cmd#L2-L5}
- `Start Harness.command`: Double-click on macOS: starts the task board of this copy. Keep this window open while you work. {src:Start Harness.command#L2}
- `Start Harness.cmd`: Double-click on Windows: starts the task board of this copy. Keep this window open while you work. {src:Start Harness.cmd#L2}

## Code map: policies (`.harness/policies/`)

Each policy is a JSON file the engine reads; its `description` says what it holds. An override goes in the `.override.json` file of the same name.

- `agents.json`: Model series, so doctor can check the agent files. {src:.harness/policies/agents.json#L3}
- `cli.json`: How the CLI prints. output.encoding: `auto` leaves a terminal to Python, and prints UTF-8 on a pipe whose … {src:.harness/policies/cli.json#L3}
- `computer.json`: The recipe for This computer (1.7.31). Empty here: the harness ships none. {src:.harness/policies/computer.json#L3}
- `connections.json`: The connections an agent may make (1.7.17): one place it reaches with the person's sign-in. {src:.harness/policies/connections.json#L3}
- `gate.json`: The gate only guards writes. It never blocks a read. {src:.harness/policies/gate.json#L3}
- `observe.json`: Call log: one file per session under .harness/runtime/logs/\<surface\>/. {src:.harness/policies/observe.json#L3}
- `target.json`: Target repositories: git repositories outside this folder that a task reads from and promotes into. {src:.harness/policies/target.json#L3}
- `task.json`: Tasks. fetch.max\_files: how many files one `task fetch` may copy. task\_file\_reminder: a prompt that wrote … {src:.harness/policies/task.json#L3}
- `tools.json`: Tools the harness may need that are not in the Python standard library. python.install\_command: the command … {src:.harness/policies/tools.json#L3}
- `user.json`: Who uses this copy of the harness, and in which language it speaks. name: what an agent writes when a file … {src:.harness/policies/user.json#L3}

## Code map: contracts (`.harness/contracts/`)

Contracts are the fixed forms other files must follow: the knowledge base standard, the tool pack protocol and the task templates.

- `kb/README.md`: Knowledge base standard, v1: The form every domain of a knowledge base takes, so that code can check it and find what went stale, and an … {src:.harness/contracts/kb/README.md#L3}
- `kb/map.md`: The repository map and the toolkit, v1: The map lists every object of the target repositories and every use between them, made by script. … {src:.harness/contracts/kb/map.md#L3}
- `kb/templates/architecture.md` {src:.harness/contracts/kb/templates/architecture.md}
- `kb/templates/domain.yaml` {src:.harness/contracts/kb/templates/domain.yaml}
- `kb/templates/environment.md` {src:.harness/contracts/kb/templates/environment.md}
- `kb/templates/exam.md` {src:.harness/contracts/kb/templates/exam.md}
- `kb/templates/objects/index.jsonl` {src:.harness/contracts/kb/templates/objects/index.jsonl}
- `kb/templates/requests.md` {src:.harness/contracts/kb/templates/requests.md}
- `toolpack/README.md`: Tool pack protocol, v1: A \*\*tool pack\*\* teaches the agent one outside tool (a database, a ticket board, a pipeline service). {src:.harness/contracts/toolpack/README.md#L3}
- `toolpack/connections.md`: Connection list, v1: `<knowledge base>/company/tools/connections.json` lists the places the agent may reach for a team. … {src:.harness/contracts/toolpack/connections.md#L3}
- Task templates in `templates/task/en/`: `INTAKE.md` {src:.harness/contracts/templates/task/en/INTAKE.md}, `LOG.md` {src:.harness/contracts/templates/task/en/LOG.md}, `REQ.md` {src:.harness/contracts/templates/task/en/REQ.md}, `TASK.md` {src:.harness/contracts/templates/task/en/TASK.md}, `TODO.md` {src:.harness/contracts/templates/task/en/TODO.md}.
- Task templates in `templates/task/zh/`: `INTAKE.md` {src:.harness/contracts/templates/task/zh/INTAKE.md}, `LOG.md` {src:.harness/contracts/templates/task/zh/LOG.md}, `REQ.md` {src:.harness/contracts/templates/task/zh/REQ.md}, `TASK.md` {src:.harness/contracts/templates/task/zh/TASK.md}, `TODO.md` {src:.harness/contracts/templates/task/zh/TODO.md}.

## Code map: agents (`.github/agents/`)

An agent file sets a Copilot agent's role, tools and models in its front matter; each entry gives the first sentences of its `description` and its tools.

- `mapper.agent.md`: The read-only chunk reader. Tools: `['read', 'search']`. {src:.github/agents/mapper.agent.md#L3-L7}
- `reviewer.agent.md`: The independent checker. The default agent calls it when the user switches checks on (\[review\]=n). Tools: `['read', 'search', 'execute']`. {src:.github/agents/reviewer.agent.md#L3-L7}
- `super.agent.md`: The talker of the board. Tools: `['read', 'search']`. {src:.github/agents/super.agent.md#L3-L7}
- `worker.agent.md`: The step doer of autorun. The default agent calls it once per TODO step, in a task with autorun on. {src:.github/agents/worker.agent.md#L3}

## Code map: harness skills (`.github/skills/harness-*`)

One line per skill: the first sentence of the `description` in its `SKILL.md`.

- `harness-admin`: Extend or debug the harness itself: change hooks, policies, the engine, agents or skills; read reports and … {src:.github/skills/harness-admin/SKILL.md#L3}
- `harness-agent-performance-review`: Agent Performance Review: reason over how the agent of one task spent its time and Credits, find the waste … {src:.github/skills/harness-agent-performance-review/SKILL.md#L3}
- `harness-autorun`: autorun (beta): the default agent only schedules: a worker does one TODO step per call, a step it cannot … {src:.github/skills/harness-autorun/SKILL.md#L3}
- `harness-my-task`: Open a task, go on with a task, switch tasks, raise the tier of a task. {src:.github/skills/harness-my-task/SKILL.md#L3}
- `harness-reinstall`: After the user got a new copy of the harness (an upgrade, a fresh clone), carry what only their machine holds … {src:.github/skills/harness-reinstall/SKILL.md#L3}
- `harness-rookie-new-knowledgebase`: Guide a user who knows nothing about knowledge bases through building one from their own code, step by step … {src:.github/skills/harness-rookie-new-knowledgebase/SKILL.md#L3}
- `harness-rookie-quick-start`: A first lesson for someone new to the harness: one true story from a request to a branch, what the harness … {src:.github/skills/harness-rookie-quick-start/SKILL.md#L3}
- `harness-rookie-wondering`: The deep course: an interactive explanation of how coding agents and this harness work and how they are built. {src:.github/skills/harness-rookie-wondering/SKILL.md#L3}
- `harness-task-archive`: Move closed tasks out of .workspace/sandbox/tasks/ into an archive folder the user picks, usually outside the … {src:.github/skills/harness-task-archive/SKILL.md#L3}
- `harness-task-fork`: Start the next task from a task that is done: RCA to development, development to test (all environments in one … {src:.github/skills/harness-task-fork/SKILL.md#L3}
- `harness-task-report`: Look at the task board, and analyse where the time and the usage of one task went. {src:.github/skills/harness-task-report/SKILL.md#L3}
- `harness-vscode-updates`: Read the newest VS Code release notes (code.visualstudio.com/updates) and judge, against the design of this … {src:.github/skills/harness-vscode-updates/SKILL.md#L3}

## Code map: generic skills (`.github/skills/generic-*`)

One line per skill: the first sentence of the `description` in its `SKILL.md`.

- `generic-build-new-skill`: Build a new skill from the template, then check and test it; or repair the form of an existing skill without … {src:.github/skills/generic-build-new-skill/SKILL.md#L3}
- `generic-capture-knowledge`: Pick out of a task what a future agent would get wrong without it, and draft it as knowledge base entries or … {src:.github/skills/generic-capture-knowledge/SKILL.md#L3}
- `generic-code-standards`: Check the code of a task against the company's code standards and fix what does not comply. {src:.github/skills/generic-code-standards/SKILL.md#L3}
- `generic-evidence-run`: Run a command on an outside system the company listed (a database, a cloud, a job) yourself, save what came … {src:.github/skills/generic-evidence-run/SKILL.md#L3}
- `generic-goal-driven`: The goal-driven flow for long-running work: the central idea, the list of steps, the progress pointer, the … {src:.github/skills/generic-goal-driven/SKILL.md#L3}
- `generic-grill-me`: When anything about a task is unclear, ask the user many questions first, until no blind spot is left and the … {src:.github/skills/generic-grill-me/SKILL.md#L3}
- `generic-impact-analysis`: Find everything a change touches before the plan is written: one search of every target repository and the … {src:.github/skills/generic-impact-analysis/SKILL.md#L3}
- `generic-kb-domains`: Map the target repositories by script (every job, package, procedure, table and who uses what) and propose how … {src:.github/skills/generic-kb-domains/SKILL.md#L3}
- `generic-kb-learn-batch`: Learn the next batch of a domain in its learn task (plan approved): read the code of each object bottom up … {src:.github/skills/generic-kb-learn-batch/SKILL.md#L3}
- `generic-kb-learn-plan`: Plan the learning of one knowledge base domain from zero, in one kb task for the whole domain: check the entry … {src:.github/skills/generic-kb-learn-plan/SKILL.md#L3}
- `generic-kb-learn-synthesize`: After the batches of a domain are learned: write architecture.md (purpose, flows, key data, where to start … {src:.github/skills/generic-kb-learn-synthesize/SKILL.md#L3}
- `generic-kb-migrate`: Move a knowledge base domain built before the harness standard (domain.yaml that lists objects … {src:.github/skills/generic-kb-migrate/SKILL.md#L3}
- `generic-kb-refresh`: Bring the cards of a knowledge base domain back in line with the code after the code changed: read only what … {src:.github/skills/generic-kb-refresh/SKILL.md#L3}
- `generic-kb-toolkit-audit`: Measure how right the repository map is before anything is learned from it: kb audit picks a sample of objects … {src:.github/skills/generic-kb-toolkit-audit/SKILL.md#L3}
- `generic-kb-toolkit-build`: Build the toolkit of an approved TOOLKIT-DESIGN.md: the extractors, toolkit.json and facts.jsonl, tried on the … {src:.github/skills/generic-kb-toolkit-build/SKILL.md#L3}
- `generic-kb-toolkit-design`: Design the toolkit that lets harness kb map read this company's own code: look at what the repositories hold … {src:.github/skills/generic-kb-toolkit-design/SKILL.md#L3}
- `generic-kb-translate`: Translate a knowledge base (or part of it) from Simplified Chinese to English, in the house style, with one … {src:.github/skills/generic-kb-translate/SKILL.md#L3}
- `generic-mapreduce`: Split a job that needs a lot of reading into parts, hand them in parallel to read-only subagents (mappers) … {src:.github/skills/generic-mapreduce/SKILL.md#L3}
- `generic-req-review`: Read the intake a person put in REQ/ (INTAKE.md and the converted business files), write REQ.md from it, check … {src:.github/skills/generic-req-review/SKILL.md#L3}
- `generic-test-guide`: After a development task is written back and the PR is up: open a test task, write TEST-GUIDE.md (what to run … {src:.github/skills/generic-test-guide/SKILL.md#L3}
- `generic-workflow-build`: Build the skills of an approved WORKFLOW-DESIGN.md: unit skills and one orchestration skill, scripts for the … {src:.github/skills/generic-workflow-build/SKILL.md#L3}
- `generic-workflow-design`: Design an agentic workflow from a repeated manual development routine, without building it: learn from the … {src:.github/skills/generic-workflow-design/SKILL.md#L3}

## Code map: text rules (instructions the model reads)

These files are text the model is asked to follow; no code enforces them by itself.

- `AGENTS.md`: This file holds only the rules every agent must follow. {src:AGENTS.md#L3}
- `.github/copilot-instructions.md`: The core rules are in \[AGENTS.md\](../AGENTS.md). This file adds what applies while you run. {src:.github/copilot-instructions.md#L3}
- `.github/instructions/agents.instructions.md`: Rules for writing and changing GitHub Copilot custom agents (.agent.md) Applies to `.github/agents/**/*.agent.md`. {src:.github/instructions/agents.instructions.md#L2}
- `.github/instructions/knowledgebase.instructions.md`: How to read the knowledge base for a task, how to keep it true, and its standard form. Applies to `knowledge-base/**`. {src:.github/instructions/knowledgebase.instructions.md#L2}
- `.github/instructions/skills.instructions.md`: Guidelines for creating high-quality Agent Skills for GitHub Copilot Applies to `.github/skills/**/SKILL.md`. {src:.github/instructions/skills.instructions.md#L2}
- `.github/instructions/workspace.instructions.md`: Rules for reading and writing files in .workspace/ Applies to `.workspace/**`. {src:.github/instructions/workspace.instructions.md#L2}
- `.harness/standards/code-standards.md`: This file ships empty. {src:.harness/standards/code-standards.md#L3}
- `.harness/INDEX.md`: For agents, to find paths. Read it only when you need to find a file. {src:.harness/INDEX.md#L3-L4}
