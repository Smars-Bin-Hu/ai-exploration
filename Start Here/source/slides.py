# The English text of Start Here, retold from zh-Hans.md (approved 2026-11-11). build.py lays it out.
# A paragraph is a list of runs: plain strings, or ('b', text) for bold, ('i', text) for italic, ('a', text) for the accent colour.

COVER = dict(kicker='AI Exploration', title='Start here',
    sub='Why AI has not taken hold in our team’s real work, what is missing, and how my harness fills the gap.')

STORY = [
 dict(kicker='The problem', title='How most of us hand a task to AI today', fig='chain', paras=[
  ['Suppose you had to hand a real intake to Copilot today, from reading the requirement all the way to updating the ticket. How would you do it?'],
  ['My guess: first, you spend half an hour finding the related code and pasting it into Copilot piece by piece. You add a long explanation of what the code does, the background of the requirement, a to-do list and a list of don’ts, and then you hope it gets the whole task right.'],
  ['Second, when it has written the code, you log on to the DEV server yourself to run the tests and check the data. Third, you open Azure DevOps and update the ticket yourself. Fourth… you still read every line it wrote, because you do not trust it.'],
 ]),
 dict(kicker='The problem', title='Four reasons AI has not taken hold in our team', cards=[
  [('b','1. AI only writes code. The rest of the work is still mine. '),'Running tests, checking data, reading pipeline errors, updating tickets, looking into incidents: this is most of a task, and AI cannot touch any of it.'],
  [('b','2. It does not know our domain, and teaching it is slower than doing the work. '),'In every new chat I explain the code flow, the entry points, how the tables relate and where the traps are, all over again. ',('i','“I know exactly where to change the code, and I still have to teach it. By the time I finish the prompt, I could have done the job.”')],
  [('b','3. I do not dare to let go. '),'Will it push, drop a table, or connect to the wrong environment? It says “All tests pass.” You run them, and they all fail. It apologizes: “Sorry, my mistake.” What can you do? Next time you watch it again.'],
  [('b','4. The boss gets no answers. '),('i','“How much time does Copilot really save us? What does a task cost? Where does it get stuck?”'),' Nobody can say, so whether to roll it out across the team is a guess.'],
 ], closing=[
  ['Each one is small, but each one wears down the team’s confidence in AI. In the end people go back to what feels safe: they write the code themselves and use AI as a Google that can think. And there is a worry nobody says out loud: if AI does everything, what do people do?'],
  [('b','AI is still a chatbot.')],
 ]),
 dict(kicker='The conclusion', title='Two abilities are missing', fig='axes', paras=[
  ['After these months, my conclusion is that a team feels unsure about AI because two abilities are missing.'],
  [('a','Vertical ability: '),('b','how much the agent can do and how much it knows. '),'It knows our domain and understands the requirement. It updates tickets and reads pipeline errors. It runs tests and queries data on DEV and IST. When an incident happens, it finds the cause. This answers reasons 1 and 2.'],
  [('a','Horizontal ability: '),('b','how safe and comfortable the agent is to use. '),'You do not write long prompts. It asks you to approve the plan before it changes code, and to approve every write to an outside system. Guardrails stop wrong actions. A second agent checks the work. You can see the progress and the cost of every task. This answers reasons 3 and 4.'],
 ]),
 dict(kicker='The root cause', title='Both abilities sit outside the model', fig='outside', paras=[
  ['Many people first think the model is not smart enough, so they switch to Opus and turn the thinking effort up to the maximum. The bill goes up, and the problems stay.'],
  ['Both abilities sit in the layer around the model: what it can reach, what it can read, what controls it and what checks it. The industry calls this layer the harness, and sums it up as ',('b','Agent = Model + Harness.')],
  ['As for what people do: they stop doing every step by hand, and make the decisions only a person can make. They set the goal, answer the agent’s questions, approve the plan and approve the result.'],
 ]),
 dict(kicker='The solution', title='My harness adds both abilities to Copilot', fig='mapping', wide=True, paras=[
  ['I built a harness that sits around GitHub Copilot. The model stays the same. What changes is the work the agent can do, what it knows, and the layer that controls and checks it. Each of the next pages shows one feature, with a screenshot from the real board.'],
 ]),
]

