# Basic 01 · Stop using AI the 2024 way

## 0 Hook
@ card "Stop using AI the 2024 way" kicker="Basic 01"
You know, it's 2026, and a lot of teams want AI to really stick in their dev work.
@ logos "claude|Claude" "codex|ChatGPT" m365-copilot
Lots of companies have already paid for AI chat or coding agents for their people,
@ logos claude-code codex github-copilot
like Claude Code, Codex, or GitHub Copilot.
@ fig small-slice step=1
But here's the thing: what we keep seeing is, a lot of teams still only use AI for a tiny slice of their work.
@ fig small-slice step=2
And plenty of people are even still using it
@ fig small-slice step=3
like a Q&A chat.

@ fig engineer step=1
So, say you're a software engineer, and you've got this huge legacy system on your hands.
@ fig engineer step=2
A request comes in from the business side,
@ fig engineer step=3
and you've built a bunch of features like it before.
You know exactly what the best fix is:
@ fig engineer step=4
which code to change, how to test it, what it depends on and what depends on it, and what else it could break.
You've done all of it before.
@ fig engineer step=5
Now you're told you have to use AI for it.
What do you do?

@ fig hook-prompt step=1
Pretty much this:
@ fig hook-prompt step=2
first, you dig up the code files you think matter, one by one, and drop them into the chat box.
@ fig hook-prompt step=3
Then you write this long explanation of what the code does and how it all fits together.
@ fig hook-prompt step=4
Then you paste in the request.
@ fig hook-prompt step=5
And finally, you write a whole screen of "do this", "add that", "never touch that".

@ fig hook-prompt step=6
The AI hasn't written a single line of code yet, and you've already spent half an hour.
@ fig hook-prompt step=7
Then you hit Enter and hope it gets it right.
@ fig hook-answer step=1
But what usually happens?
The AI gives you something you're, like, 80 to 90% happy with.
@ fig hook-answer step=2
You paste its code back in, run the tests yourself, check the results yourself...
@ fig hook-answer step=3
and some of it's still wrong.
@ fig hook-answer step=4
So now you're spending even more time reviewing the code...
@ fig hook-answer step=5
And in the end you're thinking, using AI is slower than just writing it myself.
@ fig hook-answer step=6
Because it can't understand your complex system, and it can't see the traps you already know about.

@ big "3" "things this video makes clear" icon=list-checks
So in this video I want to make three things clear:
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=1
where this way of using AI goes wrong,
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=2
why it's so hard for dev teams to really put AI to work,
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=3
and what the missing piece is called.

## 1 Your pain points
@ list "Your pain points" "It doesn't know your project|folder-search" "It forgets|brain" "It doesn't always follow your rules|list-x" "It's always sure of its own work|badge-check" "You can't see what it did|eye-off"
If you've used AI like this, you've probably hit every one of the things I'm about to list.

@ fig pain-context step=1
One: it doesn't know your project.
@ fig pain-context step=2
Every single time, you have to find the code, paste the code, explain the code.

@ fig pain-memory step=1
Two: it forgets.
@ fig pain-memory step=2
Open a new chat, and everything you told it is gone.
@ fig pain-memory step=3
You have to say it all again from scratch.
@ fig pain-memory step=4
And you'll notice, the longer you chat in the same conversation, the worse it seems to get.
@ fig pain-memory step=5
Stuff you agreed on earlier, it forgets later.

@ fig pain-rules step=1
Three: you give it a bunch of dos and don'ts, but it doesn't always follow them.
@ fig pain-rules step=2
Most of the time it listens,
@ fig pain-rules step=3
but every now and then it skips exactly the step you care about most.
@ fig pain-rules step=4
And it gets worse the longer the chat goes: the more history there is, the more its attention drifts, and the less it remembers the older stuff.

@ fig pain-confident step=1
Four: it's always super confident when it checks its own work.
@ fig pain-confident step=2
"Done, all tests pass."
@ fig pain-confident step=3
Then you look, and there are still tons of errors.

@ fig pain-blind step=1
Five: you can't see what it actually did.
@ fig pain-blind step=2
Which files it changed,
@ fig pain-blind step=3
which commands it ran,
@ fig pain-blind step=4
why it made those changes...
@ fig pain-blind step=5
it's hard to explain any of that afterwards.

