# Basic 01 · Stop using AI the 2024 way

## 0 Hook
@ basic-01/p03 crop=0.490,0.320,0.450,0.430
Say you're building a feature with AI today.
@ basic-01/p03 crop=0.490,0.320,0.450,0.430 box=0.515,0.365,0.385,0.125
You find the code files you think matter, and paste them into the chat, one by one.
You write a long explanation of what the code does and how it fits together.
@ basic-01/p03 crop=0.490,0.320,0.450,0.430 box=0.515,0.491,0.300,0.033
You paste in the requirement.
@ basic-01/p03 crop=0.490,0.320,0.450,0.430 box=0.515,0.526,0.250,0.116
Then a whole screen of "do this", "add that", "never touch that".
@ basic-01/p03 crop=0.490,0.320,0.450,0.430 box=0.505,0.350,0.420,0.370
The AI hasn't written a line of code, and you've already spent half an hour.
Then you hit Enter and hope it gets it right.
@ card "What's wrong · Why · What's missing"
This video covers three things: what's wrong with working this way, where the problem really comes from, and what the missing piece is called.

## 1 Your pain points
@ card "Five pain points"
If you've used AI like this, you've probably hit every one of these.
@ basic-01/p04 crop=0.490,0.400,0.360,0.360
One: it doesn't know your project.
@ basic-01/p04 crop=0.490,0.400,0.360,0.360 box=0.505,0.455,0.305,0.265
Every time, you have to find the code, paste the code, explain the code.
@ basic-01/p04 crop=0.490,0.400,0.360,0.360 box=0.505,0.455,0.305,0.170
Two: it forgets.
Open a new chat, and everything you said before is gone.
You start over.
@ basic-06/p05 crop=0.490,0.340,0.450,0.430
And you'll notice the longer one chat goes on, the worse it seems to get.
@ basic-06/p05 crop=0.490,0.340,0.450,0.430 box=0.510,0.580,0.410,0.155
Things you agreed on early, it forgets later.
@ basic-01/p05 crop=0.490,0.380,0.450,0.320
Three: you tell it lots of dos and don'ts, and it doesn't always listen.
Most of the time it does.
@ basic-01/p05 crop=0.490,0.380,0.450,0.320 box=0.585,0.475,0.085,0.145
But every so often, it skips the one step you cared about most.
@ basic-01/p07 crop=0.500,0.400,0.430,0.280
Four: it's always confident when it checks its own work.
@ basic-01/p07 crop=0.500,0.400,0.430,0.280 box=0.525,0.458,0.168,0.125
"Done. All tests pass."
@ basic-01/p07 crop=0.500,0.400,0.430,0.280 box=0.737,0.458,0.168,0.125
Then you look, and there's a pile of bugs.
@ basic-01/p08 crop=0.490,0.300,0.450,0.450
Five: you can't see what it actually did.
Which files it changed, which commands it ran, why it made those changes.
@ basic-01/p08 crop=0.490,0.300,0.450,0.450 box=0.722,0.580,0.135,0.100
Afterwards, it's hard to tell.

## 2 The root cause
@ basic-01/p09 crop=0.490,0.450,0.450,0.270
Is this how you use AI right now?
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.495,0.360,0.375,0.200
That's actually how people used AI in 2024: as a chatbot.
@ basic-01/p13 crop=0.490,0.280,0.450,0.520
The problem isn't that the AI isn't smart enough.
The problem is that the work around it, work a program should be doing, all lands on you.
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.495,0.395,0.130,0.135
Finding the code, keeping track of the context, making sure it follows the process, checking its results.
You do all of it by hand.
And when you get tired, you miss things.
So it's exhausting, and it's still not reliable.

