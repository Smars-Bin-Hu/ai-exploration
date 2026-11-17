# Harness Guide: questions the agent must answer

The test for the Harness Guide agent. Each question has the key points a right answer must contain, the Guide section it should cite and the course or tutorial it should name. Answers are graded against these. This file is **not** a knowledge source of the agent: it stays outside `AI Exploration/2 Ask the Harness Guide/Knowledge/`.

The Guide helps people understand the harness; it is not a tutorial. Its questions come in four layers, from shallow to deep, plus two kinds of test:

- **Layer 1 · the harness:** what it is, what problem it solves.
- **Layer 2 · features:** its common features (task, board, approvals).
- **Layer 3 · design:** how it is designed and built, and where in the source.
- **Layer 4 · ideas:** the harness engineering knowledge behind it; the answer links the course on smarshu.com that teaches it.
- **How-to:** "how do I…". The right answer is short (a few sentences from the Guide), then names the harness tutorial that teaches it step by step, in `AI Exploration/3 Courses/Harness tutorials/`. The tutorial names are the working names of GOAL.md (not confirmed): when they change, change them here and in `AGENT.md`.
- **Not covered:** the right answer says "The Harness Guide does not cover this yet." and makes nothing up.

How to read each entry:

- **Grain:** `broad` (the whole design) or `detail` (one mechanism).
- **Should cite:** the Guide file and section, as written in the page. The Guide's knowledge is two files: `00 Harness at a glance` (`pages/00-at-a-glance.md`) and `11 Task` (`pages/11-task.md`). Every question here is answerable from these two. `21 Start a task and give it the requirement` is not knowledge any more: an answer that cites it, or sends the reader to it, is wrong.
- **Course:** the link written in the front matter of the cited page (the PDF lists it under "courses to learn more"), exactly as written. `AGENT.md` tells the agent to link the course of the file its answer is mostly built on, so where should-cite names both files, the course of either file is right; each such entry lists both. A how-to answer names the tutorial instead.
- **Key points:** each with its code location in the harness at tag `1.7.45`, checked against the 1.7.45 copy. The code locations are for the grader: a right answer gives the Guide's own links for what it says; it need not repeat every location listed here.
- **Wrong if:** what makes an otherwise good answer wrong.
- **Beyond the pages:** where the code says more than 00 and 11, the key notes it for the grader under this label. An answer that says only what the pages say is not wrong for leaving it out.
- Every answer must come from the Guide only. An answer that uses the asker's own work (their repository, mail, chats, files) to make an example is wrong, whatever else it gets right.
- The person signs off the expected answers of the questions about guarantees: Q3, Q8, Q9, Q10.

The 15 questions of the first pilot (P1–P15) and their expected answers are in git (commit 74cab51); they were written for the old goal and are not used any more.

## Pilot (15)

| # | Question | Layer | Grain | Should cite |
|---|---|---|---|---|
| Q1 | What is this harness, and what problem does it solve? | 1 · harness | broad | 00 |
| Q2 | Where does the harness run, and what does our team have to bring to it? | 1 · harness | broad | 00 |
| Q3 | Is the harness a sandbox? What does it protect against, and what not? | 1 · harness | broad | 00 |
| Q4 | What is a task, and how is it different from a chat session? | 2 · features | broad | 11 |
| Q5 | What kinds of tasks are there, and how does each one end? | 2 · features | detail | 11, 00 |
| Q6 | What does the board show, and what does "waiting for you" mean? | 2 · features | detail | 11, 00 |
| Q7 | How does a task move from one stage to the next? Is that controlled by a skill or by code, and where in the code? | 3 · design | detail | 11, 00 |
| Q8 | How does the gate block dangerous commands, and where are its rules? | 3 · design | detail | 00 |
| Q9 | How does the approval code work, and why can't the agent approve its own plan? | 3 · design | detail | 11 |
| Q10 | Why isn't a rule in the prompt or in `AGENTS.md` enough to keep the agent safe? | 4 · ideas | broad | 00 |
| Q11 | Why does the harness keep the work in tasks instead of in the chat? | 4 · ideas | broad | 11 |
| Q12 | What is the idea behind the approval gates, and where does a person hold the keys? | 4 · ideas | detail | 00, 11 |
| Q13 | I maintain a data pipeline repository. How do I start a task and give the agent my requirement documents? | how-to | detail | 00 |
| Q14 | The agent says my command was refused. How do I get it run? | how-to | detail | 00 |
| Q15 | How does autorun work? Can a task run on its own overnight? | not covered | detail | none |

