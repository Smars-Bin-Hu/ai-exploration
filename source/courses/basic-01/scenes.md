# Basic 01 · Stop using AI the 2024 way

## 0 Hook
@ card "Stop using AI the 2024 way" kicker="Basic 01"
It's 2026, and a lot of teams want AI to be a real part of how they build software.
@ logos "claude|Claude" "codex|ChatGPT" m365-copilot
Plenty of companies already pay for an AI chat tool or a coding agent,
@ logos claude-code codex github-copilot
like Claude Code, Codex or GitHub Copilot.
@ fig small-slice step=1
But what we actually see is that many teams still use it for only a small slice of their work.
@ fig small-slice step=2
And lots of people still use it the same old way, as a chat.
@ fig small-slice step=3
Ask a question, get an answer.
Here's what I mean.
@ fig engineer step=1
Say you're a software engineer, and you've got a huge legacy system on your hands.
@ fig engineer step=2
The business side gives you a requirement.
@ fig engineer step=3
You've built plenty of features like this, and you know the best way to do it.
@ fig engineer step=4
Which code to change, how to test it, what depends on what, what it might break.
You've seen it all.
@ fig engineer step=5
Now you're told to do it with AI.
What do you do?
@ fig hook-prompt step=1
Probably something like this.
@ fig hook-prompt step=2
First, you dig out the files you think matter, one by one, and paste them into the chat.
@ fig hook-prompt step=3
Then you write a long explanation of what the code does and how it all fits together.
@ fig hook-prompt step=4
Then you paste in the requirement.
@ fig hook-prompt step=5
And finally, a whole screen of "do this", "add that", "whatever you do, don't touch that".
@ fig hook-prompt step=6
The AI hasn't written a single line yet, and you've already spent half an hour.
@ fig hook-prompt step=7
Then you hit Enter and hope it gets it right.
@ fig hook-answer step=1
What you usually get is an answer you're maybe eighty or ninety percent happy with.
@ fig hook-answer step=2
You paste its code back in, run the tests yourself, check the results yourself,
@ fig hook-answer step=3
and some of it's still wrong.
@ fig hook-answer step=4
So you spend even longer reviewing it.
@ fig hook-answer step=5
In the end, it feels faster to just write it yourself.
@ fig hook-answer step=6
The AI doesn't get your complex system, and it can't see the traps you know are there.
@ big "3" "things this video makes clear" icon=list-checks
In this video I want to make three things clear.
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=1
What's wrong with using AI this way.
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=2
Why it's so hard for development teams to really adopt AI.
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=3
And what the missing piece is called.

## 1 Your pain points
@ list "Your pain points" "It doesn't know your project|folder-search" "It forgets|brain" "It doesn't always follow your rules|list-x" "It's always sure of its own work|badge-check" "You can't see what it did|eye-off"
If you've used AI like this, you've probably hit every one of these.
@ fig pain-context step=1
One: it doesn't know your project.
@ fig pain-context step=2
Every single time, you have to find the code, paste the code, explain the code.
@ fig pain-memory step=1
Two: it forgets.
@ fig pain-memory step=2
Open a new chat, and everything you said before is gone.
@ fig pain-memory step=3
You have to say it all again.
@ fig pain-memory step=4
And the longer a chat goes on, the worse it seems to get.
@ fig pain-memory step=5
It forgets things you agreed on at the start.
@ fig pain-rules step=1
Three: you give it a list of dos and don'ts, and it doesn't always follow them.
@ fig pain-rules step=2
Most of the time it listens.
@ fig pain-rules step=3
But every so often, it skips exactly the step you cared about most.
@ fig pain-rules step=4
And the longer the chat gets, the more its attention drifts, and the less it remembers from earlier.
@ fig pain-confident step=1
Four: it's always sure of its own work.
@ fig pain-confident step=2
"Done, and all the tests pass."
@ fig pain-confident step=3
Then you look for yourself, and there's still a pile of mistakes.
@ fig pain-blind step=1
Five: you can't see what it actually did.
@ fig pain-blind step=2
Which files did it change?
@ fig pain-blind step=3
Which commands did it run?
@ fig pain-blind step=4
Why did it do it that way?
@ fig pain-blind step=5
After the fact, it's hard to tell.

## 2 The root cause
@ fig hook-prompt step=5
Is this how you use AI right now?
@ fig human-carries step=1
Well, that's how people used AI in 2024.
As a chatbot.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=1
Back then, most people were busy learning to write better prompts to get better answers.
That was called prompt engineering.
But here's the problem.
@ fig human-carries step=2
Even if the model is smart enough, you're still treating it like someone who just answers questions.
@ fig human-carries step=3
You haven't let it get its hands on the work.
@ fig human-carries step=4
It answers your questions, and everything else is still on you.
@ fig human-carries step=5
Finding the code, sorting out the requirement, running the tests,
@ fig human-carries step=6
remembering the context, making sure it follows the process, checking its results.
@ fig human-carries step=7
You do all of it by hand.
@ card "The same old lines" icon=messages-square
And in the end, you hear the same old lines.
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=1
AI isn't reliable.
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=2
AI makes mistakes.
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=3
AI can only help with part of my work.

