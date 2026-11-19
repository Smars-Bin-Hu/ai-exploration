# Basic 01 · Stop using AI the 2024 way

// The whole script in the author's spoken style (style/author-style.md, section 5): same points, same order, same pictures as scenes.md.
// Modules 1 and 2 are style/pain-points-author.md and style/root-cause-author.md. [.3] is a pause mark in seconds (never spoken, never shown).

## 0 Hook
@ card "Stop using AI the 2024 way" kicker="Basic 01"
So, [.3] you know, [.2] it's 2026, and a lot of teams want AI to [.3] really stick in their dev work.
@ logos "claude|Claude" "codex|ChatGPT" m365-copilot
And, [.3] I know a lot of companies have already paid for AI chat or coding agents [.2] for their people,
@ logos claude-code codex github-copilot
like, [.2] Claude Code, Codex, or GitHub Copilot, [.3]
@ fig small-slice step=1
but here's the thing, [.2] what we keep seeing is, a lot of teams are still only using AI for [.3] a tiny slice of their work.
@ fig small-slice step=2
And plenty of people are even still using it [.3]
@ fig small-slice step=3
as a Q&A chat, [.2] one question, one answer, right?

@ fig engineer step=1
So, [.3] let's say you are a software engineer, and you have [.3] a huge legacy system on your hands,
@ fig engineer step=2
and, [.3] a request comes in from the business side.
@ fig engineer step=3
And you have built a bunch of features like it before, [.3] so you know exactly what the best solution is,
@ fig engineer step=4
like, [.2] which code to change, how to test it, [.2] what it depends on and what depends on it, [.3] and what else it could break.
And you have done all of it before, [.3]
@ fig engineer step=5
but now, [.3] you're told you have to use AI for it, so, [.3] what do you do?

@ fig hook-prompt step=1
I guess, [.3] pretty much like this,
@ fig hook-prompt step=2
first, [.2] you have to find the code files you think matter, [.2] one by one, and drop them into the chat box.
@ fig hook-prompt step=3
And after that, [.3] you have to write [.3] this long explanation of what the code does, [.2] and how it all fits together,
@ fig hook-prompt step=4
and then you paste in the request, [.2]
@ fig hook-prompt step=5
and finally, [.3] you write a whole screen of "do this", "add that", [.2] "never touch that".

@ fig hook-prompt step=6
Yeah, so, [.3] the AI has not written a single line of code yet, and you have already spent [.3] half an hour.
@ fig hook-prompt step=7
And then you hit Enter, [.2] and hope it gets it right,
@ fig hook-answer step=1
but what usually happens is, [.3]
the AI gives you something you're, like, [.2] 80 or 90 percent happy with, right?
@ fig hook-answer step=2
And you paste its code back in, [.2] run the tests yourself, check the results yourself, and... [.4]
@ fig hook-answer step=3
some of it [.3] is still wrong,
@ fig hook-answer step=4
so now, [.2] you have to spend even more time [.3] reviewing the code.
@ fig hook-answer step=5
And in the end, [.2] you feel, like, oh, [.3] using AI is slower than just writing it myself,
@ fig hook-answer step=6
because the AI cannot understand our complex system, and it cannot see [.3] the traps I already know about.

@ big "3" "things this video makes clear" icon=list-checks
So, [.3] in this video, [.2] I want to make three things clear, [.3]
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=1
where this way of using AI goes wrong, [.2]
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=2
why it's so hard for dev teams to [.3] really put AI to work,
@ list "This video" "What's wrong with using AI this way|circle-alert" "Why it's so hard for teams to adopt AI|users" "What the missing piece is called|puzzle" lit=3
and what the missing piece [.3] is called.

## 1 Your pain points
@ list "Your pain points" "It doesn't know your project|folder-search" "It forgets|brain" "It doesn't always follow your rules|list-x" "It's always sure of its own work|badge-check" "You can't see what it did|eye-off"
So, [.3] if you have used AI like this, I know you have probably hit [.2] every single one of the things I'm about to list.

@ fig pain-context step=1
So, [.3] number one is, [.2] it does not know your project.
@ fig pain-context step=2
So, every single time, you have to find the code, [.2] paste the code, [.2] explain the code, [.3] all by yourself, right?

