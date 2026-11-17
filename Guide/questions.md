# Harness Guide: questions the agent must answer

The test for the Harness Guide agent. Each question has the key points a right answer must contain, the file it should cite and the course it should link. Answers are graded against these. This file is **not** a knowledge source of the agent: it stays outside `Guide/Knowledge/`.

- **Grain:** `broad` (the whole design, or how to use it at all) or `detail` (one mechanism or one step).
- **Type:** `use` (how do I…), `how` (how does it work, why this way), `safety` (can it go wrong, can it be bypassed). The person signs off the expected answers of every `safety` question.
- **Files:** `at-a-glance` = Harness at a glance; `task` = Task; `start-task` = Start a task and give it the requirement.

## Pilot (15)

| # | Question | Grain | Type | Should cite |
|---|---|---|---|---|
| P1 | What is this harness, and what does it do? | broad | how | at-a-glance |
| P2 | Tell me how to use the harness. | broad | use | at-a-glance, start-task |
| P3 | What is a task, and how is it different from a chat session? | broad | how | task |
| P4 | Is it safe to let the agent work on our code? What stops it from going wrong? | broad | safety | at-a-glance |
| P5 | What does a person still have to do, and what does the agent do alone? | broad | how | at-a-glance |
| P6 | How do I start a task and give the agent my requirement documents? | detail | use | start-task |
| P7 | How does a task move from one stage to the next? Is that controlled by a skill or by code? | detail | how | at-a-glance, task |
| P8 | How are dangerous commands blocked? | detail | safety | at-a-glance |
| P9 | Can the agent approve its own plan? | detail | safety | task |
| P10 | What happens if the requirement changes after I approved the plan? | detail | how | task |
| P11 | I closed VS Code yesterday. Can a new chat continue the same task, and how? | detail | use | task |
| P12 | Where is a task's record kept, and what is in it? | detail | how | task |
| P13 | Can the agent write files outside its task folder? | detail | safety | task |
| P14 | What does "waiting for you" on the board mean, and what should I do? | detail | use | start-task, task |
| P15 | How is the knowledge base built? | detail | how | none in the pilot: the right answer says the Guide does not cover it yet, and does not make one up |

## Expected answers

Written in step 3, with the evidence for each key point, then fact-checked.

Code locations are in the harness at tag `1.7.41`. "Cite" names the Guide file and section the answer should point to; "Course" the link it should give.

### P1. What is this harness, and what does it do?

- It wraps the GitHub Copilot agent in VS Code: a hook checks every tool call before it runs (`.github/hooks/harness.json`; `.harness/engine/hook.py` L1-L15).
- Work is done in tasks: a folder under `.workspace/sandbox/tasks/<name>/` with requirement, plan, results and a state file (`.harness/engine/core/tasks.py` L1-L36); opening one is asked of the agent by text, not forced (`AGENTS.md` L46-L47).
- A person approves the plan and every write-back to a code repository with a typed code (`.harness/engine/core/approval.py` L1-L8, L17-L58); the requirement is confirmed with a code too, but its confirmation is a text line in `REQ.md` the agent can write (`modules/task/taskreview.py` L88-L110).
- It carries no business knowledge: the team plugs in knowledge base, skills and target repositories (`AGENTS.md` L7-L15). The harness has no remote server: everything of it, the board's local web server included, runs on the person's computer; the model runs in Copilot's service (`docs/00-overview.md` L159; `modules/task/boardserve.py` L8-L9).
- It is a guardrail, not a sandbox: the gate reads command text (`.harness/engine/modules/gate/terminal.py` L1-L5).

