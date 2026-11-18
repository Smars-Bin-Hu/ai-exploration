---
title: Autorun
subject: Autorun
layer: concept
file: 20 Autorun
harness_tag: 1.8.3
course: The book · 5.7 Unattended: when it must stop | https://smarshu.com/book/read/5-7-when-to-stop.html
course: The book · 5.8 Long work across sessions | https://smarshu.com/book/read/5-8-long-work.html
course: The book · 2.3 Use subagents sparingly | https://smarshu.com/book/read/2-3-subagents.html
---
## Autorun: what it is and what problem it solves

Autorun (beta; this design since 1.8.0) is a mode of a task in which the agent works down the steps of `TODO.md` without a person watching each step. The task's default agent only schedules: for each open step it calls the `worker` subagent, which does that one step in a fresh context and hands back one line. Code, not a model, decides when the run stops. Nothing is written back on the way: the run ends with the write-back plan, which still needs the person {src:.harness/engine/modules/task/autorun.py#L1-L23} {src:.github/agents/worker.agent.md#L1-L50}.

It solves the long, settled part of a task: after the plan is approved, a person saying "go on" after each step, or one chat filling with every step's details, is the bottleneck. Autorun moves each step out of the main chat, parks what needs the person, and brings the person back once for the questions and once for one diff. Three layers keep a run going: the scheduler's loop, the Stop hook, and the board relay {src:docs/05-design.md#L116-L117}.

## Autorun: how a run works, step by step

![Autorun: the person starts it, the task's chat calls the worker step by step, hooks check each call and push the chat on, and the served board wakes and compacts the chat](fig/autorun.svg)

1. **Ready.** The plan is approved, `TODO.md` has open steps (`- [ ] <text>`, optionally ending in `(model: <id>)`, the worker's model for that step), and independent checks are on {src:.harness/engine/modules/task/autorun.py#L125-L257} {src:.github/instructions/workspace.instructions.md#L17-L19}.
2. **Switched on by the person** (next section): code writes `.task/autorun.json` and the `autorun` state in `.task/task.json`, which a later session continues. From the board, Start then sets Allow all, sends `/compact` if the chat has history, and sends `/harness-autorun` with the scheduler model; if the first turn ran on another model, the card warns `model-not-switched` and the run goes on {src:.harness/engine/modules/task/autorun_start.py#L1-L10}.
3. **Scheduling loop**, told by the skill `harness-autorun`: take the first open step (not `[x]`, not `[?]`), call `worker` with the step and the task path, read its line, tick the step, update `TASK.md`, add one `LOG.md` line, go on. A failed call is tried once more, then parked {src:.github/skills/harness-autorun/SKILL.md#L1-L98}.
4. **Checkpoint at every worker call.** The task hook refuses the call when autorun is off; ends the run when a stop fact holds; says "end this turn" when a pit stop waits; refuses a model the person did not allow; and says "park this step" when the last calls moved nothing. A call let through is counted and opens a ledger line {src:.harness/engine/modules/task/autorun.py#L310-L450} {src:.harness/engine/modules/task/handler.py#L278-L337}.
5. **The worker** reads `TASK.md` and the section of `PLAN.md` its step names, does only that step, runs the check the step's procedure names, and answers `DONE: <what> | files: <paths> | check: <result>`, plus `QUESTION: <question> | took: <the way it chose, or none>` when something is open {src:.github/agents/worker.agent.md#L1-L50}.
6. **End of the list.** Code tells the agent what comes next, in this order: an open step; all open questions in one ask; parked steps whose questions are answered, turned back to `[ ]`; the independent check until it passes; `task promote --dry-run`. When none is left, the run ends with `done` {src:.harness/engine/modules/task/autorun.py#L310-L450}.


## Autorun: who can start it, and how

Only a person switches autorun on, with a typed code. The gate refuses `task autorun on` on the agent's command line, and the command needs a person at their own terminal or the board's paired browser {src:.harness/policies/gate.json#L131-L137} {src:.harness/engine/modules/task/autorun.py#L125-L257}. It is refused without an approved, unchanged plan, without an open step, with independent checks off ("with nobody watching there must be a reviewer"), in a round already written back, and (without `--force`) while the agent is mid-turn. The code stands for the task, round, plan digest and every step's text, checked again under the task's lock {src:.harness/engine/modules/task/autorun.py#L125-L257}.

**On the board: Start** on the task page (paired browser, board linked to the task's chat). The form offers:

- the **scheduler model**: Claude models the host offers only, a Claude Haiku first, with low thinking; the server refuses any other model whatever the page sends;
- the **worker model**: by default the model the steps name most often, else a Claude Sonnet; allowed are this default plus every `(model: x)` in the steps;
- the **compact percent** (0–95, 0 never, default 70) and the **minutes** (up to 7 days, default 480);
- the **spend limit**: none, the recommended Credits, twice or four times that {src:.harness/engine/modules/task/autorun_board.py#L23-L204}.

Then the person types the code and the board runs the Start order; a failure to set Allow all shows `allow-all-not-set` on the run card {src:.harness/engine/modules/task/boardserve.py#L1375-L1432}. The **Approve plan** window's box "I will switch autorun on next: do not wake the agent" keeps the approval from starting a turn first (see the file 14 Plans and approvals).

**In a terminal: `harness task autorun on`.** It shows the steps, limits and scope, asks only the spend limit as a number (Enter picks the recommended one) and the code; minutes and compact percent come from the policy, and no model is set. The person then does the Start by hand: `/compact` if needed, a Claude model, Allow all, `/harness-autorun` {src:.harness/engine/core/messages.en.json#L133-L195}. The recommended limit is 500 Credits for up to 20 steps, 1,000 up to 60, 2,000 above; the code marks it as to be tuned with real runs {src:.harness/engine/modules/task/autorun.py#L86-L198}.

## Autorun: parked steps, QUESTIONS.md and held calls

A step that cannot be settled is parked, not a reason to stop. The scheduler marks it `[?]` and writes `- [ ] Q<n> (step <N>) <question> | took: <way taken, or none>` into `QUESTIONS.md`; `took: none` parks the step, any other `took` lets it be ticked and keeps the question for the end {src:.github/instructions/workspace.instructions.md#L17-L19} {src:.harness/engine/core/autorunfiles.py#L15-L76}.

Nobody is asked during the steps: the task hook refuses the question tool (`ask_user`) to the scheduler while a step is open, and always to the worker; this never stops the run {src:.harness/engine/modules/task/handler.py#L550-L613}.

**Held calls.** When the gate refuses a worker's call or sends it to a confirmation, the gate itself adds `[held: <tool>] <command> | took: held` to `QUESTIONS.md`; a held line does not park the step, since the worker may have finished it another way. Scope mistakes (the write split, a write outside the folder) are only counted {src:.harness/engine/modules/gate/handler.py#L722-L755}. In a run a subagent may make only the outside calls the policy lets pass with no approval, and a call that would wait for a person is refused to the scheduler too {src:.harness/engine/modules/gate/handler.py#L273-L283} {src:.harness/engine/modules/gate/handler.py#L405-L415}. Answering a held line runs nothing; an outside write needs its usual approval after the run (see the file 19 Tool packs, connections and MCP).

**Asked once, at the end, before the independent check.** With no open step left, the agent is told to ask all open questions in one ask (at most 20 at a time), held lines included, write the answers, turn answered `[?]` back to `[ ]` and do those steps; only then the check. The person's answering time, up to 24 hours, is added to the run's end time {src:.harness/engine/modules/task/autorun.py#L310-L450} {src:.harness/engine/modules/task/autorun.py#L463-L554}.

## Autorun: the board relay and the pit stop

The board relay wakes the task's chat when it stopped while autorun is on. It exists only in a served board (`task board --serve`) linked to VS Code, for a task whose chat is bound; it looks at each such chat about once a second {src:.harness/engine/modules/task/autorun_relay.py#L1-L14}:

- **busy:** nothing, unless the context reached the compact percent (pit stop, below); **waiting for a confirmation:** nothing (a worker's confirmation can be approved on the board);
- **last turn cancelled** in VS Code: the run ends with `person`;
- **last turn complete:** after 15 seconds, the fixed text "Autorun is on. Go on with <task>/TODO.md." with the chat's model, never read from a file; it counts toward `steps`;
- **last turn in error:** wait 60, 300, then 900 seconds; 3 errors in a row end the run with `error`; progress resets the count.

**Pit stop.** When the chat is busy and its context reaches the compact percent, the board marks a pit stop; the next worker call is refused with "End this turn now"; the Stop hook lets the turn end without counting a stall; the board sends `/compact` (waiting 5 minutes at most), counts the pit stop and relays. A mark older than 10 minutes is dropped. `/compact` runs only between turns, which the loop seldom ends; Copilot's own compaction at about 80% stays {src:.harness/engine/modules/task/autorun_relay.py#L1-L14} {src:.harness/policies/task.json#L32-L39}.

**Stop hook cap and no board.** The Stop hook blocks an early stop at most 8 times in a row (`stop_cap`); then the stop goes through, the run stays on, and the board relays {src:.harness/engine/modules/task/autorun.py#L310-L450}. With no board there is no Start order, relay or pit stop, and a cancel in VS Code is not read as a stop; the loop, the Stop hook and the spend limit still work, and a chat that stopped waits, run still on, for a message from the person {src:docs/07-release-notes.md#L58-L88}.

## Autorun: every stop reason

A run ends on a fact read by code; the reason, detail and time are kept in the task's `autorun.stopped` and history, and the board shows "autorun stopped" until someone answers, except after `person` {src:.harness/engine/modules/task/autorun.py#L1-L23}.

- **`done`**: no open step, question or parked step; the check passed or was waived; the write-back plan is made, or nothing goes back.
- **`plan`**: `PLAN.md`, or the requirement it was approved for, is no longer what the person approved.
- **`review`**: the independent checks are used up without the passes, and none is waiting.
- **`handoff`**: the agent handed the person a run outside the harness (`task handoff run`).
- **`stalled`**: 3 (`max_stalls`) stops in a row of the scheduler with nothing moved (no step ticked or parked, no check, no write-back change); a parked step counts as progress. Worker calls with nothing moved are only refused ("park this step"), not a stop.
- **`time`**: past the end time (start plus the minutes, plus the time spent answering).
- **`steps`**: Stop hook pushes plus board relays reached max(20, `steps_per_todo` × steps in `TODO.md`). Worker calls do not count.
- **`budget`**: Credits spent since the start reached the spend limit.
- **`error`**: the board failed to wake the chat 3 times in a row, or its Start order failed (no `/compact` end in time, chat stayed busy, send failed) {src:.harness/engine/modules/task/autorun_start.py#L1-L10}.
- **`person`**: `task autorun off` in the person's terminal, **Stop** on the run card (which also stops the chat's turn), or a cancel in VS Code seen by the board {src:.harness/engine/modules/task/boardserve.py#L1375-L1432}.
- **`agent`**: the agent ran `task autorun off --reason "<why>"`; the reason is required, and the skill allows it only when going on would do harm {src:.github/skills/harness-autorun/SKILL.md#L1-L98}.

`plan`, `time`, `handoff`, `budget` and `review` are checked at every worker call, stop and relay; `steps`, `stalled` and `done` at stops and relays {src:.harness/engine/modules/task/autorun.py#L310-L450}. A gate refusal no longer stops a run.

**The run ends before the write-back.** The agent is told not to promote; it runs `task promote --dry-run`, links `PROMOTE-PLAN.diff` and stops. The write-back needs the person's `task approve-promote` with a code, which the gate refuses to the agent (see the file 16 Write-back) {src:.harness/policies/gate.json#L131-L137}.

## Autorun: the spend limit and the settings

The spend limit is the Credits a run may add to what the task's session had spent at the start, picked at every start (or none) and kept in `.task/autorun.json`, which the agent's edit tools cannot write {src:.harness/engine/modules/task/autorun.py#L86-L198}. Hooks read the spend from Copilot's record of the session holding the task, every usage record counted, the worker's and reviewer's included {src:.harness/engine/modules/task/autorun_spend.py#L1-L5}; so the limit holds without a board. When the spend cannot be read (no session, record missing) the limit does not stop the run, and the status and run card say so {src:.harness/engine/core/messages.en.json#L133-L195}.

The policy `.harness/policies/task.json` holds, under `autorun`: `minutes` 480, `max_stalls` 3, `steps_per_todo` 3, `stop_cap` 8, `compact_percent` 70, and `relay` (`grace_seconds` 15, `backoff` [60, 300, 900], `max_errors` 3); a value that is not a number falls back to its default {src:.harness/policies/task.json#L32-L39}. Per run, `.task/autorun.json` holds the scheduler model, the worker's default and allowed models, the compact percent, the minutes and the spend limit; a missing or broken file means no spend limit, no worker model list and no pit stop {src:.harness/engine/modules/task/autorun.py#L86-L198}.

## Autorun: the gate's write split

While autorun is on, the gate fixes who writes what in the task folder, for the VS Code edit tools. The scheduler may write only `TODO.md`, `TASK.md`, `LOG.md` and `QUESTIONS.md` at the folder's root; the worker anything else the usual rules allow (`DEV/` only with the plan approved; never `REQ/`, `REF/`, `INBOX/`, `.task/` or a target repository), but not those four. The gate tells them apart by whether the session is a subagent's {src:.harness/engine/modules/gate/handler.py#L64-L109}. A refusal here parks the step. Terminal commands are outside the split: the worker is told by text not to write from the terminal, and the ledger compares the files before and after each call {src:.github/agents/worker.agent.md#L1-L50}. More in the file 15 The gate and guardrails.

## Autorun: the run ledger and the run card

The run ledger `.task/autorun-run.jsonl` is written by hooks, not by the agent. Each worker call gets a start line (call, time, step number and text, model) and an end line (time; result `done`, `parked` for `took: none`, or `failed`; the worker's Credits, marked approximate when unsure; files changed; calls refused and held). A failed write of a line never stops a run {src:.harness/engine/modules/task/autorun.py#L463-L554}. `LOG.md` is the agent's own account, not the record.

The run card on the task page (paired browser; while on and a day after) shows steps done, parked and left, spend of the limit, time left, pushes, relays, pit stops, warnings, open questions, the stop reason, and one row per worker call. A row opens Trace at that call; **Stop** is on the card {src:.harness/engine/modules/task/autorun_board.py#L23-L204}. In a terminal: `harness task autorun status`.

## Autorun: what is enforced by code, and what is only an instruction

Enforced by code: switching on (person, code, preconditions); when the worker may be called and with which model; the write split; the refused question tool and outside calls; the held lines; every stop reason, the spend reading, relay, pit stop and ledger; no write-back without the person {src:.harness/engine/modules/task/handler.py#L278-L337} {src:.harness/engine/modules/gate/handler.py#L64-L109}.

Only an instruction (the skill `harness-autorun`, `AGENTS.md`, `worker.agent.md`): one worker call per step, in order; tick only finished steps; a `LOG.md` line per step; retry once; park on `took: none`; never fix a finding itself; switch off only on harm; the worker does one step, writes nothing from the terminal, runs its check, decides no trade-off {src:.github/skills/harness-autorun/SKILL.md#L1-L98} {src:AGENTS.md#L54}. Code does not check that a ticked step was done; the reviewer and the person do.

Who decides: the **person** starts it, picks models, minutes, compact percent and spend limit, stops it, answers, approves the write-back; **code** decides when it stops, which calls and writes go, and when the board wakes or compacts the chat; the **scheduler** only judges done or parked, and harm; the **worker** how to do its step, reporting any safe way it chose in `took`.

## Autorun: why it is built this way, and what it replaced

**The old autorun (1.3.0 to 1.7.46)**: the default agent did every step in its own chat, pushed on by the Stop hook each time it stopped; it stopped after 2 gate refusals (`max_denies`, reason `denied`), 20 pushes, 120 minutes, or when the agent said it could not go on {src:docs/07-release-notes.md#L3495-L3507}. 1.8.0 retired it with `max_denies` and `denied` {src:docs/07-release-notes.md#L58-L88}. Why, from the design notes: a long list meant many pushes of one chat, and Copilot drops a Stop hook's blocks after a few in a row; every step's details filled that chat; a question or a refusal ended the run, so the person came back to a half-done list. Now steps run as worker calls inside one scheduler turn, and the Stop hook and relay are fallbacks.

- **One mode, hard rules**: with one kind of autorun the split can sit in the gate: the scheduler cannot do the work, the worker cannot tick its own step {src:.harness/engine/modules/gate/handler.py#L64-L109}.
- **Park, ask once**: a question mid-run stalls a run nobody watches, and a model told "the user is away" guesses and loses it; refusing the question tool makes the agent write it down, answered before the check so the check sees the final work.
- **Not Copilot's Autopilot**, whose "done" is the model's word: autorun ends on facts {src:docs/02-features.md#L131-L150}.
- **Cheap scheduler, capable worker, Claude only**: the scheduler only schedules, so a small model does; the cheapest model costs more in rework than it saves, so the worker is a Sonnet by default. With a GPT model picked by Copilot, the Claude worker got tool names that did not exist and could not write files {src:.harness/engine/modules/task/autorun_board.py#L23-L204}.
- **Ledger by code**: `LOG.md` is the agent's, so it cannot be the audit record. Inside the loop there is no stop, so plan, time and spend are checked at every worker call.

## Autorun: where in the source

Under `.harness/engine/` {src:.harness/engine/modules/task/autorun.py#L1-L23}: `modules/task/autorun.py` (on, off, stop facts, Stop push, worker checkpoint, ledger); `core/autorunfiles.py` (`TODO.md`, `QUESTIONS.md`, ledger file); `modules/task/autorun_relay.py`, `autorun_start.py`, `autorun_board.py`, `autorun_spend.py` (relay and pit stop, Start order, form and card, spend); `modules/task/handler.py` and `modules/gate/handler.py` (hooks, write split). Also `.github/agents/worker.agent.md`, `.github/skills/harness-autorun/`, tests `.harness/tests/test_autorun*.py`.

## Autorun: common questions

**Q: Can a task run on its own overnight?** Yes, if the board is served (`harness task board --serve`) and linked to VS Code, so it can wake the chat when it stops; within the minutes (480 by default), the spend limit and the caps on pushes and stalls; it stops at the write-back plan. Without the served board, a chat that stops after 8 Stop-hook blocks or on an error waits, run still on, for the person's message {src:.harness/engine/modules/task/autorun.py#L310-L450} {src:.harness/engine/modules/task/autorun_relay.py#L1-L14}.

**Q: Can the agent switch autorun on, or write back by itself?** No: the gate refuses `task autorun on` and `task approve-promote` on its command line, and both need a typed code. The agent may only switch it off, with a reason {src:.harness/policies/gate.json#L131-L137}.

**Q: Does autorun skip the gate?** No: every gate rule holds, autorun adds the write split and refuses outside calls needing a person; Allow all only removes Copilot's boxes {src:.harness/engine/modules/gate/handler.py#L405-L415}.

**Q: How is the cost capped?** By the spend limit picked at each start; the run stops with `budget` when reached, unless the spend cannot be read {src:.harness/engine/modules/task/autorun.py#L86-L198}.

## Autorun: limits

- **Beta**: whether it beats a person watching to the end has not been evaluated {src:docs/02-features.md#L131-L150}.
- **Allow all is set for the run**: Copilot's confirmation for the gate's ask list does not show, and a call the gate sends there is listed as held though it ran {src:.harness/engine/modules/task/autorun_start.py#L1-L10}.
- **Claude-only scheduler**: the board refuses another model; the terminal only warns, and a chat on another model leaves the worker unable to write files. If the host keeps another model after Start, the card only warns {src:.harness/engine/modules/task/autorun_board.py#L23-L204}.
- **The spend limit is checked between calls** (a call under way can pass it) and does nothing when the record cannot be read {src:.harness/engine/modules/task/autorun_spend.py#L1-L5}.
- **The write split covers edit tools only**: a terminal write by the scheduler into `DEV/` is not refused by it; and every subagent of the chat, the reviewer too, falls under the worker's rule {src:.harness/engine/modules/gate/handler.py#L64-L109}.
- **A tick is the scheduler's word**: code does not check the work; the ledger's result is the worker's own reply {src:.harness/engine/core/autorunfiles.py#L15-L76}.
- **A Start order lives in the board's memory**: after a board restart the relay wakes the run with the chat's current model {src:.harness/engine/modules/task/autorun_relay.py#L1-L14}.
- **Some words lag behind 1.8.0**: the board's text for `agent` says "the agent said it cannot go on"; the gate's refusal of the scheduler's own outside call tells it to switch autorun off and stop, while the skill says park; the reference says the terminal asks for models and that `max_stalls` counts worker calls {src:.harness/engine/core/messages.en.json#L456} {src:docs/04-reference.md#L100-L225}.

## Autorun: related files

Files 11 Task, 14 Plans and approvals, 15 The gate and guardrails, 16 Write-back, 17 Independent checks, 19 Tool packs, connections and MCP (held calls), 21 Super agent, 22 Cost and usage. How-to: no harness tutorial in `3 Courses/Harness tutorials/` covers autorun yet; "1 A day with the harness" shows the task page it starts from. The autorun rules for the agent are in `AGENTS.md` {src:AGENTS.md#L54}.