@ fig pain-memory step=1
And number two is, [.2] the AI forgets.
@ fig pain-memory step=2
Like, [.3] if you open a new chat, everything you told it [.3] is gone,
@ fig pain-memory step=3
and you have to say it all again [.2] from scratch.
@ fig pain-memory step=4
And another thing is, [.2] you'll probably notice, the longer you chat in the same conversation, the worse it seems to get, [.3]
@ fig pain-memory step=5
and stuff you agreed on earlier, [.2] the AI [.3] forgets later.

@ fig pain-rules step=1
// bare-referent kept: "follow them" is the script's (the dos and don'ts just named)
And the third thing is, [.2] you give it a bunch of dos and don'ts, [.3] but it does not always follow them.
@ fig pain-rules step=2
Most of the time, the AI will listen,
@ fig pain-rules step=3
but every now and then, [.3] it skips exactly the step [.2] you care about most.
@ fig pain-rules step=4
And as I said, [.2] it gets worse the longer the chat goes, [.3] because the more history there is, [.2] the more its attention drifts, and... [.4] the less it remembers the older stuff.

@ fig pain-confident step=1
And number four is, [.2] it's always super confident when it checks its own work.
@ fig pain-confident step=2
Sometimes the AI will say, hey, [.2] "Done, all tests pass."
@ fig pain-confident step=3
Then you take a look, [.3] and there are still [.3] a lot of errors, and you have to spend a lot of time to fix them, right?

@ fig pain-blind step=1
And the last one is, [.2] you cannot see what it actually did [.2] behind the scenes,
@ fig pain-blind step=2
like, [.2] which files it changed,
@ fig pain-blind step=3
which commands it ran, [.2]
@ fig pain-blind step=4
and... [.4] why it made those changes, [.3]
@ fig pain-blind step=5
it's really hard to explain any of that afterwards.

## 2 Root cause
@ fig hook-prompt step=5
So, [.3] is this how you use AI right now?

@ fig human-carries step=1
Yeah, [.2] this is how people used AI back in 2024, [.3] they were treating it like [.3] a chatbot, so you ask a question, and it gives you an answer, right?

@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=1
And in 2024, [.2] I know most people were still trying to figure out how to write a good prompt, so the AI can do a better job, [.3] and that's what people called [.3] Prompt Engineering.
// split-thought kept: the author turns with "But the problem is," after a full stop; the paragraph is still one voice call
But the problem is, [.3]
@ fig human-carries step=2
even if the model is smart enough, you are still treating it as someone who [.3] just answers your questions,
@ fig human-carries step=3
and you have not let the AI actually do the work.
@ fig human-carries step=4
And that means, [.2] apart from answering you, everything else [.3] is still on you, [.3] like,
@ fig human-carries step=5
finding the code, [.2] sorting out the request, running the tests, [.2]
@ fig human-carries step=6
and remembering the context, watching it to make sure it sticks to the process, [.2] and checking its results, [.4]
@ fig human-carries step=7
all of that, [.2] you have to do it by hand, right?

@ card "The same old lines" icon=messages-square
And so, [.3] in the end, [.2] you hear the same thing everywhere, [.3] people say, like, oh, [.3]
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=1
AI is not reliable, [.3]
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=2
AI makes mistakes, [.3]
@ list "The same old lines" "AI isn't reliable.|thumbs-down" "AI makes mistakes.|circle-x" "AI can only help with part of my work.|chart-pie" lit=3
and AI can only help with [.3] part of my work...

## 3 What is an agent
@ card "What is an AI agent?" icon=bot
So, [.3] here, we have to talk about [.3] what an AI agent actually is.

@ fig llm-vs-agent step=1
When you normally chat with AI, [.2] you are really talking straight to [.3] the large model, the LLM,
@ fig llm-vs-agent step=2
and it thinks, [.2] and then it writes some text back to answer you.
@ fig llm-vs-agent step=3
And an agent adds [.3] tool calling on top of the LLM, [.2] which means, it has the ability to use tools.
@ fig llm-vs-agent step=4
And you can think of tools as [.3] its hands,
@ fig llm-vs-agent step=5
so once it has thought things through, it can change the code files on your machine [.2] by itself, [.2] run commands, search the web, [.3] and open a browser.
And the thing is, [.2] having hands [.3] is still not enough,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right"
the key is, [.3] it loops,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=2
like, [.2] it calls a tool,
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=3
looks at the result, [.2]
@ loop "LLM|bot" "Tool|square-terminal" "Result|file-text" "Next step|arrow-right" lit=4
and then decides what to do next.
@ fig llm-vs-agent step=6
And then it calls again, looks again, [.3] and keeps going until the job is done, right?

