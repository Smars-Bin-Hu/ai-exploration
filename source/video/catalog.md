# Picture catalog

Page renders are 3840x2160 (re-render: `swiftc -O source/video/pages/render.swift -o /tmp/render && /tmp/render <pdf> <outdir> 3840`); fractions in `box=`/`crop=` do not depend on size. Ids are used in `@ <id>` lines (see FORMAT.md). Dimensions are width x height in pixels. The last column flags a real person's name or a local user path (other than `alex`, `/Users/alex`, `/Users/Shared`); "also" lists exact-duplicate copies under other ids (use the id in this table). Page renders are at `source/video/pages/<deck>/pNN.png`; images under `source/tutorials/img/`.

## Board screens (`source/tutorials/img/_board/`)

Screens of the harness, a web board for GitHub Copilot agents; made-up demo data (user "Alex", paths under /Users/alex). Footer "© 2026 Smars Hu" on the landing screens is flagged.

| id | what it shows | good for explaining | WxH | flag / also |
| --- | --- | --- | --- | --- |
| board/accept | Task page "why-orders-slow" with orange "to accept" card, Accept and close / Not yet buttons | Accepting finished work; the final human step | 2216x762 | also: tutorials/1_day/accept |
| board/approve-code | Dialog "Confirm requirement · fix-total-rounding" asking you to type a code to approve | Typed-code approval gate before the agent proceeds | 1124x622 | also: tutorials/3_stopped/approve-code |
| board/changes-promote | Task "limit-order-items" Changes tab: diff of three files, "Approve promote" card | Reviewing the diff before promoting code to the repo | 2216x1720 | also: tutorials/2_tour/changes-promote |
| board/checks-chip | "Independent review 2" chip opened: popover with count buttons off,1-5 | Setting how many independent review checks are required | 632x550 | also: tutorials/4_checks/checks-chip |
| board/checks-dismiss | Dialog "Dismiss check · check-coupon-codes", type code E8D105 to dismiss | Overruling a wrong reviewer verdict, with code gate | 1124x559 | also: tutorials/4_checks/checks-dismiss |
| board/checks-more | Dialog "More checks · check-coupon-codes": checks done 3, limit 3, type code | Giving the reviewer more rounds when checks run out | 1124x500 | also: tutorials/4_checks/checks-more |
| board/checks-used-review | check-coupon-codes Review tab: three FAIL rounds listed with reasons, checks used up | Seeing why independent review failed round by round | 2216x2223 | also: tutorials/4_checks/checks-used-review |
| board/checks-used-up | Orange "Waiting for you": More checks, Waive checks, Dismiss check buttons | Choices when all review checks are used up | 2216x685 | also: tutorials/4_checks/checks-used-up |
| board/checks-waive | Dialog "Waive checks · check-coupon-codes", type code to let this version through | Waiving review and taking responsibility yourself | 1124x564 | also: tutorials/4_checks/checks-waive |
| board/commit-message | Closed task "raise-stock-timeout", Changes tab with commit message and Copy buttons | Copying the commit message after promote to commit | 2216x986 |  |
| board/enter | HARNESS landing screen with robot logo, setup checklist, Restart VS Code and Enter buttons | Opening screen and readiness checklist before entering | 2560x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/1_day/enter |
| board/go-on-new-chat | Task "validate-sku-format" waiting for you: Answer... and "Go on in a new chat" buttons | Continuing a task in a fresh VS Code chat | 2216x509 |  |
| board/intake | Task "import-price-list" Intake tab: drop files area, paste table option | Uploading Word/Excel documents as the requirement | 2216x1264 | also: tutorials/1_day/intake |
| board/intake-files | Intake file list (three price-list files) and "Tell the agent" message with Copy message | Handing requirement documents to the agent via INTAKE.md | 2216x1142 | also: tutorials/1_day/intake-files |
| board/kb-changes-promote | Task "fix-orders-card" Changes tab: promote card and diff of a knowledge-base file | Knowledge-base edits also need approval before promote | 2216x1359 | also: tutorials/6_kb/kb-changes-promote |
| board/kb-company | Knowledge base Company tab: Demo company, selected tools 0, skills 34 | Seeing what company skills and tools the agent has | 2404x1524 | also: tutorials/6_kb/kb-company |
| board/kb-domains | Knowledge base Domains tab: orders learned (6 cards), inventory not started, Learn buttons | Checking which knowledge domains are learned | 2404x1524 | also: tutorials/6_kb/kb-domains |
| board/kb-health | Knowledge base Health tab: toolkit audit passed, one stale card for orders | Spotting stale knowledge cards and map gaps | 2404x1524 | also: tutorials/2_tour/kb-health, tutorials/6_kb/kb-health |
| board/kb-lookup | Knowledge base Look up tab: stored procedure with used-by and uses lists | Tracing what an object depends on | 2404x1524 | also: tutorials/2_tour/kb-lookup, tutorials/6_kb/kb-lookup |
| board/kb-map | Knowledge base Map tab: single "orders" domain node, Who uses what toggle | Visualising domains and their dependencies | 2404x1524 | also: tutorials/2_tour/kb-map, tutorials/6_kb/kb-map |
| board/kb-overview | Knowledge base Overview: progress steps, counts of domains, cards, stale cards | Knowledge base status at a glance and next step | 2404x1524 | also: tutorials/2_tour/kb-overview, tutorials/6_kb/kb-overview |
| board/list | Task board List view: ten tasks with states, waits, action buttons, summary counters | The whole board: states and what needs you | 2376x2193 | also: tutorials/4_checks/list |
| board/live-waiting | Task "add-gift-wrap" Live tab: agent question waiting for your answer, Answer... button | Seeing the agent ask a clarifying question | 2216x1678 | also: tutorials/2_tour/live-waiting, tutorials/3_stopped/live-waiting |
| board/lobby | Lobby: robot icons per task, grouped Waiting for you and At work | Friendly overview of all agents and who waits | 2216x1833 | also: tutorials/6_kb/lobby |
| board/new-task | New task dialog "show-delivery-date": fields, first message preview, Create and send | Filling in a new task; no knowledge-base choice shown | 2164x1771 | also: tutorials/2_tour/new-task, tutorials/6_kb/new-task |
| board/one-01-new-task | New task dialog "show-delivery-date" with knowledge base None/orders chips | Step 1 of the day: creating the task | 2164x1807 | also: tutorials/1_day/one-01-new-task |
| board/one-02-lobby | Cropped lobby strip: three robots add-gift-wrap, add-stock-m..., show-delivery... with alerts | New task appearing among waiting agents | 960x230 |  |
| board/one-03-list-asked | List filtered to show-delivery-date: waits for you, Answer... and Go on in a new chat | Agent has asked its questions first | 2376x686 | also: tutorials/1_day/one-03-list-asked |
| board/one-04-list-req | List filtered to show-delivery-date: requirement waits, Confirm requirement button | Requirement written, waiting for confirmation | 2376x686 | also: tutorials/1_day/one-04-list-req |
| board/one-05-requirement | Requirement tab: REQ show-delivery-date, what to do, what not to do, Done when | Reading the requirement before confirming it | 2216x1759 | also: tutorials/1_day/one-05-requirement |
| board/one-06-approve-code | Dialog "Confirm requirement · show-delivery-date", type code E43645 to approve | Approving the requirement with a typed code | 1124x622 | also: tutorials/1_day/one-06-approve-code |
| board/one-07-list-go-req | List: requirement confirmed, buttons Send to agent and Go on in a new chat | Next step after confirming: send to agent | 2376x686 |  |
| board/one-08-send-to-agent | Task "show-delivery-date": requirement confirmed, Send to agent and Go on in a new chat | Choosing how to hand the confirmed requirement to the agent | 2216x532 | also: tutorials/1_day/one-08-send-to-agent |
| board/one-09-send-panel | Send to agent dialog: fixed message, reply language, model, note, Send to chat/Copy message | What the send message says and its options | 1124x1027 | also: tutorials/1_day/one-09-send-panel |
| board/one-10-list-plan | List filtered to show-delivery-date: plan waits for approval, Approve plan button | Plan written, waiting for your approval | 2376x686 |  |
| board/one-11-plan | Plan tab: PLAN show-delivery-date, files to change, steps, how checked, risks | Reading the agent's plan before approving it | 2216x1963 | also: tutorials/1_day/one-11-plan |
| board/one-12-list-working | List filtered to show-delivery-date: state working, progress dots 2/5 | Agent working; nothing for you to press | 2376x686 | also: tutorials/1_day/one-12-list-working |
| board/one-13-live | Live tab "No chat is linked to this task", Nothing waits for you notice | What the board shows while the agent works | 2216x1355 |  |
| board/one-14-todo | TODO tab: 2 of 5 steps ticked, current step marked "<- now" | Following the agent's progress step by step | 2216x1099 | also: tutorials/1_day/one-14-todo |
| board/one-15-list-promote | List filtered to show-delivery-date: promote waits, Approve promote button, 5/5 | Work done, code waits for promote approval | 2376x686 | also: tutorials/1_day/one-15-list-promote |
| board/one-16-changes-promote | Changes tab for show-delivery-date: diff of api.py, Approve promote card | Reading the code diff before promoting | 2216x2187 | also: tutorials/1_day/one-16-changes-promote |
| board/one-17-list-closed | List with Closed filter: show-delivery-date closed, 5/5 green dots, Archive button | A finished, closed task in the list | 2376x685 | also: tutorials/1_day/one-17-list-closed |
| board/one-18-closed-changes | Closed task Changes tab: commit message for show-delivery-date, Copy commit message | Taking the commit message after the task closes | 2216x1024 | also: tutorials/1_day/one-18-closed-changes |
| board/outside-enter-not-ready | HARNESS landing screen, red NOT READY: VS Code started without settings, Restart VS Code | Setup problem; fix by restarting VS Code | 2560x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/5_outside/outside-enter-not-ready |
| board/outside-held-card | Task "answer-ticket-t7": orange "an outside call waits for your approval", View/Approve buttons | Agent's write to an outside system waiting for you | 2216x855 | also: tutorials/3_stopped/outside-held-card, tutorials/5_outside/outside-held-card |
| board/outside-held-view | Dialog showing the exact demotracker command the agent wants to run, with a code | Inspecting an outside command before approving it | 1804x1065 | also: tutorials/3_stopped/outside-held-view, tutorials/5_outside/outside-held-view |
| board/outside-link | Task "answer-ticket-t7" with ticket link field "demo:300100" and held outside call | Linking a ticket to the task | 2216x600 | also: tutorials/5_outside/outside-link |
| board/outside-open-to-agent | "Open to the agent" dialog: linked items option, writes pass through, Prod never opens | Letting the agent write to linked tickets without asking | 624x713 | also: tutorials/5_outside/outside-open-to-agent |
| board/outside-task-head | Header strip of "answer-ticket-t7": outside call waits, ticket chip demo:T-7 | Showing a task linked to a ticket | 2216x273 | also: tutorials/5_outside/outside-task-head |
| board/outside-tools-connections | Connections & sign-ins dialog: demo tracker connection, Sign in and Test buttons | Where outside connections and accounts are managed | 1644x437 | also: tutorials/5_outside/outside-tools-connections |
| board/outside-tools-packs | Tool packs dialog: ado, demotracker (used), sqlserver, Turn on/off buttons | Choosing which outside tools the agent may use | 1644x1324 | also: tutorials/2_tour/outside-tools-packs, tutorials/5_outside/outside-tools-packs |
| board/plan | Plan tab for "add-order-notes": files to change, steps, risks, Approve plan card | Reading the plan before approving it | 2216x1906 | also: tutorials/2_tour/plan, tutorials/5_outside/plan, tutorials/6_kb/plan |
| board/requirement | Requirement tab for "fix-total-rounding": what to do, what not to do, Confirm requirement | Reading the written requirement before confirming | 2216x1703 |  |
| board/review | Review tab for "validate-sku-format": rounds 001 FAIL, 002 and 003 PASS with reasons | Independent reviewer results across rounds | 2216x2471 | also: tutorials/1_day/review, tutorials/2_tour/review, tutorials/4_checks/review |
| board/run | Task "cache-stock-counts" waits for your run (DEV): form for pasting output | Handing the agent results of something you ran | 2216x2443 | also: tutorials/1_day/run, tutorials/4_checks/run, tutorials/5_outside/run |
| board/state-busy-greyed | Working task: plan card with greyed-out Approve plan button, at-work notice | Buttons are disabled while the agent is working | 2216x660 | also: tutorials/1_day/state-busy-greyed, tutorials/3_stopped/state-busy-greyed |
| board/state-cancelled | List filtered to tidy-order-errors: state "cancelled, waits for you" | How a cancelled task looks in the list | 2376x686 |  |
| board/state-cancelled-page | Task "tidy-order-errors" page: "Cancelled, waits for you" card | A cancelled message leaves the agent stopped | 2216x494 | also: tutorials/3_stopped/state-cancelled-page |
| board/state-get-ready-repos | Setup row "Code repositories": two valid git repos under /Users/alex/repos | Adding the code repositories the agent may change | 1464x470 | also: tutorials/1_day/state-get-ready-repos |
| board/state-promote-branch | Red error: promote cannot run, branch feature/limit_order_items already exists | Promote blocked by an existing branch name | 1124x342 | also: tutorials/1_day/state-promote-branch, tutorials/3_stopped/state-promote-branch |
| board/state-promote-dirty | Red error: promote cannot run, working tree not clean, uncommitted files | Promote blocked by uncommitted changes in the repo | 1124x515 | also: tutorials/1_day/state-promote-dirty, tutorials/3_stopped/state-promote-dirty |
| board/state-queue-held | Terminal "task queue" with JSON: repo not clean, held by show-delivery-date; harness doctor | Why the promote queue is held by another task | 984x704 | also: tutorials/1_day/state-queue-held, tutorials/3_stopped/state-queue-held |
| board/state-quiet | List filtered to log-stock-misses: state "quiet" | How a quiet task looks in the list | 2376x686 | also: tutorials/3_stopped/state-quiet |
| board/state-quiet-page | Task "log-stock-misses" page: quiet state, "No sign of the agent for a while" | Agent session silent; what to do next | 2216x1316 |  |
| board/state-recover | Task "add-stock-moves": promote failed halfway, Recover the repository button | Undoing a half-finished write-back to the repo | 2216x523 | also: tutorials/1_day/state-recover, tutorials/3_stopped/state-recover |
| board/state-recover-list | List filtered to add-stock-moves: "promote failed halfway", Recover the repository button | Failed promote shown in the list | 2376x686 |  |
| board/state-round-one | Task show-delivery-date viewing Round 1 (read-only) with promoted file list | Looking back at an earlier round of the task | 2216x1005 | also: tutorials/1_day/state-round-one |
| board/state-round-two | Round 2 (current): requirement changed, must confirm requirement again | A changed requirement needs reconfirmation | 2216x626 | also: tutorials/1_day/state-round-two |
| board/state-stuck | List filtered to speed-up-totals: working state with warning triangle icon | Stuck warning icon in the task list | 2376x686 | also: tutorials/3_stopped/state-stuck |
| board/state-stuck-page | Task "speed-up-totals" Agent actions tab: warning "Stuck? no tool call for 11 minutes" | Spotting an agent that has stopped doing anything | 2216x649 | also: tutorials/3_stopped/state-stuck-page |
| board/state-waits-for-you | Task show-delivery-date "waits for you": Answer... and Go on in a new chat | Basic "waiting for you" state card | 2216x532 | also: tutorials/3_stopped/state-waits-for-you |
| board/stop-agent-actions | Agent actions tab of add-order-export: four blocked calls (delete, checkout, push, edit) | Seeing what the harness stopped the agent from doing | 2216x1503 | also: tutorials/2_tour/stop-agent-actions, tutorials/3_stopped/stop-agent-actions, tutorials/5_outside/stop-agent-actions |
| board/stop-git-code | One blocked git checkout call with instruction to approve the command by code | Git changes need your approval, never the agent's | 2216x405 | also: tutorials/3_stopped/stop-git-code |
| board/todo | TODO tab of "retry-stock-calls": 2 of 5 steps ticked | The agent's step checklist | 2216x1099 |  |
| board/tour-archive-dialog | Dialog "Archive 1 task(s)": folder path input, one-way warning | Archiving closed tasks out of the repository | 1124x648 |  |
| board/tour-close-dialog | Dialog "Close design-order-events": Close the task / Cancel | Closing a task when work is done | 1124x314 |  |
| board/tour-dock-full | Narrow side dock of five round icons: home, settings, book with badge 1, help, sliders | The dock buttons at the screen edge | 176x600 |  |
| board/tour-enter | HARNESS landing screen collapsed checklist "READY", Restart VS Code and Enter | Cleanest opening screen for the first step | 2560x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/2_tour/tour-enter |
| board/tour-enter-open | HARNESS landing screen, READY: full checklist of setup items, Restart VS Code, Enter | Everything ready; press Enter to start | 2560x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/1_day/tour-enter-open, tutorials/2_tour/tour-enter-open |
| board/tour-everything | "Everything you can ask for" dialog: First lesson, Full course, review helpers, Start buttons | Built-in lessons and helpers you can start | 1524x1377 | also: tutorials/2_tour/tour-everything |
| board/tour-files-edit | Files tab of add-order-notes: file tree and PLAN.md open in an editor | Editing task files directly, including the plan | 2216x2118 | also: tutorials/1_day/tour-files-edit, tutorials/2_tour/tour-files-edit |
| board/tour-help | "How can I help?" popup: ask box, two quick buttons, Everything you can ask for | The built-in help assistant | 784x358 | also: tutorials/2_tour/tour-help |
| board/tour-list | Full List view: 17 tasks, many waiting, with filters, counters, action buttons | Overview of the whole task list | 2376x2887 | also: tutorials/2_tour/tour-list, tutorials/3_stopped/tour-list |
| board/tour-list-closed | List filtered to Closed: learn-orders and raise-stock-timeout, Archive buttons | Finding closed tasks to archive | 2376x817 | also: tutorials/1_day/tour-list-closed, tutorials/2_tour/tour-list-closed |
| board/tour-list-kind | List filtered by kind "knowledge base update": fix-orders-card with Approve promote | Filtering the list by task kind | 2376x823 |  |
| board/tour-list-search | List with search "stock": cache-stock-counts and retry-stock-calls | Searching tasks by name | 2376x832 | also: tutorials/2_tour/tour-list-search |
| board/tour-lobby | Full Lobby: robots grouped Waiting for you, At work, Resting, Closed | Lobby layout with all robot groups | 2216x2085 | also: tutorials/2_tour/tour-lobby |
| board/tour-lobby-left-alone | Lobby groups "At work" and "Left alone": robots retry-stock-calls and tidy-readme | Tasks left alone, with no agent session | 2216x720 | also: tutorials/1_day/tour-lobby-left-alone, tutorials/2_tour/tour-lobby-left-alone, tutorials/3_stopped/tour-lobby-left-alone |
| board/tour-new-task-fields | New task form lower part: What to do, Model, Thinking, Context window, Reply language | Choosing model, thinking and language for a task | 1070x724 | also: tutorials/2_tour/tour-new-task-fields |
| board/tour-off-work | List after "Off work": 14 tasks paused, Back to work button | Pausing all tasks at the end of the day | 2216x1407 | also: tutorials/1_day/tour-off-work, tutorials/2_tour/tour-off-work |
| board/tour-performance | Agent Performance Review for raise-stock-timeout: credits, each prompt, call timeline | Reviewing where an agent spent time and credits | 2160x1720 | also: tutorials/2_tour/tour-performance |
| board/tour-readybar-red | Red banner "The agent cannot work right now": VS Code started without settings, Restart | A blocking setup problem on the board | 2216x580 | also: tutorials/1_day/tour-readybar-red, tutorials/2_tour/tour-readybar-red |
| board/tour-readybar-yellow | Yellow banner "Not fully ready for your company's tasks", harness doctor note, Run doctor | A non-blocking readiness warning | 2216x472 | also: tutorials/1_day/tour-readybar-yellow, tutorials/2_tour/tour-readybar-yellow |
| board/tour-reply | "Say something to the agent" dialog: message box, quick prompts, model, permissions, Send | Writing a message to the agent yourself | 1224x1079 | also: tutorials/1_day/tour-reply, tutorials/2_tour/tour-reply, tutorials/3_stopped/tour-reply, tutorials/6_kb/tour-reply |
| board/tour-report | Task analysis report for raise-stock-timeout: time, prompts, key points, time bar | The task report summarising time and effort | 2080x1659 | also: tutorials/2_tour/tour-report |
| board/tour-run-block | "Check it yourself" block: grep command with Ask agent, Run, Copy buttons | Running a suggested command yourself | 2216x353 | also: tutorials/2_tour/tour-run-block |
| board/tour-run-dialog | Dialog "Run this command yourself?": grep command, red warning gate does not check, Run now | Running a command from the board; what to check first | 1124x569 | also: tutorials/2_tour/tour-run-dialog |
| board/tour-search | Search popup with "coupon": result check-coupon-codes, move/open/esc hints | Finding any task with the search box | 1344x387 | also: tutorials/2_tour/tour-search |
| board/tour-settings | Settings panel: theme, rendering, background, language EN/中文, Restart board | Where theme, language and background are set | 712x1332 | also: tutorials/2_tour/tour-settings |
| board/tour-setup-local | Setup section 4 Local: python programs, network, MCP not allowed, Save | Local tools and network settings in setup | 1644x602 | also: tutorials/2_tour/tour-setup-local |
| board/tour-setup-repos | Setup row "Code repositories": two valid git repos under /Users/alex/repos | Adding code repositories, with Browse and Add | 1644x470 | also: tutorials/2_tour/tour-setup-repos |
| board/tour-setup-window | Setup sections You (name Alex, language) and From the company (knowledge base, skills) | First-time setup form: you and company items | 1644x1080 | also: tutorials/2_tour/tour-setup-window, tutorials/6_kb/tour-setup-window |
| board/tour-tab-design | Design tab of design-order-events: options table A vs B, proposal, open question | Reading a design task's options and proposal | 2216x1720 | also: tutorials/2_tour/tour-tab-design |
| board/tour-tab-evidence | Evidence tab of test-sku-check: one DEV run E1 saved, not cited | Test run evidence saved on the task | 2216x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/2_tour/tour-tab-evidence |
| board/tour-tab-files | Files tab of import-price-list: file tree, originals, converted CSV/MD files | Seeing every file in the task folder | 2216x1720 |  |
| board/tour-tab-history | Records, Task Record tab of raise-stock-timeout: timeline of approvals and promote | Audit trail of who approved what and when | 2216x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/2_tour/tour-tab-history |
| board/tour-tab-log | Records, Log tab of raise-stock-timeout: LOG.md heading and notes | The agent's append-only log of decisions | 2216x1720 | FLAG: footer "© 2026 Smars Hu" (real name); also: tutorials/1_day/tour-tab-log, tutorials/2_tour/tour-tab-log |
| board/tour-tab-overview | Overview tab of add-order-notes: TASK.md kind, tier, status, files to read | The task's one-page status summary | 2216x1940 | also: tutorials/1_day/tour-tab-overview, tutorials/2_tour/tour-tab-overview |
| board/tour-tab-rca | RCA tab of why-orders-slow: slow orders on Monday, root cause, evidence | Reading a root-cause analysis for an investigation task | 2216x1720 | also: tutorials/2_tour/tour-tab-rca |
| board/tour-tab-test | Results, Test tab of test-sku-check: DEV pass, IST steps with curl command, pass criteria | Reading the test guide and running it yourself | 2216x1720 | also: tutorials/2_tour/tour-tab-test |
| board/tour-tab-trace | Records, Agent actions of limit-order-items: prompts, calls, blocked-by-hook counters | Seeing what the agent did per prompt | 2216x1720 |  |
| board/tour-task-head | Header strip of validate-sku-format: waits for you, Independent review 2, progress dots | The task header: state, progress and review chips | 2216x272 | also: tutorials/2_tour/tour-task-head |
| board/tour-task-more | "More" menu: Time and usage, Save as HTML, Autorun on, Pause, Close explanations | What the task's three-dot menu offers | 484x802 | also: tutorials/1_day/tour-task-more, tutorials/2_tour/tour-task-more |
| board/tour-terminal | Terminal panel "doctor": harness doctor output, all [OK], errors 0 | Running harness doctor to check the install | 984x704 | also: tutorials/2_tour/tour-terminal |
| board/tour-tools-local | Local dialog: programs (python), network proxy fields, MCP allow/do not allow | Local tool, network and MCP settings in detail | 1644x1090 |  |