## 2 Root cause
@ fig hook-prompt step=5
So, is this how you use AI right now?

@ fig human-carries step=1
Well, this is how people used AI back in 2024: treating it like a chatbot.

@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=1
In 2024, most people were still figuring out how to write a good prompt so the AI would do better.
So that's what people called Prompt Engineering.
But the problem is,
@ fig human-carries step=2
even if the model is smart enough, you're still treating it as someone who just answers questions.
@ fig human-carries step=3
You haven't let it actually do the work.
@ fig human-carries step=4
Apart from answering you, everything else is still on you:
@ fig human-carries step=5
finding the code, sorting out the request, running the tests,
@ fig human-carries step=6
remembering the context, watching it to make sure it sticks to the process, checking its results.
@ fig human-carries step=7
All of that, you do by hand.

@ card "The same old lines" icon=messages-square
And so in the end, you hear the same thing everywhere:
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=1
AI isn't reliable,
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=2
AI makes mistakes,
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=3
AI can only help with part of my work...

## 3 What is an agent
@ card "What is an AI agent?" icon=bot
So here we've got to explain what an AI agent is.

@ fig llm-vs-agent step=1
When you normally chat with AI, you're really talking straight to the large model, the LLM.
@ fig llm-vs-agent step=2
It thinks, then writes some text back to answer you.
@ fig llm-vs-agent step=3
An agent adds tool calling on top of the LLM, basically, the ability to use tools.
@ fig llm-vs-agent step=4
Think of tools as its hands:
@ fig llm-vs-agent step=5
once it's thought things through, it can change code files on your machine by itself, run commands, search the web, open a browser.
But having hands isn't enough.
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right"
Here's the key: it loops.
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=2
It calls a tool,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=3
looks at the result,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=4
then decides what to do next.
@ fig llm-vs-agent step=6
Then it calls again, looks again, and keeps going until the job's done.

@ formula "Agent" "LLM" "Hands + Loop"
Hands, plus the ability to loop on its own, and that's when you get an agent.
@ fig llm-vs-agent step=7
It doesn't just answer you anymore.
@ fig llm-vs-agent step=8
It can finish a task by itself.

## 4 What is a harness
@ card "New problems" kicker="Once an agent works on its own" icon=triangle-alert
OK, so now agents can do work on their own.
But that brings new problems.

@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work"
Look back at the last few years.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=1
In 2024, people were working on how to write good prompts.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=2
In 2025, people figured out they needed to get context engineering right, you know, managing what's in the AI's context, so it'd perform consistently.
@ logos claude-code codex github-copilot
And by 2026, coding agents like Claude Code, Codex, and GitHub Copilot can really do work for you.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=3
And being able to do work brings new problems too.

@ fig nine-gaps step=1
Companies found that to really put agents to work, they have to solve these problems:

@ fig nine-gaps step=2
It doesn't know your systems and projects, so someone still has to walk it through them every time.

@ fig nine-gaps step=3
How do you keep memory across sessions?
If one session breaks, how does another one pick up the task?

@ fig nine-gaps step=4
People only use the agent to change code.
Everything else, like running tests, the CI/CD pipeline, updating tickets, people still do themselves.

@ fig nine-gaps step=5
It doesn't always follow the rules you agreed on.

@ fig nine-gaps step=6
People don't dare give it access to servers, because it might do something dangerous, like dropping a table.

@ fig nine-gaps step=7
When it finishes a task, it tends to be totally sure its result is right.

@ fig nine-gaps step=8
Where did the money and time go, and how do you cut them down?
The plan, the logs, the traces of how the task went... none of it gets recorded.

@ big "5" "sessions at most, before human attention is the bottleneck" icon=messages-square
One person can keep an eye on five sessions, tops.
So human attention becomes the bottleneck for the agent's work.

@ fig nine-gaps step=10
On a long or complex task, the agent always stops partway through.

@ fig nine-gaps step=11
That's way too many problems.
And the skill of getting an agent to work both steadily and well,
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Harness engineering" now=3
that's called harness engineering.

