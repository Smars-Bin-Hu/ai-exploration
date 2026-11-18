# The one page at the top of "AI Exploration/3 Courses/Harness tutorials/": where Install is, when to open each deck,
# and the words the decks use. No map of the folder: the build adds the pointer to AI Exploration/0 MUST READ.pdf
# under the text. The two /harness-rookie-* courses are on that map, so they are not repeated here.

COVER = None
PAGES = []

CLOSING = dict(kicker='Harness tutorials · Read this first', title='Six picture manuals: when to open each',
  text=[
   'Not installed yet? First **AI Exploration/4 Install the harness/**.',
   ('steps', [
    '**A day with the harness**: read it first. One task, start to your commit.',
    '**A tour of the harness**: after 1, look through once to see what it can do.',
    '**When the agent is stopped**: open it the first time the agent stops.',
    '**Independent checks**: only when you turn checks on.',
    '**Outside systems and connections**: only if your company has tool packs.',
    '**Knowledge base**: steps 33–37 for any task; all of it if you own the team KB.',
   ]),
   ('list', [
    '**task**: one job, one folder · **board**: the page of all tasks · **gate**: checks each agent call',
    '**requirement**, **plan**: you confirm each · **write-back** = **promote**: its files into your repo',
    '**round**: one more pass · **Live**: the chat as it runs · **Records**: what happened · **Credits**: Copilot usage',
    '**Paired**: this browser can press the buttons · **No chat**: the board cannot reach the agent',
   ]),
  ],
  notes='When to open: the person (2026-11-17). Install: the folder AI Exploration/4 Install the harness/. '
        'Words, harness 1.7.45: task = one folder (docs/00-overview.md part 2); board = harness task board (docs/04-reference.md); '
        'gate checks every tool call (docs/00-overview.md part 2, docs/12-guardrails-and-gate.md); requirement and plan = '
        'Confirm requirement, Approve plan, each with a code (docs/01-quickstart.md part 5, steps 3 and 5); write-back = promote, the task’s files into the repository: '
        'a new branch feature/<task>, not committed (a knowledge base: committed on its base branch, promote_target.py L1-11) (quickstart step 9; messages.en.json promote.question "the promote (write-back repo)"); '
        'round = task open again after a promote, a new plan and approval (messages promote.done_already; quickstart "One more round after a write-back"); '
        'Live follows the chat (messages desk.live.hint); Records = Log, Task Record, Agent actions (modules/task/web/desk.js GROUPS); '
        'Credits = the usage Copilot records (docs/02-features.md, the columns of the list); Paired = the buttons act, approvals still ask '
        'the code (messages board.serve.paired); No chat = no VS Code chat linked, nothing is sent (messages board.vscode.nochat, send.refused.unbound).')
