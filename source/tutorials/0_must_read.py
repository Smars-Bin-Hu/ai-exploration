# The one page at the top of "AI Exploration/3 Courses/Harness tutorials/": who the decks are for, the order,
# one line per deck, and the two courses inside the harness. No map of the folder: the build adds the pointer
# to AI Exploration/0 MUST READ.pdf under the text.

COVER = None
PAGES = []

CLOSING = dict(kicker='Harness tutorials · Read this first', title='Five picture books for working with the harness',
  text=[
   'Installed the harness? These picture books, one step per page, start where **Install the harness** ends.',
   ('steps', [
    '**A day with the harness**: one task, from the board to your commit. Read it first.',
    '**When the agent is stopped**: why the harness stops it, and what you do. When it happens.',
    '**Independent checks**: a second agent checks the work. When you want checks.',
    '**Outside systems and connections**: calls to company systems. When yours are connected.',
    '**Knowledge base**: pages on your code for the agent. When your team builds or keeps one.',
   ]),
   'Inside the harness, two courses run in Copilot chat in VS Code. Type:',
   ('list', [
    '`/harness-rookie-quick-start`: a first lesson that takes a newcomer through one practice task.',
    '`/harness-rookie-wondering`: how a coding agent and the harness work underneath. The agent reads '
    'the harness files, so it is the most direct way in, but it spends GitHub Copilot credits.',
   ]),
  ],
  notes='Decks: the cover lines of 1-5 (1.7.45). Courses: .github/skills/harness-rookie-quick-start/SKILL.md (description, '
        'part 4 practice task) and harness-rookie-wondering/SKILL.md (description; "read the real files" when the '
        'reference files do not have it). Credits: every chat turn is a Copilot request.')
