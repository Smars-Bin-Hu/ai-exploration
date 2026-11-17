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
  title='[Task name: what was asked, in one plain sentence]',
  facts=m('[Kind] · Ticket: [ado:12345] · Repositories and environments: [shop_dw, DEV, IST] · Pull request: [link]'),
  body=[m('[What was asked, and what the agent understood: the questions it raised before it wrote any code.]'),
        m('[What it did: the problems it found, what it changed, how it was checked.]'),
        m('[What people decided: the few points where a person stepped in. Everything else the agent did.]'),
        m('[Where it is now: a pull request, an RCA on the ticket, an answer the team used.]')]),
 pages=[('tall', None, [m('[What this screenshot shows, and why it matters. Two or three sentences.]')]),
        ('wide', None, [m('[What this screenshot shows, and why it matters. Two or three sentences.]')])],
)

SAMPLE = dict(
 file='Sample (fake data)', footer='Showcase · Sample: fake data from test copies of the harness', task_kicker='Sample task',
 summary=dict(
  title='Load the region of every customer into the customer dimension',
  facts=['Development · Ticket: ado:300100 · Repository: warehouse_sql, tested on DEV and IST · Branch: feature/customer_dim_backfill'],
  body=[['The intake did not say what to do with accounts that have no region code. The agent asked before writing any code; the business answered: use the billing region, and “n/a” when there is none.'],
        ['The first version used an inner join, which drops those accounts. The independent review (a second agent that checks the work) failed it at load_customer.sql line 5. The fix is a left join; a count on DEV and IST shows every account kept.'],
        ['People answered two questions, approved the plan, one comment on the ticket and the write-back. The agent did everything else.'],
        ['The change is on a branch, ready for a pull request; the ticket has the test result.']]),
 pages=[('tall', 's-intake-tall', [['We dropped the business document, the field mapping, the meeting notes and a screenshot into the task. A program turned them into text, with no tokens spent.'],
          ['The agent read them all and wrote down what was still unclear, before it touched any code.']]),
        ('tall', 's-review-tall', [['The independent review read only the requirement and the change. In round 1 it failed the work: the inner join drops every account with no region code.'],
          ['The agent fixed it, and the next two rounds passed. Without this, the gap would have reached QAT.']]),
        ('wide', 's-changes', [['The fix, line by line: a left join, then the billing region, then “n/a”. You read the change before it goes anywhere near the repository.']]),
        ('wide', 's-held-both', [['The comment with the test result was held as a card with the exact text. It went in only after a person typed the code and approved.']]),
        ('wide', 's-refusals-list', [['git push, git reset and a direct change to the repository were refused by code, each with its reason. A sentence in a prompt could not have done this.']])],
)
