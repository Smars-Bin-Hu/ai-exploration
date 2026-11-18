# Basic 01 · Stop using AI the 2024 way

## 0 Hook
@ card "2026 · AI in the team"
It's 2026, and a lot of teams want AI to really land in how they build software.
@ card "Claude Code · Codex · GitHub Copilot"
Plenty of companies have bought their people an AI chat service or a coding agent, like Claude Code, Codex or GitHub Copilot.
@ basic-01/p09 crop=0.490,0.450,0.450,0.250
But in practice, we see that many teams still only use AI for a small slice of their daily work.
@ basic-01/p09 crop=0.490,0.450,0.450,0.250 box=0.505,0.512,0.420,0.100
And lots of people still use AI the same old way: ask a question, get an answer, chat.
@ card "A legacy system you know well"
Here's an example.
Say you're a software engineer, and you've got a huge legacy system on your hands.
The business side gives you a requirement.
You've built lots of features like this before, and you know exactly what the best solution is.
Which code to change, how to test it, what depends on what before and after, what it might affect: you've got the experience for all of it.
@ basic-01/p03 crop=0.490,0.340,0.450,0.340
Now someone makes you do it with AI.
What do you do?
Probably something like this.
@ basic-01/p03 crop=0.490,0.340,0.450,0.340 box=0.515,0.365,0.385,0.125
First you dig out the code files you think matter, one by one, and hand them to the chat box.
Then you write a long explanation: what this code does, and how it all connects.
@ basic-01/p03 crop=0.490,0.340,0.450,0.340 box=0.515,0.491,0.300,0.033
Then you paste in the requirement.
@ basic-01/p03 crop=0.490,0.340,0.450,0.340 box=0.515,0.526,0.250,0.116
And last, a whole screen of "do this", "add that", "whatever you do, don't touch that".
@ basic-01/p03 crop=0.490,0.340,0.450,0.340 box=0.505,0.355,0.420,0.315
The AI hasn't written a single line of code, and you've already been busy for half an hour.
Then you hit Enter, and hope it gives you the right result.
@ basic-01/p07 crop=0.505,0.420,0.425,0.200 box=0.525,0.458,0.168,0.125
But what you usually get is an answer you're maybe 80 to 90 percent happy with.
@ basic-01/p07 crop=0.505,0.420,0.425,0.200 box=0.737,0.458,0.168,0.125
You paste the code it wrote back in, run the tests yourself, check the results yourself... and find some parts are still wrong.
@ basic-01/p06 crop=0.495,0.450,0.445,0.185
So you spend even more time reviewing the code...
In the end you feel it's faster to just write it yourself.
AI can't understand your complex system, and it can't see the traps you know about.
@ card "What's wrong · Why it's hard · What's missing"
This video wants to make three things clear: what's wrong with using AI this way, why it's so hard for development teams to make AI really land, and what the missing piece is called.

## 1 Your pain points
@ card "Five pain points"
If you've used AI like this, you've probably run into every one of these.
@ basic-01/p04 crop=0.490,0.400,0.360,0.360
One: it doesn't know your project.
@ basic-01/p04 crop=0.490,0.400,0.360,0.360 box=0.505,0.455,0.305,0.265
Every single time, you have to find the code, paste the code, explain the code.
@ basic-01/p04 crop=0.490,0.400,0.360,0.360 box=0.678,0.455,0.132,0.140
Two: it loses its memory.
Open a new chat, and everything you said before is gone.
You have to say it all again from the start.
@ basic-06/p05 crop=0.490,0.340,0.450,0.430
And you'll notice that the longer one chat goes on, the worse it seems to do.
@ basic-06/p05 crop=0.490,0.340,0.450,0.430 box=0.510,0.580,0.410,0.155
Things you agreed on early, it forgets later.
@ basic-01/p05 crop=0.490,0.400,0.450,0.240
Three: you tell it lots of things to do and not to do, and it doesn't always do them.
Most of the time it listens.
@ basic-01/p05 crop=0.490,0.400,0.450,0.240 box=0.585,0.475,0.085,0.145
But every so often, it skips exactly the step you cared about most.
@ basic-06/p05 crop=0.490,0.340,0.450,0.430 box=0.509,0.616,0.025,0.080
Especially as the chat gets longer and the history piles up, the AI's attention drifts, and it remembers the older stuff less and less.
@ basic-01/p07 crop=0.505,0.420,0.425,0.200
Four: it's always confident when it checks itself.
@ basic-01/p07 crop=0.505,0.420,0.425,0.200 box=0.525,0.458,0.168,0.125
"It's done, and all the tests pass."
@ basic-01/p07 crop=0.505,0.420,0.425,0.200 box=0.737,0.458,0.168,0.125
Then you get it back, take a look, and there's still a pile of mistakes.
@ basic-01/p08 crop=0.490,0.320,0.450,0.365
Five: you can't see what it actually did.
Which files it changed, which commands it ran, why it changed things that way.
@ basic-01/p08 crop=0.490,0.320,0.450,0.365 box=0.722,0.580,0.135,0.100
Afterwards, it's hard to say.

