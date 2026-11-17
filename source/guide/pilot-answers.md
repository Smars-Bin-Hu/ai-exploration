# Pilot answers

One round, knowledge `pdf/` only (`00 Harness at a glance`, `11 Task`). Ask each question of `questions.md` in a new chat, paste the answer under its heading below, then fill its row of the table. Plain text is fine; a screenshot of the answer is fine too.

- **Cited:** the files and sections the answer shows as references.
- **Links:** were the GitHub and course links in the answer, and did they open? (yes / some / no)
- **Learn more:** the course link or, for a how-to question, the tutorial it named.
- **Own work:** did it use anything of the asker's own work, mail, chats or files? (no / yes: what)
- **Grade:** right / mostly right / partly right / wrong, against the key points of `questions.md`.

## Round 1 · pdf

Setup seen: 

| # | Layer | Cited | Links | Learn more | Own work | Grade |
|---|---|---|---|---|---|---|
| Q1 | 1 · harness | | | | | |
| Q2 | 1 · harness | | | | | |
| Q3 | 1 · harness | | | | | |
| Q4 | 2 · features | | | | | |
| Q5 | 2 · features | | | | | |
| Q6 | 2 · features | | | | | |
| Q7 | 3 · design | | | | | |
| Q8 | 3 · design | | | | | |
| Q9 | 3 · design | | | | | |
| Q10 | 4 · ideas | | | | | |
| Q11 | 4 · ideas | | | | | |
| Q12 | 4 · ideas | | | | | |
| Q13 | how-to | | | | | |
| Q14 | how-to | | | | | |
| Q15 | not covered | | | | | |

### Q1 · What is this harness, and what problem does it solve?
Answer:

Notes:

### Q2 · Where does the harness run, and what does our team have to bring to it?
Answer:

Notes:

### Q3 · Is the harness a sandbox? What does it protect against, and what not?
Answer:

Notes:

### Q4 · What is a task, and how is it different from a chat session?
Answer:

Notes:

### Q5 · What kinds of tasks are there, and how does each one end?
Answer:

Notes:

### Q6 · What does the board show, and what does "waiting for you" mean?
Answer:

Notes:

### Q7 · How does a task move from one stage to the next? Is that controlled by a skill or by code, and where in the code?
Answer:

Notes:

### Q8 · How does the gate block dangerous commands, and where are its rules?
Answer:

Notes:

### Q9 · How does the approval code work, and why can't the agent approve its own plan?
Answer:

Notes:

### Q10 · Why isn't a rule in the prompt or in `AGENTS.md` enough to keep the agent safe?
Answer:

Notes:

### Q11 · Why does the harness keep the work in tasks instead of in the chat?
Answer:

Notes:

### Q12 · What is the idea behind the approval gates, and where does a person hold the keys?
Answer:

Notes:

### Q13 · I maintain a data pipeline repository. How do I start a task and give the agent my requirement documents?
Answer:

Notes:

### Q14 · The agent says my command was refused. How do I get it run?
Answer:

Notes:

### Q15 · How does autorun work? Can a task run on its own overnight?
Answer:

Notes:

## Overall

- Did it answer at the depth of the question (layers 1 to 4)?
- Did the how-to answers stay short and name the right tutorial?
- Did it say "does not cover this yet" for Q15 and make nothing up?
- Did clicking a citation open the right file?

## Old pilot (2026-11-16, before the goal changed)

The first pilot asked how to use the harness as well as how it works, with the old questions P1–P15 (in git, commit 74cab51). Paused after P2 when the goal changed. Kept as it was written.

Setup seen 2026-11-16: knowledge held both `pdf` and `docx` folders (SharePoint), Cloud files on, Outlook, Teams, connectors and web search off. P1 and P2 were asked with both folders in; from P2 on, only `pdf` (P2 asked again).

### P1 · What is this harness, and what does it do?
Answer (transcribed from 3 phone photos, 2026-11-16; citation chips shown as [c]):