## 3 What is an agent
@ basic-01/p11 crop=0.470,0.380,0.480,0.340
So what's an agent?
@ basic-01/p11 crop=0.470,0.380,0.480,0.340 box=0.490,0.440,0.190,0.135
When you chat with AI, you're really talking straight to the large language model, the LLM.
It thinks, then writes you an answer in text.
@ basic-01/p11 crop=0.470,0.380,0.480,0.340 box=0.596,0.440,0.238,0.135 text="Tool calling"
An agent is an LLM plus tool calling: the ability to use tools.
Think of tools as its hands.
@ basic-01/p11 crop=0.470,0.380,0.480,0.340 box=0.727,0.426,0.210,0.160
Once it's worked out what to do, it can go and change the code files on your machine, run commands, search the web, open a browser.
But hands aren't enough.
@ basic-01/p11 crop=0.470,0.380,0.480,0.340 box=0.565,0.556,0.290,0.110 text="The agent loop"
The key is that it loops.
@ basic-01/p12 crop=0.480,0.290,0.460,0.480
It calls a tool, looks at the result, and decides what to do next.
@ basic-01/p12 crop=0.480,0.290,0.460,0.480 box=0.797,0.324,0.135,0.280
Then it calls another one, looks again, and keeps going until the job is done.
@ card "Agent = LLM + tools + loop"
Hands, plus a loop of its own. That's how you get an agent.
It doesn't just answer you anymore. It can finish a piece of work by itself.

## 4 What is a harness
@ card "A new problem"
Once an agent can work on its own, a new problem shows up.
Look back over the last few years.
@ card "2024 · Prompt engineering"
In 2024, everyone was figuring out how to write good prompts.
@ card "2025 · Context engineering"
In 2025, people found you need good context engineering, managing what's in the AI's context, before it performs consistently.
@ basic-01/p16 crop=0.480,0.300,0.470,0.460 box=0.502,0.556,0.425,0.135
By 2026, coding agents can really do work for you: Claude Code, Codex, GitHub Copilot.
@ basic-06/p04 crop=0.500,0.310,0.440,0.450 box=0.520,0.345,0.390,0.380
And if it can do work, it can also do dangerous things.
@ card "2026 · Harness engineering"
Getting an agent to do the work reliably and well is a skill of its own.
It's called harness engineering.
@ basic-01/p15 crop=0.480,0.330,0.470,0.380
There's a formula: Agent = Model + Harness.
@ basic-01/p15 crop=0.480,0.330,0.470,0.380 box=0.615,0.360,0.190,0.235
Everything outside the model is the harness.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530
Hold that up against the five pain points.
The harness takes care of exactly five things:
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.352,0.430,0.056 text="Context management"
It doesn't know the project, and it forgets: that's context management.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.415,0.430,0.056 text="Workflows and approvals"
It doesn't always do what you say: that's workflows and approvals.
@ basic-06/p12 crop=0.480,0.280,0.470,0.470 box=0.502,0.352,0.425,0.065
It might do something dangerous: that's blocking dangerous actions.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.480,0.430,0.056 text="Another agent checks"
It's too confident checking itself: that's having another agent check it.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.500,0.670,0.430,0.056 text="Audit afterwards"
It's a black box: that's being able to audit what it did afterwards.
@ basic-01/p03 crop=0.490,0.320,0.450,0.430 box=0.505,0.350,0.420,0.370
All of this used to be you, reminding it again and again in the prompt.
@ basic-01/p10 crop=0.480,0.330,0.460,0.400 box=0.495,0.565,0.430,0.140
Now a program does it.

