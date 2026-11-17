---
title: Board (self test)
subject: Board
layer: concept
file: zz Self test good
harness_tag: 1.7.41
course: Basic 06 · A prompt cannot stop a dangerous action | https://smarshu.com/writing/basic-06-prompt-cannot-stop
course: The book · 5.1 Tasks | https://smarshu.com/book/read/5-1-tasks.html
---
## Board: what it is

The board lists every task that is not closed and what it waits for {src:.harness/engine/modules/task/boardserve.py#L1-L10}.

![The board page, with one card per open task and what each waits for](img/board.png)

## Board: common questions

**Q: Who can start the board server?** Only a person at a terminal {src:.harness/engine/modules/task/boardserve.py#L5-L6}.