> The harness is a set of files and Python code that wraps the GitHub Copilot agent in VS Code, so the agent can work on real code under explicit rules and human approval points. In harness version 1.7.45, its main job is to turn an open-ended Copilot chat into controlled, persistent tasks, check the agent's tool calls, and require a person before important changes are written back to repositories. 00 Harness at a glance [c]
>
> **What it actually does** — Think of it as a control layer around the coding agent:
> 1. **Checks what the agent is about to do.** A gate is run by hooks before tool calls. It can allow, ask about, or refuse writes and terminal commands. For example, it refuses certain dangerous commands, protects harness guardrail files, and restricts direct writes to target repositories. [c]
> 2. **Turns work into persistent tasks instead of relying on chat history.** A task is a folder such as `.workspace/sandbox/tasks/<task name>/` containing the requirement, plan, working files, results, handover information, and harness-managed state. A later Copilot chat can reopen that task and continue from those files. 11 Task [c]
> 3. **Separates what the agent does from what a person authorizes.** For development work, the normal path is roughly: Requirement → human confirmation → plan → human approval → development → dry run → human write-back approval → repository branch. The plan and write-back approvals use typed codes tied to hashes of what is being approved. [c +1]
> 4. **Provides a local board for managing agent work.** The board runs locally on the person's computer. It shows tasks, their stage, what they are waiting for, and actions such as Confirm requirement, Approve plan, Approve promote, and Accept and close. 21 Start a task and give it the requirement [c]
>
> So the practical idea is: *Copilot still does the engineering work, but the harness gives that work state, boundaries, approval gates, and a human-controlled write-back path.* [c]
>
> **An important limitation** — The Guide is explicit that the harness is not a sandbox. The agent runs as the person's operating-system user, and some protections inspect the text of commands. The Guide therefore says it is intended to guard against agent mistakes, not against an agent deliberately trying to circumvent the harness. [c]
> Also, some behavior is enforced by code, while other behavior is merely requested of the model through instructions and skills. For example, the model is told to open a task before producing or changing files, but the Guide explicitly says code does not force that particular behavior. [c +1]
>
> **Evidence** — 00 Harness at a glance, "Harness: what it is" and "Harness: the parts and how a piece of work flows through them". [c]
> Key code locations cited by the Guide: `.github/hooks/harness.json` lines 1–113 · `.harness/engine/modules/gate/handler.py` lines 1–14 · `.harness/engine/core/tasks.py` lines 19–37 · `.harness/engine/core/approval.py` lines 17–58 (all shown as links)
>
> **See it** — 21 Start a task and give it the requirement shows "The board's list: six tasks waiting for you…", including task states and actions such as Approve plan, Approve promote, and Approve a call. [c]
>
> **Learn more** — The book · 5.2 The agent writes the requirement, the person confirms it · The book · 5.1 Manage tasks, not chats [c]
>
> **You could ask next** — Walk me through one development task end to end. · What does the harness actually guarantee, and what can still be bypassed?

Cited: 00 Harness at a glance, 11 Task, 21 Start a task (chips; "Sources" list not opened) · Links: yes, code and course links shown as link text, and they open (person, 2026-11-16) · Notes: see grade below.

Grade (main): **mostly right.** Nothing invented: every claim traces to 00/11/21, section names and the screenshot caption quoted word for word, all four code locations exist in 00. Missed from the key: (a) the harness carries no business knowledge, the team plugs in KB, skills, target repos; (b) the model runs in Copilot's service (only "the board runs locally" survives); (c) the scope condition that the requirement's confirmation is a text line the agent can write (says only "human confirmation"). Wrong course: gave 5.2 and 5.1 (front matter of 21 and 11) instead of 0.1 and Basic 06 from 00, the file the answer is built on.

### P2 · Tell me how to use the harness.
Answer (transcribed from 5 phone photos, 2026-11-16; citation chips shown as [c]; one company-specific example left out):

