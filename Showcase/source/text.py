# The words of the Showcase deck: one real task (one intake) per deck. A summary page, then one page per screenshot,
# tall or wide. TEMPLATE holds grey hints ('m' runs) for the person to replace; SAMPLE is the same filled with fake data.
# An evidence page is (layout 'tall' | 'wide', picture or None, small heading, conclusion paragraphs).

def m(t): return [('m', t)]

SHOTS = ('Screenshots that make good evidence (one per page, all from this task): what it read and the questions it asked '
         '(Overview → Requirement, the part “Not clear yet”); the problem it found (Results → RCA, Results → Test, or a finding in Results → Review); '
         'what it changed (Results → Changes); how it was checked (Results → Test, or a query on DEV or IST); '
         'a plan, a write or a write-back that waited for your approval (the bar or card at the top of the task page); '
         'an action that was stopped (Records → Agent actions). Crop each one to the part that proves the point.')

TEMPLATE = dict(
 file='Real task template', footer='AI Exploration · Showcase · Real task', task_kicker='Real task',
 summary=dict(
  kind='[Development / RCA / Question]',
  title='[Task name: what was asked, in one plain sentence]',
  facts=m('Ticket: [ado:12345] · Repositories and environments: [shop_dw, DEV, IST] · Independent review: [rounds, how many FAIL] · People decided: [how many times]'),
  cards=[('What it understood', m('[What the requirement really asked, in plain words; the questions it raised before it wrote any code, and what you answered.]')),
         ('Problems it found', m('[Problems a person had not seen: a gap in the requirement, data that did not match, the real cause of a failure. Say who found it: the agent itself, or the independent review (a second agent that checks the work). Who would have found it otherwise, and when?]')),
         ('How it solved them', m('[What it changed or proposed, and how it was checked: tests on DEV or IST, a query, the independent review.]')),
         ('What people decided', m('[The few points where a person decided: answers, the plan, a write to a ticket or data, the write-back. Everything else the agent did.]'))],
  result=m('[What came out, and where it is now: a branch ready for a pull request, an RCA attached to the ticket, an answer the team used.]'),
  notgood=m('[Optional, but it makes the rest believable: where it went the wrong way, or where a person had to step in.]')),
 pages=[('tall', None, m('[Small heading: what this picture shows, in a few words]'),
         [m('[Conclusion: what the agent did, or what the harness gave us, and why it matters to the team. Two or three sentences.]')]),
        ('wide', None, m('[Small heading: what this picture shows, in a few words]'),
         [m('[Conclusion: what the agent did, or what the harness gave us, and why it matters to the team. Two or three sentences.]')])],
)

SAMPLE = dict(
 file='Sample (fake data)', footer='Showcase · Sample: fake data from test copies of the harness', task_kicker='Sample task',
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
 pages=[('tall', 's-intake-tall', ['It read the business papers itself'],
         [['We dropped the business document, the field mapping, the meeting notes and a screenshot into the task. A program turned them into text, with no tokens spent.'],
          ['The agent read them all and wrote down what was still unclear, before it touched any code.']]),
        ('tall', 's-review-tall', ['A second agent caught a bug'],
         [['The independent review read only the requirement and the change. In round 1 it failed the work: the inner join drops every account with no region code, at load_customer.sql line 5.'],
          ['The agent fixed it, and the next two rounds passed. Without this, the gap would have reached QAT.']]),
        ('wide', 's-changes', ['The fix, line by line'],
         [['A left join, then the billing region, then “n/a”. You read the change before it goes anywhere near the repository.']]),
        ('wide', 's-held-both', ['It waited for us before writing to the ticket'],
         [['The comment with the test result was held as a card with the exact text. It went in only after a person typed the code and approved.']]),
        ('wide', 's-refusals-list', ['What it was stopped from doing'],
         [['git push, git reset and a direct change to the repository were refused by code, each with its reason. A sentence in a prompt could not have done this.']])],
)