## 2 The root cause
@ basic-01/p10 crop=0.480,0.330,0.460,0.400
Is this how you use AI right now?
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.495,0.360,0.375,0.200
Actually, this is how people used AI in 2024: as a chatbot.
@ card "2024 · Prompt engineering"
In 2024, most people were still working out how to write a good prompt so the AI would do better, and people called it Prompt Engineering.
@ basic-01/p13 crop=0.490,0.280,0.450,0.450
But here's the problem.
Even if the AI model is smart enough, you're still treating it as someone who answers questions.
You haven't let it get its hands on the work.
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.497,0.400,0.125,0.125
Apart from answering your questions, every other job still lands on you: finding the code, sorting out the requirement, running the tests, remembering the context, watching it follow the process, checking its results.
You do all of it by hand.
@ basic-01/p09 crop=0.490,0.450,0.450,0.250 box=0.655,0.640,0.120,0.040
And in the end, it's easy to hear the same old line: AI isn't reliable, AI makes mistakes, AI can only help with part of my work...

## 3 What is an agent
@ basic-01/p11 crop=0.480,0.400,0.460,0.265
So here, I have to explain what an AI agent is.
@ basic-01/p11 crop=0.480,0.400,0.460,0.265 box=0.490,0.440,0.190,0.135
When you chat with AI day to day, you're really talking straight to the large language model, the LLM.
It thinks, then writes you a piece of text as an answer.
@ basic-01/p11 crop=0.480,0.400,0.460,0.265 box=0.599,0.448,0.233,0.122 text="Tool calling"
An agent is an LLM with tool calling added: the ability to use tools.
Think of tools as its hands.
@ basic-01/p11 crop=0.480,0.400,0.460,0.265 box=0.727,0.426,0.210,0.160
Once it's thought things through, it can go and change the code files on your machine by itself, run commands, search the web, open a browser.
But hands alone aren't enough.
@ basic-01/p11 crop=0.480,0.400,0.460,0.265 box=0.565,0.568,0.290,0.095 text="The agent loop"
The key is that it loops.
@ basic-01/p12 crop=0.490,0.310,0.450,0.300
It calls a tool, takes a look at the result, then decides what to do next.
@ basic-01/p12 crop=0.490,0.310,0.450,0.300 box=0.797,0.322,0.135,0.280
Then it calls again, looks again, and keeps going until the job is done.
@ card "Agent = LLM + tools + loop"
With hands, and a loop of its own, an agent is born.
It doesn't just answer you anymore.
It can get a piece of work done by itself.