@ formula "Agent" "Model" "Harness"
There's a formula: Agent = Model + Harness.
@ fig harness-around step=1
Everything outside the model is the harness.

@ fig program-vs-agent step=1
Before, all of this depended on you reminding it in the prompt.
@ fig program-vs-agent step=2
Now it's handed over to programs.
@ fig program-vs-agent step=3
Because a program does the same thing every time,
@ fig program-vs-agent step=4
it doesn't cost tokens, and it doesn't depend on the model behaving itself.
@ fig program-vs-agent step=5
So the fixed, predictable stuff goes to programs,
@ fig program-vs-agent step=6
and the stuff that needs judgment and thinking goes to the agent.

## 5 My harness
@ board/tour-list crop=0,0,1,0.42
So I built a harness framework myself,
@ logos github-copilot vscode
and it runs on GitHub Copilot in VS Code.

@ logos m365-copilot github-copilot
If your team's a Microsoft customer, you're most likely using two Copilots at once: M365 Copilot and GitHub Copilot.
@ logos "m365-copilot|chat, mail, documents" "github-copilot|coding agent"
GitHub Copilot is the one we call a coding agent,
@ fig harness-around step=2
and my harness helps you drive GitHub Copilot better.

@ fig nine-gaps step=12
So let's go back to the gaps on that list and see what each one looks like in my harness.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=1
It doesn't know your systems and projects, so someone still has to walk it through them every time.

@ fig kb-build step=1
I built a standard framework that turns a codebase into a knowledge base.
@ fig kb-build step=2
It uses a set of tools to learn your codebase,
@ fig kb-build step=3
find the hidden dependencies between files,
@ board/real-kb-card crop=0.3,0.08,0.65,0.49 box=0.305,0.32,0.64,0.095 text="A card: what it reads, what it writes, who calls it"
and write what it finds into cards.
@ fig kb-build step=5
Once it's done learning, it generates a summary file and an index, kind of like a table of contents.
@ fig kb-build step=6
So the agent doesn't have to re-read the code every time.
@ fig kb-build step=7
It just loads the summary file and a few of the cards,
@ board/real-kb-summary crop=0.29,0.09,0.53,0.62 box=0.3,0.225,0.5,0.25 text="The summary file of a domain: purpose, flows, key data"
and it gets a rough picture of your codebase.
@ board/kb-lookup crop=0,0.03,0.7,0.42 box=0.015,0.2,0.45,0.245 text="Look up: who uses it, what it uses, which file"
And if it needs to, it can jump straight to the right files through the index.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=2
How do you keep memory across sessions?
@ fig task-folder step=1
If one session breaks, how does another one pick up the task?

@ fig task-folder step=2
Each task is a folder.
@ fig task-folder step=3
It holds the files for the task's whole life:
@ fig task-folder step=4
the task plan, history logs, status,
@ fig task-folder step=5
requirement docs, test scripts, the changed code,
@ board/real-files-top crop=0.02,0.58,0.26,0.41 box=0.035,0.677,0.235,0.305 text="A real task folder: the diff, the commit message, the plans, …"
and anything the agent produces while it works.
It all gets saved in there.
@ board/real-files-top crop=0.29,0.08,0.7,0.5 box=0.295,0.165,0.68,0.105 text="TASK.md: a new session reads this first"
So even if one session dies, another session just scans that task folder and picks right up.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=3
People only use the agent to change code.
Everything else, like running tests, the CI/CD pipeline, updating tickets, people still do themselves.
@ big "DROP TABLE" "the one command nobody wants an agent to run" icon=database-zap
And people don't dare give it access to servers, because it might do something dangerous, like dropping a table.