## Real tasks (2026-11-18)

Board screens from real Copilot runs in the demo workspace (harness 1.7.45, made-up repos, a made-up Shop database in a local SQL Server container registered as shop-qat). Paths are scrubbed to ~/harness; footers cropped. 82.5 Credits spent in all.

| id | what it shows | good for explaining | WxH | flag / also |
| --- | --- | --- | --- | --- |
| board/real-report | Report (Time and usage) of real task refuse-zero-count: 2 min 3 s working, 73.9 Credits, 2 premium requests, 97% cache read, 1 independent check passed, key points, where the time went | A task report with real numbers from a real Copilot run | 2080x2164 |  |
| board/real-report-prompts | Same report, Every prompt (37.5 and 36.4 Credits, claude-sonnet-5) and Stages table (Requirement 35.7, Developing 18.3, Independent check 11.9, Promote 6.2 Credits; tokens in/out) | Where the credits of a real task went, by prompt and stage | 2080x1463 |  |
| board/real-review | Results, Review of refuse-zero-count: Independent review 1, round-001 PASS, the reviewer findings citing api.py lines and REQ items, and saying it did not run pytest | What an independent reviewer subagent answers, and that it only reads | 2216x1676 |  |
| board/real-agent-actions-dev | Records, Agent actions of refuse-zero-count, prompt 2: edits in DEV/orders-service, the test copy and rm -rf the gate asked about, the reviewer subagent (claude-sonnet-5.5) | The agent doing its own DEV work and self-test, with the gate watching each call | 2216x2239 |  |
| board/real-files-top | Files tab of refuse-zero-count, subfolders folded: REQ/, REF/, DEV/, REVIEW/, SNAPSHOT/, TEST/ and the top files (CHANGES.diff, COMMIT-MESSAGE.md, LOG.md, PLAN.md, PROMOTE-PLAN.diff, REQ.md, TASK.md, TODO.md), TASK.md open | The task folder: one folder holds everything of a task | 2216x1572 |  |
| board/real-sql-blocked | Records, Agent actions of clean-shop-qat: 2 blocked by a hook; sqlcmd DROP TABLE dbo.summary and TRUNCATE TABLE dbo.order_lines refused on shop-qat (qat), the UPDATE ... WHERE held | The SQL Server tool pack refusing destructive SQL, from a real agent run | 2216x1670 |  |
| board/real-sql-held | Task page of clean-shop-qat: the agent reports two refused calls and one held; the held card (write, shop-qat qat, Shop, target dbo.stock, the UPDATE statement, Approve / Do not approve) | A write to a database waiting for the person, with the exact statement | 2216x2674 |  |
| board/real-sql-live | Live tab of clean-shop-qat close up: Refused by the gate x2 (DROP, TRUNCATE), Held by the gate (UPDATE), then the agent summary of each call | What the agent sees and says when the gate refuses or holds | 2216x725 |  |
| board/real-sql-report | Report of clean-shop-qat: key points (hook refused 2, held 1), Agent Performance Review 3, Gate blocks (2) table with Right to block / Wrong block verdict buttons | Gate blocks in the report, and judging a block as right or wrong | 2080x2115 |  |
| board/real-kb-summary | Files tab of the prepared demo task learn-orders: the knowledge base domain files, architecture.md open (Purpose, Flows, Key data, Where to start, Traps). Prepared demo content, not a live Learn run | The summary file of a knowledge base domain | 2216x1219 |  |
| board/real-kb-card | Same, objects/sp.md open: cards for usp_load_orders and usp_build_summary (what, reads/writes, called by, level verified at a commit, cited lines, traps). Prepared demo content | What a knowledge base card holds | 2216x1193 |  |
| board/real-vscode-sessions | VS Code chat Sessions list (cropped): the two chats the board made, clean-shop-qat and refuse-zero-count (+78 -18) | Each board task is a Copilot chat in VS Code | 682x310 |  |

