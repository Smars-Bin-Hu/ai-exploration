# The words of the Showcase decks. TEMPLATE: what to fill in, as grey italic hints ('m' runs). SAMPLE: the same pages filled
# with fake data from a test copy of the harness, to show how a finished one looks.
# A box is (label, picture or None, where to take it, which tasks need it, caption).

def m(t): return [('m', t)]

TEMPLATE = dict(
 file='Real task template', footer='AI Exploration · Showcase · Real tasks', kicker='Showcase · Real tasks', task_kicker='Real task',
 overview=dict(
  title='[What these real tasks show, in one sentence]',
  paras=[m('[One person can keep several agents working at once: the board shows each task, and the person only deals with the ones that wait for them.]'),
         [('b', 'Tasks in this folder')],
         m('[Task name] · [Development / RCA / Question] · [one line: what it did]'),
         m('[Task name] · [kind] · [one line]'),
         m('[Task name] · [kind] · [one line]'),
         [('b', 'How to read each task')],
         ['A one-page summary, then the evidence: what the agent understood and found (vertical ability), and where people decided and what was stopped (horizontal ability). The saved task page (HTML) sits next to it with every detail.']],
  box=('Several tasks at once', None, 'Board → List, taken while several tasks are working, not only waiting; crop to the rows', 'All', m('[One line: how many tasks ran side by side, and how many waited for you]'))),
 summary=dict(
  kind='[Development / RCA / Question]',
  title='[Task name: what was asked, in one plain sentence]',
  facts=m('Ticket: [ado:12345] · Repositories and environments: [shop_dw, DEV, IST] · Independent review: [rounds, how many FAIL] · People decided: [how many times]'),
  cards=[('What it understood', m('[What the requirement really asked, in plain words; the questions it raised before it wrote any code, and what you answered.]')),
         ('Problems it found', m('[Problems a person had not seen: a gap in the requirement, data that did not match, the real cause of a failure. Say who found it: the agent itself, or the independent review (a second agent that checks the work). Who would have found it otherwise, and when (in QAT? in PROD?).]')),
         ('How it solved them', m('[What it changed or proposed, and how it was checked: tests on DEV or IST, a query, the independent review.]')),
         ('What people decided', m('[The few points where a person decided: answers, the plan, a write to a ticket or data, the write-back. Everything else the agent did.]'))],
  result=m('[What came out, and where it is now: a branch ready for a pull request, an RCA attached to the ticket, an answer the team used.]'),
  notgood=m('[Optional, but it makes the rest believable: where it went the wrong way, or where a person had to step in.]')),
 vertical=dict(
  task='[task name]', title='What it understood and found',
  boxes=[('1  What it read and asked', None, 'Overview → Requirement: the part “Not clear yet”; or Intake; or the chat where it asked', 'All', m('[One line: what this shows]')),
         ('2  The problem it found', None, 'Results → RCA (an RCA task); Results → Test (a query on DEV or IST); or Results → Review (a finding)', 'All', m('[One line: what this shows]')),
         ('3  What it changed', None, 'Results → Changes (development); for a question, its answer in the chat', 'Development, Question', m('[One line: what this shows]')),
         ('4  How it was checked', None, 'Results → Test: the results by environment; or the query and its output on DEV or IST', 'Development, RCA', m('[One line: what this shows]'))]),
 horizontal=dict(
  task='[task name]', title='Where people decided, and what was stopped',
  boxes=[('The plan waited for your approval', None, 'The bar at the top of the task page; or Overview → Plan', 'Development', m('[One line]')),
         ('A write waited for your approval', None, 'The card on the task page (a comment, a field, data)', 'When it wrote to a ticket or data', m('[One line]')),
         ('An action it was stopped from', None, 'Records → Agent actions: the box of blocked calls', 'When anything was blocked', m('[One line]')),
         ('The write-back waited for your approval', None, 'The bar at the top of the task page, before you approve it', 'Development', m('[One line]'))]),
)

SAMPLE = dict(
 file='Sample (fake data)', footer='Showcase · Sample: fake data from test copies of the harness', kicker='Showcase · Sample, fake data', task_kicker='Sample task',
 overview=dict(
  title='One person, several agents at once',
  paras=[['Several test tasks ran on one board at the same time. The person only dealt with the tasks that waited for them; the rest went on by themselves.'],
         [('b', 'Tasks in this folder')],
         ['customer_dim_backfill · Development · loaded the region of every customer into the customer dimension'],
         ['rca-build · RCA · found why the nightly pipeline failed'],
         ['qa-linked · Question · answered a question on a ticket and wrote the answer back'],
         [('b', 'How to read each task')],
         ['A one-page summary, then the evidence: what the agent understood and found (vertical ability), and where people decided and what was stopped (horizontal ability). The saved task page (HTML) sits next to it with every detail.']],
  box=('Several tasks at once', 's-board-list', '', '', ['Four open tasks on one board; each line says what it waits for from the person. (The pictures in this sample come from several test tasks.)'])),
 summary=dict(
  kind='Development',
  title='Load the region of every customer into the customer dimension',
  facts=['Ticket: ado:300100 · Repository: warehouse_sql, tested on DEV and IST · Independent review: 3 rounds, 1 FAIL · People decided: 5 times'],
  cards=[('What it understood', ['It read the intake (a business document, a field mapping and meeting notes) and saw that it did not say what to do with accounts that have no region code. It asked before writing any code. The business answered: use the billing region, and “n/a” when there is none.']),
         ('Problems it found', ['The first version still used an inner join, which drops every account without a region code. The independent review (a second agent that checks the work) caught it and pointed to load_customer.sql, line 5. Without it, the missing accounts would have shown up in QAT, in front of the business.']),
         ('How it solved them', ['A left join, then the billing region, then “n/a”. A count on DEV and IST shows every account is still there with a region. The review then passed twice in a row.']),
         ('What people decided', ['Answered two questions, approved the plan, approved one comment on the ticket, and approved the write-back. The agent did everything else.'])],
  result=['The change is on the branch feature/customer_dim_backfill, not committed, ready for a pull request. The ticket has a comment with the test result.'],
  notgood=['The first version had the inner join; only the independent review stopped it.']),
 vertical=dict(
  task='customer_dim_backfill', title='What it understood and found',
  boxes=[('1  What it read and asked', 's-intake', '', '', ['The intake: a business document, a field mapping, meeting notes and a screenshot, turned into text with no tokens spent.']),
         ('2  The problem it found', 's-task-review-rounds', '', '', ['Round 1 failed: the inner join drops accounts with no region code. Round 2 passed.']),
         ('3  What it changed', 's-changes', '', '', ['The fix: a left join, then the billing region, then “n/a”.']),
         ('4  How it was checked', 's-test', '', '', ['The test guide it wrote: run on DEV (passed), then on IST.'])]),
 horizontal=dict(
  task='customer_dim_backfill', title='Where people decided, and what was stopped',
  boxes=[('The plan waited for your approval', 's-approve-plan', '', '', ['Until the plan was approved, it could not write code.']),
         ('A write waited for your approval', 's-held-both', '', '', ['A comment to the ticket waited, then went in once approved.']),
         ('An action it was stopped from', 's-refusals-list', '', '', ['git push, git reset and a direct change to the repository were refused.']),
         ('The write-back waited for your approval', 's-promote', '', '', ['The change goes to a new branch only after this approval.'])]),
)