## 3 What is an agent
@ card "What is an AI agent?" icon=bot
So let me explain what an AI agent is.
@ fig llm-vs-agent step=1
When you chat with AI, you're talking straight to the large language model, the LLM.
@ fig llm-vs-agent step=2
It thinks, then writes you an answer in text.
@ fig llm-vs-agent step=3
An agent is an LLM plus tool calling, meaning it can use tools.
@ fig llm-vs-agent step=4
Think of tools as its hands.
@ fig llm-vs-agent step=5
Once it's thought things through, it can go and change the code on your machine itself, run commands, search the web, open a browser.
But hands alone aren't enough.
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right"
The key is that it loops.
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=2
It calls a tool,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=3
looks at the result,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=4
and decides what to do next.
@ fig llm-vs-agent step=6
Then it calls again, looks again, and keeps going until the job's done.
@ formula "Agent" "LLM" "Hands + Loop"
Give an LLM hands and a loop of its own, and you've got an agent.
@ fig llm-vs-agent step=7
It doesn't just answer you anymore.
@ fig llm-vs-agent step=8
It can finish a piece of work on its own.

## 4 What is a harness
@ card "New problems" kicker="Once an agent works on its own" icon=triangle-alert
But once an agent can work on its own, you get a new set of problems.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work"
Look back over the last few years.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=1
In 2024, people were figuring out how to write good prompts.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=2
In 2025, people found that to get steady results, you have to manage the AI's context well.
That's context engineering.
@ logos claude-code codex github-copilot
And by 2026, coding agents like Claude Code, Codex and GitHub Copilot can really get work done for you.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=3
And that's where the new problems start.
@ fig nine-gaps step=1
Companies found that to really adopt agents, they have to solve these.
@ fig nine-gaps step=2
One: it doesn't know your systems or your projects, so someone still has to explain them every time.
@ fig nine-gaps step=3
Two: how do you keep its memory from one session to the next?
If a session dies, how does a new one pick up the task?
@ fig nine-gaps step=4
Three: people only use the agent to change code.
Running tests, the CI-CD pipeline, updating tickets, people still do all of that.
@ fig nine-gaps step=5
Four: it doesn't always follow the rules you agreed on.
@ fig nine-gaps step=6
Five: you don't dare give it access to your servers, in case it does something dangerous, like dropping a table.
@ fig nine-gaps step=7
Six: when it finishes a task, it's usually sure it got it right.
@ fig nine-gaps step=8
Seven: where did the time and money go, and how do you spend less?
The plan, the logs, the steps it took.
None of it gets recorded.
@ big "5" "sessions at most, before human attention is the bottleneck" icon=messages-square
Eight: one person can keep an eye on five sessions at most, so human attention becomes the bottleneck.
@ fig nine-gaps step=10
Nine: on a long or complex task, the agent always stops partway through.
@ fig nine-gaps step=11
That's a lot of problems.
Getting an agent to work well, and keep working well, is a craft of its own.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Harness engineering" now=3
It's called harness engineering.
@ formula "Agent" "Model" "Harness"
There's a simple formula: agent equals model plus harness.
@ fig harness-around step=1
Everything outside the model is the harness.
@ fig program-vs-agent step=1
All of this used to be you, reminding it in the prompt.
@ fig program-vs-agent step=2
Now a program does it.
@ fig program-vs-agent step=3
A program is deterministic.
@ fig program-vs-agent step=4
It doesn't spend tokens, and it doesn't depend on the model behaving itself.
@ fig program-vs-agent step=5
So jobs with a fixed answer go to programs,
@ fig program-vs-agent step=6
and anything that needs judgment goes to the agent.

