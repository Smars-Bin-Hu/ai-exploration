# Basic 01 · Stop using AI the 2024 way

## 0 Hook

It's 2026, and a lot of teams want AI to really land in how they build software. Plenty of companies have bought their people an AI chat service or a coding agent, like Claude Code, Codex or GitHub Copilot. But in practice, we see that many teams still only use AI for a small slice of their daily work. And lots of people still use AI the same old way: ask a question, get an answer, chat.

// picture: Claude Code, Codex and GitHub Copilot need to appear

Here's an example. Say you're a software engineer, and you've got a huge legacy system on your hands. The business side gives you a requirement. You've built lots of features like this before, and you know exactly what the best solution is. Which code to change, how to test it, what depends on what before and after, what it might affect: you've got the experience for all of it. Now someone makes you do it with AI. What do you do?

Probably something like this. First you dig out the code files you think matter, one by one, and hand them to the chat box. Then you write a long explanation: what this code does, and how it all connects. Then you paste in the requirement. And last, a whole screen of "do this", "add that", "whatever you do, don't touch that".

The AI hasn't written a single line of code, and you've already been busy for half an hour. Then you hit Enter, and hope it gives you the right result.

But what you usually get is an answer you're maybe 80 to 90 percent happy with. You paste the code it wrote back in, run the tests yourself, check the results yourself... and find some parts are still wrong. So you spend even more time reviewing the code... In the end you feel it's faster to just write it yourself. AI can't understand your complex system, and it can't see the traps you know about.

// picture: a long prompt, the AI's answer, you falling apart

This video wants to make three things clear: what's wrong with using AI this way, why it's so hard for development teams to make AI really land, and what the missing piece is called.

## 1 Your pain points

If you've used AI like this, you've probably run into every one of these.

One: it doesn't know your project. Every single time, you have to find the code, paste the code, explain the code.

Two: it loses its memory. Open a new chat, and everything you said before is gone. You have to say it all again from the start. And you'll notice that the longer one chat goes on, the worse it seems to do. Things you agreed on early, it forgets later.

Three: you tell it lots of things to do and not to do, and it doesn't always do them. Most of the time it listens. But every so often, it skips exactly the step you cared about most. Especially as the chat gets longer and the history piles up, the AI's attention drifts, and it remembers the older stuff less and less.

Four: it's always confident when it checks itself. "It's done, and all the tests pass." Then you get it back, take a look, and there's still a pile of mistakes.

Five: you can't see what it actually did. Which files it changed, which commands it ran, why it changed things that way. Afterwards, it's hard to say.

// picture: one image per pain point

## 2 The root cause

Is this how you use AI right now?

Actually, this is how people used AI in 2024: as a chatbot.

In 2024, most people were still working out how to write a good prompt so the AI would do better, and people called it Prompt Engineering. But here's the problem. Even if the AI model is smart enough, you're still treating it as someone who answers questions. You haven't let it get its hands on the work. Apart from answering your questions, every other job still lands on you: finding the code, sorting out the requirement, running the tests, remembering the context, watching it follow the process, checking its results. You do all of it by hand.

And in the end, it's easy to hear the same old line: AI isn't reliable, AI makes mistakes, AI can only help with part of my work...

## 3 What is an agent

So here, I have to explain what an AI agent is.

When you chat with AI day to day, you're really talking straight to the large language model, the LLM. It thinks, then writes you a piece of text as an answer. An agent is an LLM with tool calling added: the ability to use tools. Think of tools as its hands. Once it's thought things through, it can go and change the code files on your machine by itself, run commands, search the web, open a browser. But hands alone aren't enough. The key is that it loops. It calls a tool, takes a look at the result, then decides what to do next. Then it calls again, looks again, and keeps going until the job is done.

With hands, and a loop of its own, an agent is born. It doesn't just answer you anymore. It can get a piece of work done by itself.

// picture: LLM → tool → result → next step, in a circle

## 4 What is a harness

Once an agent can do work on its own, new problems come with it.

Look back over the last few years. In 2024, people were figuring out how to write good prompts. In 2025, people found you need good context engineering, managing the AI's context, before it performs consistently. By 2026, coding agents can really get work done for you, like Claude Code, Codex and GitHub Copilot. And being able to do work also brings new problems.

