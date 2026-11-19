---
title: Cost and usage
subject: Cost and usage
layer: concept
file: 22 Cost and usage
harness_tag: 1.8.3
course: The book · 1.1 Don't pick a model by token price alone | https://smarshu.com/book/read/1-1-models-and-cost.html
course: The book · 6.2 A report a person can read in five minutes | https://smarshu.com/book/read/6-2-task-report.html
course: The book · 3.1 Context is a budget | https://smarshu.com/book/read/3-1-context-budget.html
course: The book · 7.3 What I cut, and what the data says | https://smarshu.com/book/read/7-3-what-we-cut.html
---
## Cost and usage: what it is and what problem it solves

Cost and usage is how the harness shows what a task cost: the agent's working time, the time it waited for a person, and the Copilot Credits it used, per prompt and per stage. Code reads the numbers from Copilot's own record of each chat, never from what the agent says, and shows them as Copilot records them, not turned into money {src:.harness/engine/core/copilot_events.py#L1-L11} {src:.harness/engine/core/messages.en.json#L311}. It answers which task is expensive, where the time went, and whether any was waste; **Agent Performance Review** finds failed and repeated work for free and, when a person starts it, has a model say whose each waste was {src:.harness/engine/modules/task/perfreview.py#L1-L17}.

## Cost and usage: what the harness itself spends

The harness's own work calls no model: hooks, the gate, task commands, document conversion, knowledge base checks and autorun's stop rules are local code and spend no Credits {src:docs/06-cost-optimization.md#L5-L13} {src:.harness/engine/modules/task/intakeconvert.py#L1-L4}. Credits are spent by model calls in Copilot chats: the agent's own work, plus what a person turns on: independent checks (one reviewer subagent per check, n + 2 unless the person gives more with `task review extend`), autorun (one worker subagent per step, under a spend limit), the super agent chat (50 Credits a day by default), the mapper of `/generic-mapreduce` (at most 4 subagents in 60 minutes), **Ask why** on a report page (a chat that explains the numbers) and **Agent Performance Review** {src:.harness/policies/task.json#L9-L31}. Looking at the report page or the board costs nothing.

## Cost and usage: where the numbers come from

The numbers come from Copilot's own record of each chat session, `~/.copilot/session-state/<session id>/events.jsonl` (or under `COPILOT_HOME`). The harness takes only numbers, times and names from it, no tool argument and no result; the first characters of what the person typed are taken for the page only, never for an agent {src:.harness/engine/core/copilot_events.py#L1-L11} {src:.harness/engine/core/copilot_events.py#L25-L59}. The policy switch `report.copilot_events` (on by default) allows this; off, or with the file missing, the report has times from the hook log and no usage {src:.harness/policies/task.json#L21-L31} {src:.harness/engine/modules/task/taskinsight.py#L1-L13}.

**Credits** are Copilot's AI Credits as its record gives them for each model call (`totalNanoAiu`); **premium requests** are a separate count from the same record. They are added up as they are; the harness holds no prices {src:.harness/engine/core/copilot_events.py#L153-L189}.

**One rule for a prompt's Credits** (1.7.41), the same in the report, Live, Rounds and Agent Performance Review: each model call's Credits go to the prompt running when the call was recorded; what Copilot's running total counts on top (the summing-up of a compaction, an older record) goes to the prompt running when it came. The prompts add up to the session's total. It replaced counting by the running total alone, which often came after the next prompt began and gave one prompt's Credits to the next {src:.harness/engine/core/copilot_events.py#L153-L189}.

**Subagent calls are included**: a reviewer's, worker's or mapper's model calls are in the same session file, their Credits in the prompt that started them, their run time and tokens listed apart {src:.harness/engine/core/copilot_events.py#L321-L334}.

## Cost and usage: what is computed for each task

![The task analysis page of a task as the board serves it: agent working against waiting for you, Credits, premium requests, the key points, and the Agent Performance Review box](img/report.png)

For each task, code takes the prompts that belong to it, across every session that held it, and works out {src:.harness/engine/modules/task/taskinsight.py#L579-L667}:

- **Per prompt**: time split into model thinking, tools, subagents, and waiting for the person's answer or approval; Credits, premium requests, tokens, turns, tool calls (failed ones too), model and thinking effort, compactions, context size.
- **Agent time against waiting-for-person time**: "waiting for you" is the gap from a prompt's end to the task's next prompt, in any session, plus the wait still going on; "agent working" is the prompts' own time. Inside a turn, time on a permission, a question to the person or `harness wait --approval` is its own share, not tool time, and the key point on waiting counts it as the person's. Paused time is neither {src:.harness/engine/core/copilot_events.py#L104-L114}.
- **Per stage** (requirement, plan, developing, independent check, write-back; a test task's guide and environments), a prompt that ran through two stages cut where the stage changed; and **per round** for a task written back more than once.
- **The cards of the page**, in order: key points; the Agent Performance Review box (only on the page the board serves and on copies saved from it, see below); where the time went; gate blocks; every prompt with its stage tag; a stage table; a context-growth line chart (one dot per prompt, a hollow dot where Copilot compacted the context); cache; a tools table (the 15 tools that took the most time, with calls, total time, longest call, failed calls and result tokens); independent checks; and a footer. Subagents have no card of their own: they show as a slice of the time bar, a column of the stage table and rows of the checks table {src:.harness/engine/modules/task/web/task.js#L352-L360}.
- **Key points**, largest first: the waiting share and longest wait, the slowest prompt, **the prompt with the most Credits** and its share, the checks' share, compactions, caches that ran out, refusals and failures {src:.harness/engine/modules/task/taskinsight.py#L785-L856}.

**Where it is shown.** The task analysis page: `report.html` beside `report.md` in `.workspace/reports/tasks/<task>/`, written at close and on `harness task report` as a snapshot of that moment, and live from **Time and usage** on the task page, which the board recomputes at each request {src:.harness/engine/modules/task/task_report.py#L1-L5}. The **Agent Performance Review** box is on the page the board serves and on copies saved from it, and not in the `report.html` written at close or by `harness task report` {src:.harness/engine/modules/task/boardserve.py#L580-L584} {src:.harness/engine/modules/task/taskboard.py#L102-L105}. The board: time, Credits and prompts on each task's card and row, and their sum over the tasks it lists {src:.harness/engine/modules/task/taskinsight.py#L886-L895}. Autorun's run card: a run's spend against its limit.

## Cost and usage: the ⚠ cost warning on the board

The board puts a ⚠ tag on an open task whose Credits reach `cost_ratio` (2.0) times the median Credits of closed tasks of the same kind, "Credits are <n> times the median of closed tasks of the same kind". The rule fires only with at least 3 such closed tasks that spent Credits. Review tasks of Agent Performance Review are left out of the median, and a review task is compared with none {src:.harness/engine/modules/task/health.py#L141-L157} {src:.harness/engine/modules/task/taskboard.py#L292}.

The tag only warns: it stops nothing and is not a budget. Sibling health rules tag a task that looks stuck, repeats a command or turns without changing a file; all read the hook log and Copilot's record, never the conversation {src:.harness/engine/modules/task/health.py#L1-L28}.

## Cost and usage: Agent Performance Review

Agent Performance Review (1.7.41) has three layers, dearer as they go down {src:.harness/engine/modules/task/perfreview.py#L1-L17}:

1. **Accounts and facts: code, free** (`perfdata.py`), shown as a box on the task analysis page the board serves and on copies saved from it (not in the `report.html` written at close), from Copilot's record, the hook log and what the board sent. Facts by fixed rules: `failed`, `refused` and `held` calls; `retry` and `repeat` (the same try again); `person` (a call that waited for the person); `slow` (2 minutes or more); `cold` (a cache that ran out, and its extra cost); `compaction`; `intervention` (the person stepping in after the agent stopped: a signal, not a verdict); and `context`, what every call carried before any work, priced by part {src:.harness/engine/modules/task/perfdata.py#L1-L23} {src:.harness/engine/modules/task/perfdata.py#L506-L571}. **Open** shows the review page `/tasks/<task>/performance`: each prompt's Credits or time and origin, and the call timeline.
2. **Lookups: code** (`perfreview.py`). `harness task performance <task> --task <review task>` writes `EVIDENCE.json` into the review task and prints the overview; `--prompt`, `--span`, `--find`, `--call` and `--check` look things up. Every cost the review states is counted by code.
3. **Reasoning and blame: a model, started by a person.** No Python file holds this layer: it is the model following the skill `harness-agent-performance-review`. The button **Agent Performance Review** opens an `rca` task named `apr-<task>`, with high thinking and the model the person picks; the dialog says about how many tokens it will read {src:.harness/engine/core/messages.en.json#L4316-L4319}.

**Only a person starts it.** The skill `harness-agent-performance-review` is marked `disable-model-invocation: true`, so Copilot does not load it for the agent; that does not stop the agent from reading the `SKILL.md` file and following it, which only the skill's text forbids. Since 1.8.2 the button's first message only opens the task; when that turn ends, the board sends `/harness-agent-performance-review <words>` to the same chat, once, with the chosen model {src:.github/skills/harness-agent-performance-review/SKILL.md#L1-L26} {src:docs/07-release-notes.md#L40-L46}.

**What the model judges.** It reads only the prompts code marked worth reading, judges each segment `needed`, `waste` or `cold` (only a cold cache's extra is waste), traces each waste back from the person's words to the result, and names its owner: `person`, `harness`, `model`, `environment`, `platform` (Copilot itself) or `knowledge`, with a confidence `certain`, `likely` or `unsure`. It critiques the person's prompts that caused waste (original, problem, better wording) and writes suggestions for each owner {src:.github/skills/harness-agent-performance-review/SKILL.md#L36-L59} {src:.github/skills/harness-agent-performance-review/references/attribution.md#L5-L22}.

**Evidence required, checked by code.** `--check` refuses a `FINDINGS.json` with an owner, confidence or verdict outside the lists, an id that does not exist, a waste segment with no owner, or a `model` or `harness` finding with no evidence unless it says `unsure`; a `certain` model finding must cite where the right way was in the agent's context. Code counts the waste in Credits and time by owner, splitting a segment with two owners evenly; the review's own Credits are shown beside it {src:.harness/engine/modules/task/perfreview.py#L349-L465}.

**Across tasks.** `harness task performance --all` (`--days N`) groups, over every task on this computer, refusals by gate rule, failures by tool and error, repeated tries, cold caches and what every call carried, plus reviewed tasks' waste by owner and suggestions; it costs nothing {src:.harness/engine/modules/task/perfroll.py#L1-L8}.

## Cost and usage: Save as HTML, to share

**Save page** on the task analysis page and **Save as HTML** in the task page's menu each download one HTML file for someone with no access to the board. It is a copy of that moment, with no buttons, and asks the network for nothing {src:.harness/engine/modules/task/boardserve.py#L597-L637}. The task copy holds the task's documents, diff and history: read it before sending.

## Cost and usage: choosing a model per task

A task has its own model: the model, thinking level and context size, chosen in New task or Task settings and kept in the task state (`chat.model`). The board sends it with the messages it sends to the task's chat, because the host keeps the last model it was given, whoever gave it {src:.harness/engine/modules/task/boardserve.py#L1565-L1590}.

**No silent fallback.** A model, level or size the host does not list now is refused with a reason, not swapped. With no model chosen the chat keeps VS Code's own choice. Since 1.6.101 a task's chat no longer starts on Copilot Fusion (Copilot picking a model per request) by itself; only a one-click chat nobody chose a model for starts on Fusion at Standard, and that is not kept on the task {src:.harness/engine/modules/task/chatnew.py#L171-L195} {src:docs/07-release-notes.md#L911-L919}.

**Why.** The model is the person's largest lever on cost, and a switch mid-task costs too: the new model "loads the whole context again" {src:.harness/engine/core/messages.en.json#L2192}.

## Cost and usage: the spend limits that exist, and the one that does not

Two limits stop spending, each set by a person:

- **Autorun's spend limit**, per run: the Credits a run may add after Start (none, or the recommended 500, 1,000 or 2,000 by step count, or twice or four times that); the run stops with `budget` (see the file 20 Autorun) {src:.harness/engine/modules/task/autorun.py#L86-L89} {src:.harness/engine/modules/task/autorun_spend.py#L1-L5}.
- **The super agent's daily limit**, `super.daily_credits` (50; `0` switches the chat off; see the file 21 Super agent) {src:.harness/policies/task.json#L21-L31}.

Independent checks (n + 2, plus what the person gives with `task review extend`) and mapper subagents (4 in 60 minutes) are capped by count, not Credits {src:.harness/engine/modules/task/taskreview.py#L161-L163}. **There is no total budget per task.** Nothing stops a task's own chat when its Credits pass a sum; the ⚠ tag only warns {src:.harness/engine/modules/task/health.py#L141-L157}.

## Cost and usage: what is enforced by code, and what is only an instruction

**Code**: reading the record and splitting Credits and time by prompt, stage and round; the ⚠ rule; the review's facts, every cost it states, and the rules on `FINDINGS.json`; leaving review tasks out of the median; refusing a model the host does not list; autorun's spend limit and the super agent's daily limit {src:.harness/engine/core/copilot_events.py#L153-L189} {src:.harness/engine/modules/task/perfreview.py#L349-L465}.

**Copilot**: `disable-model-invocation: true` keeps Copilot from loading the review skill for the agent (its file stays readable); the gate's person-only list does not name `harness task performance` {src:.harness/policies/gate.json#L131-L137}.

**Only an instruction** (the skill's text): never start a review on its own; read only the prompts worth reading; stop early when the task was quiet; never estimate a cost; never judge a short correction as a bad prompt; suggest, never change; never paste thinking, commands or results into a ticket or message {src:.github/skills/harness-agent-performance-review/SKILL.md#L36-L59}.

**Who decides.** The **person** picks each task's model, starts any review, sets the spend limits and policy numbers (`cost_ratio`, `daily_credits`), and decides whether to send a saved page; **code** counts every number and fires the warning; **the review's model** judges waste, owner and confidence, and suggests {src:.github/skills/harness-agent-performance-review/references/attribution.md#L5-L22}.

## Cost and usage: why it is built this way, and what was removed

**Code counts, the model judges.** Everything with one right answer is code: the accounts, the facts, the cost of any stretch of calls, the check of the findings. The model reads only what code picked, so a review's cost is mostly what it reads, not the model's tier; hence the button sets high thinking but no model, and says how much it will read {src:.harness/engine/modules/task/perfreview.py#L1-L17}. An earlier version let the model estimate costs; `--span` now gives them from the record.

**Removed in 1.1: Levels and their budgets.** 1.0 had three Levels (L1 quick answers, L2 medium tasks, L3 several agents), and L1 searches had a limit by count {src:docs/07-release-notes.md#L3684-L3694}. 1.1.0 removed the Levels with their search budget, skills and policy `task-levels.json`; searches and tool calls have had no limit by count since {src:docs/07-release-notes.md#L3586-L3601}. The reasons: only L2 was used, picking a level first was a needless step, two sets of rules confused the agent, and L3's three agents were no better on tasks with a clear requirement, at about 4.5 times the usage {src:docs/05-design.md#L57-L68}.

## Cost and usage: the call logs and what they keep

The harness's own log is one JSONL line per hook call, in `.harness/runtime/logs/<surface>/<session id>.jsonl` {src:.harness/engine/core/logs.py#L1-L4}. A line keeps the event, the tool and the decision, and for a refusal or confirmation the deciding module and reason. It keeps no tool arguments, except the paths and command of a call refused or sent to a person, the paths a finished call touched, a short hash of a terminal command, skill and knowledge base file names, and an outside call's system, environment, verb and target, never its result {src:.harness/engine/core/callrecord.py#L1-L10}. The log holds no tokens and no Credits; usage is only in Copilot's record. Nothing deletes logs by itself; `harness logs prune --days N` deletes old ones. It is meant for a person but not person-only: the gate only asks Copilot's confirmation, which does not show under Allow all, so an agent can run it {src:.harness/engine/modules/observe/prune.py#L1} {src:.harness/policies/gate.json#L176-L181}.

## Cost and usage: where in the source

Under `.harness/engine/` {src:.harness/engine/core/copilot_events.py#L1-L11}: `core/copilot_events.py` (Copilot's record, Credits rule); `modules/task/taskinsight.py`, `task_report.py`, `taskhtml.py` (numbers, reports, saved copies); `health.py` (⚠); `perfdata.py`, `perfreview.py`, `perfroll.py` (the review); `core/callrecord.py` (hook log). Also `.github/skills/harness-agent-performance-review/` and `.harness/policies/task.json`.

## Cost and usage: common questions

**Q: What does running the harness cost? Does it spend tokens itself?** Its hooks, commands and checks call no model; Credits go to the Copilot chats and to the extras a person turns on {src:docs/06-cost-optimization.md#L5-L13}.

**Q: How do I see what a task cost, and can I trust it?** On the task analysis page and the board; code reads it from Copilot's own record, not from the agent {src:.harness/engine/modules/task/taskinsight.py#L1-L13}.

**Q: Can I see it in money?** No: Credits and premium requests as Copilot records them; the harness holds no prices {src:.harness/engine/core/messages.en.json#L311}.

**Q: Can I cap what a task spends?** Only an autorun run and the super agent chat have limits; a task's own chat has none, and the ⚠ tag only warns {src:.harness/engine/modules/task/health.py#L141-L157}.

**Q: Can the agent start a review, or blame me without proof?** Copilot does not load the review skill for the agent, though the agent could still read its file; only text forbids it. `--check` demands evidence for `model` and `harness` findings; for `person` only the skill's text asks for the prompt {src:.harness/engine/modules/task/perfreview.py#L349-L465}.

## Cost and usage: limits

- **Only what Copilot recorded on this computer.** A session file missing, cleaned up, over 300 MB or in a format the reader does not know gives times only, no Credits {src:.harness/engine/core/copilot_events.py#L25-L59}.
- **Autorun's limit is checked between calls**, so a call under way can pass it {src:.harness/engine/modules/task/autorun_spend.py#L1-L5}.
- **The ⚠ rule needs 3 closed tasks of the same kind** and compares the task's Credits over all its rounds {src:.harness/engine/modules/task/health.py#L141-L157}.
- **The review's verdicts are a model's**: thinking may be empty, `--find` matches words not meaning; the person checks the evidence {src:.github/skills/harness-agent-performance-review/SKILL.md#L36-L59}.
- **`EVIDENCE.json` keeps commands, results and thinking**, cut and passed through redaction, in the review task's folder on this computer {src:.harness/engine/modules/task/perfdata.py#L1-L23}.
- **Docs lag**: `docs/06-cost-optimization.md` section 7 still says the harness cannot see real usage {src:docs/06-cost-optimization.md#L63-L67}.

## Cost and usage: related files

File 22b Cost and usage internals (the code-level detail behind this file: the log, the Credits and time rules, the cards of the page, the review's checks, the gate review). Files 00 Harness at a glance, 11 Task (the report at close), 12 The board, 17 Independent checks, 20 Autorun (spend limit, run card), 21 Super agent (daily limit), 23 Skills (`disable-model-invocation`), 34 Version history, 41 Ideas behind the harness. How-to: the harness tutorial "2 A tour of the harness" in `3 Courses/Harness tutorials/` shows Time and usage, Save as HTML and the review page on screen {src:.harness/engine/modules/task/task_report.py#L1-L5}.