## 5 My harness
@ board/tour-list crop=0,0,1,0.42
I've built my own harness framework,
@ logos github-copilot vscode
on top of GitHub Copilot in VS Code.
@ logos m365-copilot github-copilot
If your company uses Microsoft, you're probably using two Copilots at once: M365 Copilot and GitHub Copilot.
@ logos "m365-copilot|chat, mail, documents" "github-copilot|coding agent"
GitHub Copilot is what we call a coding agent.
@ fig harness-around step=2
My harness helps you steer it better.
@ fig nine-gaps step=12
Let's go back to those problems and see how my harness handles each one.
@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=1
First: it doesn't know your systems or your projects, so someone has to explain them every time.
@ fig kb-build step=1
I built a standard framework that turns a codebase into a knowledge base.
@ fig kb-build step=2
A set of tools studies your codebase,
@ fig kb-build step=3
finds the hidden dependencies between files,
@ fig kb-build step=4
and writes them up as cards.
@ fig kb-build step=5
When it's done, it produces a summary file and an index.
@ fig kb-build step=6
So the agent doesn't have to reread the code every time.
@ fig kb-build step=7
It just loads the summary and a few cards,
@ tutorials/6_kb/kb-go-on-docs box=0.025,0.315,0.95,0.4 text="The knowledge base: 5 domains, 74 cards"
and it gets a rough picture of your codebase.
@ board/kb-lookup crop=0,0.03,0.7,0.42 box=0.015,0.2,0.45,0.245 text="Look up: who uses it, what it uses, which file"
And when it needs more, the index takes it straight to the right file.
@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=2
Second: how do you keep its memory from one session to the next?
@ fig task-folder step=1
If a session dies, how does a new one pick up the task?
@ fig task-folder step=2
Every task is a folder.
@ fig task-folder step=3
It holds everything from the task's whole life.
@ fig task-folder step=4
The plan, the history log, the status,
@ fig task-folder step=5
the requirement doc, the test scripts, the changed code,
@ board/tour-tab-files crop=0,0.31,0.75,0.69 box=0.03,0.475,0.27,0.52 text="The Files tab: the whole task folder"
and anything else the agent produces along the way.
@ board/go-on-new-chat box=0.13,0.72,0.8,0.2 text="A new chat picks the task up from its files"
So if a session dies, a new one just scans the folder and carries on right away.
@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=3
Third: people only use the agent to change code, and still handle the tests, the CI-CD pipeline and the tickets themselves.
@ big "DROP TABLE" "the one command nobody wants an agent to run" icon=database-zap
And you don't dare give it access to your servers, in case it does something dangerous, like dropping a table.
@ fig tool-pack step=1
Give the agent access to your dev and test environments,
@ fig tool-pack step=2
and it can build things, write its own test scripts, run them, and fix what fails.
@ fig tool-pack step=3
To keep that safe, here's what I do.
@ fig tool-pack step=4
With a standard tool pack, the agent gets read-only access to the lower environments.
@ board/outside-held-card box=0.045,0.845,0.72,0.1 text="A write waits for a person and a typed code"
Anything that writes or executes needs a person to approve it.
@ board/outside-tools-packs crop=0,0,1,0.56 box=0.027,0.405,0.946,0.12 text="The sqlserver tool pack ships with the harness"
Take Microsoft's SQL Server.
@ fig guard-layers step=1
I've tested my harness against thousands of injected dangerous commands.
@ fig guard-layers step=2
Between a blacklist, a whitelist,
@ fig guard-layers step=3
a human making the call, and the account's own permissions,
@ board/stop-agent-actions box=0.04,0.495,0.92,0.49 text="What the gate stopped, kept on the task's record"
the agent's access stays safe.
@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=4
Fourth: when it finishes a task, it's usually sure it got it right.
@ fig reviewer step=1
I bring in an independent reviewer as a subagent.
@ fig reviewer step=2
It reviews everything the agent did on the task
@ board/review crop=0,0.57,1,0.43 box=0.035,0.805,0.93,0.185 text="Each round: a verdict and its reasons"
and gives a test verdict.
@ board/checks-used-review crop=0,0.46,1,0.54 box=0.04,0.79,0.92,0.2 text="Caught: capital letters and digits were never checked"
In practice, the reviewer catches lots of cases the main agent never thought of.
@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=5
Fifth: where did the time and money go, and how do you spend less?
@ fig task-report step=1
The plan, the logs, the steps it took.
None of it gets recorded.
@ board/tour-report crop=0,0.03,1,0.37 box=0.012,0.17,0.975,0.2 text="Task analysis: the whole task in numbers"
I built a report panel that shows the numbers for the whole task.
@ board/tour-report crop=0,0.78,1,0.2 box=0.035,0.805,0.93,0.15 text="Where the time went"
Where the time went,
@ board/tour-performance crop=0,0.37,1,0.32 box=0.01,0.39,0.98,0.28 text="Credits, prompt by prompt"
where the money went,
@ board/stop-agent-actions crop=0,0.36,1,0.64 box=0.655,0.385,0.305,0.09 text="Blocked and failed calls, counted"
which tool calls failed.
@ fig task-report step=2
It's all there at a glance.
@ board/tour-lobby crop=0,0,1,0.62
There's a lot more, but no time to cover it all here.

## 6 Summary
@ card "AI hasn't gotten dumber" icon=brain
So, AI hasn't gotten dumber.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Harness engineering" now=1
The way we use it is just stuck in 2024.
@ fig who-does-what step=1
We treat it as a chatbot, and people still do the copying and pasting, watch the process, and do the checks.
@ fig who-does-what step=2
With an agent, a program does the copying and pasting.
@ fig who-does-what step=3
With a harness, a program also handles the process, the checks and the boundaries.
@ fig who-does-what step=4
And people can finally step back,
@ board/accept box=0.045,0.85,0.135,0.11 text="You make the call: Accept and close"
make the calls, and sign off.
@ quote "Which stronger model should we switch to?" by="Don't ask this first"
If you're rolling out AI on your team, don't rush to ask, "Which stronger model should we switch to?"
@ fig harness-around step=3
Ask this first: "What's missing around our AI?"
@ board/one-01-new-task box=0.02,0.54,0.47,0.165 text="Your first task starts here"
If you want to try it yourself,
@ card "Install the harness, start your first task" kicker="Next video" icon=play
in the next video I'll walk you through installing this harness and starting your first task.