Companies found that to make agents really land, they have to solve these problems.

One: it doesn't know your systems and projects, so a person still has to introduce them every time.

Two: how do you keep memory across sessions? If one session dies, how does another session pick up the task?

Three: people only use the agent to change code. Running the tests, the CI/CD pipeline, updating the tickets: people still do all of that.

Four: rules you agreed on, it doesn't always follow.

Five: you don't dare open up your servers to it, because it might do something dangerous, like dropping a table.

Six: when it finishes a task, it tends to confidently believe its result is right.

Seven: where did the money and the time go, and how do you cut them down? The plan, the logs, the trail of the task: none of it is recorded.

Eight: a person can keep an eye on five sessions at most, so human attention becomes the bottleneck for the agent's work.

Nine: on a long or complex task, the agent always ends up stopping partway.

There are just so many problems. Getting an agent to work steadily and well is a craft of its own, and it's called harness engineering.

There's a formula: Agent = Model + Harness. Everything outside the model is the harness.

All of this used to be you, reminding it in the prompt. Now a program does it. Because a program is deterministic: it doesn't spend tokens, and it doesn't rely on the model behaving itself. We hand the deterministic jobs to programs, and the things that need judgment and thinking to the agent.

// picture: Agent = Model + Harness, five things around the model

## 5 My harness

I've built a harness framework myself, based on GitHub Copilot in VS Code.

If your team is a Microsoft customer, you're most likely using two Copilots at the same time: M365 Copilot and GitHub Copilot. GitHub Copilot is what we call a coding agent. My harness is there to help you steer GitHub Copilot better.

Let's go back to those gaps, and see what each one looks like in my harness.

First: it doesn't know your systems and projects, so a person still has to introduce them every time.

I built a standard framework that turns a codebase into a knowledge base. A set of tools studies your codebase, finds the hidden dependencies between files, and writes them up as cards. When the learning is done, it produces a summary file and an index. The agent doesn't have to read the code again every time. It only loads the summary file and a few cards, and it has a rough idea of your codebase. And if it needs to, it can go straight to the right file through the index.

Second: how do you keep memory across sessions? If one session dies, how does another session pick up the task?

Every task is a folder. It holds the files for the task's whole life: the task plan, the history log, the status, the requirement document, the test scripts, the changed code, and anything else the agent produces while it works. It's all saved in there. So even if one session dies, another session only has to scan this task folder, and it can carry on right away.

Third: people only use the agent to change code, and running the tests, the CI/CD pipeline and updating the tickets are still done by people. And you don't dare open up your servers to it, because it might do something dangerous, like dropping a table.

Give the agent access to the development and test environments, and it can build things itself, write its own test scripts, run them itself, and fix them itself. For safety, here's what I do. Through a standard tool pack, the agent gets read-only access to the lower environments. Write and execute access has to be approved by a person. Take Microsoft's SQL Server: I've run my harness against thousands of cases of dangerous commands being injected. With a blacklist, a whitelist, a person making the call, and the account's own permissions, the agent's access stays safe.

Fourth: when it finishes a task, it tends to confidently believe its result is right.

I bring in an independent reviewer as a subagent. The subagent reviews everything the agent did on the task, and gives a test verdict. In practice, the reviewer finds lots of cases the main agent never thought of.

Fifth: where did the money and the time go, and how do you cut them down? The plan, the logs, the trail of the task: none of it is recorded.

I built a task report panel just for the whole task's numbers: where the time went, where the money went, which tool calls failed. Every conclusion, clear at a glance.

And there's a lot more, but there isn't time to go through it all here.

## 6 Summary

So, AI hasn't gotten dumber. It's that the way we use it is still stuck in 2024: treating it as a chatbot, with people doing the copying and pasting, watching the process, and doing the checks.

Agents hand the copying and pasting to a program. A harness hands the process, the checks and the boundaries to a program too. People can finally step back, and just make the calls and sign off.

If you're pushing AI on your team, don't rush to ask "which stronger model should we switch to?" First, ask one question: "What's missing around our AI?"

If you want to try it yourself, in the next video I'll help you install this harness and start your first task.