## 4 What is a harness
@ card "New problems"
Once an agent can do work on its own, new problems come with it.
Look back over the last few years.
@ card "2024 · Prompt engineering"
In 2024, people were figuring out how to write good prompts.
@ card "2025 · Context engineering"
In 2025, people found you need good context engineering, managing the AI's context, before it performs consistently.
@ basic-01/p16 crop=0.490,0.315,0.450,0.390 box=0.502,0.556,0.425,0.135
By 2026, coding agents can really get work done for you, like Claude Code, Codex and GitHub Copilot.
And being able to do work also brings new problems.
@ basic-01/p13 crop=0.490,0.280,0.450,0.450
Companies found that to make agents really land, they have to solve these problems.
@ basic-01/p13 crop=0.490,0.280,0.450,0.450 box=0.505,0.320,0.112,0.058
One: it doesn't know your systems and projects, so a person still has to introduce them every time.
@ basic-01/p13 crop=0.490,0.280,0.450,0.450 box=0.650,0.675,0.130,0.058
Two: how do you keep memory across sessions?
If one session dies, how does another session pick up the task?
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.497,0.400,0.125,0.125
Three: people only use the agent to change code.
Running the tests, the CI/CD pipeline, updating the tickets: people still do all of that.
@ basic-01/p05 crop=0.490,0.400,0.450,0.240 box=0.585,0.475,0.085,0.145
Four: rules you agreed on, it doesn't always follow.
@ basic-06/p04 crop=0.500,0.310,0.440,0.450 box=0.520,0.345,0.390,0.380
Five: you don't dare open up your servers to it, because it might do something dangerous, like dropping a table.
@ basic-01/p13 crop=0.490,0.280,0.450,0.450 box=0.505,0.652,0.112,0.058
Six: when it finishes a task, it tends to confidently believe its result is right.
@ basic-01/p13 crop=0.490,0.280,0.450,0.450 box=0.795,0.485,0.125,0.225
Seven: where did the money and the time go, and how do you cut them down?
The plan, the logs, the trail of the task: none of it is recorded.
@ board/tour-lobby crop=0.000,0.000,1.000,0.455 box=0.035,0.165,0.930,0.290
Eight: a person can keep an eye on five sessions at most, so human attention becomes the bottleneck for the agent's work.
@ board/state-stuck-page crop=0.000,0.000,0.650,1.000 box=0.025,0.885,0.350,0.080
Nine: on a long or complex task, the agent always ends up stopping partway.
@ card "2026 · Harness engineering"
There are just so many problems.
Getting an agent to work steadily and well is a craft of its own, and it's called harness engineering.
@ basic-01/p15 crop=0.495,0.350,0.440,0.235
There's a formula: Agent equals model plus harness.
@ basic-01/p15 crop=0.495,0.350,0.440,0.235 box=0.617,0.355,0.184,0.228
Everything outside the model is the harness.
@ basic-01/p03 crop=0.490,0.340,0.450,0.340 box=0.515,0.526,0.250,0.116
All of this used to be you, reminding it in the prompt.
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.495,0.565,0.430,0.140
Now a program does it.
@ basic-01/p15 crop=0.495,0.350,0.440,0.235 box=0.617,0.355,0.184,0.228
Because a program is deterministic: it doesn't spend tokens, and it doesn't rely on the model behaving itself.
@ basic-01/p15 crop=0.495,0.350,0.440,0.235 box=0.500,0.380,0.096,0.180
We hand the deterministic jobs to programs, and the things that need judgment and thinking to the agent.

## 5 My harness
@ basic-01/p17 crop=0.490,0.285,0.450,0.460 box=0.500,0.293,0.430,0.293
I've built a harness framework myself, based on GitHub Copilot in VS Code.
@ card "M365 Copilot · GitHub Copilot"
If your team is a Microsoft customer, you're most likely using two Copilots at the same time: M365 Copilot and GitHub Copilot.
@ basic-01/p16 crop=0.490,0.315,0.450,0.390 box=0.502,0.556,0.425,0.135
GitHub Copilot is what we call a coding agent.
@ basic-01/p16 crop=0.490,0.315,0.450,0.390 box=0.500,0.328,0.432,0.205
My harness is there to help you steer GitHub Copilot better.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.725,0.315,0.205,0.420
Let's go back to those gaps, and see what each one looks like in my harness.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.350,0.430,0.058
First: it doesn't know your systems and projects, so a person still has to introduce them every time.
@ board/kb-overview crop=0.000,0.000,1.000,0.680
I built a standard framework that turns a codebase into a knowledge base.
@ board/kb-lookup crop=0.000,0.180,0.480,0.280 box=0.012,0.275,0.450,0.165
A set of tools studies your codebase, finds the hidden dependencies between files, and writes them up as cards.
@ basic-01/p19 crop=0.410,0.130,0.550,0.670
When the learning is done, it produces a summary file and an index.
The agent doesn't have to read the code again every time.
@ basic-01/p19 crop=0.410,0.130,0.550,0.670 box=0.555,0.405,0.090,0.060
It only loads the summary file and a few cards, and it has a rough idea of your codebase.
@ board/kb-lookup crop=0.000,0.180,0.480,0.280 box=0.012,0.205,0.460,0.060
And if it needs to, it can go straight to the right file through the index.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.543,0.430,0.058
Second: how do you keep memory across sessions?
If one session dies, how does another session pick up the task?
@ tutorials/1_day/lifecycle box=0.015,0.045,0.290,0.115
Every task is a folder.
@ board/tour-tab-files crop=0.000,0.290,0.700,0.710 box=0.030,0.475,0.270,0.515
It holds the files for the task's whole life: the task plan, the history log, the status, the requirement document, the test scripts, the changed code, and anything else the agent produces while it works.
It's all saved in there.
@ board/go-on-new-chat box=0.130,0.730,0.155,0.160
So even if one session dies, another session only has to scan this task folder, and it can carry on right away.
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.497,0.400,0.125,0.125
Third: people only use the agent to change code, and running the tests, the CI/CD pipeline and updating the tickets are still done by people.
@ basic-06/p04 crop=0.500,0.310,0.440,0.450 box=0.520,0.345,0.390,0.380
And you don't dare open up your servers to it, because it might do something dangerous, like dropping a table.
@ board/one-14-todo box=0.045,0.665,0.400,0.290
Give the agent access to the development and test environments, and it can build things itself, write its own test scripts, run them itself, and fix them itself.
@ board/outside-tools-packs crop=0.000,0.000,1.000,0.540 box=0.025,0.160,0.950,0.370
For safety, here's what I do.
Through a standard tool pack, the agent gets read-only access to the lower environments.
@ board/outside-held-card box=0.045,0.850,0.725,0.100
Write and execute access has to be approved by a person.
@ board/outside-tools-packs crop=0.000,0.000,1.000,0.540 box=0.025,0.410,0.950,0.115
Take Microsoft's SQL Server: I've run my harness against thousands of cases of dangerous commands being injected.
@ board/stop-agent-actions box=0.040,0.500,0.920,0.485
With a blacklist, a whitelist, a person making the call, and the account's own permissions, the agent's access stays safe.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.479,0.430,0.058
Fourth: when it finishes a task, it tends to confidently believe its result is right.
@ board/review crop=0.000,0.000,1.000,0.580 box=0.600,0.045,0.160,0.040
I bring in an independent reviewer as a subagent.
@ board/review crop=0.000,0.315,1.000,0.255 box=0.035,0.343,0.930,0.225
The subagent reviews everything the agent did on the task, and gives a test verdict.
@ board/review crop=0.000,0.800,1.000,0.200 box=0.035,0.805,0.930,0.180
In practice, the reviewer finds lots of cases the main agent never thought of.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.670,0.430,0.058
Fifth: where did the money and the time go, and how do you cut them down?
The plan, the logs, the trail of the task: none of it is recorded.
@ board/tour-report crop=0.000,0.020,1.000,0.400 box=0.012,0.160,0.975,0.230
I built a task report panel just for the whole task's numbers: where the time went, where the money went, which tool calls failed.
@ basic-01/p22 crop=0.420,0.060,0.530,0.600
Every conclusion, clear at a glance.
@ card "And a lot more"
And there's a lot more, but there isn't time to go through it all here.