L = ['The problem it solves', 'How it works', 'Key points', 'What you can do with it', 'Behind it']
FEATURES = [
 ('Vertical', 'Knows our domain and the requirement', 'kb-overview', [
  'The agent does not know our domain, so you explain it again in every new chat. It reads a requirement word by word, and the traps in it show up only after the code is written.',
  'The agent learns a domain once and keeps it in a knowledge base: one small card per object, saying what it is for, its rules, what it uses and where the traps are. Scripts work out the structure; the model writes the meaning. When it reads a requirement, it checks it against the knowledge base, lists every point that is unclear or does not match, and asks you.',
  'Every card records the version of the code it was read from, so when the code changes, the cards that are out of date can be listed and learned again. Word and Excel files from the business are turned into text by a program, with no tokens spent.',
  'New people, new chats and new agents all start from the same knowledge, and you do not explain it again. Problems in the requirement are listed before any code is written, ready for you to take to the business.']),
 ('Vertical', 'Reads and writes tickets and pipelines', 'reach', [
  'Tickets and pipelines live in Azure DevOps, where the agent cannot reach. Reading a ticket, posting a result, checking a pipeline: you still do it yourself.',
  'The harness wraps Azure DevOps in a tool pack: a fixed program and a set of skills, so the agent never builds commands by hand. It reads tickets, their comments and history, pipeline runs, logs and test results. It adds comments, changes fields, creates tickets and links them. Connections and sign-ins are set up once on the board, one line per system: its status, the identity it uses, and when it was last checked.',
  'There is no delete. A ticket that is not linked to the task cannot be written. Every write waits for your approval. Many companies switch MCP off; a tool pack runs in the terminal the editor already allows, so it works on a company computer too.',
  'Link the ticket when you open a task. The agent reads the requirement from it, and writes the result back when the work is done.']),
 ('Vertical', 'Finds the cause when a pipeline fails', 'rca', [
  'When a pipeline fails or an incident happens, someone goes through the logs and the commits by hand, and it often takes half a day.',
  'The agent reads the pipeline run, its log and the commits in it by itself, and writes an RCA: what it saw; the evidence, each item pointing to the command that produced it; the cause; how it checked; and the next step.',
  'A task that looks for a cause only reads; it changes nothing. Every piece of evidence can be checked again, so it is not just the agent’s opinion.',
  'Send the RCA to a colleague or attach it to the ticket. Then fork it into a fix task, and its findings and material go with it.'],
  'A test task against a test copy of Azure DevOps.'),
 ('Vertical', 'Runs tests and checks data on DEV and IST', None, [
  'Once the code is written, you still log on to the server to run the tests, and query and compare the data yourself.',
  'The agent connects to the DEV and IST databases with sqlcmd in the terminal, runs the tests and queries the data. Every command and what it returned is kept in the task.',
  'Read-only queries run straight away. Statements that change data run only after you open the DEV or IST connection for this task. QAT is not opened by default, and PROD is never opened.',
  'Let the agent run the tests and check the data, then give you the results to review.']),
 ('Horizontal', 'No long prompts: start a task from a form', 'new-task', [
  'Opening a task meant writing a long prompt with the background, the rules and the steps, which is slower than doing the work yourself.',
  'A new task starts from a form on the board: its name, the kind of task, the knowledge base, the linked tickets, what to do, the model and the thinking effort. The board writes the first message to the agent for you. Each task is a folder: the requirement, the plan and the progress are files, not chat history.',
  'The process and the rules live in the harness, not in your prompt. The kind of task decides how much process it goes through: light for a question, full for development. Start a new chat at any time, and the task picks up where it stopped.',
  'Fill in only what you alone know, and open a task in a few sentences.']),
 ('Horizontal', 'Two approvals: the plan and the write-back', 'approve-plan', [
  'AI starts writing code straight away, and you find out what it changed afterwards. Nobody checks before the code goes into the repository.',
  'The agent can write only in its own task folder. Until you approve the plan, it cannot even write to the place for code in that folder. When the code is done, you approve again before it is written back to the repository.',
  'An approval is a button on the board, and you type a code tied to this plan; if the plan changes, it needs a new approval. Only a browser paired with your terminal can press it, so the agent cannot. The write-back only creates a branch; it does not commit or push.',
  'See what it will change before it starts, and what it changed before it is written back.']),
 ('Horizontal', 'Your approval before any write to an outside system', 'held-both', [
  'People let the agent read tickets but do not dare to let it write: it might write to the wrong ticket, or write the wrong thing.',
  'Every write the agent makes to an outside system is stopped first and becomes a card on the board: which ticket, what kind of write, and the exact text it will write.',
  'You type the code on the card and press Approve. The approval covers only this one command and lasts 10 minutes. The agent cannot approve it itself.',
  'Let the agent write to tickets, with the last step in your hands.']),
 ('Horizontal', 'Guardrails', 'refusals', [
  'People worry it will push, reset, delete files, change the wrong repository, or even change the rules that control it. Writing “do not” in a prompt does not stop it.',
  'Before any tool call runs, it goes through the same check program, the gate. Dangerous git commands, direct changes to the target repository, changes to the gate’s own rules, and writing code before the plan is approved are all refused by code, with the reason.',
  'Code does the stopping, not a sentence in a prompt. Every refusal is recorded and counted in the report.',
  'Give the agent more room to work, without worrying that it crosses the line.']),
 ('Horizontal', 'Independent review', 'task-review', [
  'An agent that checks its own work grades itself generously: “All tests pass”, and then they all fail.',
  'Finished work goes to a second agent, the reviewer. It has not seen the author’s reasoning and looks only at the requirement, the result and the change. It has no edit tools. Every finding must point to a file and a line, and its first line says PASS or FAIL.',
  'You choose on the task page how many checks in a row the work must pass (off, or 1 to 5); only you can switch it on. Code counts the passes; the agent does not report them. Each extra round costs more, and the board tells you so.',
  'Turn “it says it is done” into “another agent checked it against the requirement”.']),
 ('Horizontal', 'The board: every task at a glance', 'board-list', [
  'With several chats and several tasks open, you cannot tell which one is working, which one is waiting for you, and for how long.',
  'Every open task is on one board: what it is doing, what it waits for from you, and how long it has waited. When the agent stops, a hook records “waiting for you”, so you do not have to go through one session after another.',
  'The states on the board come from the harness’s own records, not from what the agent says.',
  'Open the board each day and deal first with the tasks that wait for you. One button carries on a task in a new chat.']),
 ('Horizontal', 'Auditability', 'report', [
  'Many teams do not know where the time and money of a complex AI task went.',
  'The harness reads Copilot’s session records and its own hook log, and counts the time of every stage, the tokens and Credits spent, the tool calls and the refused calls, and the results of the independent checks.',
  'Every report is generated by code, not written by the agent, and reading it costs no tokens.',
  'Save any report as an HTML file, to share with the team or to report to a leader.',
  'The /harness-task-report skill reads the report for you, then goes through the agent’s reasoning and tool calls to find where it went the long way round: a badly written tool, an unclear rule, or the wrong context loaded. Then the harness can be fixed where it is really wrong. [Second skill: to be added]']),
]

INDEX = dict(kicker='Where to go next', title='What is in this folder', fig='tree', paras=[
  [('b','Learn harness engineering. '),'Go to ',('a','Harness Engineering 101/'),'. Slidedoc courses, from Basic to Advanced, then Mindset.'],
  [('b','See real work. '),'Go to ',('a','Showcase/'),'. ',('a','Real Tasks/'),' holds real task pages, each with a one-page note. ',('a','Lessons/'),' holds the wrong turns I took on the way.'],
  [('b','Use it yourself. '),'Go to ',('a','Harness/'),'. The install package, the knowledge base, the programs it needs, and the install and user guides.'],
])