Cite: 00 Harness at a glance, "Harness: what it is" and "Harness: the parts and how a piece of work flows through them". Course: The book 0.1 What is Harness Engineering? (https://smarshu.com/book/read/0-1-the-gap-and-the-map.html).

### P2. Tell me how to use the harness.

- Start the board (`Start Harness` or `harness task board`) and use the browser it pairs (`.harness/engine/modules/task/boardserve.py` L1-L17; `core/messages.en.json` L1080-L1082).
- Say in one sentence what to do and in which repository, in the chat or with **New task**; the agent asks, then opens a task (`.harness/engine/modules/task/chatnew.py` L1-L8; `.github/skills/harness-my-task/SKILL.md` L35-L65).
- Give documents on the Intake tab and confirm the requirement with **Confirm requirement** and its code (`.harness/engine/modules/task/intake.py` L1-L10; `modules/task/task.py` L568-L610).
- Approve the plan and the write-back with a code when the board says the task waits for you (`modules/task/task.py` L426-L473, L941-L980; `modules/task/tasklife.py` L276-L336).
- Commit the new branch, or press **Accept and close** for a task that changes no repository (`modules/task/accept.py` L1-L11).

Cite: 00 Harness at a glance, "Harness: how a person uses it day to day"; 21 Start a task and give it the requirement, "Start a task: steps". Course: The book 5.1 Manage tasks, not chats (https://smarshu.com/book/read/5-1-tasks.html).

### P3. What is a task, and how is it different from a chat session?

- A task is a folder holding one piece of work and its state `.task/task.json`, written only by harness code (`core/tasks.py` L1-L36; `.harness/policies/gate.json` L24-L33).
- A session is one Copilot chat; it lives as long as the chat; Copilot compacts it near 80% of its context (`core/copilot_events.py` L1; `.harness/policies/task.json` L3).
- They point at each other: the session's `active_task`, the task's `session_id`; a session holds at most one task, and opening another leaves the first open (`modules/task/task.py` L138-L216).
- Any later session can pick the task up from its files; a subagent inherits its parent's task, a subagent or admin session cannot open one (`core/state.py` L252-L303; `modules/task/tasklife.py` L126-L135).

Cite: 11 Task, "Task: what it is" and "Task: how it differs from a chat session". Course: The book 5.1 Manage tasks, not chats.

### P4. Is it safe to let the agent work on our code? What stops it from going wrong?

- The harness itself writes a target repository only through `task promote`, after the person approved the same plan digest (branch, base commits, sha256 of every file), to a new uncommitted branch; a registered knowledge base gets one commit on its base branch (`modules/task/task.py` L898-L901; `modules/task/promote_target.py` L1-L14, L114-L118). A git command the person approves with `approve-command` can also write there (`modules/gate/handler.py` L132-L141). The agent's edit tools, and terminal commands that name a path there in full or after a `cd` in the same line, are refused; scripts and run-time paths are not seen (`modules/gate/handler.py` L47-L52; `modules/gate/policy.py` L149-L156; `modules/gate/terminal.py` L1-L5, L65-L117).
- The gate checks every call: guardrail files (except in a chat the person switched to admin mode, where only `.harness/runtime/**`, `admin_locked_paths` and the integrity-list folder `~/.copilot-harness` stay closed, and ending admin mode accepts the files as they are), `.git`, a deny list of dangerous commands, person-only commands; git writes need the person's code when target repositories are set up (`modules/gate/handler.py` L38-L146; `.harness/policies/gate.json` L87-L143; `core/guardrails.py` L21-L61; `integrity.py` L1-L5).
- Approvals need a person and a typed code bound to a sha256; the agent is refused the commands (`core/approval.py` L17-L58; `gate.json` L130-L136).
- Once the person has accepted them, the engine, policies, hook files, tool packs and `registry.json` are checked against that list before every call (not in admin mode), and a failing hook refuses commands and writes (`.harness/engine/hook.py` L11-L15, L312-L323, L342-L360; `integrity.py` L18-L26).
- Limits must be stated: `task allow --conn`/`--links` is not refused by the gate (its pattern lists only the retired `allow --env`), and an opened connection passes writes with no further approval (`gate.json` L135; `modules/task/tasklife.py` L541-L546; `modules/gate/handler.py` L266-L287); the terminal is not confined to the task folder; the folder binds only a chat holding an open task, and only the listed VS Code edit tools; the requirement's confirmation is a text line; after plan approval `task`-marked outside calls and `task allow` connections pass; it is not a sandbox (`modules/gate/handler.py` L64-L118, L266-L287; `modules/task/taskreview.py` L88-L110; `modules/gate/scriptcheck.py` L1-L11).

Cite: 00 Harness at a glance, "Harness: the main safety guarantees and their exact scope" and "Harness: known limits". Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can (https://smarshu.com/writing/basic-06-prompt-cannot-stop).

### P5. What does a person still have to do, and what does the agent do alone?

- The person: says what they want, confirms the requirement, approves the plan and the write-back, approves git writes and held outside calls, gives more checks or waives them, commits, accepts or closes a task that changes no repository (`gate.json` L130-L143); the board closes a written-back task without waiting for the commit (`modules/task/accept.py` L186-L218).
- The agent alone: asks, opens the task, writes `REQ.md`, `PLAN.md` and code in the task folder, fetches files, runs the checks, the dry run, and the write-back once approved (`core/tasks.py` L1-L8; `modules/task/task.py` L868-L914).
- Code enforces the gates between them; text (skills, instructions, hook lines) only asks the agent (`AGENTS.md` L42-L64; `modules/task/handler.py` L88-L121).
- Closing is the person's: the agent is told never to close a task and the gate refuses `task close` on its command line; the command itself has no person check, so a script is not stopped (`gate.json` L137-L143; `modules/task/commands.py` L123-L133).

Cite: 00 Harness at a glance, "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person". Course: The book 5.3 Two gates: where a person approves (https://smarshu.com/book/read/5-3-two-approvals.html).

### P6. How do I start a task and give the agent my requirement documents?

- Say what you want in the chat or with **New task**; the agent asks with numbered options, then runs `harness task new <name> --kind <kind>`, which makes the folder with the tier's files (`SKILL.md` L35-L65; `modules/task/tasklife.py` L163-L174, L39-L45).
- Drop the documents on the task's **Intake** tab (paired browser): the original goes to `REQ/originals/`, the text to `REQ/` as Markdown and CSV, with a report of what was left out; no AI (`modules/task/intake.py` L1-L10; `modules/task/boardserve.py` L2007-L2010).
- Trim, **Create INTAKE.md**, send the **Tell the agent** message; terminal equivalents `harness task intake convert/paste/init` (`core/messages.en.json` L1310-L1311, L1351-L1352; `modules/task/commands.py` L317-L335).
- Read `REQ.md` on **Requirement** and press **Confirm requirement**, typing the code (`modules/task/task.py` L568-L610).

Cite: 21 Start a task and give it the requirement, "Start a task: steps". Course: The book 5.2 The agent writes the requirement, the person confirms it (https://smarshu.com/book/read/5-2-requirements.html).

### P7. How does a task move from one stage to the next? Is that controlled by a skill or by code?

- Both: the skill `harness-my-task` and the hook's next-step text tell the agent the order; code holds the gates (`SKILL.md` L73-L97; `core/messages.en.json` L14-L15).
- The stage is derived each time from files and state, not stored or set by the agent (`modules/task/taskstages.py` L1-L15, L56-L67).
- Gates in code: plan refused while the "User confirmed" line of `REQ.md` is not filled in (a text line the agent can write; no `REQ.md` or no line is not checked) (`modules/task/task.py` L441-L449, L549-L565; `modules/task/taskreview.py` L88-L110); for the chat that holds the task, `DEV/` closed to edit tools until the plan is approved, a chat with no task is not bound, and the write-back approval still covers what reaches a repository (`modules/gate/handler.py` L64-L84); dry run needs an approved plan and enough review passes, promote the approval of the same digest (`modules/task/task.py` L868-L901; `modules/task/taskreview.py` L563-L568).
- A person holds the keys at each gate; the agent cannot close (`gate.json` L130-L143).

Cite: 11 Task, "Task: how it moves from one stage to the next"; 00 Harness at a glance, "Harness: common questions". Course: The book 5.3 Two gates: where a person approves.

### P8. How are dangerous commands blocked?

- The gate (a PreToolUse hook module) reads every terminal command before it runs; deny beats ask beats allow (`modules/gate/handler.py` L96-L146; `core/events.py` L77-L93).
- Rules in `.harness/policies/gate.json`: writes to guardrail files refused (L34-L86); a deny list: `rm -rf` of root/home/current folder, download piped to a shell, `mkfs`/`dd`, `sudo`/`runas`, recursive `chmod`, `docker rm`, `kubectl delete`, `terraform apply/destroy` (L87-L129); person-only harness commands refused (L130-L143); an ask list for deletes, git history rewrites, network, installs (L145-L181).
- Git writes need the person's `approve-command` code once; `push`, `clean`, `filter-branch`, `filter-repo`, `update-ref`, `prune`, `reset --hard`, `branch -D`, force never approved, when target repositories are set up (`modules/gate/gitcmd.py` L22-L37, L272-L282; `modules/gate/handler.py` L761-L770).
- Commands inside `bash -c`/`pwsh -Command` and scripts writing guardrail files are checked too (`modules/gate/handler.py` L119-L126; `modules/gate/scriptcheck.py` L1-L11).
- Limits: it reads text, not a sandbox; the ask list is only Copilot's confirmation, absent under Allow all (`modules/gate/terminal.py` L1-L5; `docs/02-features.md` L50; `modules/task/chatnew.py` L25-L26).

Cite: 00 Harness at a glance, "Harness: how dangerous commands are blocked". Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can.

### P9. Can the agent approve its own plan?

- No, by the ways the harness gives it: the gate refuses on the agent's command line `task confirm-req`, `approve-plan`, `approve-promote`, `recover`, `review set/extend/waive/dismiss`, `test runner`, `pause`, `resume`, `offwork`, `onwork`, `autorun on`, `task board` (not `--once`), `approve-command`, `approve-action`, `admin on`, `doctor --accept`, read as the shell reads them (`gate.json` L130-L136; `modules/gate/harnesscmd.py` L1-L8). It does not refuse `task allow --conn`/`--links` (pattern has only the retired `allow --env`); only that command's terminal check, with no code, stands in the way (`modules/task/tasklife.py` L541-L546; `modules/task/commands.py` L357-L365).
- The command needs a person at their own terminal and a typed code; the board's Terminal window gives no keyboard input for a code (`core/approval.py` L28-L58; `docs/04-reference.md` L9).
- On the board, approvals go through the paired browser's buttons with the typed code; the agent cannot start the board server or call its port (`modules/task/boardserve.py` L11-L16, L812-L823; `modules/gate/handler.py` L559-L564).
- The code is six capitals of a sha256 of `PLAN.md`; the file is re-checked under the lock; a changed plan is not approved (`core/approval.py` L17-L25; `modules/task/task.py` L458-L469; `core/tasks.py` L154-L159).
- Exceptions: the requirement's confirmation line is text the agent can write; the approval records are in `.task/`, which a script the agent runs is not checked for (`modules/task/taskreview.py` L88-L110; `modules/gate/scriptcheck.py` L1-L11).

Cite: 11 Task, "Task: who approves, and why the agent cannot approve its own plan". Course: The book 5.3 Two gates: where a person approves.

### P10. What happens if the requirement changes after I approved the plan?

- The approval keeps a digest of What to do, What not to do and Done when; a change there makes the plan count as not approved (`core/tasks.py` L112-L159).
- For the chat that holds the task, the gate refuses edit-tool writes to `DEV/` and tells the agent to stop and ask for a new confirmation and approval (`modules/gate/handler.py` L80-L84; `core/messages.en.json` L397).
- The person confirms the requirement and approves the plan again with one code (`--with-req`, or **Approve plan**); dry run and write-back need the plan approved as it is now; the work in `DEV/` stays (`modules/task/task.py` L442-L467, L872, L950).
- The agent is told by text to change `REQ.md` first; a change only said in the chat changes nothing in code (`core/messages.en.json` L108).
- In an open task the requirement is just changed in `REQ.md` (`core/messages.en.json` L108). After a write-back, the same goal is a new round (`task open`) (`modules/task/task.py` L172-L181, L232-L249). Only when a closed task of a kind without write-back is opened again is the agent told that a changed requirement is a forked task (`modules/task/tasklife.py` L189-L192; `core/messages.en.json` L17).

Cite: 11 Task, "Task: what happens when the requirement changes after the plan was approved". Course: The book 5.2 The agent writes the requirement, the person confirms it.

### P11. I closed VS Code yesterday. Can a new chat continue the same task, and how?

- Yes: the task lives in its folder, not in the chat (`core/tasks.py` L1-L36).
- In a new chat say "go on with" and the task's name; a session without a task is told the open tasks, and the agent runs `harness task open <name>` (`modules/task/handler.py` L124-L137; `core/messages.en.json` L107; `SKILL.md` L58-L65).
- `task open` makes the new session the holder (`sessions[]`, `session_id`, `active_task`) and tells it to read `TASK.md` first (`modules/task/task.py` L172-L207; `modules/task/tasklife.py` L155-L160).
- Or press **Go on in a new chat** on the task page; what was said only in the old chat does not come along (`core/messages.en.json` L2139-L2140).

Cite: 11 Task, "Task: how a new chat continues the same task". Course: The book 5.1 Manage tasks, not chats.

### P12. Where is a task's record kept, and what is in it?

- In `.workspace/sandbox/tasks/<name>/` on the person's computer, ignored by git (`core/tasks.py` L19-L36; `.gitignore` L27-L30).
- Files by tier: `TASK.md`, `REQ.md`, `REQ/`, `REF/`, `LOG.md`, `TODO.md`, `DEV/`, `TEST/`, plus `PLAN.md` and command-owned `.task/`, `REVIEW/`, `SNAPSHOT/`, diffs (`modules/task/tasklife.py` L39-L45; `gate.json` L24-L33).
- `.task/task.json`: status, kind, tier, round, session_id and sessions[] (last 100), req and plan digests, promote state, waiting, review, events[] (last 200), rounds[], chat (`modules/task/task.py` L36-L39, L163-L188, L467).
- At close: the chat's rounds in `.task/transcript.jsonl` and a report in `.workspace/reports/tasks/<name>/report.md` (`modules/task/task.py` L384-L396; `modules/task/chatrounds.py` L1-L10).

Cite: 11 Task, "Task: where its record is kept, and what is in it". Course: The book 5.1 Manage tasks, not chats.

### P13. Can the agent write files outside its task folder?

- With its VS Code edit tools, not while its chat holds an open task: writes outside the folder are refused; `REQ/`, `REF/`, `INBOX/` always; `DEV/` until the plan is approved (`modules/gate/handler.py` L64-L88). A tool the harness does not list as an edit tool (an unlisted file-writing MCP server) gets no path check (`adapters/tool_kinds.json`; `modules/gate/handler.py` L724-L734).
- For every chat, edit tools are refused on command-owned files, `.git` and target repositories, and on guardrail files except in an admin chat, where only `.harness/runtime/**`, `admin_locked_paths` and the integrity-list folder stay closed (`modules/gate/handler.py` L38-L61; `core/guardrails.py` L21-L61).
- Its terminal commands are not confined to the folder: only writes that name a guardrail, command-owned, `.git` or target path in full or after a `cd` in the same line, and scripts found (best effort) to write guardrail files, are refused; the terminal's real working folder is not used (`modules/gate/handler.py` L96-L118; `modules/gate/terminal.py` L65-L117; `modules/gate/scriptcheck.py` L1-L11).
- A session holding no task, or a closed one, is not confined by the edit-tool check (`modules/gate/handler.py` L67-L72).

Cite: 11 Task, "Task: what the agent may write". Course: The book 5.1 Manage tasks, not chats.

### P14. What does "waiting for you" on the board mean, and what should I do?

- The task's next move is the person's and its agent is not in the middle of a turn: the board's state "waiting" (`modules/task/tasklife.py` L840-L853; `modules/task/web/board.js` L329).
- The reason is told from facts in order: a question, a failed write-back, the plan, the write-back, checks used up, to accept, the requirement (full tier), a held outside call, a handed-over run, commit, an approval not yet told to the agent, autorun stopped, the agent stopped, a cancelled turn (`modules/task/tasklife.py` L276-L336).
- "waits for you" alone: the Stop hook marked that the agent ended its turn; reply, and the next message clears it (`modules/task/handler.py` L398-L411, L210-L211).
- What to do: the task page puts the reason first as a card with the button (Confirm requirement, Approve plan, Approve promote, Accept and close, Send to agent...).

Cite: 21 Start a task and give it the requirement, "Start a task: what "waiting for you" means and what to do"; 11 Task, "Task: what "waiting for you" means". Course: none needed; if one, The book 5.1 Manage tasks, not chats.

### P15. How is the knowledge base built?

- The right answer says the Harness Guide does not cover how the knowledge base is built yet, and makes nothing up. It may say that the Guide's overview names the knowledge base only as something the team brings and the agent is told to read.

Cite: none (00 Harness at a glance, "Harness: related files", says it is not covered). Course: none.