@ formula "Agent" "LLM" "Hands + Loop"
So, [.3] hands, plus the ability to loop on its own, [.3] and that's when you get [.3] an agent.
@ fig llm-vs-agent step=7
And that means, [.2] it does not just answer you anymore,
@ fig llm-vs-agent step=8
but it can actually finish a task [.3] by itself.

## 4 What is a harness
@ card "New problems" kicker="Once an agent works on its own" icon=triangle-alert
So, [.3] now agents can do work on their own, [.3] but that also brings [.3] new problems.

@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work"
And if you look back at the last few years,
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=1
in 2024, [.2] people were working on how to write good prompts.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=2
And in 2025, [.2] people figured out they needed to get [.3] context engineering right, [.2] you know, managing what's in the AI's context, [.2] so it can perform consistently.
@ logos claude-code codex github-copilot
And by 2026, [.3] coding agents like Claude Code, Codex, and GitHub Copilot can really do the work for you,
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Coding agents at work" now=3
and being able to do the work [.3] also means new problems, right?

@ fig nine-gaps step=1
And companies found that, [.3] to really put agents to work, they have to solve [.3] these problems.

@ fig nine-gaps step=2
So, [.3] number one is, [.2] it does not know your systems and projects, so someone still has to walk it through them [.3] every time.

@ fig nine-gaps step=3
And number two is, [.2] how do you keep memory [.3] across sessions,
and if one session breaks, [.2] how does another one [.3] pick up the task?

@ fig nine-gaps step=4
And the third thing is, [.2] people only use the agent [.3] to change code,
and everything else, like, [.2] running tests, the CI/CD pipeline, [.2] updating tickets, [.3] people still do all of that themselves.

@ fig nine-gaps step=5
And another thing is, as I said, [.2] it does not always follow [.3] the rules you agreed on.

@ fig nine-gaps step=6
And people do not dare to give it access to servers, [.3] because it might do something dangerous, like, [.2] dropping a table, right?

@ fig nine-gaps step=7
And when it finishes a task, [.3] it tends to be totally sure [.2] its result is right.

@ fig nine-gaps step=8
And then, [.2] where did the money and the time go, [.2] and how do you cut them down?
And the plan, the logs, the traces of how the task went, [.4] none of it gets recorded.

@ big "5" "sessions at most, before human attention is the bottleneck" icon=messages-square
And one person can keep an eye on [.3] five sessions, tops,
so human attention becomes [.3] the bottleneck for the agent's work, right?

@ fig nine-gaps step=10
And the last one is, [.2] on a long or complex task, [.3] the agent always stops [.3] partway through.

@ fig nine-gaps step=11
And as you can see, [.3] that's way too many problems,
and the skill of getting an agent to work [.3] both steadily and well,
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Harness engineering" now=3
that's called [.3] harness engineering.

@ formula "Agent" "Model" "Harness"
And there's a formula, [.3] Agent = Model + Harness,
@ fig harness-around step=1
and everything outside the model, [.3] that's the harness.

@ fig program-vs-agent step=1
And before, [.3] all of this depended on you [.3] reminding it in the prompt,
@ fig program-vs-agent step=2
but now, [.2] it's handed over to programs.
@ fig program-vs-agent step=3
And this is because [.3] a program does the same thing every time, [.2]
@ fig program-vs-agent step=4
it does not cost tokens, [.2] and it does not depend on the model [.3] behaving itself, right?
@ fig program-vs-agent step=5
So, [.3] the fixed, predictable stuff [.3] goes to programs,
@ fig program-vs-agent step=6
and the stuff that needs judgment and thinking [.3] goes to the agent.

## 5 My harness
@ board/tour-list crop=0,0,1,0.42
So, [.3] I built a harness framework myself,
@ logos github-copilot vscode
and it runs on [.3] GitHub Copilot in VS Code.

