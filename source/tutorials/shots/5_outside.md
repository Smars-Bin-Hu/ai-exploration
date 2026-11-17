# Screenshots to take: 5 Outside systems and connections

Placeholders in `source/tutorials/5_outside.py`. Take them on this Mac with the 1.7.45 demo workspace (made-up data: the demo ticket board `demo`, task `answer-ticket-t7`). Step numbers are the ones printed in the PDF; page numbers count the cover as page 1.

Before you start: `python3 source/tutorials/shots/demo.py pack on`, then `demo.py start`, then `demo.py hold` (the held call lives 10 minutes). When you are done: `demo.py pack off`, `demo.py stop`.

Nothing below needs a model call. Never press **Tell the agent to run it**, **Tell the agent to run it again** or **Go on in a new chat**: they send a message to a Copilot chat.

| Page | Step | What to capture | How, without spending credits |
| --- | --- | --- | --- |
| 4 | 5 | Your own terminal after `harness connections find demo`: the lines it prints for the demo connection | In a terminal in the demo workspace, run `harness connections find demo` (a read; no chat, no model) and screenshot the window |
| 8 | 16 | The card of the held call of answer-ticket-t7 right after **Approve**: the green **Approved** card with its code, and **Tell the agent to run it** if the board shows it | On the board's task page of answer-ticket-t7, press **View**, click the code, close the window, press **Approve**. Screenshot the card. Do not press Tell the agent to run it |
| 9 | 19 | The same kind of card after **Open linked items of demo for this task** was pressed with the code: **Opened**, and **Tell the agent to run it again** if shown | Run `demo.py hold` again for a fresh card; press **View**, click the code, close the window, press **Open linked items of demo for this task**. Screenshot the card. Do not press Tell the agent to run it again. Then close it: **Open to the agent** › **Close** |
| 9 | 20 | Your own terminal after `harness task allow --conn demo --on --task answer-ticket-t7`, then `harness task allow --conn demo --off --task answer-ticket-t7`: both answers | Run both in your own terminal in the demo workspace (it needs a real terminal; no chat, no model) and screenshot the window with both answers |
