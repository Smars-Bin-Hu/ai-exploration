# Screenshots to take: 4 Independent checks

Placeholders in `source/tutorials/4_checks.py`. Take them on this Mac with the 1.7.45 demo workspace (`source/tutorials/shots/demo.py`, made-up data, no company data). Step numbers are the ones printed in the PDF; page numbers count the cover as page 1.

Never send a prompt just for a picture: a chat or board state that is already there, a message typed but not sent, or a harness command run in your own terminal is enough. Nothing below needs a model call.

| Page | Step | What to capture | How, without spending credits |
| --- | --- | --- | --- |
| 3 | 4 | VS Code: the Copilot chat of a task, with `[review]=1` typed at the start of a message | Open the existing add-gift-wrap chat, type `[review]=1 check the work of add-gift-wrap` in the chat box, screenshot before pressing Enter; then clear the box |
| 6 | 12 | The dry run refused: `harness task promote --dry-run` and its output “It cannot be promoted yet: independent check passes needed in a row: 1; so far: 0.” | In a VS Code terminal panel in the demo workspace (not the agent), run the demo's `harness task promote --task check-coupon-codes --dry-run` yourself: it is refused and changes nothing. Screenshot the command and its output |
| 8 | 18 | A task page whose state reads “the checks are decided: tell the agent to go on”, with the **Send to agent** button | In the demo, on check-coupon-codes press **More checks** and type the code it shows (no chat is involved); screenshot the card at the top of the task page; do not press Send to agent. Then run `python3 source/tutorials/shots/demo.py build --fresh` to put the demo back for the checks-* screens |
| 10 | 22 | A terminal: `harness task review waive --task check-coupon-codes` waiting at “To stop checking and let this version through, type …” | In a terminal in the demo workspace run the command; screenshot at the code prompt; then press Enter with nothing typed (“anything else cancels”) |
