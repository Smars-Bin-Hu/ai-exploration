---
title: Ideas behind the harness
subject: Ideas
layer: idea
file: 41 Ideas behind the harness
harness_tag: 1.8.3
course: Basic 01 · Stop using AI the 2024 way: why you need a harness | https://smarshu.com/writing/basic-01-stop-using-ai-the-2024-way
course: Basic 06 · A prompt cannot stop a dangerous action: a harness can | https://smarshu.com/writing/basic-06-prompt-cannot-stop
course: The book · 0.1 What is Harness Engineering? | https://smarshu.com/book/read/0-1-the-gap-and-the-map.html
course: The book · 1.1 Don't pick a model by token price alone | https://smarshu.com/book/read/1-1-models-and-cost.html
course: The book · 1.2 When an Agent misuses a tool, check its description and errors first | https://smarshu.com/book/read/1-2-tool-calling.html
course: The book · 2.1 How does an Agent actually work? | https://smarshu.com/book/read/2-1-agent-loop.html
course: The book · 2.2 Hooks, the point every call passes through | https://smarshu.com/book/read/2-2-hooks.html
course: The book · 2.3 Use subagents sparingly | https://smarshu.com/book/read/2-3-subagents.html
course: The book · 3.1 Context is a budget | https://smarshu.com/book/read/3-1-context-budget.html
course: The book · 3.2 Long chats get worse | https://smarshu.com/book/read/3-2-long-sessions.html
course: The book · 3.3 Instructions and skills, load only what you need | https://smarshu.com/book/read/3-3-instructions-and-skills.html
course: The book · 4.1 A rule in a prompt is a request | https://smarshu.com/book/read/4-1-requests-and-rules.html
course: The book · 4.2 Asking is not a limit | https://smarshu.com/book/read/4-2-ask-vs-refuse.html
course: The book · 4.3 Guard the files that hold the rules | https://smarshu.com/book/read/4-3-guardrails.html
course: The book · 4.4 Build the enforcement layer like software | https://smarshu.com/book/read/4-4-enforcement-design.html
course: The book · 4.5 Some things you never hand over | https://smarshu.com/book/read/4-5-least-privilege.html
course: The book · 4.6 Text the agent reads can give it orders | https://smarshu.com/book/read/4-6-untrusted-input.html
course: The book · 5.1 Manage tasks, not chats | https://smarshu.com/book/read/5-1-tasks.html
course: The book · 5.2 The agent writes the requirement, the person confirms it | https://smarshu.com/book/read/5-2-requirements.html
course: The book · 5.3 Two gates: where a person approves | https://smarshu.com/book/read/5-3-two-approvals.html
course: The book · 5.4 Let the agent check its own work | https://smarshu.com/book/read/5-4-self-checks.html
course: The book · 5.5 Make a pass count | https://smarshu.com/book/read/5-5-counted-checks.html
course: The book · 5.6 Can a model check a model? | https://smarshu.com/book/read/5-6-model-checks-model.html
course: The book · 5.7 Unattended: when it must stop | https://smarshu.com/book/read/5-7-when-to-stop.html
course: The book · 5.8 Long work across sessions | https://smarshu.com/book/read/5-8-long-work.html
course: The book · 5.9 Who decides: code, a cheap model, the main model, a person | https://smarshu.com/book/read/5-9-who-decides.html
course: The book · 6.1 Record what happened, not what the agent said | https://smarshu.com/book/read/6-1-observe.html
course: The book · 6.2 A report a person can read in five minutes | https://smarshu.com/book/read/6-2-task-report.html
course: The book · 7.3 What I cut, and what the data says | https://smarshu.com/book/read/7-3-what-we-cut.html
course: The book · 8.1 A knowledge base: an honest index of the code | https://smarshu.com/book/read/8-1-why-a-knowledge-base.html
course: The book · 8.2 The toolkit: scripts that draw a map of the code | https://smarshu.com/book/read/8-2-kb-toolkit.html
course: The book · 8.3 Is the map right? A blind audit | https://smarshu.com/book/read/8-3-kb-audit.html
---
## Ideas: how to use this file

