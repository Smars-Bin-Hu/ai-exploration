# Screenshots to take: 3 Independent checks

Four placeholders in `source/tutorials/3_checks.py`. Take them on the company computer, with harness 1.7.45; no company names or data in view (a made-up task is fine). Page numbers count the cover as page 1.

| Page | Step | What to capture | Where in the app |
| --- | --- | --- | --- |
| 5 | Step 1 · Or in a message | A message that starts with `[review]=1`, sent in the chat of a task, with the agent's first reply under it | VS Code, the Copilot chat that holds a task |
| 6 | Step 2 · Let it check | The Live tab while a check runs: the call to the reviewer, with its latest steps open under it, and the task in the state **working** | Board › a task with Independent review on, while the reviewer runs › tab **Live** |
| 9 | Before the write-back | The dry run refused: the agent's `task promote --dry-run` and the line “It cannot be promoted yet: independent check passes needed in a row: …; so far: …” | VS Code, the Copilot chat of a `dev` task with checks on, before enough passes (expand the terminal call to show its output) |
| 10 | Step 4 · When checks run out | The waiting box at the top of the task page: **the checks are used up and wait for your decision**, with **More checks** and **Waive checks** (and **Dismiss check** if shown) | Board › a task whose checks are used up without enough passes › its task page |
