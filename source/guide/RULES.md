# Writing a Harness Guide file

The Harness Guide is the knowledge of an agent in Microsoft 365 Copilot. Leaders, architects and curious engineers ask it to understand the harness, in four layers: what it is and what problem it solves; its common features; how it is designed and built, and where in the code; the harness engineering ideas behind it. It is not a tutorial: "how do I" questions get a short answer and the name of a harness tutorial in `AI Exploration/3 Courses/Harness tutorials/`. The agent searches these files, finds passages, and answers from them with the code locations and course links it finds there. A person who clicks the citation opens the file and reads it.

So every file has two readers. **The agent** sees text only, in passages cut out of the file. **The person** sees the whole page, pictures included. Write for both.

## Sources

- Anything in the harness repository at the pinned tag is a source: the code, tests, policies, agent and skill files, `docs/`, the screenshots in `docs/images/`, the git history. Read with `git -C ~/Developer/DE-agentic-harness show 1.7.45:<path>`.
- **How to use** may follow the harness `docs/`. **How it works and whether it is safe** must be checked against the code: the docs are not always exact. Example: `docs/02-features.md` says the agent never fills the confirmation line of `REQ.md`; the code reads that line as text, and the agent's edit tools may write it.
- The facts of `source/deep-dive/topics/04-task/NOTES.md` were fact-checked three times against 1.7.41; use them.
- Never invent. What the code does not show, do not say.

## The three layers

- `overview`: the whole harness, for broad questions ("what is it", "how do I use it", "is it safe"). Answers them directly, then points to the files that go deeper.
- `concept`: one thing of the harness (a task, the gate, approvals, the knowledge base…): what it is, how it works, how it differs from its neighbours, its limits.
- `how-to`: one thing a person does, step by step, with a screenshot for every step that shows something on screen. How-to pages are no longer Guide knowledge: the build skips the pages in `NOT_KNOWLEDGE` (`build.py`), which stay in `pages/` for the harness tutorials.

## Every passage stands alone

The agent finds passages, not files. A passage it finds must make sense with nothing around it.

- **Every `##` heading names the subject** of the file, then what the section says: `## Task: how it differs from a chat session` (checked). Never "Overview" or "How it works" alone.
- Name things, never "it", "this" or "the above" across sections. Repeat the subject in the first sentence of a section.
- No "see above", no "as said before". To point elsewhere, name the file: "(see the file Gate)".
- **The code location goes right after the claim**, as `{src:path#L10-L40}` (checked: every section of an `overview` or `concept` file cites code, except sections whose heading ends in "questions" or "terms"). It renders as "(code: path lines 10–40)" with a link; the full URLs are listed at the end of the file by the build.
- No footnotes (checked).

## Write the way people ask

- Each `concept` and `overview` file has a section `## <Subject>: common questions` with 4–8 questions in the words a leader or an architect would use ("Can the agent approve its own plan?"), each answered in 1–3 sentences with its code location.
- Start each section with the answer, then the detail. A broad question gets the first sentences; a detailed one reads on.
- **Absolute words must hold without exception**: "only", "every", "never", "cannot", "all". Check each against every path: the terminal as well as the edit tools, a session that holds no task, the board as well as the CLI. When one does not hold, scope it ("for the session that holds the task", "the edit tools") and say the exception in the file's limits. Three rounds of fact-checking on the Task topic found mostly this kind of mistake.
- Say what is enforced by **code**, what is asked of the model by **text** (instructions, skills), and what is left to a **person**. That is the question architects ask most.

## Sections

`concept`:
1. `## <Subject>: what it is` — two or three sentences a leader can repeat.
2. `## <Subject>: how it works` — the mechanism, with a figure if it helps.
3. `## <Subject>: how it differs from <neighbour>` — when people confuse them.
4. `## <Subject>: what is enforced by code, and what is not`
5. `## <Subject>: common questions`
6. `## <Subject>: limits`
7. `## <Subject>: related files` — the other Guide files to read next, by name.

`how-to`:
1. `## <Subject>: before you start`
2. `## <Subject>: steps` — numbered; one screenshot per step that shows a screen.
3. `## <Subject>: when something goes wrong` — the refusals and messages a person may see, and what to do.
4. `## <Subject>: why it works this way` — two or three sentences, and the concept file to read.

The build adds `## <Subject>: code locations` and `## <Subject>: courses to learn more` at the end.

## Pictures

- Markdown: `![<caption>](img/name.png)`. The caption is a full sentence that says what the picture shows (checked: at least 5 words), because the agent reads the caption and not the picture.
- Screenshots: `git -C ~/Developer/DE-agentic-harness show 1.7.45:docs/images/<name>.png > img/<name>.png`. Do not use a screenshot whose labels or layout no longer match the code at the tag: compare its button names with `.harness/engine/core/messages.en.json`. List the screenshots you need and do not have in your report.
- Diagrams: SVG in `fig/`, as in `source/deep-dive/RULES.md` ("Figures"); the Task topic's diagrams in `source/deep-dive/topics/04-task/fig/` may be reused. Every fact in a diagram must also be in the text.

## Courses

Front matter lines `course: <title> | <url>` (checked: the link answers). Existing courses:

- Basic 01 · Stop using AI the 2024 way: https://smarshu.com/writing/basic-01-stop-using-ai-the-2024-way
- Basic 06 · A prompt cannot stop a dangerous action: a harness can: https://smarshu.com/writing/basic-06-prompt-cannot-stop
- The book, Harness Engineering, one chapter per page: https://smarshu.com/book/read/<chapter>.html, e.g. `5-1-tasks`, `4-3-guardrails`, `8-1-why-a-knowledge-base` (chapter ids: `ls ~/Developer/copilot-harness-engineering/book/src`).

Link the one or two that teach the idea behind the file, not every one that mentions it.

## Front matter

```
---
title: <Subject as a title, e.g. "Task">
subject: <the word every heading starts with, e.g. "Task">
layer: overview | concept | how-to
file: <output name with an order number, e.g. "11 Task">
harness_tag: 1.7.45
course: <title> | <url>
---
```

## Style

Plain, exact English. Short sentences. Name the real thing: the file, the command, the state. No press-release words (checked). No code blocks; a command or a file name in backticks is fine.

## Done

- `python3 source/guide/build.py <name>` passes.
- Open `source/guide/_pages/<name>/full.png` and look at it.
- Read the text back as the agent would: `pandoc source/guide/_build/<name>.md -t plain` (the text the PDF holds). Every section must still make sense on its own. The knowledge is PDF only: a DOCX copy lost every link in the pilot.
