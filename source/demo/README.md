# Demo workspace for recording

A workspace of harness 1.7.45 with made-up repositories and made-up tasks, and its board, to record screen videos in. Nothing in it comes from a person or a company.

## Commands

Run them from the root of this repository.

| Command | What it does |
| --- | --- |
| `python3 source/demo/demo.py setup` | Makes the workspace in `/Users/Shared/harness-demo` (about a minute), keeps its starting point, starts the board and opens it in your browser. Run it again to make it from scratch. |
| `python3 source/demo/demo.py reset` | Stops the board, puts the workspace back to the starting point (a few seconds), starts the board again. |
| `python3 source/demo/demo.py stop` | Stops the board. |
| `python3 source/demo/demo.py start` | Starts the board again, after a stop. |
| `python3 source/demo/demo.py open` | Opens the running board in your browser again, if you closed the tab. |

Each command takes `--at FOLDER` for another folder; give the same folder to every command. `--no-vscode` starts a board that does not connect to VS Code, so no button on it can reach a chat (good for a rehearsal). `--no-browser` keeps the pairing link in `FOLDER/pair-url.txt` instead of opening it.

The board runs on `http://127.0.0.1:8846/` (the screenshot rig in `source/tutorials/shots/` uses 8845, so both can run). It needs `~/Developer/DE-agentic-harness` with the tag `1.7.45`; another path goes in `HARNESS_GIT`.

To record a live chat, open the workspace in VS Code first: `code /Users/Shared/harness-demo/harness`.

## What is in it

Three made-up repositories: `orders-service` (Python), `shop-dw` (SQL) and a knowledge base for `shop-dw`. The person is called Alex.

| Task | State | Use it to show |
| --- | --- | --- |
| `fix-total-rounding` | The requirement waits for Confirm requirement | The first approval: read REQ.md, Confirm requirement, type the code. Start a flow live from here. |
| `add-order-notes` | The plan waits for Approve plan | Reading PLAN.md and approving it. |
| `limit-order-items` | Dry run done, waits for Approve promote | The Changes tab, the diff, and the write-back approval. |
| `cache-stock-counts` | Waits for your run on DEV | A task blocked on the person: the run form, and what the agent asked for. |
| `raise-stock-timeout` | Closed, written back | The Changes tab of a finished task, the commit message, the report. |
| `learn-orders` | Closed, a knowledge base task | The knowledge base: the domain `orders` and its cards. |

For a brand new task, use New task on the board with words such as: `Let a customer ask for gift wrap on an order in orders-service. Done when an order can carry gift_wrap: true and the confirmation says so.` That spends credits (see below).

The prepared tasks have no real chat behind them. Once you confirm or approve on one of them, the board offers Go on in a new chat, which makes a real one.

## Buttons that spend Copilot credits

Every one of these makes a Copilot chat in VS Code or sends a message to one. Each turn the agent then takes is a premium request.

| Where | Button |
| --- | --- |
| Lobby, New task window | Create and send |
| Task page, card of a wait (after Confirm requirement, Approve plan, Approve promote, Recover) | Send to agent |
| Task page and Lobby, on a task with no chat | Go on in a new chat (it shows the message first; its Send makes the chat) |
| Task page, Say something panel (key R) | Send, Steer, Queue, Try again |
| Task page, context card | Compact |
| Task page, a code block in a delivered file | Ask agent, then Send to agent |
| Task page, run form | Save and send to the agent (only when the task has a chat) |
| Task page, a held call or Intake | Tell the agent to run it, Tell the agent again, Tell the agent |
| Bottom right, the one-click skills | Send |
| Gate, approving a held call whose agent stopped | The board sends the decision to the chat by itself |

Safe, they spend nothing: Enter, the tabs, Confirm requirement, Approve plan, Approve promote (each asks for a code), Accept and close, Close, Archive, Run on a code block (it runs on your computer), Stop, Withdraw.

## What can still show personal data

The workspace lives in `/Users/Shared`, not in your home folder, so every path the board shows is `/Users/Shared/harness-demo/...`. The person in the workspace is Alex, and the repositories are committed by "Demo Developer". A check of the Enter screen, the Lobby, every tab of every task, the New task window, the report, and the windows at the bottom right found no login name and no home path, except these:

| Where | What it shows | What to do |
| --- | --- | --- |
| Get ready (the sliders button at the bottom right, `/setup`) | Your own `harness` command, `/Users/<login>/bin/harness`, and the Python path when you point at it | Do not open Get ready on camera. |
| The footer of every page | `© 2026 Smars Hu · Apache License 2.0`, the harness's own license line | It names the author of the harness. Crop it out if you do not want the name on screen. |
| Restart VS Code (Enter screen) | The titles of every chat that runs in VS Code, in any folder | Close your other chats first, or do not press it on camera. |
| VS Code itself | Your GitHub account (Accounts icon, Copilot status), recent folders, a terminal prompt with your login name | Show only the chat panel, and use a terminal whose prompt shows no name. |
| The browser | The first link carries a pairing code | Start recording once the board is open. |

A chat you make while recording stays in VS Code after `reset`. Delete it there if you do not want it in the list.