This file holds the AI harness engineering ideas the harness is built on, one section per idea: the idea in plain words, one sentence on where the harness applies it, and "Learn more", the course on smarshu.com that teaches it (a chapter of the book Harness Engineering or a Basic post). When a question asks why the harness works the way it does ("why tasks instead of chats", "why a separate reviewer", "why not a rule in the prompt"), the answer gives the idea, the sentence on the harness, and the "Learn more" link written out. How the harness does it in detail is in the feature file each section names.

## Ideas: an agent is a model plus a harness

The idea: harness engineering is building the rules, checks and limits around a model so that an agent can be trusted with real work. Agent = Model + Harness, where the harness is every piece of code, configuration and execution logic that is not the model. The same model does far more inside a good harness than in a chat box, because most of the gap between a demo and real work lies outside the model. So when an agent lets a team down, the first question is what was missing around it (a rule, a check, a file it never saw), not which bigger model to buy.

In the harness: the harness is that outside layer for GitHub Copilot in VS Code, made of one hook entry point that runs at every prompt and before and after every tool call, task folders that hold the work, and approvals only a person can give {src:.github/hooks/harness.json#L1-L113} {src:.harness/engine/core/approval.py#L1-L8}; the file 00 Harness at a glance has the whole picture.

Learn more: Basic 01 · Stop using AI the 2024 way: why you need a harness — https://smarshu.com/writing/basic-01-stop-using-ai-the-2024-way ; The book · 0.1 What is Harness Engineering? — https://smarshu.com/book/read/0-1-the-gap-and-the-map.html

## Ideas: the agent loop and tool calling

The idea: an agent is a loop in which the model asks for a tool call, a program outside the model runs it, and the result goes back so the model can pick the next step. The model cannot touch files on its own and knows a tool only by its name, description and error messages, so how those words are written decides how well the tool is used. The loop has four places a team can change: what the agent reads, which tools it has, a check before a call and a check after it. The loop stops when the model wants no more tools, not when the work is finished, so an agent's "done" is a claim to check.

In the harness: the harness stands at those places, adding a few lines on where the task stands to every prompt, deciding each tool call before it runs and logging it after, and answering a refused call with a reason that tells the agent what to do instead {src:.harness/engine/modules/task/handler.py#L93-L126} {src:.harness/engine/hook.py#L1-L15} {src:.harness/engine/modules/gate/handler.py#L117-L167}; see the file 15 The gate and guardrails.

Learn more: The book · 2.1 How does an Agent actually work? — https://smarshu.com/book/read/2-1-agent-loop.html ; The book · 1.2 When an Agent misuses a tool, check its description and errors first — https://smarshu.com/book/read/1-2-tool-calling.html

## Ideas: hooks, the place where code can say no

The idea: a hook is code the platform runs at fixed points of every turn, inside subagents too, so it is where the rules that must hold every time live. A hook sees the text of a call, not what a command does once it runs, and it can fail quietly: in Copilot as the book observed it, a hook that times out counts as a pass. The enforcement layer is software and will fail, so decide in advance whether a failure lets the call through (fail open) or blocks it (fail closed), write that down, and build the layer so it can be tested.

In the harness: one hook entry point serves every event and fails closed: when the engine cannot load, a guardrail module fails, or the session state cannot be read, it refuses every terminal command and every tool that may change a file and keeps reads, while only helpers such as the log may fail without stopping work (chapter 4.4 describes an earlier version, whose hook failed open; it fails closed since 1.7.38) {src:.harness/engine/hook.py#L1-L15} {src:AGENTS.md#L56-L59}; see the file 15 The gate and guardrails.

Learn more: The book · 2.2 Hooks, the point every call passes through — https://smarshu.com/book/read/2-2-hooks.html ; The book · 4.4 Build the enforcement layer like software — https://smarshu.com/book/read/4-4-enforcement-design.html

## Ideas: a rule in a prompt is a request, a rule in code is a rule

The idea: text in a prompt, a rule file or a skill asks the model, which may ignore it or never receive it; only code that runs before the call holds a rule every time. Words still do most of the work, because they tell the agent the goal, the background and the order of work. A rule moves into code when it keeps being broken, when breaking it once does harm that cannot be undone, or when other steps rely on it. And a rule the agent can edit is a rule it can remove, so the files that hold the code rules must be out of its reach, with any human override limited and recorded.

In the harness: opening a task is asked only by text, while keeping `DEV/` closed to the task chat's edit tools until the plan is approved is code, and so is the rule that nothing is fetched into it or written back without that approval, and the code rules (engine, policies, hook files) are guardrail paths the agent's edit tools and named terminal writes cannot change outside admin mode, while the text rules (`AGENTS.md`, instructions, skills) are not protected {src:AGENTS.md#L46-L47} {src:.harness/engine/modules/gate/handler.py#L64-L94} {src:.harness/engine/modules/task/task.py#L404-L406} {src:.harness/policies/gate.json#L4-L19}; the file 00 Harness at a glance gives the full split between code, text and person.

Learn more: Basic 06 · A prompt cannot stop a dangerous action: a harness can — https://smarshu.com/writing/basic-06-prompt-cannot-stop ; The book · 4.1 A rule in a prompt is a request — https://smarshu.com/book/read/4-1-requests-and-rules.html ; The book · 4.3 Guard the files that hold the rules — https://smarshu.com/book/read/4-3-guardrails.html

## Ideas: asking is not a limit

The idea: "ask me first" is not a safety limit, because people click Allow the hundredth time, and the platform even offers ways to remove the box. A limit is a refusal the agent cannot argue with, graded by what the action could break, and given with a written reason the agent can act on. A question to a person is kept for the few cases that need judgment.

In the harness: the gate refuses a deny list of dangerous commands outright; when target repositories are set up it never approves `git push`, `reset --hard` and the like and holds other git writes until the person approves that exact command with a code, and it leaves only a short ask list to Copilot's own confirmation, which shows no box in a chat set to Allow all {src:.harness/policies/gate.json#L88-L130} {src:.harness/engine/modules/gate/gitcmd.py#L22-L37} {src:.harness/policies/gate.json#L146-L182}; see the file 15 The gate and guardrails.

Learn more: The book · 4.2 Asking is not a limit — https://smarshu.com/book/read/4-2-ask-vs-refuse.html

## Ideas: some things you never hand over

The idea: a hook blocks only what it can see, and it can fail, so a guard that holds most of the time is the wrong tool for what is not yours or cannot be undone. For production, credentials and other people's repositories, the best defence is not to give them to the agent at all: the agent works on a copy, or a person runs the step and pastes the result back. That is slower, so it is kept for harm that is large or cannot be undone.

In the harness: the agent works on copies in the task folder, its edit tools are refused inside a target repository, a write-back goes to a new branch that the person commits (a registered knowledge base excepted), the person's identities stay in `.harness/.env`, which the gate refuses the agent to read, and on a `prod` connection only a read passes by default {src:.harness/engine/modules/task/promote_target.py#L1-L14} {src:.harness/engine/core/connections.py#L8-L11} {src:.harness/engine/core/systems.py#L36-L38}; see the files 16 Write-back and 19 Tool packs, connections and MCP.

Learn more: The book · 4.5 Some things you never hand over — https://smarshu.com/book/read/4-5-least-privilege.html

## Ideas: text the agent reads can give it orders

The idea: a model cannot reliably tell the person's orders from orders hidden in a web page, a document or a tool result it reads. The danger comes when three things meet: the agent can read private data, it reads text nobody vouched for, and it can send data out. Taking away any one of the three removes the danger, while filters on the text only lower the odds,.

In the harness: the harness has no check aimed at injected text; it narrows the three instead, judging a call to a listed outside system by what it does (a write waits for the person, a destroy is refused) and letting no call it cannot judge pass, while going on the network is only on the ask list, which shows no box under Allow all {src:.harness/engine/core/systems.py#L36-L38} {src:AGENTS.md#L56-L59} {src:.harness/policies/gate.json#L146-L182}; see the files 15 The gate and guardrails and 19 Tool packs, connections and MCP.

Learn more: The book · 4.6 Text the agent reads can give it orders — https://smarshu.com/book/read/4-6-untrusted-input.html

## Ideas: context is a budget, so load only what is needed

The idea: rules, knowledge, files and tool results share one context window, and each crowds out the others; room left in the window does not make it work well, and a rule buried in a long, noisy context is more likely to be missed. So the always-loaded rules are kept few and short, and the rest is fetched when a task needs it: a skill is a manual read on demand, and like any written rule it is not enforced.

In the harness: `AGENTS.md` holds only the core rules, instruction files are added when a matching file is involved, a skill's body loads only when a request matches its description, and the hook adds a few lines on where the task stands instead of all the rules {src:AGENTS.md#L33-L40} {src:.github/instructions/skills.instructions.md#L6-L12} {src:.harness/engine/modules/task/handler.py#L93-L126}; see the file 23 Skills.

Learn more: The book · 3.1 Context is a budget — https://smarshu.com/book/read/3-1-context-budget.html ; The book · 3.3 Instructions and skills, load only what you need — https://smarshu.com/book/read/3-3-instructions-and-skills.html

## Ideas: tasks, not chats, and memory in files

The idea: a chat gets worse as it grows, the platform compacts it, and the summary drops details such as the person's exact words and the reason for a choice; a new chat knows nothing. So the unit of work is the task, one folder with a handover file, and anything that matters is written into files (the requirement, the plan, the to-do list), since what was said only in an old chat does not come along. Big work is split into steps small enough to accept one by one.

In the harness: a task is a folder under `.workspace/sandbox/tasks/` with `TASK.md`, `REQ.md`, `PLAN.md` and a state file that harness code writes, and any later chat picks the task up by name and reads `TASK.md` first, while Copilot compacts a chat at about 80% of its window {src:.harness/engine/core/tasks.py#L1-L37} {src:.harness/engine/modules/task/tasklife.py#L155-L160} {src:.harness/policies/task.json#L3}; see the file 11 Task.

Learn more: The book · 5.1 Manage tasks, not chats — https://smarshu.com/book/read/5-1-tasks.html ; The book · 3.2 Long chats get worse — https://smarshu.com/book/read/3-2-long-sessions.html ; The book · 5.8 Long work across sessions — https://smarshu.com/book/read/5-8-long-work.html

## Ideas: the requirement before the plan

The idea: requests are vague, leave things out and shift over time. If the agent starts from the first message, every guess it makes is built into the result and found only at the end. So for anything bigger than a small change, the agent writes the requirement on one page, with a list of what is not clear yet, the person confirms it, and from then on everyone works from that page.

In the harness: the agent writes `REQ.md` and the person confirms it with a code, the plan approval checks that confirmation, and a later change to what `REQ.md` asks undoes the plan's approval, although the confirmation is a line of text the agent's tools can write {src:.harness/engine/modules/task/task.py#L443-L451} {src:.harness/engine/core/tasks.py#L152-L164} {src:.harness/engine/modules/task/taskreview.py#L88-L110}; see the file 13 Requirement and intake.

Learn more: The book · 5.2 The agent writes the requirement, the person confirms it — https://smarshu.com/book/read/5-2-requirements.html

## Ideas: two gates where a person approves

The idea: a person is put where a step costs money, grants power or cannot be undone, and nowhere else, since with too many gates people stop reading. The approval must come through a channel the agent cannot reach, because a confirmation box can be switched off for a session and an approval the agent can give itself is no approval. It must also be bound to exactly the content the person read; that stops a swap, not a careless yes.

In the harness: approving `PLAN.md` opens `DEV/`, and approving the write-back covers the exact digest of the files and base commits; each needs the person at their own terminal or the paired board and a code made from a sha256 of what is approved, and the gate refuses these commands to the agent {src:.harness/engine/core/approval.py#L1-L8} {src:.harness/engine/modules/task/task.py#L941-L944} {src:.harness/policies/gate.json#L131-L137}; see the file 14 Plans and approvals.

Learn more: The book · 5.3 Two gates: where a person approves — https://smarshu.com/book/read/5-3-two-approvals.html

## Ideas: self-checks, and checks that count

The idea: an agent stops when its work looks done, so it needs a check it can run and read inside the loop, such as tests, a build or a linter. For anyone else, "I had it checked" proves nothing: a pass counts only when code keeps the record and counts it, on the version that ships. A second model as checker catches some errors but shares blind spots with the author; hiding the author's reasoning and asking a narrow question help, by an amount that has to be measured, so a pass means "a second reader found nothing", not "it is correct".

In the harness: the skill's text asks a development task for a record of self-testing, and the independent check is a separate `reviewer` subagent that sees only the requirement, the work and the diff, while code counts, in a task whose checks the person switched on, n passes in a row by new reviewers on the result as it is now, drops a finding with no real `file:line`, and refuses the write-back's dry run without the passes unless the person waives them {src:.github/skills/harness-my-task/SKILL.md#L47} {src:.github/agents/reviewer.agent.md#L1-L12} {src:.harness/engine/modules/task/taskreview.py#L1-L22} {src:.harness/engine/modules/task/reviewcheck.py#L1-L9}; see the file 17 Independent checks.

Learn more: The book · 5.4 Let the agent check its own work — https://smarshu.com/book/read/5-4-self-checks.html ; The book · 5.5 Make a pass count — https://smarshu.com/book/read/5-5-counted-checks.html ; The book · 5.6 Can a model check a model? — https://smarshu.com/book/read/5-6-model-checks-model.html

## Ideas: another agent only when it buys something, and why role teams were cut

The idea: dividing work among agents has no value in itself, and every subagent starts with an empty context and adds usage. Another agent is worth it only for one of four things: an independent check, parallel reading, work that runs unattended, or a hard limit on its tools. A team of job-title agents, by contrast, cost about 4.5 times the usage and 6 times the time of one agent for the same result in the book's small test (four tasks, one run each), so it was cut; every part is asked what it bought and what would make it safe to remove.

In the harness: three subagents remain, each for one of the four (the `reviewer` for the independent check, the read-only `mapper` for parallel reading once the person starts it, the `worker` for autorun), the task hook refuses any other, and the three-role flow and the Levels of 1.0 were removed in 1.1.0 {src:.harness/engine/modules/task/handler.py#L278-L300} {src:docs/05-design.md#L57-L63} {src:docs/07-release-notes.md#L3601-L3602}; see the files 17 Independent checks and 20 Autorun.

Learn more: The book · 2.3 Use subagents sparingly — https://smarshu.com/book/read/2-3-subagents.html ; The book · 7.3 What I cut, and what the data says — https://smarshu.com/book/read/7-3-what-we-cut.html

## Ideas: unattended work needs stop rules set in advance

The idea: once the person leaves, they are no longer the stop rule, and a run can loop for hours, spend a night's usage on a step that cannot succeed, or stop early and say it is finished. So the stop rules are set before the run, as a total budget and not only a step count, every stop hands back a reason, and "done" is decided from facts, not from the agent's word.

In the harness: code decides autorun's stops from facts, without asking a model: the run is done only when no step is open, the questions are answered, the checks passed and the write-back plan is made, and it stops at the spend limit the person picked, the step or time limit, a stall or a changed plan, as well as when the agent says going on would do harm or the person turns it off (chapter 5.7 describes an earlier version with no total budget; the spend limit came in 1.8.0) {src:.harness/engine/modules/task/autorun.py#L1-L23} {src:.harness/engine/modules/task/autorun_spend.py#L1-L5}; outside autorun a task has no total budget, see the files 20 Autorun and 22 Cost and usage.

Learn more: The book · 5.7 Unattended: when it must stop — https://smarshu.com/book/read/5-7-when-to-stop.html

## Ideas: who decides: code, a cheap model, the main model, a person

The idea: each judgment goes to the cheapest level that can make it well: code first, then a cheap model, then the main model, then a person. What has one right answer belongs in code, which is faster, gives the same answer every time and spends no tokens. Giving everything to the main model wastes usage and gives different answers on different days; pushing judgment into code fails the other way, with full confidence on the first case nobody foresaw. A person keeps what cannot be taken back.

In the harness: document conversion runs with no AI, the knowledge base's form and staleness are checked by script, costs are computed from the record and never estimated by a model, and autorun's stops are decided from facts {src:.harness/engine/modules/task/intakeconvert.py#L1-L5} {src:.harness/engine/core/kbstd.py#L1-L12} {src:.harness/engine/modules/task/perfreview.py#L1-L14} {src:.harness/engine/modules/task/autorun.py#L1-L23}; see the file 22 Cost and usage. Code also keeps the main model's context small: on each prompt the hook works out where the task stands and gives the agent a few lines (stage and next step, checks, autorun), not all the rules again, because context is a budget {src:.harness/engine/modules/task/handler.py#L93-L126}.

Learn more: The book · 5.9 Who decides: code, a cheap model, the main model, a person — https://smarshu.com/book/read/5-9-who-decides.html

## Ideas: record what happened, not what the agent said

The idea: an agent's summary of its own work can be wrong, or leave out what cost the most; a record written by code can be checked. So every call and every refusal is logged, one line each, and when something fails the trace is read rather than the story. A log is not a report, because nobody reads thousands of lines: every finished task also needs one page a person can read in five minutes, built from that record.

In the harness: the observe module writes one line per tool call to the session log with the final decision and its time, keeping no tool arguments beyond a few named exceptions such as a refused or held call, and the task's report page shows time, usage, failures and refusals worked out by code from that log and Copilot's own session record {src:.harness/engine/core/callrecord.py#L1-L10} {src:.harness/engine/modules/task/perfreview.py#L1-L14}; see the file 22 Cost and usage.

Learn more: The book · 6.1 Record what happened, not what the agent said — https://smarshu.com/book/read/6-1-observe.html ; The book · 6.2 A report a person can read in five minutes — https://smarshu.com/book/read/6-2-task-report.html

## Ideas: cost is what it takes to finish a task, not the price of a token

The idea: a model is chosen by what it costs to finish a task, not by the price of a token. On a long agent task most of the money goes to what the model rereads, so reading less and redoing less save the most, and caching helps only while the start of the input stays the same. When results are poor, the cheap fixes come first (a missing rule, a missing check, a lost thread), and only then a bigger model.

In the harness: each task has its own model, which the person picks, and the board splits each task's Credits and time by prompt and stage from Copilot's record, with a warning tag when a task spends a set multiple of the median of closed tasks of its kind {src:.harness/engine/modules/task/boardserve.py#L1565-L1590} {src:.harness/engine/modules/task/health.py#L141-L157}; see the file 22 Cost and usage.

Learn more: The book · 1.1 Don't pick a model by token price alone — https://smarshu.com/book/read/1-1-models-and-cost.html

## Ideas: a knowledge base is an honest index of the code

The idea: the code is the truth, and a knowledge base is an index and summary of it, worth having only while it is cheaper to read than the code and gives a better answer. It aims to be honest rather than complete: each card says which version of its source it read, and each gap is written where the next reader will see it. Which objects exist and who uses whom has one right answer, so scripts compute that map, and its accuracy is measured against a blind reading instead of trusted.

In the harness: a read log keeps which knowledge base files each task read, so `harness kb reads` shows what nobody reads {src:.harness/engine/core/kbreads.py#L1-L9}; the knowledge base instructions say a page that is no longer cheaper than the code is the problem, a fixed form lets scripts check the base, each object keeps the git blob of its source so `kb stale` asks git what changed, and `kb audit` measures the map's recall and precision against blind readings {src:.github/instructions/knowledgebase.instructions.md#L8} {src:.harness/engine/core/kbstd.py#L1-L12} {src:.harness/engine/core/kbaudit.py#L1-L9}; see the file 18 Knowledge base.

Learn more: The book · 8.1 A knowledge base: an honest index of the code — https://smarshu.com/book/read/8-1-why-a-knowledge-base.html ; The book · 8.2 The toolkit: scripts that draw a map of the code — https://smarshu.com/book/read/8-2-kb-toolkit.html ; The book · 8.3 Is the map right? A blind audit — https://smarshu.com/book/read/8-3-kb-audit.html
