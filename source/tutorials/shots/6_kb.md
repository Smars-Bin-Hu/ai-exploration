# Screenshots to take: 6 Knowledge base

Placeholders in `source/tutorials/6_kb.py`. Take them on this Mac with the 1.7.45 demo workspace (made-up data, no company data). Step numbers are the ones printed in the PDF; page numbers count the cover as page 1.

Never send a prompt just for a picture, and never press a button with a speech bubble or “in a chat” in its name: each opens a Copilot chat. A state that is already there, a command typed but not sent, or a file or terminal command is enough. Nothing below needs a model call.

| Page | Step | What to capture | How, without spending credits |
| --- | --- | --- | --- |
| 6 | 12 | The knowledge base window, tab **Overview**, with **Toolkit** as the next step: “Next is the toolkit…” and the button **Do the next step in a chat** | In a scratch copy of the demo workspace, move `knowledge-base/toolkit/` aside, open the book, press **Refresh**, screenshot the Overview; do not press the button. Put `toolkit/` back |
| 6 | 13 | VS Code: a Copilot chat with `/harness-rookie-new-knowledgebase` typed in the chat box, not sent | Open a new chat, type the command, screenshot, clear the box |
| 7 | 15 | VS Code: a new Copilot chat with `/generic-kb-toolkit-build` typed in the chat box, not sent | As above |
| 10 | 21 | The knowledge base window, tab **Overview**, with “Next: finish <domain> in the task learn-<domain>: write its architecture, then promote it.” and no button | Needs a demo learn task whose batches are all ticked and not promoted (`kb status` stage learn, no flows). Make it with files and harness commands only (tick every batch line in the demo learn task’s `TODO.md`), never with a chat; then **Refresh** and screenshot |
| 14 | 30 | Terminal in the demo `knowledge-base/` folder: `git log -1` showing the commit the harness made (after fix-orders-card is promoted), then `git push` typed, not run | Run `git log -1 --oneline` in the demo knowledge base; type `git push` without Enter |
| 15 | 32 | VS Code: the Copilot chat of a demo task, showing the agent reading `knowledge-base/README.md` and the domain’s `architecture.md` | Open an existing demo chat in the chat history where the agent read the knowledge base, scroll to those tool calls; do not send anything |
| 16 | 33 | Terminal: the output of `harness kb reads --task <a demo task>` listing knowledge base files and their reads | Run the command in the board’s Terminal window or your own terminal; it reads logs only |
| 16 | 34 | VS Code: `report.md` of a closed demo task open at the section **Knowledge base files read** | Open `.workspace/reports/tasks/<closed demo task>/report.md` (run `harness task report <task>` first if it is missing); a task that read no knowledge base file has no such section |
