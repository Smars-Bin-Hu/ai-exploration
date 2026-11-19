# Basic 01 · English draft

## 0 Hook

Say you're building a feature with AI today.

You find the code files you think matter, and paste them into the chat, one by one. You write a long explanation of what the code does and how it fits together. You paste in the requirement. Then a whole screen of "do this", "add that", "never touch that".

The AI hasn't written a line of code, and you've already spent half an hour. Then you hit Enter and hope it gets it right.

// picture: a very long prompt

This video covers three things: what's wrong with working this way, where the problem really comes from, and what the missing piece is called.

## 1 Your pain points

If you've used AI like this, you've probably hit every one of these.

One: it doesn't know your project. Every time, you have to find the code, paste the code, explain the code.

Two: it forgets. Open a new chat, and everything you said before is gone. You start over. And you'll notice the longer one chat goes on, the worse it seems to get. Things you agreed on early, it forgets later.

Three: you tell it lots of dos and don'ts, and it doesn't always listen. Most of the time it does. But every so often, it skips the one step you cared about most.

Four: it's always confident when it checks its own work. "Done. All tests pass." Then you look, and there's a pile of bugs.

Five: you can't see what it actually did. Which files it changed, which commands it ran, why it made those changes. Afterwards, it's hard to tell.

// picture: one image per pain point

## 2 The root cause

Is this how you use AI right now?

That's actually how people used AI in 2024: as a chatbot.

The problem isn't that the AI isn't smart enough. The problem is that the work around it, work a program should be doing, all lands on you. Finding the code, keeping track of the context, making sure it follows the process, checking its results. You do all of it by hand. And when you get tired, you miss things. So it's exhausting, and it's still not reliable.

## 3 What is an agent

So what's an agent?

When you chat with AI, you're really talking straight to the large language model, the LLM. It thinks, then writes you an answer in text.

An agent is an LLM plus tool calling: the ability to use tools. Think of tools as its hands. Once it's worked out what to do, it can go and change the code files on your machine, run commands, search the web, open a browser.

But hands aren't enough. The key is that it loops. It calls a tool, looks at the result, and decides what to do next. Then it calls another one, looks again, and keeps going until the job is done.

Hands, plus a loop of its own. That's how you get an agent. It doesn't just answer you anymore. It can finish a piece of work by itself.

// picture: LLM → tool → result → next step, in a circle

## 4 What is a harness

Once an agent can work on its own, a new problem shows up.

Look back over the last few years. In 2024, everyone was figuring out how to write good prompts. In 2025, people found you need good context engineering, managing what's in the AI's context, before it performs consistently. By 2026, coding agents can really do work for you: Claude Code, Codex, GitHub Copilot. And if it can do work, it can also do dangerous things. Getting an agent to do the work reliably and well is a skill of its own. It's called harness engineering.

There's a formula: Agent = Model + Harness. Everything outside the model is the harness.

Hold that up against the five pain points. The harness takes care of exactly five things:

- It doesn't know the project, and it forgets: that's context management.
- It doesn't always do what you say: that's workflows and approvals.
- It might do something dangerous: that's blocking dangerous actions.
- It's too confident checking itself: that's having another agent check it.
- It's a black box: that's being able to audit what it did afterwards.

All of this used to be you, reminding it again and again in the prompt. Now a program does it.

// picture: Agent = Model + Harness, five things around the model

## 5 My harness

I built a harness framework myself. It's based on GitHub Copilot in VS Code.

If your team is a Microsoft customer, you're most likely using two Copilots: M365 Copilot and GitHub Copilot. GitHub Copilot is the coding agent here, the same kind of thing as the well-known Claude Code and Codex. My harness helps you steer GitHub Copilot better.

Let's go through those five things again, and see what each one looks like in my harness.

One: memory. Every task gets its own folder, with the requirement, the plan and the progress written inside. Close the chat, no problem. Open a new one, and it picks up from the folder. Your team can also keep a knowledge base, with how the project is laid out and where the traps are. The agent reads it every time before it starts.

// picture: a task folder; a new chat picks up where the last one stopped

Two: process. A development task always goes like this. First, confirm the requirement. Then, approve the plan. Last, approve the write-back. At each step, you type a code on the board yourself. The agent can't skip it, and it can't do it for you.

// picture: the three approvals, the window where you type the code

Three: boundaries. The agent only changes a copy of the code. It can't touch your repo. If it tries `git push`, a check called the gate stops it on the spot, and tells it why.

// picture: the blocked command and the reason

Four: checking. You can have another agent check its work on its own. If the work fails, it goes back to be fixed. Only once it passes can it be written back.

// picture: the independent check finds a problem

Five: audit. Every step it took, every time it was blocked, how much time it spent, it's all on the board. Afterwards, you can see it at a glance.

// picture: the board's Records and the task report

## 6 Summary

So, AI hasn't gotten dumber. The way we use it is still stuck in 2024: treat it as a chatbot, and have people do the copying and pasting, watch the process, and check the work.

Agents hand the copying and pasting to a program. A harness hands the process, the checks and the boundaries to a program too. People can finally step back, and just make the calls and sign off.

If you're pushing AI on your team, don't start by asking "which stronger model should we switch to?" Start by asking: "What's missing around our AI?"

If you want to try it yourself, in the next video I'll walk you through installing this harness and starting your first task.