@ fig tool-pack step=1
So I give the agent access to the dev and test environments,
@ board/real-agent-actions-dev crop=0.04,0.27,0.92,0.19 box=0.045,0.298,0.91,0.148 text="In a real task: the agent edits code and tests in DEV, then tests a copy"
so it can develop on its own, write test scripts on its own, run them on its own, and fix things on its own.
@ fig tool-pack step=3
For safety, here's how I did it:
@ fig tool-pack step=4
through a standard Toolpack, the agent gets read-only access to the non-prod environments,
@ board/real-sql-held crop=0.12,0.795,0.78,0.2 box=0.135,0.966,0.735,0.026 text="An UPDATE on shop-qat waits for a person and a typed code"
and anything that writes or executes needs a person to approve it.
@ board/outside-tools-packs crop=0,0,1,0.56 box=0.027,0.405,0.946,0.12 text="The sqlserver tool pack ships with the harness"
For example, with Microsoft's SQL Server,
@ fig guard-layers step=1
I've tested my harness against thousands of attempts to sneak in dangerous commands.
@ fig guard-layers step=2
And between a blacklist, a whitelist,
@ fig guard-layers step=3
a person making the call, and the account's own permissions,
@ board/real-sql-live crop=0.09,0,0.81,1 box=0.1,0.12,0.8,0.4 text="DROP and TRUNCATE refused, the UPDATE held"
the agent's access stays safe.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=4
When it finishes a task, it tends to be totally sure its result is right.

@ fig reviewer step=1
I bring in an independent reviewer as a subagent.
@ fig reviewer step=2
The subagent reviews everything the main agent did
@ board/real-review crop=0.04,0.565,0.78,0.42 box=0.05,0.585,0.34,0.06 text="PASS, and each point cites a line and the requirement"
and gives a test verdict.
@ board/checks-used-review crop=0,0.46,1,0.54 box=0.04,0.79,0.92,0.2 text="Caught: capital letters and digits were never checked"
And in practice, the reviewer catches a lot of cases the main agent didn't think of.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=5
Where did the money and time go, and how do you cut them down?
@ fig task-report step=1
The plan, the logs, the traces of how the task went... none of it gets recorded.

@ board/real-report crop=0,0.075,1,0.26 box=0.012,0.178,0.975,0.152 text="A real task: 2 min 3 s of work, 73.9 Credits"
I built a task report dashboard just for looking at the stats of a whole task:
@ board/real-report crop=0,0.85,1,0.15 box=0.03,0.885,0.94,0.05 text="Agent working 2 min 3 s, waiting for you 8 min 49 s"
where the time went,
@ board/real-report-prompts crop=0.02,0.53,0.66,0.46 box=0.43,0.6,0.245,0.375 text="Credits by stage: the requirement took 48%"
where the money went,
@ board/real-sql-report crop=0.02,0.13,0.96,0.31 box=0.035,0.135,0.17,0.024 text="Another task's report: 3 of 5 tool calls failed"
which tool calls failed.
@ fig task-report step=2
All the conclusions, right there at a glance.

@ board/tour-lobby crop=0,0,1,0.62
And there's a lot more, but to save time, I won't list it all here.

## 6 Summary
@ card "AI hasn't gotten dumber" icon=brain
So, AI hasn't gotten dumber.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Harness engineering" now=1
It's that the way we use it is still stuck in 2024:
@ fig who-does-what step=1
treating it like a chatbot, with people doing all the legwork in between, watching the process, and doing the checks.

@ fig who-does-what step=2
The agent hands that legwork over to programs,
@ fig who-does-what step=3
and the harness hands the process, the checks, and the boundaries over to programs too.
@ fig who-does-what step=4
So people can finally step back,
@ board/accept box=0.045,0.85,0.135,0.11 text="You make the call: Accept and close"
and just make the calls and be the gatekeepers.

@ quote "Which stronger model should we switch to?" by="Don't ask this first"
If you're trying to get your team using AI, don't rush to ask "which stronger model should we switch to?"
@ fig harness-around step=3
First ask: "What's missing around our AI?"

@ board/one-01-new-task box=0.02,0.54,0.47,0.165 text="Your first task starts here"
And if you want to try it yourself,
@ card "Install the harness, start your first task" kicker="Next video" icon=play
in the next video I'll help you install this harness and kick off your first task.

// notes
// Every picture's idea is still said in the new text; none had to be parked on a nearby line.
// The bullet items in 4 and 5 ("- ...") are spoken without the dash, each item its own paragraph as in scenes.md (en-casual-v2 has no blank lines between the items in 4).
// In 0 Hook, en-casual-v2 runs "Then you hit Enter..." and "But what usually happens?" in one paragraph (no blank line), so hook-prompt step=7 and hook-answer step=1 now share one audio clip.