## Tutorial-only images (`source/tutorials/img/<slug>/`)

Only images that exist nowhere else. Every other file in the tutorial folders is a byte-identical copy of a board image: use the `board/...` id (the copies are listed in its "also" column).

| id | what it shows | good for explaining | WxH | flag / also |
| --- | --- | --- | --- | --- |
| tutorials/1_day/lifecycle | Diagram: task folder Requirement, Plan, Work, then You commit; three typed-code approval points | The task lifecycle and where you approve | 2400x960 |  |
| tutorials/2_tour/tour-dock-wide | Wider crop of the side dock: home, settings, book with badge 1, help, sliders | Introducing the dock buttons | 440x600 |  |
| tutorials/3_stopped/held-both | Held outside call (ado item 300101) above a green Approved card: Tell the agent | Approving a held call, then running it | 2448x973 |  |
| tutorials/3_stopped/refusals-list | Red "Blocked and failed: 5" list of refused writes, git reset and push | What the harness refuses the agent from doing | 2410x950 | FLAG: local paths ~/Developer/temp/slidedoc-demo |
| tutorials/6_kb/board-list | Dark-theme task list with 7 tasks, sales_mart_design, customer_dim_backfill, buttons | Dark-mode board with knowledge-base style tasks | 1360x760 |  |
| tutorials/6_kb/kb-go-on-docs | Dark-theme Knowledge base Overview: 5 domains, 74 cards, orders/returns/customer rows | Knowledge base with several domains, partly learned | 1160x800 |  |

