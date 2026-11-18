# Screenshots to take: 3 When the agent is stopped

Placeholders in `source/tutorials/3_stopped.py`. Take them on this Mac with the 1.7.45 demo workspace (made-up data, no company data). Step numbers are the ones printed in the PDF; page numbers count the cover as page 1.

Never send a prompt just for a picture. Where a step needs the agent to have run a command, use a chat in the demo where it already happened, or have the person type the command into the VS Code terminal in place of the agent where noted. Nothing below needs a new model call.

| Page | Step | What to capture | How, without spending credits |
| --- | --- | --- | --- |
| 8 | 20 | Your own terminal after `harness approve-command`: the waiting git command listed, and the line that asks for the code (code not typed) | One capture serves steps 20 and 46: see step 46 |
| 8 | 21 | VS Code: the Copilot chat with an agent terminal command waiting for confirmation, the **Allow** button under it, its menu closed | Only in a chat whose Permissions is not Allow all. Use an existing chat that already waits on a confirmation; screenshot, then leave it (do not allow). The same sitting gives steps 34, 36 and 37 |
| 10 | 26 | Task page, tab **Live**: a terminal command marked **Refused by the gate**, with the reason showing on hover | Needs a live chat whose command the gate refused. Use an existing demo chat where the agent ran `git push` (or another refused command) earlier; open its task page, tab Live, hover the line. If no such chat exists, skip until one does: do not send a prompt for it |
| 10 | 27 | VS Code: the Copilot chat right after a refused command: the refused tool call and the agent's reply saying what was refused and why | Same existing chat as step 26, scrolled to that turn |
| 13 | 34 | VS Code: the Copilot chat with an agent terminal command (for example a `curl`) waiting for confirmation, the Allow button's menu open (showing **Allow in this Session**) | Same chat as step 21; open the menu, screenshot, then press Escape (do not allow) |
| 13 | 36 | Board, List: a task whose State reads “the agent asks to run: …” and whose Do column shows **Allow · deny** | While the chat of step 21 waits, take the board List view; do not press the button |
| 13 | 37 | Board: the **Allow · deny** window, with the command and its Allow, Deny and Cancel buttons | Press Allow · deny on that row, screenshot, then press **Cancel** |
| 16 | 46 | Your own terminal after `harness approve-command`: the waiting git command listed, and the line that asks for the code (code not typed) | The demo already holds a git write that waits (add-order-export, `git -C ../repos/orders-service checkout -b try-export`). In a terminal in the harness folder run `harness approve-command`, screenshot at the code prompt, then press Enter on an empty line to cancel |
| 17 | 49 | Enter screen (or the notice above the board after Enter): the red line saying guardrail files differ, with the **Accept these files** button | Only on a demo copy where a guardrail file really changed (for example a comment edited in `.harness/engine/`); start the board, screenshot, do not press the button yet |
| 17 | 50 | Your own terminal after `harness doctor --accept`: the guardrail files it lists and takes in | Same demo copy; run it in a terminal in the harness folder (not the board's Terminal window). No model involved |
| 17 | 51 | VS Code: a new Copilot chat, no task, with `/harness-admin` typed in the chat box | Open a new chat, type `/harness-admin`, screenshot before pressing Enter; then clear the box and close the chat |