@ logos m365-copilot github-copilot
And if your team is a Microsoft customer, [.2] I guess you are most likely using [.3] two Copilots at once, [.2] M365 Copilot and GitHub Copilot.
@ logos "m365-copilot|chat, mail, documents" "github-copilot|coding agent"
And GitHub Copilot is the one we call [.3] a coding agent,
@ fig harness-around step=2
and my harness is there to help you drive GitHub Copilot [.3] better.

@ fig nine-gaps step=12
So, [.3] let's go back to that list of problems, and see what each one [.3] looks like in my harness.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=1
So, [.3] number one is, [.2] it does not know your systems and projects, so someone still has to walk it through them [.3] every time.

@ fig kb-build step=1
And for that, [.3] I built a standard framework that turns a codebase into [.3] a knowledge base,
@ fig kb-build step=2
and it uses a set of tools to learn your codebase, [.2]
@ fig kb-build step=3
find the hidden dependencies between files, [.2]
@ board/real-kb-card crop=0.3,0.08,0.65,0.49 box=0.305,0.32,0.64,0.095 text="A card: what it reads, what it writes, who calls it"
and write what it finds [.3] into cards.
@ fig kb-build step=5
And once it's done learning, it generates a summary file and an index, [.2] kind of like a table of contents.
@ fig kb-build step=6
And that means, [.2] the agent does not have to [.3] re-read the code every time,
@ fig kb-build step=7
it just loads the summary file and a few of the cards,
@ board/real-kb-summary crop=0.29,0.09,0.53,0.62 box=0.3,0.225,0.5,0.25 text="The summary file of a domain: purpose, flows, key data"
and it gets [.3] a rough picture of your codebase, right?
@ board/kb-lookup crop=0,0.03,0.7,0.42 box=0.015,0.2,0.45,0.245 text="Look up: who uses it, what it uses, which file"
And if it needs to, [.3] it can jump straight to the right files [.2] through the index.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=2
And number two is, [.2] how do you keep memory [.3] across sessions,
@ fig task-folder step=1
and if one session breaks, [.2] how does another one [.3] pick up the task?

@ fig task-folder step=2
So, [.3] in my harness, each task is a folder.
@ fig task-folder step=3
And it holds the files for [.3] the task's whole life,
@ fig task-folder step=4
like, [.2] the task plan, history logs, status, [.2]
@ fig task-folder step=5
requirement docs, test scripts, the changed code, [.3]
@ board/real-files-top crop=0.02,0.58,0.26,0.41 box=0.035,0.677,0.235,0.305 text="A real task folder: the diff, the commit message, the plans, …"
and anything the agent produces [.3] while it works,
all of it gets saved in there.
@ board/real-files-top crop=0.29,0.08,0.7,0.5 box=0.295,0.165,0.68,0.105 text="TASK.md: a new session reads this first"
So, [.2] even if one session dies, [.3] another session just scans that task folder, and picks right up.

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=3
And the third thing is, [.2] people only use the agent [.3] to change code,
and everything else, like, [.2] running tests, the CI/CD pipeline, [.2] updating tickets, [.3] people still do all of that themselves.
@ big "DROP TABLE" "the one command nobody wants an agent to run" icon=database-zap
And people do not dare to give it access to servers, [.3] because it might do something dangerous, like, [.2] dropping a table.

@ fig tool-pack step=1
So, [.3] I give the agent access to [.3] the dev and test environments,
@ board/real-agent-actions-dev crop=0.04,0.27,0.92,0.19 box=0.045,0.298,0.91,0.148 text="In a real task: the agent edits code and tests in DEV, then tests a copy"
so it can develop on its own, [.2] write test scripts on its own, run them on its own, [.3] and fix things on its own.
@ fig tool-pack step=3
And for safety, [.3] here's how I did it,
@ fig tool-pack step=4
through a standard Toolpack, the agent gets [.3] read-only access to the non-prod environments,
@ board/real-sql-held crop=0.12,0.795,0.78,0.2 box=0.135,0.966,0.735,0.026 text="An UPDATE on shop-qat waits for a person and a typed code"
and anything that writes or executes [.3] needs a person to approve it.
@ board/outside-tools-packs crop=0,0,1,0.56 box=0.027,0.405,0.946,0.12 text="The sqlserver tool pack ships with the harness"
For example, [.2] with Microsoft's SQL Server,
@ fig guard-layers step=1
I have tested my harness against [.3] thousands of attempts to sneak in dangerous commands,
@ fig guard-layers step=2
and between a blacklist, [.2] a whitelist,
@ fig guard-layers step=3
a person making the call, [.2] and the account's own permissions, [.3]
@ board/real-sql-live crop=0.09,0,0.81,1 box=0.1,0.12,0.8,0.4 text="DROP and TRUNCATE refused, the UPDATE held"
the agent's access [.3] stays safe, right?

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=4
And number four is, [.2] when it finishes a task, [.3] it tends to be totally sure [.2] its result is right.

