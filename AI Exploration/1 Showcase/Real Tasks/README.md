# Real Tasks

Company only. One folder per real task (one intake): a short deck, and the task page saved from the board (**Save as HTML** at the top of the task page).

The deck shows a lead what the agent really did and what the harness gave us: it understood the task, found problems a person had missed, solved them, and people stayed in control with little effort.

## How to make one

1. Copy `_template/Real task template.pptx` into a new folder named after the task.
2. Fill the white summary page (page 1): the task name, one line of facts, and a few paragraphs on what happened. Replace every grey hint.
3. For each screenshot, copy the page with the right shape (tall or wide), paste the picture over the dashed box and delete the box. One picture per page, all from this task, cropped to the part that proves the point.
4. The dark pages have no heading: the screenshot is the page. Write two or three sentences beside or under it: what it shows, and why it matters.
5. Save the task page as HTML into the same folder.

Good screenshots are listed in the notes of every page. See `_template/Sample (fake data).pdf` for a filled one. Only `_template/` and this file go to GitHub; real tasks never do.

Build the template again: `.venv/bin/python source/showcase/build.py` (words in `source/showcase/text.py`), from the repository root.
