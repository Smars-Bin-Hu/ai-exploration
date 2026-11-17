# The one page at the top of "AI Exploration/3 Courses/Harness tutorials/": who the decks are for, the order,
# one line per deck, and the two courses inside the harness. No map of the folder: the build adds the pointer
# to AI Exploration/0 MUST READ.pdf under the text.

COVER = None
PAGES = []

CLOSING = dict(kicker='Harness tutorials · Read this first', title='Six picture manuals for the harness',
  text=[
   'For after **Install the harness**. Numbered small steps, a screenshot each.',
   ('steps', [
    '**A day with the harness**: one task, from start to your commit. Read it first.',
    '**A tour of the harness**: every screen of the harness and what you can do there.',
    '**When the agent is stopped**: why, and what you do.',
    '**Independent checks**: a second agent checks the work.',
    '**Outside systems and connections**: calls to company systems.',
    '**Knowledge base**: the team knowledge base, built and kept up.',
   ]),
   'After installing, in VS Code Copilot chat:',
   ('list', [
    '`/harness-rookie-quick-start` walks you through a first task.',
    '`/harness-rookie-wondering` teaches it all from the code (spends Copilot credits).',
   ]),
  ],
  notes='Decks: the cover lines of 1-6 (1.7.45). Courses: .github/skills/harness-rookie-quick-start/SKILL.md (description, '
        'part 4 practice task) and harness-rookie-wondering/SKILL.md (description; "read the real files" when the '
        'reference files do not have it). Credits: every chat turn is a Copilot request.')