## Expected answers

### Q1. What is this harness, and what problem does it solve?

Layer 1 · broad.

- A set of files and Python code that wraps the GitHub Copilot agent in VS Code so that a team can let it work on real code under rules; the Guide describes version 1.7.45 (`docs/00-overview.md` L159).
- The problem: rules that are only written for the model ask it, and it can ignore them; the harness makes the rules that must hold into code, and leaves what cannot be taken back to a person (`docs/02-features.md` L3; `docs/00-overview.md` L163-L164; `.harness/engine/modules/task/handler.py` L88-L121).
- It does three things. A hook checks every tool call of the agent before it runs (`.github/hooks/harness.json` L1-L113; `.harness/engine/hook.py` L1-L15). Work is done in tasks, folders with the requirement, the plan, the results and a state file; opening one is asked of the agent by text, not forced (`.harness/engine/core/tasks.py` L1-L8; `AGENTS.md` L46-L47). A person approves the plan and every write-back to a code repository by typing a code, and confirms the requirement the same way, though that confirmation is a text line the agent can write (`.harness/engine/core/approval.py` L1-L8; `.harness/engine/modules/task/taskreview.py` L88-L110).
- It is not a sandbox: it guards against an agent's mistakes, not against an agent set on getting round it (`.harness/engine/modules/gate/terminal.py` L1-L5).

