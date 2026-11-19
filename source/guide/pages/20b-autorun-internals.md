---
title: Autorun internals
subject: Autorun internals
layer: reference
file: 20b Autorun internals
harness_tag: 1.8.3
course: The book · 5.7 Unattended: when it must stop | https://smarshu.com/book/read/5-7-when-to-stop.html
course: The book · 5.8 Long work across sessions | https://smarshu.com/book/read/5-8-long-work.html
course: The book · 2.3 Use subagents sparingly | https://smarshu.com/book/read/2-3-subagents.html
---
This file holds the code-level detail behind the feature file 20 Autorun: why autorun is a mode and not an agent, where the person-only switch is checked, how the scheduler and the worker are kept apart, the stop reasons in the order the code tests them, the Stop hook, the board relay with its pit stop, the Start order, the spend limit, the run ledger, and how autorun's stops differ from the runtime's "ask the user". It is for "how does it work" and "where in the code" questions. The code is in `.harness/engine/modules/task/` (`autorun.py`, `autorun_relay.py`, `autorun_start.py`, `autorun_board.py`, `autorun_spend.py`, `handler.py`, `vslink.py`), `.harness/engine/core/` (`autorunfiles.py`, `copilot_events.py`, `approval.py`) and `.harness/engine/modules/gate/handler.py`.

## Autorun internals: a mode of a task, not an agent

Autorun is state in the task, not an agent. The module's first lines say "It is a mode of a task, not an agent", and that its stop decisions are told from facts by code: "nothing here asks a model, and nothing uses the runtime's `ask`" {src:.harness/engine/modules/task/autorun.py#L1-L23}. The state is the `autorun` object of the task, so another session that picks the task up goes on with the same counts {src:.harness/engine/modules/task/autorun.py#L248-L254}.

The design rule is in the design notes, not in code: there is no dedicated dispatching agent, because the agent that holds the task is the one that moves it; a new agent must buy an independent point of view (the reviewer), parallel work (the mapper) or a fresh context per step (the worker). Only the worker passes that test, so the scheduler is the task's default agent with no agent file of its own; the `worker` file lists Claude Sonnet models and no nested agents {src:docs/05-design.md#L112-L117} {src:.github/agents/worker.agent.md#L1-L8}.

## Autorun internals: why only a person switches it on