@ fig reviewer step=1
So, [.3] I bring in an independent reviewer [.3] as a subagent,
@ fig reviewer step=2
and the subagent reviews everything the main agent did, [.2]
@ board/real-review crop=0.04,0.565,0.78,0.42 box=0.05,0.585,0.34,0.06 text="PASS, and each point cites a line and the requirement"
and gives a test verdict, [.3] so it's not just the main agent [.3] checking its own work anymore.
@ board/checks-used-review crop=0,0.46,1,0.54 box=0.04,0.79,0.92,0.2 text="Caught: capital letters and digits were never checked"
And in practice, [.3] the reviewer catches [.3] a lot of cases the main agent did not think of, right?

@ list "How my harness handles them" "It doesn't know your systems|folder-search" "Memory across sessions|history" "Tests, pipelines, tickets · server access|server" "Sure it got it right|badge-check" "Time and money, not recorded|receipt" lit=5
And the last one is, [.2] where did the money and the time go, [.2] and how do you cut them down?
@ fig task-report step=1
And the plan, the logs, the traces of how the task went, [.4] none of it gets recorded.

@ board/real-report crop=0,0.075,1,0.26 box=0.012,0.178,0.975,0.152 text="A real task: 2 min 3 s of work, 73.9 Credits"
So, [.3] I built a task report dashboard just for looking at [.3] the stats of a whole task,
@ board/real-report crop=0,0.85,1,0.15 box=0.03,0.885,0.94,0.05 text="Agent working 2 min 3 s, waiting for you 8 min 49 s"
like, [.2] where the time went,
@ board/real-report-prompts crop=0.02,0.53,0.66,0.46 box=0.43,0.6,0.245,0.375 text="Credits by stage: the requirement took 48%"
where the money went, [.2]
@ board/real-sql-report crop=0.02,0.13,0.96,0.31 box=0.035,0.135,0.17,0.024 text="Another task's report: 3 of 5 tool calls failed"
and which tool calls failed,
@ fig task-report step=2
so all the conclusions are [.3] right there at a glance.

@ board/tour-lobby crop=0,0,1,0.62
And there's a lot more, [.3] but to save time, I will not list it all here.

## 6 Summary
@ card "AI hasn't gotten dumber" icon=brain
So, [.3] AI has not gotten dumber.
@ timeline "2024|Prompt engineering" "2025|Context engineering" "2026|Harness engineering" now=1
It's just that [.2] the way we use it [.3] is still stuck in 2024,
@ fig who-does-what step=1
like, [.2] we still treat it as a chatbot, and people still do all the legwork in between, [.2] watch the process, [.3] and do the checks.

@ fig who-does-what step=2
And the agent hands that legwork [.3] over to programs,
@ fig who-does-what step=3
and the harness hands the process, [.2] the checks, [.2] and the boundaries over to programs too,
@ fig who-does-what step=4
so people can finally [.3] step back,
@ board/accept box=0.045,0.85,0.135,0.11 text="You make the call: Accept and close"
and just make the calls [.2] and be the gatekeepers, right?

@ quote "Which stronger model should we switch to?" by="Don't ask this first"
So, [.3] if you are trying to get your team using AI, [.3] don't rush to ask, [.2] "Which stronger model should we switch to?"
@ fig harness-around step=3
First, [.3] ask, "What's missing around our AI?"

@ board/one-01-new-task box=0.02,0.54,0.47,0.165 text="Your first task starts here"
And if you want to try it yourself,
@ card "Install the harness, start your first task" kicker="Next video" icon=play
in the next video, [.3] I will help you install this harness, and kick off [.3] your first task.
