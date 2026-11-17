# The English text of the leader deck (Why AI-assisted development has not taken off), retold by meaning from zh-Hans.md (v4, 2026-11-12). build.py lays it out.
# A paragraph is a list of runs: plain strings, or ('b', text) for bold, ('i', text) for italic, ('a', text) for the accent colour.

COVER = dict(kicker='AI Exploration', title='Why AI-assisted development has not taken off in our team, and what is missing',
    sub='And how the layer I added around Copilot, a harness, fills the gap.')

STORY = [
 dict(kicker='The problem', title='How we hand a task to AI today', fig='chain', paras=[
  ['Take an ordinary intake, from getting the requirement to closing the ticket. It takes about eight things: read the requirement, find the code to change, change it, run the tests on DEV, check that the data is right, look for errors in the pipeline, update the ticket, and check everything once more. Of those eight, Copilot helps with one: changing the code.'],
  ['Even for that one, you first spend half an hour getting it ready. You find the related code and paste it into the chat piece by piece. You explain what the code does and where the requirement came from, and add a list of things to do and things not to do. Then you hope it gets it right the first time.'],
  ['When it is done, the rest is still yours. You log on to DEV to run the tests and check the data, open Azure DevOps to update the ticket, and read every line it wrote, because you do not dare to trust it.'],
 ]),
 dict(kicker='The problem', title='Four reasons AI is not part of our real work', cards=[
  [('b','1. AI only writes code. The rest of the work is still mine. '),'Running tests, checking data, reading pipeline errors, updating tickets, looking into incidents: this is most of a task, and AI cannot touch any of it.'],
  [('b','2. It does not know our systems, and teaching it is slower than doing the work. '),'In every new chat I put the code flow, the entry points, how the tables relate and where the traps are into the prompt, all over again. ',('i','“I know exactly where to change the code, and I still have to teach it. By the time I finish the prompt, I could have done the job.”')],
  [('b','3. I do not dare to let go. '),'Will it push, drop a table, or connect to the wrong environment? It says “All tests pass.” You run them, and they all fail. It apologizes: “Sorry, my mistake.” What can you do? Next time you watch it again.'],
  [('b','4. The boss gets no answers. '),('i','“How much time does Copilot really save us? What does a task cost? Where does it get stuck?”'),' Nobody can say, so whether to roll it out across the team is a guess.'],
 ], closing=[
  ['Each one is small, but each one wears down the team’s confidence in AI. In the end people go back to what feels safe: they write the code themselves and use AI as a Google that can think. And there is a worry nobody says out loud: if AI does everything, what do people do?'],
  [('b','AI is still a chatbot.')],
 ]),
 dict(kicker='The conclusion', title='Two abilities are missing', fig='axes', textw=6.6, paras=[
  ['After these months, my conclusion is that a team has no confidence in AI because two abilities are missing.'],
  ['First, a chat and an agent are different. A chat only answers you; reading files, running commands and updating tickets are still up to you. An agent acts by itself: it reads files, runs commands and uses tools, step by step. Copilot’s agent mode is an agent. But an agent alone is not enough.'],
  [('a','Vertical ability: '),('b','how much the agent can do and knows. '),'It knows our systems and understands the requirement. It reads and updates tickets in Azure DevOps and reads pipeline errors. It runs tests and checks data on DEV and IST. When something fails, it finds the cause. This answers reasons 1 and 2.'],
  [('a','Horizontal ability: '),('b','how safe and easy the agent is to use. '),'No long prompt to start a task. You approve its plan before it starts, and it waits for you before it puts code into the repository, writes to a ticket or changes data. Code stops dangerous actions. A second agent checks the work. You see the progress, time and cost of every task. This answers reasons 3 and 4, and the long prompt in reason 2.'],
 ]),
 dict(kicker='The root cause', title='Both abilities sit outside the model', fig='outside', paras=[
  ['Many people first think the model is not smart enough, so they switch to Opus and turn its thinking setting up to the maximum. The bill goes up, and the problems stay.'],
  ['That is because neither ability is in the model. Both are in the layer around it: which systems the agent can reach, what it can read, what controls it and what checks it. The industry calls this layer the harness, and sums it up as ',('b','Agent = Model + Harness.')],
  ['So what do people do? They stop doing every step by hand, and make the decisions only a person can make: they set the goal, answer the agent’s questions, approve the plan and approve the result.'],
 ]),
 dict(kicker='The solution', title='My harness adds both abilities to Copilot', fig='what', paras=[
  ['I built a harness that sits around GitHub Copilot. It is a folder on your own computer: you unzip it from the Harness folder, follow the install guide once, and open it in VS Code. From then on, Copilot works by its rules.'],
  ['It holds two things: rules written for Copilot, which Copilot reads whenever it opens a folder; and small programs that run before and after every step of the agent, to check it and record it. Copilot supports both by itself. It needs only Python, and no server.'],
  ['Two words appear on every page after this one:'],
  [('b','Task. '),'In the harness, one piece of work is one task. A task is a folder: the requirement, the plan, the progress and the result are files in it, not chat history.'],
  [('b','Board. '),'A page the harness opens in your browser, from your own computer. On it you start tasks, give approvals, and see how far each task has got.'],
 ]),
 dict(kicker='The solution', title='Which feature answers which reason', fig='mapping', wide=True, paras=[
  ['The model stays the same. What changes is what the agent can do, what it knows, and the layer that controls and checks it. Each of the next pages shows one feature; the screenshots are from the real harness, with test data.'],
 ]),
]