Autorun is person-only because it hands over control and spends money while nobody watches, not only because nobody watches: the design notes say these features must be switched on by the user because they "cost money or hand over control" {src:docs/05-design.md#L118-L118}. The person alone also sets the spend limit {src:.harness/engine/modules/task/autorun.py#L152-L168}. Three locks hold, each in code and none depending on the others:

- **The gate rule** refuses `harness task autorun on` on the agent's command line {src:.harness/policies/gate.json#L131-L137}.
- **The command's own person check.** `turn_on` begins with `task_ops.person`, which calls `approval.require_person`: the command needs a terminal with a keyboard and a screen (stdin and stdout are a TTY) or the board's Terminal window, which the board vouches for with a one-time code; otherwise it raises `Refused`. This holds even if the gate rule were bypassed {src:.harness/engine/modules/task/autorun.py#L201-L206} {src:.harness/engine/core/approval.py#L28-L47}.
- **The typed code.** `task_ops.typed` asks for six capital letters taken from a sha256 over the task, the round, the plan digest and the text of every step (`code_source`); another answer raises `Refused`. The board path passes `interactive=True` and the code typed in its Start form, and works only from a paired browser {src:.harness/engine/modules/task/autorun.py#L143-L145} {src:.harness/engine/core/approval.py#L50-L58} {src:.harness/engine/modules/task/boardserve.py#L1375-L1398}.

The skill `harness-autorun` carries `disable-model-invocation: true`, but that flag is only a request that the model not load the skill; what locks the switch is the code above {src:.github/skills/harness-autorun/SKILL.md#L5-L5} {src:.github/skills/harness-autorun/SKILL.md#L25-L25}. Anyone may switch autorun off: a person records `person`; otherwise `turn_off` needs a non-empty `--reason` and records `agent` {src:.harness/engine/modules/task/autorun.py#L269-L279}.

## Autorun internals: what `turn_on` checks and writes

`turn_on` runs in this order: the person check; `tasklife.require_idle` (refused while the agent is mid-turn unless `force`); `requirements`; the screen (the first 10 open steps, models, limits, scope); the spend limit; the typed code; then, inside the task's lock, `code_source` and `requirements` are compared again, and a difference is refused. Only then anything is written {src:.harness/engine/modules/task/autorun.py#L201-L257}. `requirements` lists up to five reasons for refusal: no `PLAN.md`; a plan not approved as it is now; no open step in `TODO.md`; independent checks off (`n < 1`); a round already written back (`promote.state` `done` or `partial`) {src:.harness/engine/modules/task/autorun.py#L125-L140}. A plan counts as approved only if its sha256 equals the stored `approved_sha256` and the `REQ.md` digest kept at approval still matches {src:.harness/engine/core/tasks.py#L152-L164}.

On success `turn_on` writes `.task/autorun.json` once (`manager_model`, `worker.default`, `worker.allowed`, `compact_percent`, `minutes`, `budget`) and the `autorun` state, with `until` = now plus the minutes and `max_steps` = max(20, `steps_per_todo` x the number of steps in `TODO.md`, ticked or not), fixed at that moment {src:.harness/engine/modules/task/autorun.py#L73-L74} {src:.harness/engine/modules/task/autorun.py#L182-L257}. `.task/**` is a gate-owned path: the agent's edit tools cannot write `autorun.json`, the ledger or the tally {src:.harness/policies/gate.json#L24-L26}. A missing or broken `autorun.json` reads as `{}`: no worker model list, no spend limit and no pit stop {src:.harness/engine/modules/task/autorun.py#L77-L83}.

The limits come from `autorun` in the policy `task.json` (values in the file 20 Autorun). A value that is not a number falls back to the default; a `backoff` list keeps only its integers and falls back to the default when none is left {src:.harness/engine/modules/task/autorun.py#L44-L70}.

## Autorun internals: scheduler and worker, who may do what

The split is enforced in three places in code and asked for in text in a fourth.

**Which subagents may be called.** The task hook decides every subagent call of the main agent: the mapper by its own rule, none in admin mode, none without an open task, the `worker` through `worker_call`, the `reviewer` only while a check round is open, any other name refused. So in autorun the scheduler can call only the worker and the reviewer {src:.harness/engine/modules/task/handler.py#L278-L300}.

**The worker is callable only while autorun is on.** `on_subagent_call` returns, when autorun is off, "Autorun is off for this task, so the worker is refused. Stop now. Do not park the other steps and do not call the worker again. Tell the user that autorun is off." The hook turns any returned text into a `deny` of kind `autorun-call`. It is not a gate refusal, is not parked as a held line and never ends a run {src:.harness/engine/modules/task/autorun.py#L415-L422} {src:.harness/engine/modules/task/handler.py#L316-L325} {src:.harness/engine/core/messages.en.json#L184-L194}.

**Five checks at every worker call**, under the task's lock, in this order; the first that fails returns its text {src:.harness/engine/modules/task/autorun.py#L415-L450}:

1. Autorun off: the text above.
2. A stop fact holds (`fact_reason`: plan, time, handoff, budget, review): the run is ended with that reason and the scheduler gets "The run is over. Stop now; the task says why."
3. A pit stop is set: "End this turn now. The run goes on after a short stop."
4. Model: a model not in `worker.allowed`, or no model when a default is set, is refused with the allowed list or the default named. With no worker list, no model is checked.
5. No progress: see the next section.

A call that passes is counted (`worker_calls` and `calls_since_tick` + 1) and opens a ledger line.

**The write split** (edit tools only). While autorun is on, `_autorun_write` lets the scheduler (a session with no `parent_session_id`) write only `TODO.md`, `TASK.md`, `LOG.md` and `QUESTIONS.md` at the task folder's root; anything else gets "Refused: in autorun you write only TODO.md, TASK.md, LOG.md and QUESTIONS.md of {task}. {shown} is for the worker: call it for this step." The worker (a session with a parent) may write what the usual task rules allow except those four, and gets "Refused: the worker does not write TODO.md, TASK.md, LOG.md or QUESTIONS.md ... The agent that called you keeps them." for them. Both have kind `autorun-write`, which is in `NOT_PARKED`: such a refusal is only counted in the call's tally (`denied`) and written to `QUESTIONS.md` as no held line. Every subagent of the chat, the reviewer too, counts as "worker" here {src:.harness/engine/modules/gate/handler.py#L64-L109} {src:.harness/engine/modules/gate/handler.py#L736-L755}.

**Text only.** That the scheduler runs only `harness task review start` and `harness task promote --dry-run`, one worker call per step in order, a tick only for finished steps and a `LOG.md` line per step are instructions of the skill; no autorun code limits the scheduler's terminal commands beyond the gate's ordinary rules {src:.github/skills/harness-autorun/SKILL.md#L50-L70}.

## Autorun internals: parked steps, questions and the no-progress refusal

A step is a `TODO.md` line `- [ ] text`, `- [x] text` or `- [?] text`, with an optional trailing `(model: x)`; `[?]` is parked (not done, not open). A question is a line `- [ ] Q<n> (step <N>) <text> | took: <way or none>` in `QUESTIONS.md`, closed with `[x]` and ` | answer: ...`; a text beginning `[held:` is a held line {src:.harness/engine/core/autorunfiles.py#L15-L76}.

`reply_result` reads a worker's reply: a line `QUESTION: <question> | took: <way>` where `took` is empty or begins with `none` as a word is `parked`; any other reply is `done`; a call the engine says ended in error (`error`, `aborted`, `cancelled`, `timeout` and similar) is `failed`. It goes into the ledger only; the `[?]` in `TODO.md` is written by the scheduler on the skill's text {src:.harness/engine/modules/task/autorun.py#L455-L505}.

**Held calls.** When the gate holds or refuses a worker call (any kind not in `NOT_PARKED`), `park_held_call` appends `- [ ] Q<n> (step <N>) [held: <tool>] <summary> | took: held` to `QUESTIONS.md` and counts it in the tally; the same call twice in a row is one line. `took: held` never parks a step, because the worker may have finished it another way {src:.harness/engine/core/autorunfiles.py#L141-L167}.

**The fourth call with no progress.** `progress` is the list [ticked steps, parked steps, checks used, passes, `promote.state`]. At each worker call that passes the first four checks, a list different from `tick_progress` stores the new list and resets `calls_since_tick` to 0; then, if `calls_since_tick` has reached `max_stalls` (3), the call is refused with "Nothing moved in the last worker calls. Mark this step `[?]` in {task}/TODO.md, write the question in QUESTIONS.md, and go on with the next step." So the fourth worker call in a row with nothing moved is the first refused. It is not a stop; the scheduler is told by text to park the step {src:.harness/engine/modules/task/autorun.py#L107-L110} {src:.harness/engine/modules/task/autorun.py#L440-L450}.

**The question tool.** In a task in autorun the task hook refuses `ask_user` always for a worker ("The worker does not ask the user. End your reply with one line: `QUESTION: ...`") and for the scheduler while `TODO.md` has an open step; it is not a gate refusal and never a reason to stop. With no open step left the call passes, and `add_wait` moves `until` out by the person's answering time (ignored above 24 hours) {src:.harness/engine/modules/task/handler.py#L550-L579} {src:.harness/engine/modules/task/autorun.py#L542-L554}.

## Autorun internals: the three layers read the same facts

The three layers are the scheduler calling the worker (a loop the skill tells, with a code checkpoint at each call), the Stop hook (`on_stop`) and the board relay (`autorun_relay.step`). They cannot disagree about stopping because they call the same functions: `fact_reason` (plan, time, handoff, budget, review), `stop_reason` (those plus steps and stalled), `next_text` (what is left; empty means `done`) and `progress`. Each reads the facts afresh from files, the plan digest, the check records and the events file {src:.harness/engine/modules/task/autorun.py#L310-L368}. Every prompt of a task in autorun also gets an injected line (`autorun.inject`: the push count and "you only call the worker for each open step ... Do not ask the user and do not promote"), added by `task_text` at session start and with every user prompt {src:.harness/engine/modules/task/handler.py#L123-L125} {src:.harness/engine/modules/task/handler.py#L162-L170}.

| Place | What it reads | What it can do |
| --- | --- | --- |
| Worker call | `fact_reason`: plan, time, handoff, budget, review | refuse the call; end the run with that reason; never `steps`, `stalled` or `done` |
| Stop hook | `stop_reason`: plan, time, handoff, budget, review, steps, stalled; then `next_text` | push on; end the run with the reason or `done`; let the stop through |
| Board relay | the same, when the chat is idle | send the relay text or `/compact`; end the run; start a pit stop |

## Autorun internals: the stop reasons, in the order the code tests them

`REASONS` holds eleven words: `done`, `plan`, `review`, `handoff`, `stalled`, `time`, `steps`, `budget`, `error`, `person`, `agent`. `stop_in` raises `ValueError` for any other word, then sets `state` `off` and `stopped = {why, detail, at}` and writes a note {src:.harness/engine/modules/task/autorun.py#L46-L46} {src:.harness/engine/modules/task/autorun.py#L260-L266}. `fact_reason` tests the first five facts and `stop_reason` the next two; the first that is true wins, so the order is **plan, time, handoff, budget, review, steps, stalled**, then `done` {src:.harness/engine/modules/task/autorun.py#L310-L344}. How each is computed:

- **`plan`**: `plan_approved` is false: the sha256 of `PLAN.md` differs from the approved one, or the requirement it was approved for is no longer the digest of `REQ.md`.
- **`time`**: now is later than `until` (start plus minutes, plus answering time), or `until` cannot be parsed.
- **`handoff`**: `data["handoff"]` is a dict with a non-empty `what`. The agent sets it with `task handoff`; the harness also sets it itself when `review start` is refused for a requirement item that needs a run outside the harness (`by: harness`) {src:.harness/engine/modules/task/tasklife.py#L498-L515} {src:.harness/engine/modules/task/taskreview.py#L338-L354}.
- **`budget`**: `autorun.json` has `budget.add_credits` as a number and `credits_spent` is readable and at least that. An unreadable spend never gives `budget`.
- **`review`**: `passed` is `passes >= n` or waived; `review` holds when not passed, no round is pending, and `checks_used >= checks_limit` {src:.harness/engine/modules/task/taskreview.py#L240-L257}.
- **`steps`**: `run.steps >= run.max_steps`. `steps` counts Stop-hook pushes and board relays, not worker calls.
- **`stalled`**: `run.stalls >= run.max_stalls`. Only the Stop hook moves `stalls`, so the run ends at the fourth identical Stop in a row: the first stores the progress list with 0, the next three make 1, 2 and 3.
- **`done`**: no fact holds and `next_text` is empty: no open step, no open question, no parked step, checks passed or waived, and, when `wants_promote` (a target repository with a file in `DEV/` outside `_manual/`, or deletes), `promote.state` is no longer `none` {src:.harness/engine/modules/task/autorun.py#L100-L104} {src:.harness/engine/modules/task/autorun.py#L351-L368}.
- **`error`**: written by the board only: `count_error` when `errors >= max_errors`, and `autorun_start.fail` when the Start order cannot be done.
- **`person`**: `turn_off` by a person (terminal, or **Stop** on the run card through `autorun_stop`), and the relay when the last turn was cancelled in VS Code {src:.harness/engine/modules/task/boardserve.py#L1418-L1432}.
- **`agent`**: `turn_off` without a person, with a reason.

`stop_in` is the only writer of `stopped`; each reason's words are `autorun.why.<reason>` {src:.harness/engine/core/messages.en.json#L157-L166}.

## Autorun internals: the Stop hook

The Stop hook (`handler.on_stop` calling `autorun.on_stop`) acts when the agent wants to end its turn while autorun is on. It does nothing for a subagent's session, in admin mode, or at the end of a question turn {src:.harness/engine/modules/task/handler.py#L599-L612}. Under the task's lock, in order {src:.harness/engine/modules/task/autorun.py#L385-L412}:

1. `in_row` (blocks in a row) goes to 0 when this Stop is not the answer to a block (`stop_hook_active` false).
2. If a pit stop is set: return at once, no stall counted, no fact read.
3. Count stalls: 0 when the stored `progress` list differs from the new one, else `stalls` + 1; store the list. The first Stop has none stored, so it counts 0.
4. `stop_reason`, then `next_text`. If a reason holds or nothing is left, `stop_in(reason or "done")` ends the run and the Stop goes through: the Stop hook ends the run here, it does not push.
5. If `in_row >= stop_cap` (8): set `relay_wanted` and let the Stop through; the run stays on and the board relays. With no board the chat waits, run on, for a person's message.
6. Otherwise `steps` + 1, `in_row` + 1, and the agent is blocked with "Autorun: going on, {step}/{limit}." plus the next-step text.

In steps 2 and 5 the task is marked waiting and the board wakes the agent {src:.harness/engine/modules/task/handler.py#L542-L547}.

## Autorun internals: the board relay

The relay (`autorun_relay.step`) runs on the board's link thread (`vslink._autorun`), about once a second (`RELAY_EVERY` 1.0 s) for each bound chat of a task whose autorun is on. It exists only in a served board linked to VS Code, and keeps away while the task's Start order is before its verify stage {src:.harness/engine/modules/task/vslink.py#L59-L60} {src:.harness/engine/modules/task/vslink.py#L740-L780}. `decide` never sleeps: each wait is a timestamp in the run state (`relay.next_at`, `pit.at`, `pit.sent`). It runs first on a copy; with no change and nothing to send the task lock is not taken; otherwise it runs again under the lock and the message is sent after the lock is released {src:.harness/engine/modules/task/autorun_relay.py#L217-L235}. In order {src:.harness/engine/modules/task/autorun_relay.py#L125-L190}:

1. A pit older than 600 s (`PIT_MAX`) is cleared: the whole mark's life.
2. **Chat busy:** a wait for a relay is dropped (`next_at` cleared: the grace is cancelled when the chat goes busy again, by a person's message or a Stop-hook push). If a `/compact` was sent, the pit is marked busy, and given back to the chat when `/compact` has run longer than 300 s (`COMPACT_WAIT`), without counting a pit. With no pit, `compact_percent` above 0 and the context percent at or above it, the pit is set. No stop fact is read.
3. **Waiting for the person** (`input`) or any other status: nothing.
4. **Idle, last turn cancelled** in VS Code (begun after the run): pit cleared, run ends with `person`.
5. **Pit sent:** wait unless the chat was seen busy or 10 s (`COMPACT_SETTLE`) have passed; then the pit ends, `pits` + 1, and `relay.pit_turn` is set to the last turn's id.
6. **Idle, last turn in error:** `count_error`, once per failed turn.
7. **Idle, last turn complete:** `errors` reset; with no pit and no wait set, `next_at` = now plus `grace_seconds` (15 s) and the pass ends.
8. When the wait is over (a pit skips it): stop facts are checked again (`stop_reason`, then `next_text` empty as `done`); a run that should end is ended instead, and the pit cleared.
9. With no pit and the percent at or above the limit, the pit is set now (the pit at an idle relay point).
10. Send: with a pit `/compact` with no model, else the relay text with the chat's model.

**Relay text and model.** The text is fixed in code: "Autorun is on. Go on with {task}/TODO.md." Nothing is read from a file. The model is `message.model` of the chat's newest message that names one, else the last turn's model, else none; nothing re-checks that it is a Claude model {src:.harness/engine/modules/task/autorun_relay.py#L63-L70} {src:.harness/engine/core/messages.en.json#L190-L190}. A sent relay counts in `steps` and `relay.count`, so relays and Stop-hook pushes share one budget, max(20, `steps_per_todo` x steps) {src:.harness/engine/modules/task/autorun_relay.py#L193-L214}.

**Refusals.** A relay the chat refuses (the chat changed, was not idle: an error carrying `why`) is not an error: `record` counts nothing and the thread holds that task for `RELAY_HOLD` (10 s) before trying again. A send error that is not such a refusal counts as an error in a row {src:.harness/engine/modules/task/vslink.py#L766-L780}.

**Backoff and errors.** `count_error` adds one to `errors` (after resetting it to 0 if the progress list changed since the previous error). The run ends with `error` (detail: the host's words from the turn's last error part, cut at 300 characters) when `errors >= max(1, max_errors)`; this is tested before the backoff list is read. Otherwise `next_at` = now plus `backoff[min(errors - 1, len(backoff) - 1)]`. With the defaults the waits are 60 s and then 300 s, and the third error ends the run; the 900 s entry is read only when `max_errors` is 4 or more {src:.harness/engine/modules/task/autorun_relay.py#L105-L122}.

**The pit stop.** While `run.pit` is set the next worker call is refused ("End this turn now") and the Stop hook lets the turn end with no stall. The pit is set when the context percent (`chatctx.meter`) reaches `compact_percent` of `autorun.json` (0 means never), while the chat is busy or at an idle relay point (step 9). A pit set while busy sends `/compact` at once when the chat goes idle, with no grace and no model; a pit set at an idle relay point comes after the grace and sends `/compact` instead of the relay text. After the pit ends, turns up to `relay.pit_turn` are not read for the percent (their usage is from before the compaction), so no second pit starts at once {src:.harness/engine/modules/task/autorun_relay.py#L73-L81}.

## Autorun internals: the Start order on the board

**Start** is offered by `taskboard.actions` only for an open task that is not in autorun and not paused, and is removed when no step is left or the plan is not approved; the board's served actions must include `autorun on` (the default list does) {src:.harness/engine/modules/task/taskboard.py#L121-L144} {src:.harness/engine/modules/task/taskboard.py#L263-L264}. `autorun_on` in `boardserve.py` draws the form on a preview call; on the act call it checks the body again and that the chat is linked, runs `turn_on` with the typed code and gives the order to the link thread {src:.harness/engine/modules/task/boardserve.py#L1375-L1416}. `autorun_start.step` then does one stage per look {src:.harness/engine/modules/task/autorun_start.py#L90-L152}:

1. **config:** set Allow all: only the host's `autoApprove` choice, never the chat mode. The board asks only when the host lists that choice or lists none; a host that lists choices without it makes Start skip the step silently. A failed send adds the warning `allow-all-not-set` and the order goes on {src:.harness/engine/modules/task/boardserve.py#L1391-L1397}. A chat with turns goes to `compact`, one with none straight to `send`.
2. **compact:** wait for an idle chat (at most 300 s), send `/compact` with no model, wait for it to end (at most 300 s). A timeout ends the run with `error`.
3. **send:** wait for an idle chat (300 s, else `error`), send `/harness-autorun` with the scheduler's `message.model`.
4. **verify:** find the first turn whose message is `/harness-autorun` and compare its `usage.model` with the chosen model; `same_model` accepts equality or either id beginning with the other, so a dated tag matches. A mismatch only adds the warning `model-not-switched` and the run goes on; with no model shown within 3600 s the order ends silently.

A host refusal (an error carrying `why`) in stages compact and send is retried at the next look; any other error ends the run with `error`. The relay and pit stop keep away while the order is before verify; **Stop** on the card cancels a pending order. The order lives in the link thread's memory: after a board restart nothing continues it, and the relay wakes a run that is on with the model of the chat's newest message {src:.harness/engine/modules/task/vslink.py#L649-L664} {src:.harness/engine/modules/task/vslink.py#L706-L738}.

## Autorun internals: the Start form and why the scheduler must be a Claude model

`autorun_board.form` offers as scheduler models only those whose id begins with `claude`, with a Claude Haiku first; the worker default is the model the steps name most often, else a Sonnet. The page disables the button when no Claude model is listed. The scheduler's message carries thinking level `low` and context size 100000 only when the model offers them {src:.harness/engine/modules/task/autorun_board.py#L23-L97}. The server checks again (`options_of`), whatever the page sent: a scheduler model the host does not list, or that is not Claude, is refused; the worker default must be one the host lists (any family); compact percent 0 to 95; minutes 1 to 10,080; the limit `null` or above 0 and at most 1,000,000. `turn_on` adds every `(model: x)` of the steps to `worker.allowed` {src:.harness/engine/modules/task/autorun_board.py#L100-L126} {src:.harness/engine/modules/task/autorun.py#L182-L198}.

**Why Claude, and what is not enforced.** The worker is a Claude agent that writes files with the tools `create` and `edit`; in a chat on a GPT model (Copilot Fusion may pick one) those tool names do not exist and the worker cannot write files. This reason is stated only in text (the board server's comment, its refusal, the skill); nothing tests the worker's tool set {src:.harness/engine/modules/task/autorun_board.py#L1-L8} {src:.github/skills/harness-autorun/SKILL.md#L40-L40}. In the terminal path no model is set; the screen says the chat must be a Claude model and the person does it by hand. After Start nothing re-checks the model: verify only warns, and the relay reuses the newest message's model.

## Autorun internals: the spend limit

The limit is read from Copilot's own record of the session that holds the task: `~/.copilot/session-state/<session id>/events.jsonl` (`COPILOT_HOME` moves the folder). `events_path` refuses a session id containing `/`, `\` or `..` and gives nothing when the file is missing or over 300 MB, so `credits_spent` is `None` {src:.harness/engine/core/copilot_events.py#L25-L59} {src:.harness/engine/modules/task/autorun_spend.py#L19-L24}. Every row of type `session.usage_record` counts: Credits = `data.usage.copilotUsage.totalNanoAiu` / 1e9 (a row without the number counts 0), the worker's and the reviewer's rows included {src:.harness/engine/core/copilot_events.py#L162-L166}.

**New bytes only.** The run keeps `cost = {session, pos, nano}`: the session read, the byte where the last read ended and the nano AIU counted so far. `lines_of` seeks to `pos`, reads, and takes only whole lines (to the last newline), so a half-written last line waits for the next read. Lines holding neither `session.` nor `subagent.` are skipped first, and a line that does not parse is skipped {src:.harness/engine/modules/task/autorun_spend.py#L42-L65}. Edge cases in `credits_spent`: at Start `fresh_cost` stores the file's size, so earlier spend is not counted (a run with no `cost` or an empty `session` takes it at the moment of reading); if the task's session id changed, the new file is read from byte 0 and the nano counted so far is kept; if the file is shorter than `pos`, reading restarts at 0 {src:.harness/engine/modules/task/autorun_spend.py#L27-L34} {src:.harness/engine/modules/task/autorun_spend.py#L68-L94}.

**Locking and checks.** `credits_spent` saves nothing itself; a hook calls it inside `task_ops.locked`, so the new `cost` is saved when the block ends, while `status` and the run card are read-only and read again from the stored byte {src:.harness/engine/modules/task/autorun.py#L113-L116} {src:.harness/engine/modules/task/autorun.py#L282-L288}. It is read in `fact_reason`: at every worker call (refused), every Stop-hook push, and in the relay before any relay text or `/compact`. A call under way can pass the limit. When the spend cannot be read (no session id, file missing or over 300 MB, I/O error) `budget` never fires and `status` adds a note when a limit is set; no board is needed {src:.harness/engine/modules/task/autorun.py#L322-L327} {src:.harness/engine/modules/task/autorun.py#L293-L294}.

**Stored value and recommended budget.** The limit is `add_credits` in `.task/autorun.json` (`base_credits` always 0.0), written once at Start; `null` means none. The choices are none, the recommended number, twice and four times it. `recommend_budget` gives 500 Credits for up to 20 steps, 1,000 up to 60, 2,000 above, counting every step in `TODO.md`; a code comment says "to be tuned with real runs". In the terminal Enter takes the recommended choice; the board's server accepts any number above 0 up to 1,000,000 {src:.harness/engine/modules/task/autorun.py#L86-L88} {src:.harness/engine/modules/task/autorun.py#L152-L179} {src:.harness/engine/modules/task/autorun_board.py#L120-L125}.

## Autorun internals: the run ledger and the run card

The run ledger `<task>/.task/autorun-run.jsonl` is append-only: one `start` line and one `end` line per worker call, written by hooks. It is a gate-owned path, so the agent cannot edit it, and a failed write never stops a run; `LOG.md` is the agent's own account, not the record {src:.harness/engine/core/autorunfiles.py#L79-L87} {src:.harness/policies/gate.json#L24-L26}.

- **Start line.** Written by the task hook on `PreToolUse` for a subagent only after the five checks pass, so a refused call leaves no line. Fields: `call` (the `worker_calls` number), `at`, `step` (the step whose first 60 characters occur in the worker prompt), `model`, `session`. The hook also writes `.task/autorun-call.json`, the tally of the running call (`files`, `denied`, `held`, a `before` hash of each result file, and `pos`, the events file's size) {src:.harness/engine/modules/task/autorun.py#L463-L476}.
- **End line.** Written by `SubagentStop` for the `worker` through `ledger_append` of `core.autorunfiles`, to the last start line that has no end: `result` (`done`, `parked`, `failed`), `files` (the paths the write hooks saw plus every result file changed since the start, which catches terminal writes), `denied`, `held`, and `credits`, the worker's usage rows in the events file between the start `pos` and now (`credits_between`; `approx` when a row's subagent start lies outside the range) {src:.harness/engine/modules/task/handler.py#L582-L596} {src:.harness/engine/modules/task/autorun.py#L497-L539} {src:.harness/engine/modules/task/autorun_spend.py#L106-L133}.

**The run card** (`autorun_board.card`, paired browser) takes steps from `TODO.md` and spend from the events file (after a stop, from `cost`), not from the ledger. Rows come from `pairs`: start and end lines paired by `call`, lines older than this run's `started_at` left out, a call with no end shown as `running`, the newest 300 rows and the first 20 files of each. The card shows while the run is on and for 24 hours after; a click on a row opens Trace from the call's start to its end, 1.5 s either side {src:.harness/engine/modules/task/autorun_board.py#L30-L31} {src:.harness/engine/modules/task/autorun_board.py#L140-L204} {src:.harness/engine/modules/task/web/desk.js#L2465-L2468}.

**A weak spot.** `turn_on` resets `worker_calls` to 0 and nothing ever rotates or deletes the ledger. A second run on the same task reuses call numbers, and `open_call` decides "ended" by call number alone: the new call 1 is taken as already ended by the old run's end line, gets no end line, and shows `running` {src:.harness/engine/modules/task/autorun.py#L249-L253} {src:.harness/engine/core/autorunfiles.py#L129-L134}.

## Autorun internals: how its stops differ from "ask the user" and from Autopilot

The code states that nothing in autorun uses the runtime's "ask" {src:.harness/engine/modules/task/autorun.py#L7-L8}. Its stops are the worker-call denials (autorun off, a fact ends the run, a pit, a model not allowed, no progress), the Stop hook's block or `stop_in` (cap 8 in a row), the question-tool denial and the write split, the board's relay and **Stop** button, and the person-only commands: each a hook decision or a state change, never a box that waits for a click. The repository docs say a hook refusal holds in every permission mode (default, Allow all, Autopilot), measured on 2026-10-10 for the gate; that autorun's hooks use the same refusal is an inference, not a separate measurement {src:docs/02-features.md#L54-L54}.

Copilot's Autopilot is described in the repository as "every tool call is agreed to automatically". The board does not offer it or Copilot's Plan; a chat set to either in VS Code shows **Back to Interactive** in its reply panel, and Start sets only Allow all, not the mode, so nothing switches an Autopilot chat back {src:docs/02-features.md#L150-L150} {src:docs/02-features.md#L296-L296} {src:.harness/engine/modules/task/boardserve.py#L1645-L1660}. What differs: autorun's end is told by code from facts; the relay wakes the agent when it stops; the limits (spend, minutes, steps, stalls, plan version) are chosen by a person; nothing is written back on the way, and the one promote plan needs the person's `approve-promote`.

**What can still be missed.** If the task module raises at a Stop event, nothing is refused and the Stop goes through (the run stays on and the board relays); if it raises on a subagent call, that call is refused (`GUARDS_FOR`). What Copilot does at a hook timeout (30 s in the shipped file) is not in the harness code. A spend that cannot be read fails open {src:.harness/engine/hook.py#L55-L87} {src:.github/hooks/harness.json#L1-L14}.

## Autorun internals: limits and mismatches between words and code

- **Words that lag behind 1.8.0.** The board's text for `agent` still says "the agent said it cannot go on" {src:.harness/engine/core/messages.en.json#L163-L163}. `stalled` is described elsewhere as "3 stops in a row" (the value of `max_stalls`); the code ends the run at the fourth identical Stop {src:.harness/engine/modules/task/autorun.py#L398-L402}.
- **No board, no relay.** Without a served board, `error` and the Start order do not exist, a cancel in VS Code is not read as `person`, and a chat that stops after 8 blocks or on an error waits, run on, for a person's message. Code does not check that a ticked step was done.

## Autorun internals: related files

- What autorun is, how a run goes and who may start it, in plain words: the file 20 Autorun.
- The gate's write split: the files 15 The gate and guardrails and 15b The gate and guardrails internals. Plan approval, typed codes: the files 14 Plans and approvals and 14b Plans and approvals internals.
- Task state and `TODO.md`: the files 11 Task and 11b Task internals. Independent checks (the `review` stop): the files 17 Independent checks and 17b Independent checks internals.
- The board's link thread and chat binding: the files 12 The board and 12b The board internals. Credits: the file 22 Cost and usage. The design: the file 36 Design decisions.
