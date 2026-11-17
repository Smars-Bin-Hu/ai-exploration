# Screenshots to take: 2 A tour of the harness

Placeholders in `source/tutorials/2_tour.py`. Every other step uses a board screenshot from `source/tutorials/img/_board/` (harness 1.7.45, the demo workspace, made-up data). Step numbers are the ones printed in the PDF; page numbers count the cover as page 1.

| Page | Step | What to capture | How |
| --- | --- | --- | --- |
| 11 | 28 | A task page while its agent works: **Stop** beside the **Say something** pill, and the reply panel open with **Steer** and **Queue** (and **Withdraw** if shown) | Only a task whose chat is in the middle of a turn shows these buttons, and a turn needs a sent message, which uses one Copilot request. Take it during real work instead of starting a chat for it. When a task you are running anyway is at work, open its page on the board and screenshot the pill with Stop. Then press **R** and screenshot the panel. Type nothing and press neither Steer nor Queue; close the panel with Esc. Save it as `source/tutorials/img/_board/tour-reply-working.png` and replace the `shot=` in step 28 with `pic=B + 'tour-reply-working.png'`. |