## 5 My harness
@ basic-01/p17 crop=0.480,0.260,0.470,0.540 box=0.500,0.293,0.430,0.293
I built a harness framework myself.
It's based on GitHub Copilot in VS Code.
@ card "M365 Copilot · GitHub Copilot"
If your team is a Microsoft customer, you're most likely using two Copilots: M365 Copilot and GitHub Copilot.
@ basic-01/p16 crop=0.480,0.300,0.470,0.460 box=0.502,0.556,0.425,0.135
GitHub Copilot is the coding agent here, the same kind of thing as the well-known Claude Code and Codex.
@ basic-01/p16 crop=0.480,0.300,0.470,0.460 box=0.500,0.330,0.440,0.200
My harness helps you steer GitHub Copilot better.
@ basic-01/p18 crop=0.480,0.280,0.470,0.530 box=0.725,0.315,0.200,0.470
Let's go through those five things again, and see what each one looks like in my harness.
@ tutorials/1_day/lifecycle box=0.015,0.045,0.290,0.115 text="Memory: the task folder"
One: memory.
Every task gets its own folder, with the requirement, the plan and the progress written inside.
@ board/go-on-new-chat box=0.122,0.700,0.850,0.210
Close the chat, no problem.
Open a new one, and it picks up from the folder.
@ basic-01/p19 crop=0.410,0.130,0.550,0.670
Your team can also keep a knowledge base, with how the project is laid out and where the traps are.
The agent reads it every time before it starts.
@ tutorials/1_day/lifecycle
Two: process.
A development task always goes like this.
@ tutorials/1_day/lifecycle box=0.005,0.560,0.228,0.240
First, confirm the requirement.
@ tutorials/1_day/lifecycle box=0.255,0.560,0.215,0.240
Then, approve the plan.
@ tutorials/1_day/lifecycle box=0.500,0.560,0.215,0.240
Last, approve the write-back.
@ board/one-06-approve-code box=0.025,0.540,0.950,0.330 text="You type the code"
At each step, you type a code on the board yourself.
The agent can't skip it, and it can't do it for you.
@ basic-06/p15 crop=0.480,0.330,0.470,0.390
Three: boundaries.
@ basic-06/p15 crop=0.480,0.330,0.470,0.390 box=0.503,0.370,0.200,0.310
The agent only changes a copy of the code.
@ basic-06/p15 crop=0.480,0.330,0.470,0.390 box=0.718,0.368,0.210,0.160
It can't touch your repo.
@ board/stop-agent-actions box=0.040,0.765,0.920,0.090 text="Stopped by the gate"
If it tries git push, a check called the gate stops it on the spot, and tells it why.
@ basic-01/p21 crop=0.490,0.050,0.390,0.830
Four: checking.
You can have another agent check its work on its own.
@ board/review box=0.035,0.805,0.930,0.180
If the work fails, it goes back to be fixed.
@ board/review box=0.035,0.343,0.930,0.225
Only once it passes can it be written back.
@ board/tour-tab-history box=0.025,0.270,0.945,0.370
Five: audit.
Every step it took, every time it was blocked, how much time it spent, it's all on the board.
@ basic-01/p22 crop=0.410,0.050,0.550,0.830
Afterwards, you can see it at a glance.

## 6 Summary
@ basic-01/p23 crop=0.480,0.310,0.430,0.420
So, AI hasn't gotten dumber.
@ basic-01/p23 crop=0.480,0.310,0.430,0.420 box=0.612,0.345,0.090,0.300
The way we use it is still stuck in 2024: treat it as a chatbot, and have people do the copying and pasting, watch the process, and check the work.
@ basic-01/p23 crop=0.480,0.310,0.430,0.420 box=0.703,0.345,0.090,0.300
Agents hand the copying and pasting to a program.
@ basic-01/p23 crop=0.480,0.310,0.430,0.420 box=0.793,0.345,0.090,0.300
A harness hands the process, the checks and the boundaries to a program too.
@ basic-01/p23 crop=0.480,0.310,0.430,0.420 box=0.580,0.650,0.270,0.045
People can finally step back, and just make the calls and sign off.
@ card "Which stronger model?"
If you're pushing AI on your team, don't start by asking "which stronger model should we switch to?"
@ card "What's missing around our AI?"
Start by asking: "What's missing around our AI?"
@ board/one-01-new-task
If you want to try it yourself, in the next video I'll walk you through installing this harness and starting your first task.

// notes
- Timeline 2024 prompts → 2025 context engineering → 2026 harness engineering: none in the catalog; three cards instead.
- "This video covers three things" overview: basic-01/p02 lists five questions, not these three; card instead.
- M365 Copilot beside GitHub Copilot: none; card instead.
- Agent = LLM + tools + loop as one summary picture: none; card instead.
- A long chat getting worse: none for chat; basic-06/p05 (rules buried in a long task) is the closest.
- Typing the code for "approve plan" and "approve write-back": only the "Confirm requirement" dialog is shown (board/one-06-approve-code).
- Install or first screen for the next-video line: board/tour-enter* carry a real name in the footer; used board/one-01-new-task instead.
- Script lines with markdown: bullet dashes in scene 4 and the backticks around git push are dropped; words unchanged.
