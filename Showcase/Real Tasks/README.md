# Real Tasks

Company only. Each real task gets a folder here with two things: the task page saved from the board (**Save as HTML** at the top of the task page), and a short deck that tells a lead in one minute what the agent understood, what it found, and where people decided.

The point is not speed. It is that the agent really understood the task and found problems a person had missed (vertical ability), and that people stayed in control with little effort (horizontal ability). One overview page for the whole folder shows several tasks running at once.

## How to make one

1. Copy `_template/Real task template.pptx` into a new folder named after the task.
2. Page 1 (overview) is for the whole folder: keep it in one copy only.
3. Take every picture from this one task, so its name shows in each. Replace every grey hint. Paste each screenshot over its dashed box, then delete the box. Each box says where on the board to take it. Delete a box the task does not need.
4. Write the one line under each picture: what it proves.
5. Save the task page as HTML into the same folder.

See `_template/Sample (fake data).pdf` for a filled one. Only `_template/` and this file go to GitHub; real tasks never do.

Build the template again: `.venv/bin/python Showcase/source/build.py` (text in `Showcase/source/text.py`).