L = ['The problem it solves', 'How it works', 'Key points', 'What you can do with it', 'Behind it']
FEATURES = [
 ('Vertical', 'Knows our systems and understands the requirement', 'kb-cards', [
  'The agent does not know our systems, so you explain them again in every new chat. It reads a requirement word for word, and the traps in it show up only after the code is written.',
  'The agent learns one area of the business at a time (orders, say) and keeps it in a knowledge base: one small card per object, such as a table or a stored procedure, with what it is for, its rules, what it uses and where the traps are. A program works out from the code which objects exist and what calls what; the model writes what each one means. When it reads a requirement, it checks it against the knowledge base and asks you about every point that is unclear or does not match. Word and Excel files from the business are turned into text by a program, with no tokens spent.',
  'Learning an area is a task of its own: you approve which objects it will learn, then it writes the cards batch by batch. If a card says one object uses another, the program checks that against the code; a link it cannot find is refused. What the code cannot tell, it lists for a person to fill in. Each card records the version of the code it came from, so out-of-date cards can be found and learned again.',
  'New people, new chats and new agents all start from the same knowledge. Problems in the requirement are listed before any code is written, ready for you to take to the business.'],
  'On screen, each area of the business is a domain.'),
 ('Vertical', 'Works with tickets and pipelines in Azure DevOps', 'reach-table', [
  'Tickets and pipelines live in Azure DevOps, where the agent cannot reach. Reading a ticket, posting a result, checking a pipeline: you still do it yourself.',
  'The harness comes with a program for Azure DevOps that the agent calls directly, so it never builds commands by hand. The agent can read tickets, their comments and history, and pipeline runs, logs and test results. It can add comments, change fields, create tickets and link them. You set up connections and sign-ins once on the board, one line per system: whether it is connected, which identity it signs in with, and when it was last checked.',
  'It cannot delete. It can write only to tickets linked to the task, and every write waits for your approval (page 14). Many companies turn off Copilot’s plug-ins (MCP servers) for safety. This program is not a plug-in: it is a normal command the agent runs in the terminal, which Copilot may already use, so it works on a company computer too.',
  'Link the ticket when you start a task. The agent reads the requirement from it by itself, and writes the result back when the work is done.']),
 ('Vertical', 'Finds out why a pipeline failed', 'rca', [
  'When a pipeline fails or an incident happens, someone goes through the logs and the commits by hand, and it often takes half a day.',
  'The agent reads the pipeline run, its log and the commits in it by itself, and writes its findings as an RCA in five parts: what it saw; the evidence, each item pointing to the command that produced it; the cause; how it checked; and the next step.',
  'A task that looks for a cause only reads; it changes nothing. Every piece of evidence can be checked by running its command again, so it is more than the agent saying “I think”.',
  'Send the RCA to a colleague or attach it to the ticket. Then start a fix task from it, and its findings and material go with it.'],
  'A test task, against a simulated Azure DevOps.'),
 ('Vertical', 'Runs tests and checks data on DEV and IST', 'envs', [
  'Once the code is written, you still log on to the server to run the tests, and query and compare the data yourself.',
  'The agent connects to the DEV and IST databases with sqlcmd in the terminal, runs the tests and queries the data. Every command and what it returned is kept in the task.',
  'Read-only queries run straight away. A statement that changes data first waits for you to approve it. Or press one button on that waiting card to open DEV or IST for this task; after that, its changes there run without asking you each time. QAT is not opened by default. PROD is always read only: no one can open it for changes in a task.',
  'Let the agent run the tests and check the data, then give you the results to review.']),
 ('Horizontal', 'No long prompts: start a task from a form', 'new-task', [
  'Starting a task meant writing a long prompt with the background, the rules and the steps, which is slower than doing the work yourself.',
  'A new task starts from a form on the board: a name, the kind of task, which knowledge base to use, which tickets to link, what to do, which model, and how hard it should think. The board writes the first message to the agent for you.',
  'The process and the rules live in the harness, not in your prompt. The kind of task decides how much process it goes through: light for a question, full for development. Start a new chat at any time, and the task picks up where it stopped, because the requirement, the plan and the progress are in its folder.',
  'Fill in only what you alone know, and start a task in a few sentences.']),
 ('Horizontal', 'You approve the plan and the result', 'approve-plan', [
  'AI starts changing code straight away, and you find out what it changed afterwards. Nobody checks the change before it goes into the repository.',
  'The agent can write only in its own task folder. Until you approve the plan, it cannot even write to the code folder in the task (DEV/ on screen, which has nothing to do with the DEV environment). The code is written in the task first; when it is done, you approve once more before it goes into the repository.',
  'You press Approve on the board and type the short code it shows; the code works only for this plan, so if the plan changes, you approve again. The agent cannot do this itself. When the change goes into the repository, the harness creates a new branch and writes the change there, but does not commit or push: you commit and push after you have looked.',
  'See what it will change before it starts, and what it changed before it goes in.']),
 ('Horizontal', 'You approve every write to a ticket or a database', 'held-both', [
  'People let the agent read tickets but do not dare to let it write: it might write to the wrong ticket, or write the wrong thing. Letting it change data is even harder.',
  'Every time the agent writes to an outside system (adding a comment, changing a field, changing data), the write is stopped first and becomes a card on the board: where it will write, what it will do, and the exact text.',
  'You type the code on the card and press Approve. The approval covers only this one command and lasts 10 minutes. After you approve, the agent runs the same command again; this time it goes through, and only then is it written. If the agent is not waiting, a button on the card tells it. The agent cannot approve anything itself. Another button opens the task’s own linked tickets to the agent; after that, its writes to those tickets stop asking you.',
  'Let the agent write to tickets, with the last step in your hands.']),
 ('Horizontal', 'Guardrails', 'refusals-list', [
  'People worry it will push, reset, delete files, change the wrong repository, or even change the rules that control it. Writing “do not” in a prompt does not stop it.',
  'Every time the agent acts (changing a file, running a command), the action first goes through the same check program (the screen calls it the gate). Dangerous git commands, direct changes to the target repository, changes to the check program’s own rules, and writing code before the plan is approved are all refused, with the reason.',
  'Code does the stopping, not a sentence in a prompt. Every refusal is recorded and counted in the report.',
  'Give the agent more work, without worrying that it crosses the line.']),
 ('Horizontal', 'Independent review', 'task-review-rounds', [
  'An agent that checks its own work grades itself generously: “All tests pass”, and then they all fail.',
  'Finished work goes to a second agent for checking. It has not seen how the first agent thought, and looks only at the requirement, the result and the change. It cannot change files. Every finding must point to a file and a line, and its first line says PASS or FAIL.',
  'You choose on the task page how many checks in a row the work must pass (off, or 1 to 5); only you can switch it on. Choose 2, for example, and it needs two PASSes in a row: after a FAIL, the agent fixes the work and it is checked again. Each check is done by a new checker, and code counts the passes, not the agent. Each extra round costs more, and the board tells you so.',
  'Turn “it says it is done” into “another agent checked it against the requirement”.']),
 ('Horizontal', 'The board: every task at a glance', 'board-list', [
  'With several chats and several tasks open, you cannot tell which one is working, which one is waiting for you, and for how long.',
  'Every open task is on the board: what it is doing, what it is waiting for from you, and how long it has waited. When the agent stops, the harness records “waiting for you”, so you do not have to go through one chat after another.',
  'The states on the board come from the harness’s own records, not from what the agent says.',
  'Open the board each day and deal first with the tasks that wait for you. One button carries a task on in a new chat.']),
 ('Horizontal', 'Auditability', 'report-key', [
  'Many teams do not know where the time and money of a complex AI task went.',
  'The harness reads the conversation record Copilot keeps and its own log, and works out the time of each stage, the tokens and Copilot usage spent (Credits on screen), how many actions the agent took, how many were stopped, and the results of the independent checks.',
  'Every report is worked out by a program, not summed up by the agent, and reading it costs no tokens.',
  'Save any report as an HTML file, to share with the team or to report to a leader. Two reviews go further; see the next page.']),
]