Should cite: 00 Harness at a glance, "Harness: what it is", "Harness: the parts and how a piece of work flows through them" and, for the problem it solves, "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person". Course: The book · 0.1 What is Harness Engineering? (https://smarshu.com/book/read/0-1-the-gap-and-the-map.html).

Wrong if: it calls the harness a sandbox or a security boundary; it gives the courses of 11 Task instead of those of 00 (the first pilot's P1 did).

### Q2. Where does the harness run, and what does our team have to bring to it?

Layer 1 · broad.

- The harness has no remote server: everything of it, the board's local web server included, runs on the person's computer; the board answers on 127.0.0.1 only (`docs/00-overview.md` L159; `.harness/engine/modules/task/boardserve.py` L1-L17).
- The model runs in GitHub Copilot's service, and the agent may call the outside systems the company connects; such a call is judged by what it does, by the company's rules for that system (`.harness/engine/core/systems.py` L37-L38; `.harness/engine/modules/gate/handler.py` L192-L293).
- The harness carries no business knowledge. The team plugs in its own knowledge base, skills and target repositories, the company code repositories the agent may change, set in `target.override.json` (`AGENTS.md` L13-L14; `.harness/engine/core/targets.py` L3). A company may also bring tool packs, which let the agent call an outside system under the gate's rules (`.harness/toolpacks/README.md` L1-L5).
- The person brings the decisions: confirming the requirement, approving the plan and the write-back (`.harness/policies/gate.json` L131-L137), committing the branch (`.harness/engine/modules/task/promote_target.py` L6).

Should cite: 00 Harness at a glance, "Harness: what it is", "Harness: the parts and how a piece of work flows through them" (the board on 127.0.0.1), "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person" (row "Outside systems"), "Harness: terms" and "Harness: common questions" ("What does a person still have to do?"). Course: The book · 0.1 What is Harness Engineering?

Wrong if: it says the harness sends code or data to a server of its own; it makes up install or setup steps.

### Q3. Is the harness a sandbox? What does it protect against, and what not?

Layer 1 · broad · guarantees.

- No. The agent runs as the person's own operating system user (`docs/02-features.md` L56), and the gate reads the text of a command, so the harness guards against an agent's mistakes, not against an agent set on getting round it (`.harness/engine/modules/gate/terminal.py` L1-L5).
- What it protects most: the harness writes a target repository only through `task promote`, in the version the person approved (the same plan digest: branch, base commit of each repository, sha256 of every file), to a new branch, never committed; a registered knowledge base gets one commit on its base branch (`.harness/engine/modules/task/task.py` L941-L944; `.harness/engine/modules/task/promote_target.py` L1-L14, L112-L116). A git command the person approves with `approve-command` can also write there (`.harness/engine/modules/gate/handler.py` L132-L141).
- Also: approvals need a person and a typed code (`.harness/policies/gate.json` L131-L137; `.harness/engine/core/approval.py` L17-L58); guardrail files are refused (`.harness/policies/gate.json` L4-L19) and, once the person has accepted them (the first start of the board), checked against that list before every call, except in an admin chat; before the first accept there is no list and no check (`.harness/engine/integrity.py` L18-L26, L171-L183; `.harness/engine/hook.py` L312-L323); when the engine cannot decide, commands and writes are refused and reads stay allowed (`.harness/engine/hook.py` L11-L15).
- What not, at least three of the known limits: the terminal is not confined to the task folder (`.harness/engine/modules/gate/handler.py` L96-L118); a script or a path made at run time is not seen (`.harness/engine/modules/gate/scriptcheck.py` L1-L11); a tool not recorded in `tool_kinds.json` gets no write check (`.harness/engine/adapters/tool_kinds.json` L1-L10; `.harness/engine/modules/gate/handler.py` L719-L734); the ask rules are only Copilot's confirmation, absent under Allow all, which is how **New task** makes a chat (`docs/02-features.md` L50; `.harness/engine/modules/task/chatnew.py` L25-L26); `task allow --conn` is not refused by the gate (`.harness/policies/gate.json` L136; `.harness/engine/modules/task/tasklife.py` L541-L546); admin mode opens the guardrails (`.harness/engine/core/guardrails.py` L21-L23).

Should cite: 00 Harness at a glance, "Harness: what it is", "Harness: the main safety guarantees and their exact scope" and "Harness: known limits". Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can (https://smarshu.com/writing/basic-06-prompt-cannot-stop).

Wrong if: it reassures beyond the Guide ("the agent cannot do anything unsafe"); it drops the limits.

### Q4. What is a task, and how is it different from a chat session?

Layer 2 · broad.

- A task is one piece of work kept as a folder, `.workspace/sandbox/tasks/<task name>/`, with `TASK.md`, `REQ.md`, `PLAN.md`, the results and the state file `.task/task.json`, written by harness code; the edit tools and a terminal command that names it are refused on it (`.harness/engine/core/tasks.py` L1-L37; `.harness/policies/gate.json` L24-L34).
- A session is one Copilot chat and lives as long as the chat; Copilot keeps it under `~/.copilot/session-state/<id>/` and compacts it at about 80% of its context (`.harness/engine/core/copilot_events.py` L1; `.harness/policies/task.json` L3).
- They point at each other: the session's `active_task`, the task's `session_id`. A session holds at most one task; opening another leaves the first open (`.harness/engine/modules/task/task.py` L140-L218).
- Any later session can pick the task up from its files; a subagent inherits its parent's task; a subagent or an admin session cannot open one (`.harness/engine/core/state.py` L252-L303; `.harness/engine/modules/task/tasklife.py` L126-L135).

Should cite: 11 Task, "Task: what it is" and "Task: how it differs from a chat session". Course: The book · 5.1 Manage tasks, not chats (https://smarshu.com/book/read/5-1-tasks.html).

### Q5. What kinds of tasks are there, and how does each one end?

Layer 2 · detail.

- Kinds: `qa`, `rca`, `design`, `dev`, `test`, `kb`, `other`; the kind says what "done" means. Tiers `light`, `medium`, `full` say which files the folder has; the default tier of `qa` is light, of `rca`, `design` and `other` medium, of `dev`, `test` and `kb` full (`.harness/engine/core/tasks.py` L19-L23; `.harness/engine/modules/task/tasklife.py` L39-L45). Beyond the pages: `task new --tier` sets another tier, and the skill asks for `full` when a repository must change (`.harness/engine/modules/task/tasklife.py` L163-L165; `.github/skills/harness-my-task/SKILL.md` L54).
- A task that changes a repository (`dev`, `kb`): requirement confirmed, plan approved, code in `DEV/`, write-back approved, files written to a new branch of each target repository without a commit (a registered knowledge base: one commit on its base branch). The board closes the task once the agent has stopped and nothing else waits, without waiting for the commit; the person commits the branch (`.harness/engine/modules/task/task.py` L984-L1024; `.harness/engine/modules/task/promote_target.py` L1-L14; `.harness/engine/modules/task/accept.py` L184-L218).
- A task whose result stays in the folder (analysis, design, test, question): the result is written there (an analysis or design at the root, test results in `TEST/`, a Q&A answer in `TASK.md`), the agent delivers it with a summary (`task deliver`), and the person presses **Accept and close** (`.harness/engine/modules/task/accept.py` L1-L11, L45-L68, L167-L181).
- Closing is the person's: the gate refuses `task close` on the agent's command line, though the command itself has no person check (`.harness/policies/gate.json` L138-L144; `.harness/engine/modules/task/commands.py` L123-L133).

Should cite: 11 Task, "Task: what it is" and "Task: how it works"; or 00 Harness at a glance, "Harness: the parts and how a piece of work flows through them". Course: The book · 5.1 Manage tasks, not chats (https://smarshu.com/book/read/5-1-tasks.html) for an answer built mainly on 11; The book · 0.1 What is Harness Engineering? (https://smarshu.com/book/read/0-1-the-gap-and-the-map.html) or Basic 06 · A prompt cannot stop a dangerous action: a harness can (https://smarshu.com/writing/basic-06-prompt-cannot-stop) for one built mainly on 00.

Wrong if: it says the write-back commits to the code repository (only a registered knowledge base gets a commit).

### Q6. What does the board show, and what does "waiting for you" mean?

Layer 2 · detail.

- The board is a page served by `harness task board` on this computer only (127.0.0.1): every task, what it waits for, and the buttons for approvals, which work only from the browser paired with the board (`.harness/engine/modules/task/boardserve.py` L1-L17).
- It picks one state per task from facts, first that holds: closed, paused, working, waiting, then quiet (held by a session, nothing to do) or no session (`.harness/engine/modules/task/tasklife.py` L840-L853). Working is read from the age of the session's hook log, five minutes by default (`.harness/engine/modules/task/tasklife.py` L774-L803).
- "Waiting for you": the next move is the person's and the agent is not in the middle of a turn. The reason is the first that holds, in order of how much it blocks: a question; a write-back stopped halfway (**Recover the repository**); the plan; the write-back; checks used up; to accept; the requirement (`full` tier); a held outside call; a run or test handed over; the commit; an approval the agent has not been told of; autorun stopped; the agent stopped; a cancelled turn (`.harness/engine/modules/task/tasklife.py` L276-L336).
- "The agent stopped" is the Stop hook's mark when the agent ends its turn; the person's next message clears it (`.harness/engine/modules/task/handler.py` L398-L411, L210-L211). The task page shows the reason at the top with a button for the answer.

Should cite: 11 Task, "Task: what "waiting for you" means"; 00 Harness at a glance, "Harness: the parts and how a piece of work flows through them". Course: The book · 5.1 Manage tasks, not chats (answer built mainly on 11); The book · 0.1 or Basic 06 (answer built mainly on 00).

Wrong if: it cites or recommends the file 21 Start a task and give it the requirement (it is not in the knowledge; 11 now names the tutorials instead).

### Q7. How does a task move from one stage to the next? Is that controlled by a skill or by code, and where in the code?

Layer 3 · detail.

- Both: the hook's next-step line and the skill `harness-my-task` tell the agent the order of work; code holds the gates; a person holds the keys (`.harness/engine/core/messages.en.json` L14-L15; `.github/skills/harness-my-task/SKILL.md` L73-L97).
- The stage is not stored or set by the agent: it is worked out each time from the files and the state, so a task whose requirement changed falls back by itself. For `dev` and `kb`: requirement, plan, developing, write-back, done (`.harness/engine/modules/task/taskstages.py` L1-L15, L56-L67). Beyond the pages: when `DEV/` holds only `DEV/_manual/`, the steps are requirement, plan, developing, apply, done (`.harness/engine/modules/task/taskstages.py` L10-L12, L63-L64).
- Requirement to plan: `task approve-plan` refuses while `REQ.md` is the bare template, its "User confirmed" line is not filled in, or what it asks changed; `--with-req` confirms and approves with one code. The line is text the agent can write, and a missing `REQ.md` or line is not checked (`.harness/engine/modules/task/task.py` L428-L469, L551-L567; `.harness/engine/modules/task/taskreview.py` L88-L110).
- Plan to developing: for the chat that holds the task, the gate refuses the edit tools any write under `DEV/` until the plan is approved as it is now, for the requirement as it is now; a chat with no task is not bound (`.harness/engine/modules/gate/handler.py` L80-L84; `.harness/engine/core/tasks.py` L152-L164).
- Developing to write-back: `task promote --dry-run` needs an approved plan and, when checks are on, enough passes; `task promote` needs the person's approval of the same digest (`.harness/engine/modules/task/task.py` L911-L928, L941-L944; `.harness/engine/modules/task/taskreview.py` L563-L568).
- Where: `.harness/engine/modules/task/task.py` (approvals, promote), `taskstages.py` (stages), `.harness/engine/modules/gate/handler.py` (write scope), as the code map of 11 Task lists them.

Should cite: 11 Task, "Task: how it moves from one stage to the next" (and its "related files" code map); 00 Harness at a glance, "Harness: common questions". Course: The book · 5.3 Two gates: where a person approves (https://smarshu.com/book/read/5-3-two-approvals.html) for an answer built mainly on 11; The book · 0.1 or Basic 06 for one built mainly on 00.

Wrong if: it says only code, or only the skill; it drops that the requirement's confirmation is a text line.

### Q8. How does the gate block dangerous commands, and where are its rules?

Layer 3 · detail · guarantees.

- The gate is a hook module that reads every terminal command before it runs and answers allow, ask or deny; a deny from any module wins over an ask, an ask over an allow (`.harness/engine/core/events.py` L77-L93).
- The rules are in `.harness/policies/gate.json`, itself a guardrail file (`.harness/policies/gate.json` L1-L23); the checks are in `.harness/engine/modules/gate/handler.py` (L96-L146).
- What it refuses: writes to guardrail files (`.harness/policies/gate.json` L35-L87), and to harness-owned task files, `.git` or a target repository's folder (`.harness/engine/modules/gate/handler.py` L100-L108; `.harness/engine/modules/gate/terminal.py` L65-L117); a git write, when target repositories are set up, until the person approves that exact command with `harness approve-command` and its code, for one run within 10 minutes, and `push`, `clean`, `filter-branch`, `filter-repo`, `update-ref`, `prune`, `reset --hard`, `branch -D` and any force never (`.harness/engine/modules/gate/gitcmd.py` L22-L37, L272-L282; `.harness/policies/gate.json` L184-L186); the harness commands only a person may run (`.harness/policies/gate.json` L131-L144); a script that writes a guardrail file, as best effort (`.harness/engine/modules/gate/scriptcheck.py` L1-L11); the deny list: recursive delete of root, home or current folder, a download piped to a shell, formatting a disk, `sudo`, recursive permission changes, `docker rm`, `kubectl delete`, `terraform apply` and `destroy` (`.harness/policies/gate.json` L88-L130), also inside `bash -c` and `pwsh -Command` (`.harness/engine/modules/gate/handler.py` L119-L126). It also refuses reading the secrets file and requests to the board's port (`.harness/engine/modules/gate/handler.py` L612-L629, L719-L723).
- Calls to listed outside systems are judged by what they do; the ask list (deletes, history rewrites, network, installs) goes to Copilot's confirmation (`.harness/engine/modules/gate/handler.py` L130-L132; `.harness/policies/gate.json` L146-L182).
- A refusal tells the agent what to do instead, and to stop retrying when it repeats (`.harness/policies/gate.json` L187-L189).
- Limits: it reads text and is not a sandbox; the ask list is only a reminder, absent under Allow all; git writes need approval only when target repositories are set up (`.harness/engine/modules/gate/terminal.py` L1-L5; `docs/02-features.md` L50; `.harness/engine/modules/gate/handler.py` L761-L770).

Should cite: 00 Harness at a glance, "Harness: how dangerous commands are blocked" and "Harness: known limits". Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can.

### Q9. How does the approval code work, and why can't the agent approve its own plan?

Layer 3 · detail · guarantees.

- The code is the first six characters, in capitals, of a sha256 of what is approved: `PLAN.md` for the plan, `REQ.md` for the requirement, the write-back plan for a write-back (`.harness/engine/core/approval.py` L17-L25). Beyond the pages: when the requirement is not confirmed yet (`--with-req`, or **Approve plan** on the task page), the one code comes from a sha256 over `REQ.md` and `PLAN.md` together (`.harness/engine/modules/task/task.py` L423-L425, L451).
- The gate refuses the approval commands on the agent's command line, read the way the shell reads them (`.harness/policies/gate.json` L131-L137; `.harness/engine/modules/gate/harnesscmd.py` L1-L8).
- Each command needs a person at their own terminal, with a keyboard and a screen, and a typed code; the board's Terminal window gives no keyboard input for a code (`.harness/engine/core/approval.py` L28-L58; `docs/04-reference.md` L9).
- On the board, the paired browser's buttons run the same function with the code the person types; the agent cannot start the board server, and its requests to the board's port are refused (`.harness/engine/modules/task/boardserve.py` L11-L16, L819-L830; `.harness/engine/modules/gate/handler.py` L559-L564).
- `task approve-plan` checks `PLAN.md` again under the task's lock, so a plan changed while the person read it is refused; the approval is compared with the files before each edit-tool write to `DEV/` (`.harness/engine/modules/task/task.py` L460-L471; `.harness/engine/core/tasks.py` L159-L164).
- The exceptions the answer must keep: the requirement's confirmation is a text line the agent can write (`.harness/engine/modules/task/taskreview.py` L88-L110); the approval records are in `.task/task.json`, and a script the agent runs is checked only for guardrail paths (`.harness/engine/modules/gate/scriptcheck.py` L1-L11); `task allow --conn` and `--links` are not refused by the gate (`.harness/policies/gate.json` L136; `.harness/engine/modules/task/tasklife.py` L541-L546).

Should cite: 11 Task, "Task: who approves, and why the agent cannot approve its own plan". Course: The book · 5.3 Two gates: where a person approves.

Wrong if: it says the agent can never approve anything, without the exceptions.

### Q10. Why isn't a rule in the prompt or in `AGENTS.md` enough to keep the agent safe?

Layer 4 · broad · guarantees.

- Text (`AGENTS.md`, `.github/instructions/`, skills, the lines the hook adds to every prompt) asks the model, which can ignore it; code (the hooks and the command line) enforces what must hold; a person decides what cannot be taken back (`docs/02-features.md` L3; `docs/00-overview.md` L163-L164; `.harness/engine/modules/task/handler.py` L88-L121).
- The Guide's own example: opening a task is only asked by text, and the code does not force it (`AGENTS.md` L46-L47); keeping `DEV/` closed until the plan is approved is code (`.harness/engine/modules/gate/handler.py` L64-L88).
- The text rules are not even protected: `AGENTS.md`, `.github/instructions/`, `.github/skills/` and `.github/agents/` are neither guardrail paths nor in the integrity list, while the code rules are guardrail files; once the person has accepted them, a changed one makes the hook refuse every command and write, except in an admin chat; before the first accept there is no list and no check (`.harness/engine/core/guardrails.py` L11-L19; `.harness/policies/gate.json` L4-L19; `.harness/engine/integrity.py` L18-L26, L171-L183; `.harness/engine/hook.py` L312-L323).
- So text is still used, to tell the model the order of work; code sets the gates; a person holds the keys.

Should cite: 00 Harness at a glance, "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person" and "Harness: common questions" ("Can the agent change the harness's own rules?"). Course: Basic 06 · A prompt cannot stop a dangerous action: a harness can.

Wrong if: it says text rules are useless or are not used.

### Q11. Why does the harness keep the work in tasks instead of in the chat?

Layer 4 · broad.

- A chat lives as long as the chat, and Copilot compacts it as its context fills, at about 80%; a task's files do not depend on the chat (`.harness/policies/task.json` L3; `.harness/engine/core/copilot_events.py` L1).
- So the work is kept on disk: requirement, plan, results and state outlive the chats that do them, and any later chat picks the task up by name and reads the handover note `TASK.md` first (`.harness/engine/core/tasks.py` L1-L37; `.harness/engine/modules/task/handler.py` L124-L137; `.harness/engine/modules/task/task.py` L174-L209; `.harness/engine/modules/task/tasklife.py` L155-L160).
- What was said only in the old chat, and is in no task file, does not come along; that is why the agent is told to write a changed requirement into `REQ.md` first (`.harness/engine/core/messages.en.json` L2145-L2146, L108).
- The state is a file that harness code writes, so the gates are checked against facts, not against what the chat says; the stage is worked out from the files (`.harness/policies/gate.json` L24-L34; `.harness/engine/modules/task/taskstages.py` L1-L15).

Should cite: 11 Task, "Task: what it is", "Task: how it differs from a chat session", "Task: how a new chat continues the same task" and, for the stage worked out from the files, "Task: how it moves from one stage to the next". Course: The book · 5.1 Manage tasks, not chats.

### Q12. What is the idea behind the approval gates, and where does a person hold the keys?

Layer 4 · detail.

- The pattern of every row of the code/text/person table: code sets the gates a piece of work must pass, text tells the model how to get there, and a person holds the keys at each gate (`docs/02-features.md` L3; `docs/00-overview.md` L163-L164).
- Two gates for a task that changes a repository: the plan, whose approval opens `DEV/` to the edit tools, and the write-back, whose approval covers the exact digest: branch, base commit of each repository, sha256 of every file (`.harness/engine/modules/task/task.py` L428-L475, L941-L944; `.harness/engine/modules/gate/handler.py` L80-L84; `.harness/engine/modules/task/promote_target.py` L112-L116). The requirement is confirmed with a code too, but that confirmation is a text line the agent can write (`.harness/engine/modules/task/task.py` L570-L612; `.harness/engine/modules/task/taskreview.py` L88-L110).
- The key is bound to what the person read: the code comes from a sha256 of the file, a file changed after the person read it gets a new code, and a change to what `REQ.md` asks (What to do, What not to do, Done when) undoes the plan's approval (`.harness/engine/core/approval.py` L17-L25; `.harness/engine/modules/task/task.py` L460-L471; `.harness/engine/core/tasks.py` L117-L164). Beyond the pages: when the requirement is not confirmed yet, the one code of **Approve plan** comes from a sha256 over `REQ.md` and `PLAN.md` together (`.harness/engine/modules/task/task.py` L423-L425, L451).
- The other keys a person holds: git writes (`approve-command`), held outside calls, more checks or waiving them (`.harness/policies/gate.json` L131-L137; `.harness/engine/modules/gate/handler.py` L132-L141, L192-L293); accepting or closing (`.harness/engine/modules/task/accept.py` L167-L181; `.harness/policies/gate.json` L138-L144); the commit (`.harness/engine/modules/task/promote_target.py` L6).

Should cite: 11 Task, "Task: how it moves from one stage to the next", "Task: who approves, and why the agent cannot approve its own plan" and "Task: what happens when the requirement changes after the plan was approved"; 00 Harness at a glance, "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person". Course: The book · 5.3 Two gates: where a person approves (https://smarshu.com/book/read/5-3-two-approvals.html) for an answer built mainly on 11; Basic 06 · A prompt cannot stop a dangerous action: a harness can (https://smarshu.com/writing/basic-06-prompt-cannot-stop) or The book · 0.1 What is Harness Engineering? for one built mainly on 00.

### Q13. I maintain a data pipeline repository. How do I start a task and give the agent my requirement documents?

How-to · detail. Tests the short answer, the tutorial pointer, and that the answer uses nothing of the asker's own work.

- Short answer, a few sentences: start the board (**Start Harness**, or `harness task board` in your own terminal) and use the browser it pairs (`docs/01-quickstart.md` L20, L87-L97); say in one sentence what you want done and in which repository, in the chat or with **New task**, and the agent asks, then opens a task (`.harness/engine/modules/task/chatnew.py` L1-L8; `.github/skills/harness-my-task/SKILL.md` L29-L65); drop the documents on the task's **Intake** tab, and confirm the `REQ.md` the agent writes with **Confirm requirement** and the code (`.harness/engine/modules/task/intake.py` L1-L10; `.harness/engine/modules/task/task.py` L570-L598).
- Then: the steps on screen are in the harness tutorial **1 A day with the harness**, in `AI Exploration/3 Courses/Harness tutorials/`.

Should cite: 00 Harness at a glance, "Harness: how a person uses it day to day". Tutorial: 1 A day with the harness. Course: none needed.

Wrong if: it writes a long step-by-step guide instead of naming the tutorial; it makes an example from the asker's own repository, mail, chats or files (the first pilot's P2 did); it cites or recommends the file 21 Start a task and give it the requirement.

### Q14. The agent says my command was refused. How do I get it run?

How-to · detail.

- Short answer: the gate refused the command before it ran, and its reason tells the agent what to do instead (`.harness/engine/modules/gate/handler.py` L96-L146; `.harness/policies/gate.json` L187-L189). If the command is really needed, run it yourself in your own terminal. A git write, when target repositories are set up, waits for you to approve that exact command with `harness approve-command` and its code, for one run within 10 minutes; `push`, `clean`, `filter-branch`, `filter-repo`, `update-ref`, `prune`, `reset --hard`, `branch -D` and any force are never approved (`.harness/engine/modules/gate/handler.py` L132-L141; `.harness/engine/modules/gate/gitcmd.py` L22-L37, L272-L282; `.harness/policies/gate.json` L184-L186).
- Then: the harness tutorial **2 When the agent is stopped**, in `AI Exploration/3 Courses/Harness tutorials/`.

Should cite: 00 Harness at a glance, "Harness: what is enforced by code, what is asked of the model by text, and what is left to a person" (row "Writes and dangerous commands") and "Harness: how dangerous commands are blocked". Tutorial: 2 When the agent is stopped. Course: none needed.

Wrong if: it suggests a way round the gate (admin mode, changing `gate.json`, switching hooks off, a script); it writes a long guide instead of naming the tutorial.

### Q15. How does autorun work? Can a task run on its own overnight?

Not covered.

- The right answer says "The Harness Guide does not cover this yet." It may add only what the Guide says in passing: `task autorun on` is one of the commands the gate refuses on the agent's command line, so only a person can switch it on (00, "Harness: the main safety guarantees and their exact scope"; `.harness/policies/gate.json` L131-L137), and "autorun stopped" is one of the reasons a task waits for you (11, "Task: what "waiting for you" means"; `.harness/engine/modules/task/tasklife.py` L276-L336). It names no tutorial: autorun is not in the first five.
- For the grader only, so that a made-up answer can be spotted: autorun works down `TODO.md` and needs an approved plan, unticked steps and `[review]=n`; it is switched on in a terminal with a typed code (`docs/04-reference.md` L100; `AGENTS.md` L54). None of this is in the Guide: an answer that says it did not get it from the Guide.

Should cite: none. Course: none.

Wrong if: it explains how autorun works or when it stops; it points to a tutorial as if one covered autorun.