## 6 Summary
@ basic-01/p23 crop=0.490,0.350,0.420,0.300
So, AI hasn't gotten dumber.
@ basic-01/p23 crop=0.490,0.350,0.420,0.300 box=0.612,0.360,0.090,0.285
It's that the way we use it is still stuck in 2024: treating it as a chatbot, with people doing the copying and pasting, watching the process, and doing the checks.
@ basic-01/p23 crop=0.490,0.350,0.420,0.300 box=0.703,0.360,0.090,0.285
Agents hand the copying and pasting to a program.
@ basic-01/p23 crop=0.490,0.350,0.420,0.300 box=0.793,0.360,0.090,0.285
A harness hands the process, the checks and the boundaries to a program too.
People can finally step back, and just make the calls and sign off.
@ card "Which stronger model?"
If you're pushing AI on your team, don't rush to ask "which stronger model should we switch to?"
@ card "What's missing around our AI?"
First, ask one question: "What's missing around our AI?"
@ board/one-01-new-task
If you want to try it yourself, in the next video I'll help you install this harness and start your first task.

// notes
// - Timeline 2024 prompts, 2025 context engineering, 2026 harness engineering: none in the catalog; three cards.
// - Claude Code, Codex and GitHub Copilot in the hook: a card (basic-01/p16 shows them later, in scene 4).
// - "A legacy system you know well", "80 to 90 percent right": no picture of the engineer's own situation; a card, then the basic-01/p07 mock-up.
// - "This video makes three things clear": basic-01/p02 lists five questions, not these three; card.
// - M365 Copilot beside GitHub Copilot: none; card.
// - Agent = LLM + tools + loop as one summary picture: none; card.
// - A long chat getting worse: none for chat; basic-06/p05 (rules buried in a long task) is the closest.
// - Five sessions at most: board/tour-lobby (13 agents waiting for you) stands in; no picture of the five-session limit itself.
// - Long task stops partway: board/state-stuck-page shows the harness's stuck warning, the closest.
// - Thousands of SQL Server injection tests, blacklist and whitelist: no picture of the tests or the lists; the sqlserver tool pack and the blocked-calls tab stand in.
// - Summary file and index of the knowledge base: no picture of the files; basic-01/p19 (knowledge base with 305 cards) stands in.
// - "And a lot more": card.