WIDE = {'kb-cards': 1.85, 'report-key': 3.0}  # screenshots shown across the page under two columns of text: name -> height in inches

BEHIND = [
 dict(side='Horizontal', title='Auditability: two reviews that look back on a task', fig='reviews', paras=[
  ['Two reviews look back on a task, and only you can start them: type the command in Copilot chat, or press its button on the board.'],
  [('b','/harness-task-report'),' reads the numbers in the report and says where the time and usage went, and why.'],
  [('b','Agent Performance Review'),' (/harness-agent-performance-review) goes deeper. It reads every action the agent took, what the check program said when it stopped one, and what the agent was thinking before each step. A program first marks the spots that look like detours. Then an agent judges each one with evidence: a limit of the harness, the agent’s own mistake, the environment, missing knowledge, or the guardrails doing their job. It ends by naming the file to change.'],
  ['It runs as a task of its own and only reads: the task it reviews is not changed. It reads the whole record, so it costs more than a usual question.'],
  ['When the cause is in the harness, it goes to the person who maintains the harness (today, that is me). So the harness is fixed where it really goes wrong, with evidence.'],
 ]),
]

INDEX = dict(kicker='Where to go next', title='After reading: where to go, who to ask',
 map=['This document is in the AI Exploration folder on OneDrive. For where to go next, open ',('a','0 MUST READ.pdf'),', the first file in that folder. It lists the four folders and who each one is for.'],
 paras=[
  [('b','See a demo first. '),'Ask me (Smars Hu) for a demo: one real task, from start to finish.'],
  [('b','Try it in the team '),'(leads and managers). Ask me to pick a few real intakes together, hand them to the harness from start to finish, and use the reports to see how much time it saved and what it cost.'],
])