## Basic 01: Stop using AI the 2024 way (24 pages)

Slides rendered from the PDF. Every page has "© 2026 Smars Hu" in the footer.

| id | what it shows | good for explaining | WxH | flag / also |
| --- | --- | --- | --- | --- |
| basic-01/p01 | Title slide: "Stop using AI the 2024 way: why you need a harness" | Opening title card | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p02 | "What this post answers": five numbered questions about AI in development teams | Previewing the five questions the video answers | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p03 | "Most of us do the AI's homework first": text plus long-prompt mock-up | Hook: the typical 2024 way of prompting | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p04 | Pain point 1: AI doesn't know your project; session 1 closes, session 2 knows nothing | Why every new session starts from zero | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p05 | Pain point 2: process in prompt; flow discuss, plan (skipped), build, test, accept | Prompted process is only a request, not enforced | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p06 | Pain point 3: checking takes longer; more rules, pricier model, bigger bill, same glitches | Why paying for a smarter model doesn't help | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p07 | Pain point 4: AI overconfident; says "Done. All tests pass", you run them, FAILED | AI grades its own work too generously | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p08 | Pain point 5: black box; boxes for lost memory, guesswork, cost, no audit trail | Remaining problems even for good AI users | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p09 | The result: you ask, AI answers, you copy it in; "a thinking Google" | People retreat to using AI as a smart search | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p10 | Root cause: chatbot diagram (you and model) vs agent diagram with program running the loop | You are the loop carrying everything in a chatbot | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p11 | Agent diagram: You, LLM, Tools, outside world; tool call and result arrows, agent loop | How tool calling and the agent loop work | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p12 | Three rounds of prompt, model, asks for a tool; round 3 asks for none: stop | The loop ends when the model says so | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p13 | Model in the centre with six outside problems: tools, memory, verification, audit, cost | A smarter model does not fix these problems | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p14 | Bar chart: same model scores 52.8% default harness, 66.5% after harness changes | Evidence that the harness, not the model, matters | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p15 | Equation: Model + Harness (loop, tools, context, rules, checks, records) = Agent | Defining agent as model plus harness | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p16 | Two kinds of harness: your team's layer on top, general harness (Claude Code, Codex, Copilot) | General harness versus your team's harness | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p17 | Your team's harness box: AGENTS.md, skills, subagents, tools, workflow, approvals, audit | What the team's own harness layer includes | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p18 | Left: problems (don't know project, no audit trail); right: the harness part that fixes each | Mapping each pain point to a harness answer | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p19 | Dark slide "Explore once, keep the result" with knowledge base screenshot (5 domains, 305 cards) | Knowledge base solves "doesn't know your project" | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p20 | Dark slide "Work is a task, and code changes pass two approvals" with plan screenshot | Task folder and the two approvals in the board | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p21 | Dark slide "A reviewer that hasn't seen the author's reasoning" with review screenshot | Independent review catching the author's blind spots | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p22 | Dark slide "Where the time went": task analysis screenshot, 2h36m waiting, 32 min agent work | Showing cost was waiting, not slow agent | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p23 | Takeaway: table chatbot/agent/harness vs carries, controls, checks, limits: you or program | Summary of who carries what in each approach | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-01/p24 | "Try it in five minutes" quote box with five-minute exercise, article and course links | Closing call to action | 1920x1080 | FLAG: © 2026 Smars Hu in footer |

## Basic 06: A prompt cannot stop a dangerous action (18 pages)

Slides rendered from the PDF. Every page has "© 2026 Smars Hu" in the footer.

| id | what it shows | good for explaining | WxH | flag / also |
| --- | --- | --- | --- | --- |
| basic-06/p01 | Title slide: "A prompt cannot stop a dangerous action: a harness can" | Opening title card | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p02 | "What this post answers": five numbered questions about rules and dangerous actions | Previewing the five questions the video answers | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p03 | "Most of us put the rules in the prompt": prompt mock-up with three ground rules | Hook: typical don't-delete, don't-push prompt rules | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p04 | Grid of 300 dots, one orange: 300 tool calls, one is git reset --hard | Safety is decided by the worst call, not average | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p05 | Reason 1: rules at start of context buried under an hour of reads and outputs | Why rules fade in long tasks | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p06 | Reason 2: agent routes around a failing step with git reset --hard to finish | The agent isn't rebelling, it is trying to finish | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p07 | Root cause 1 diagram: model writes a request, a program outside the model runs it | The model never touches your files itself | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p08 | Root cause 2: prompt to model to git push, dashed box "no check here" | Nothing checks the action between model and run | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p09 | A hook checks every tool call first, then allow, ask you, or refuse with reason | Introducing hooks and their three answers | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p10 | Ask path (Allow/Deny, you decide) versus refuse path (git push, refused with reason) | When to ask and when to refuse outright | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p11 | A hook sees only the call: script cleanup.sh hides rm -rf and git push --force | The limit of hooks: scripts hide commands | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p12 | Left: what the agent tries; right: what harness does (refuse, ask, plan approval) | Summary of the harness's checkpoints for risky actions | 1920x1080 | FLAG: footer "© 2026 Smars Hu" |
| basic-06/p13 | Dark slide "Every tool call is checked before it runs" with red blocked-calls screenshot | Real record of five refused dangerous calls | 1920x1080 | FLAG: local paths ~/Developer/temp/slidedoc-demo (tiny, in screenshot); © 2026 Smars Hu in footer |
| basic-06/p14 | Git commands in three tiers: read-only runs, commit waits for approval, push/reset never | Sorting git commands by danger level | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p15 | Task folder (agent writes here) beside locked boxes: your repository, rules and hook files | Guarding where the agent writes, not only commands | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p16 | Dark slide "Code changes pass two approvals from you" with plan-approval screenshot (fix-orders-discount) | The two approvals gating code changes | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p17 | Takeaway: Prompt box (goal, context, done) versus Code hook box (push, reset, rule edits) | Prompt for what to do, code for never | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
| basic-06/p18 | "Try it in five minutes": test git push in the harness, or build a hook | Closing call to action | 1920x1080 | FLAG: © 2026 Smars Hu in footer |