> For Harness 1.7.45, the normal workflow is: prepare the Harness environment, create a **task** (the persistent unit of work), give the agent the requirement, review `REQ.md`, approve the plan, let the agent make changes in DEV, review the checks/results, and then explicitly approve write-back. The important point is that requirements, plans, development artifacts, state, and approvals remain associated with the task rather than depending on one chat session. [c +2]
>
> **Step by step**
> 1. **Prepare your environment.** Before starting the task, have these ready: Harness · VS Code · the Harness board running · a paired browser · the target repository/repositories configured. The board is where you interact with and monitor the task workflow. [c]
> 2. **Create a task.** Start a new task for the piece of work you want Copilot to perform. A task is a persistent folder-based unit containing things such as: requirements · plans · results · task state. Harness supports different task kinds, including QA, RCA, design, development, testing, and knowledge-base work, as well as task tiers. [c +1] For example, for your ETL work, the initial request could be something concise like: *[a one-line request naming a real company ETL package and data problem — left out here]*. Harness uses that starting request to begin the task workflow. [c]
> 3. **Give the agent the requirement.** Provide enough information for the agent to understand what you need. If supporting requirement documents exist, the Guide says they can be uploaded through the board's Intake tab and converted into editable text without AI. [c] The agent may ask clarification questions. Answer those before treating the requirement as final. [c]
> 4. **Review `REQ.md`.** The agent writes the understood requirement into `REQ.md`. Review it carefully. This is the point where you verify that the agent's understanding matches what you actually asked for before allowing the work to progress. [c]
> 5. **Confirm the requirement.** Once `REQ.md` is correct, explicitly confirm the requirement. This is an important human checkpoint in Harness 1.7.45. The workflow is designed around explicit user confirmation, rather than assuming the generated requirement is correct. [c]
> 6. **Review and approve the plan.** After requirement confirmation, the agent develops a plan. Review that plan and give **plan approval** before development proceeds through the controlled workflow. So conceptually: Request → `REQ.md` → Requirement confirmation → Plan → Plan approval. [c +1]
> 7. **Let the agent perform the development work.** After plan approval, the workflow moves into file changes in DEV. Harness wraps the GitHub Copilot agent in VS Code rather than simply giving the agent unrestricted repository access. A **hook** and **gate** participate in controlling what the agent is allowed to do. [c +1] The safeguards described by the Guide include blocks around areas such as: guardrail changes · dangerous commands · unauthorized repository writes · secrets access · selected outside access. The Guide distinguishes controls enforced in code from model-facing instructions and decisions deliberately reserved for a person, so these should not be interpreted as a general claim that "the agent cannot do anything unsafe." [c]
> 8. **Review the independent checks/results.** The workflow includes independent checks after the development changes. Review the resulting artifacts and task state from the task/board rather than relying only on what the agent says in chat. [c +1]
> 9. **Approve write-back.** If the resulting changes are acceptable, approve write-back. This is another human-controlled transition. The Guide describes approved write-back as going to a new uncommitted branch rather than silently committing the agent's work into your repository. [c] So the final portion is roughly: Development → Checks → Human review → Write-back approval → New uncommitted branch. [c]
> 10. **Review the branch normally.** At that point the Harness-controlled workflow has produced the changes for you to inspect through your normal engineering process. For someone working the way you do with Git/ETL repositories, the useful mental model is: *Harness does not replace Git or your engineering review. It puts a controlled task and approval workflow around the Copilot agent before its work reaches the repository.* That task persists across chat sessions and carries the requirement, plan, results, and state with it. [c +1]
>
> **The whole workflow in one line** — Prepare Harness → Create task → Provide requirement → Answer clarification questions → Review `REQ.md` → Confirm requirement → Review plan → Approve plan → Agent works in DEV → Checks → Review results → Approve write-back → New uncommitted branch. [c +2]
>
> **Evidence:** 00 Harness at a glance.docx, 11 Task.docx, and 21 Start a task and give it the requirement.docx, all describing Harness 1.7.45. The available Guide excerpts do not expose the section-level GitHub/code links, screenshot captions, or course URL, so I won't invent them. [c +2]
>
> **You could ask next:** What exactly happens after I click "create task"? · Show me one realistic Harness example using an ETL code change.

Asked with both folders in knowledge: this answer drew on the DOCX copies, so it counts as a round-2 (docx) data point; P2 is asked again with `pdf` only.

Cited: 00 Harness at a glance.docx, 11 Task.docx, 21 Start a task.docx (named in its Evidence line; "Sources" list not opened) · Links: **no**: no code links, no course link, no screenshot; the agent says the excerpts it got do not contain them · Notes: see grade below.

Grade (main): **partly right; two process failures.**
- Steps match the key in order and nothing about the harness is invented ("Intake… with no AI" and the tiers are both in 21/11). Kept one good limit: "not a general claim that the agent cannot do anything unsafe".
- Missing from the key: how to start the board (`Start Harness` / `harness task board`); that a task starts from one sentence in the chat or **New task**; that confirmations and approvals are made by typing a code; the **Accept and close** path for a task that changes no repository; that the person commits the branch.
- Scope lost: step 8 says the workflow "includes independent checks"; the Guide says they run only when the person asked for them. The dry run is dropped from the flow.
- **Off-Guide content:** it built an example from the asker's own work context (a real company ETL package and data problem), which the instructions forbid ("answer only from the Guide files").
- **Format broke:** cited `.docx` files, and gave no code links, no course link, no screenshot, saying the excerpts do not contain them. In the DOCX build every URL is a hyperlink behind link text (pandoc), so text extraction may drop the URL; the PDF has the URL in the text layer.
