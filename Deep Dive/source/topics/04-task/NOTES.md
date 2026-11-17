# Notes for the fact-checker: 04 Task

All paths at tag `1.7.41` of `~/Developer/DE-agentic-harness`. Line ranges as `git show 1.7.41:<path>` numbers them.

## Page 1 (pattern): the problem and the idea (fig/idea.svg)

- A chat is compacted as its context fills (Copilot's own compaction near 80%): `.harness/policies/task.json` L3 (`health.context_percent` text: "below Copilot's own compaction at about 80%").
- A chat's record is Copilot's file; the harness copies the rounds into the task at close: `.harness/engine/modules/task/chatrounds.py` L1-L10, L163-L172; called from `task.py` L384-L389. Path of the record: `.harness/engine/core/copilot_events.py` L1. ("ends when it is closed" was removed: `task.json` L3 supports only the compaction.)
- A confirmation in the chat cannot hold an approval ("Allow in this Session"): `.harness/engine/core/approval.py` L1-L8.
- A task is a folder with handover note, requirement, plan, results, state: `.harness/engine/core/tasks.py` L1-L37; tier files `.harness/engine/modules/task/tasklife.py` L39-L45.
- Any later chat opens it and goes on: `tasklife.py` L177-L193 (`open_task`), `task.py` L138-L216 (`attach`).
- Open until the person accepts it: `.harness/engine/modules/task/accept.py` L1-L11; agent refused `task close`: `.harness/policies/gate.json` L137-L143.

## Page 2 (pattern): parts and lifecycle (fig/pattern.svg)

- Agent holds one task at a time: `.harness/engine/core/state.py` L5-L6; `task.py` L138-L141, L207.
- Task hook tells the agent where the task stands at SessionStart and every UserPromptSubmit (not every tool call): `.harness/engine/modules/task/handler.py` L3-L4, L157-L172, L478-L483.
- Gate keeps edit/create tool writes inside the task folder: `.harness/engine/modules/gate/handler.py` L38-L88, L765-L782 (terminal calls take another path, L96-L146, which does not confine writes to the task folder).
- The agent's tools cannot write the state: `gate.json` L24-L33 (`cli_owned_paths`). Harness code that writes `task.json`: CLI (`task.py` L80-L96), hook (`handler.py` L79-L85, L287-L300, L398-L411; `tasklife.py` L458-L470, L755-L761), board (`boardserve.py` L1480-L1489).
- Lifecycle, code path: requirement confirmed `task.py` L568-L610; plan approved L426-L473; code in DEV/ only after approval `gate/handler.py` L80-L84; write-back approved L941-L980; written back L868-L914; closed by the board when nothing waits `accept.py` L184-L217 and `boardserve.py` L426-L442.
- Lifecycle, result path: deliver `accept.py` L45-L68; accept closes `accept.py` L167-L181.
- Bold border (a move the agent cannot make): `gate.json` L130-L143 (person-only commands and `task close`); approvals need a person `.harness/engine/core/approval.py` L28-L42; the board closes a written-back task that waits for nothing `accept.py` L184-L217.
- Any later chat may open it again: `tasklife.py` L177-L193; a closed task reopened `task.py` L172-L181.

## Page 3 (pattern): the guarantee (fig/guarantee.svg)

- The code typed is the first 6 characters, upper case, of a sha256 of what is approved: `approval.py` L17-L25, L50-L58.
- Person = TTY or the board's vouched terminal: `approval.py` L28-L42. Board page: same functions, typed code: `.harness/engine/modules/task/boardserve.py` L1-L17, L140-L153, L799-L823.
- No approval carries over to a changed file: `tasks.py` L154-L159 (approved digest must equal the current one), `task.py` L458-L461.
- Files checked again under the lock before the approval is recorded: `task.py` L458-L469 (plan), L971-L979 (promote), L588-L593 (requirement).
- Recorded: `plan.approved_sha256`, `plan.req_sha256`: `task.py` L467.
- Guard reads it before every DEV/ write: `gate/handler.py` L73, L80-L84; `tasks.py` L154-L159 (`plan_approved`).
- Stale when PLAN.md or the asked-for sections of REQ.md change: `tasks.py` L109-L152 (`_REQ_ASKS`, `req_digest_of`, `plan_req_changed`). Test: `.harness/tests/test_reqbinding.py` L65-L83; `test_task.py` L164-L170.
- Write-back the same way: `task.py` L898-L901 (promote needs dry run and approval of the same `plan_sha256`), L941-L980; digest `promote_target.py` L114-L118.
- Agent cannot run the approval commands: `gate.json` L130-L136.

## Page 4 (depth): the parts in code (fig/arch.svg)

- Commands write `task.json` under a lock: `task.py` L80-L96; hook and board write their own marks: `tasklife.py` L458-L470, `boardserve.py` L1480-L1489.
- Hook engine runs each module on the events it subscribes to: `.harness/engine/hook.py` L1-L15, L97-L99; task module events `.harness/registry.json` (modules.task.events).
- Target repositories: a new branch, not committed; a knowledge base is committed on its base branch: `promote_target.py` L1-L12; `task.py` L885, L917-L930.
- Board calls the same functions: `boardserve.py` L140-L153.
- Box contents: Terminal person-only commands `gate.json` L132-L135; board pairing `boardserve.py` L11-L16; board reads session state `tasklife.py` L815-L827; Copilot record read for time, usage, cancels `copilot_events.py` L1, `tasklife.py` L396-L406; templates `tasklife.py` L39, L86-L98; target repos new branch, not committed `task.py` L917-L930, `promote_target.py` L454-L490; session state path `state.py` L3, `paths.py` L86-L87; hook config `.github/hooks/harness.json`; task handler `handler.py` L1-L19; gate `gate/handler.py` L64-L88; stage ribbon `taskstages.py` L1-L15.

## Page 5 (depth): session and task (fig/task-vs-session.svg)

- `attach` sets `active_task`; the task left stays open: `task.py` L157-L158, L207; test `test_tasklife.py` L195-L202.
- `sessions[]` every pick-up, last 100: `task.py` L39, L182-L184.
- `session_id` latest holder: `task.py` L180.
- Subagent's session inherits the task: `state.py` L252-L303 (L297); test `test_tasklife.py` L235-L240.
- Subagent or admin session cannot open: `tasklife.py` L126-L135; `task.py` L153-L156.
- Gate follows the task the session holds: `test_tasklife.py` L206-L215; another session picks it up L151-L157.
- Session state fields: `state.py` L1-L10, L44-L62, L84-L95; written under a lock `state.py` L155-L186.
- Hook log path: `.harness/engine/core/logs.py` L35-L36.
- task.json fields: `task.py` L163-L170 (initial), `events` L93-L96 (200), `rounds` L245-L249, `req` L609, `plan` L467, `promote` L885-L888, `waiting` L185, `paused` `tasklife.py` L682-L693, `deliver` `accept.py` L60-L63, `handoff` `tasklife.py` L511, `review` `task.py` L195, `allow_conn` `tasklife.py` L518, `links` `tasklife.py` L610-L635, `chat` `chatlink.py` L1-L17.
- `round` +1 when reopened after a write-back: `task.py` L176-L178, L249.
- task.json replaced whole: `state.py` L123-L141 (`atomic_write`). Written only by harness code (CLI, hook, board), see page 2 notes.

## Page 6 (depth): task files (fig/task-files.svg)

- Tier files: `tasklife.py` L39-L45, L78-L83; never overwrites: L108-L123; tiers only go up L210-L211.
- TASK.md handover: `.harness/contracts/templates/task/en/TASK.md` L1-L3.
- REQ.md sections, confirmation line: `contracts/templates/task/en/REQ.md`; hashed sections `tasks.py` L109-L144.
- LOG.md newest on top: `contracts/templates/task/en/LOG.md` L3.
- TODO.md unticked steps stop deliver and close: `accept.py` L51-L54; `task.py` L348-L351.
- DEV/ after plan approval: `gate/handler.py` L80-L84; `DEV/_manual/`: `tasks.py` L29, L172-L175.
- TEST/ results per environment: `taskstages.py` L122-L139.
- Results at the root without a plan: `tasks.py` L3-L7; message `task.step.plan` in `core/messages.en.json`.
- REQ/ REF/ INBOX/ person's, read only: `tasks.py` L36; `gate/handler.py` L85-L87.
- CLI-owned paths: `gate.json` L24-L33. `.task/base/` `task.py` L5-L7; rewind `rewind.py` L1-L14 (taken by the hook, `handler.py` L212-L218); transcript `chatrounds.py` L8-L9; REVIEW/SNAPSHOT `tasksnap.py` L1-L7; OUTBOX `gate/handler.py` L408-L411; diffs `task.py` L792-L802, L862-L865.
- One owner each, with exceptions: CLI fills REQ.md's confirmation line `task.py` L599-L610; deliver/accept/sweep rewrite TASK.md's Status line `accept.py` L85-L101; close appends to TODO.md `task.py` L357-L359.
- `task list` reads the state not Markdown: `test_tasklife.py` L592-L596.
- The hook keeps no prompt while the task runs: `test_tasklife.py` L618-L625; `state.py` L307-L309. At close the chat's rounds are copied to `.task/transcript.jsonl`: `task.py` L384-L389, `chatrounds.py` L163-L172.

## Page 7 (depth): pick-up (fig/pickup.svg)

- Session without a task told the open tasks (newest five): `handler.py` L124-L137, L157-L172 (`OPEN_TASKS_SHOWN` L39).
- `task open` → `attach` refusals: `tasklife.py` L177-L193, L126-L135; `task.py` L148-L156, L173-L175.
- Writes: `task.py` L180-L188, L207.
- `read_first` TASK.md and `next`: `tasklife.py` L155-L160; `task.py` L258-L303.
- Every prompt: `handler.py` L88-L121, L187-L220.
- Stop: blocks for an unupdated TASK.md (L335-L347), unpassed checks (L316-L332), write-back loose ends (L350-L371), the knowledge-base offer (L374-L395), autorun (L442-L451); all in `on_stop` L454-L475; otherwise waiting mark L398-L411.

## Page 8 (depth): lifecycle (fig/lifecycle.svg)

- Status: new (folder, no task.json) and broken `tasklife.py` L856-L867, `tasks.py` L87-L92; `task open` on an unreadable task.json starts it over (`tasks.read` returns None, `task.py` L159-L171, `core/tasks.py` L77-L84); `task new` `tasklife.py` L163-L174; `task open` L177-L193; another session L151-L157 of `test_tasklife.py`; close via Accept `accept.py` L167-L181, sweep L202-L217, person's `task close` `commands.py` L125-L133; all call `task.close` `task.py` L343-L396; reopen `task.py` L172-L181; folder stays `tasklife.py` L10-L11, test L159-L169.
- Paused flag: `tasklife.py` L666-L712, L755-L761; prompt resumes `handler.py` L203-L209.
- Promote (the write-back, `task promote`): none→dry_run `task.py` L868-L897 (plan approved L872, checks `taskreview.py` L563-L568); dry_run (approved or not)→none on fetch L651-L652, delete L729-L730, set_branch L326-L330; a new dry run of another plan drops the approval L885-L888; "approved" is stored as state `dry_run` plus `approved_plan_sha256` L976-L977; no kind check on promote (L828-L916), so the header says "meant to write back"; done for a knowledge base = commit on its base branch `promote_target.py` L7-L10; approve `task.py` L941-L980; promote L898-L914; partial `promote_target.py` L454-L476; recover `task.py` L983-L1017; new round `task.py` L232-L249.

## Page 9 (depth): gates (fig/gates.svg)

- confirm-req `task.py` L568-L596; approve-plan L426-L473; DEV/ write `gate/handler.py` L64-L88 + `tasks.py` L147-L159; fetch L616-L653 (not done/partial L632-L633), delete L708-L732 (needs a fetched file L721-L722, no done/partial check); deliver refuses dev and kb tasks written back `accept.py` L58-L59; dry run L868-L897; approve-promote L941-L980; promote L898-L914; recover L983-L1017; deliver `accept.py` L45-L68; Accept `accept.py` L167-L181; close `task.py` L343-L366; pause `tasklife.py` L682-L693 (refused while at work unless `--force`, `require_idle` L806-L809).
- Person-only commands and refusal of `task close`: `gate.json` L130-L143; read as the shell reads them: `gate/harnesscmd.py` L1-L10.
- Approvals typed in a terminal also wait while the agent is in a turn: `commands.py` L106-L117.

## Page 10 (depth): derived state and stages (fig/derived.svg)

- `state_of`: `tasklife.py` L840-L853; states list L812; working `at_work` L791-L803, `active_now` L777-L785 (300 s, `policies/task.json` `board.active_seconds`), `subagent_running` L830-L837, `held` L824-L827.
- Waiting reasons in order: `tasklife.py` L276-L336 (figure lists the main ones; autorun ended and cancelled at L328-L335 are left out, as the label says).
- Ribbon: `taskstages.py` L1-L15, L46-L67 (dev/kb), L177-L185 (test), L261-L280 (kinds; qa none). Test: `test_taskstages.py` L170-L207.

## Page 11 (depth): design decisions (fig/decisions.svg)

From git history (commit, date):
- Levels and L3 request dropped (1.1.0): `675adb73` (2026-10-10, "Drop the Levels and the L3 request", 110 files changed, 1,799 insertions, 9,892 deletions); L3 agents added in `2bcf06df` (B8), request module `2d3c3571` (B7), L2 task mode `51691e12`. Code trace: `state.py` L110-L119.
- B24, switching tasks leaves the old one open: `01d5ab5c`; before it `request/task.py` `start` refused ("first `task close`") at `01d5ab5c^`.
- Hook captured prompts into `REQ/request.md` (never released, so "five of them after a release") → REQ.md by agent: `a6e60cdf`.
- 1.4.30, approval bound to the requirement: `64db099b`.
- 1.5.16, seven states incl. "no session": `77958fc5`.
- 1.7.38, closing is the person's acceptance; gate refuses agent's `task close`: `a28ce296`, `b0d1a8a3`.
- Alternatives taken: digest approval vs dialog `approval.py` L1-L8; derived stages `taskstages.py` L1-L4; reopen in place, fork hint `tasklife.py` L177-L193; lock directory and atomic write `state.py` L123-L176.

## Page 12 (depth): limits and code map

- Stop checks only that TASK.md was written: `handler.py` L335-L347.
- `attach` checks only that the session's state file exists: `task.py` L148-L149.
- Opening a task changes only the opening session's state (`session(...)` of `session_id` only): `task.py` L152-L207. An earlier session whose `active_task` still names the task keeps it; its gate (`gate/handler.py` L67-L72) still binds it to that task. This is my reading of the code; no test states it.
- Shell commands are not confined to the task folder: terminal path `gate/handler.py` L96-L146 refuses only guardrail, CLI-owned, `.git` and target-tree writes; the write-back still needs approval of the exact files (`plan_sha256` over file digests, `promote_target.py` L114-L118; `task.py` L898-L901).
- Working inferred from the hook log age, `board.active_seconds` 300 (`policies/task.json` L41): `tasklife.py` L774-L803; a tool call longer than that looks idle. A served board also corrects "working" from VS Code's chat state (`boardserve.py` L193-L199), not mentioned on the page.
- `task close` CLI does not refuse an agent (its docstring still says "the agent closes a task it finished"); the gate's pattern does: `commands.py` L125-L133, `gate.json` L137-L143.

## Unsure

- The "new" state on the lifecycle figure is a list row state for a folder without `task.json` (`tasklife.py` L862-L867), not a stored status value.
- Page 2 shows "Requirement confirmed" on both paths; a light (Q&A) task has no REQ.md and skips it (`tasklife.py` L41-L45).
- The before-1.1.0 designs are described from commit messages and the removed `request/task.py`; why the Levels were dropped is not stated in the commit, so the page says only what replaced them.

## Screenshots wanted

- The approve-plan dialog as of 1.7.41: `docs/images/approve-dialog.png` shows an 8-character lower-case code ("type cc845c08"), but `approval.py` L17 now uses 6 capitals. A fresh screenshot would let page 3 show the real approval screen.
- The board's "to accept" card of a delivered task (summary, **Accept and close**, **Not yet**): proves that closing is the person's act (pages 2 and 8). None exists in `docs/images/`.

## Round 2 corrections (scope of absolute words)

- State file and the agent: edit tools are refused outright (`gate/handler.py` L59-L60, `owned_match`, any session). A terminal command is refused when it names the path (`gate/policy.py` L125-L132, `gate/terminal.py` L140-L142); `scriptcheck.py` L1-L12 reads scripts for guardrail paths only. Pages say "the edit tools cannot write it; a terminal command that names it is refused".
- The gate's task-folder confinement applies only to a session that holds an open task: `gate/handler.py` L67-L72 return None otherwise. The write-back guarantee still holds: the approved promote plan digest covers every file's sha256 (`promote_target.py` L114-L118; `task.py` L898-L901, L971-L977). Limit on page 12.
- Requirement confirmation: read from a text line of REQ.md (`taskreview.py` L88-L110); no REQ.md or no line gives state `none`, which approve-plan accepts; `unwritten` is refused and `open`/`changed` need the joint code (`task.py` L442-L447, L549-L565). Only `confirm-req` is refused to the agent (`gate.json` L130-L136). "Requirement confirmed" no longer has a bold border; limit on page 12.
- unheld: `held()` checks only the session named in task.json (`tasklife.py` L824-L827); wording now "the session that last opened it no longer holds it".
- Fourth close path: the board's Close calls `task.close` directly with `check_todo=False` (`boardserve.py` L690-L701); Accept also passes `check_todo=False` (`accept.py` L179). The TODO check applies to the terminal command only.
- INBOX/ is made when the person gives something on the task page (`taskinbox.py` L1-L7; `tasks.py` L36), not by a tier (`tasklife.py` L41-L45).
- What is saved at close is the chat's rounds: prompts, the agent's text, tool names, time, credits; no thinking, tool results or subagent text (`chatrounds.py` L1-L10).
- recover asks for the code of its record's `plan_sha256` and has no locked re-check (`task.py` L983-L1017); page 9 now limits the "re-check under the lock" sentence to the requirement, plan and write-back approvals. Board pause needs no pairing (`boardserve.py` L10).
- Commit numbers are those of the commit `675adb73`, not of the 1.0.0..1.1.0 range.
- The approval commands: the gate refuses them to the agent (`gate.json` L130-L136; `harnesscmd.py`); the text no longer says "cannot".

## Round 3 corrections

- Requirement confirmed is a person move (`task.py` L568-L596: `person()`, `typed()`; `gate.json` L135) and also plain text the agent can write (`taskreview.py` L88-L110). Page 2 draws it bold with a "*" note pointing to Limits.
- The main guarantee is scoped to the write-back: `task.py` L898-L901, L970-L977; `promote_target.py` L114-L118. Outside-system route: after plan approval a call marked `task` passes (`gate/handler.py` L266-L271), and a connection opened with `task allow` passes writes and runs (`gate/handler.py` L282-L287; `tasklife.py` L541-L545). Limit on page 12.
- State file and the terminal: only write patterns that name the path are refused; reads never (`gate.json` L3, L24-L86; `gate/handler.py` L100-L102; `gate/terminal.py` L140-L142).
- set_branch changes the branch, not DEV/, and resets a dry run (`task.py` L317-L333); an edit-tool change to DEV/ leaves promote.state, and promote refuses because the plan digest no longer matches (`task.py` L898-L901).
- Page 6 now "a set of files fixed by tier, each with one main writer"; REQ/, REF/, INBOX/ always refused to the edit tools of the holding session, DEV/ until approval (`gate/handler.py` L80-L87).
- Terminal writes: refused by named path (`gate/handler.py` L96-L108) or when a script the line runs writes a guardrail path (`gate/handler.py` L115-L118; `scriptcheck.py` L1-L11); scripts are not read for the task's own files.
- Terminal box on page 4 now lists confirm-req and ends with "…" (`gate.json` L132-L135).
- Page 11: a reopened task of a kind without write-back rounds is pointed to `task fork` when its requirement changes (`tasklife.py` L189-L192).
- Page 7 step 6: the next-step text tells a new session to read TASK.md first, then REQ.md, REQ/ and REF/ (`core/messages.en.json` L14-L15).
- The page-12 limit "`task close` itself admits an agent" was dropped to fit the word and footnote limits; the fact stays on page 9 (gate refuses it) and in the round-1 notes (`commands.py` L125-L133).
