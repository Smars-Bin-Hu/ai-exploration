# Basic 01 · Stop using AI the 2024 way

## 0 Hook

It's 2026, and a lot of teams want AI to be a real part of how they build software. Plenty of companies already pay for an AI chat tool or a coding agent, like Claude Code, Codex or GitHub Copilot. But what we actually see is that many teams still use AI for only a small slice of their work. And lots of people even still use it the same old way, as a chat: ask a question, get an answer.

// picture: Claude Code, Codex and GitHub Copilot need to appear

Here's what I mean: say you're a software engineer, and you've got a huge legacy system on your hands. The business side gives you a requirement. You've built plenty of features like this, and you know the best way to do it: which code to change, how to test it, what depends on what, what it might break. You've seen it all. Now you're told to do it with AI. What do you do?

Probably something like this: first, you dig out the files you think matter, one by one, and paste them into the chat. Then you write a long explanation of what the code does and how it all fits together. Then you paste in the requirement. And finally, a whole screen of "do this", "add that", "whatever you do, don't touch that".

The AI hasn't written a single line yet, and you've already spent half an hour. Then you hit Enter and hope it gets it right.

But what you usually get is an answer you're maybe eighty or ninety percent happy with. You paste its code back in, run the tests yourself, check the results yourself, and some of it's still wrong, so you spend even longer reviewing it. In the end, it feels faster to just write it yourself, because the AI doesn't get your complex system, and it can't see the traps you know are there.

// picture: a long prompt, the AI's answer, you falling apart

In this video I want to make three things clear: what's wrong with using AI this way, why it's so hard for development teams to really adopt AI, and what the missing piece is called.

## 1 Your pain points

If you've used AI like this, you've probably run into every one of the following problems.

One: it doesn't know your project. Every single time, you have to find the code, paste the code, explain the code.

Two: it forgets. Open a new chat, and everything you said before is gone, so you have to say it all again. And the longer you stay in the same chat, the worse the AI seems to do: it forgets things you agreed on at the start.

Three: you give it a list of dos and don'ts, and it doesn't always follow them. Most of the time it listens, but every so often it skips exactly the step you care about most. That's especially true in long chats: the more history piles up, the more its attention drifts, and the less it remembers from earlier.

Four: it's always sure of its own work. "Done, and all the tests pass." Then you look for yourself, and there's still a pile of mistakes.

Five: you can't see what it actually did. Which files did it change, which commands did it run, why did it do it that way? After the fact, it's hard to tell.

// picture: one image per pain point

## 2 The root cause

Is this how you use AI right now?

Well, that's how people used AI in 2024: as a chatbot.

Back then, most people were busy learning to write better prompts to get better answers. That was called prompt engineering. But here's the problem: even if the model is smart enough, you're still treating it like someone who just answers questions. You haven't let it get its hands on the work. It answers your questions, and everything else is still on you: finding the code, sorting out the requirement, running the tests, remembering the context, making sure it follows the process, checking its results. You do all of it by hand.

And in the end, you hear the same old lines: AI isn't reliable, AI makes mistakes, AI can only help with part of my work.

## 3 What is an agent

So let me explain what an AI agent is.

When you chat with AI, you're talking straight to the large language model, the LLM: it thinks, then writes you an answer in text. An agent is an LLM plus tool calling, meaning it can use tools. Think of tools as its hands: once it's thought things through, it can go and change the code on your machine itself, run commands, search the web, open a browser. But hands alone aren't enough, the key is that it loops. It calls a tool, looks at the result, and decides what to do next. Then it calls again, looks again, and keeps going until the job's done.

Give an LLM hands and a loop of its own, and you've got an agent. It doesn't just answer you anymore, it can finish a piece of work on its own.

// picture: LLM → tool → result → next step, in a circle

## 4 What is a harness

But once an agent can work on its own, you get a new set of problems.

Look back over the last few years: in 2024, people were figuring out how to write good prompts. In 2025, people found that to get steady results, you have to manage the AI's context well, and that's context engineering. And by 2026, coding agents like Claude Code, Codex and GitHub Copilot can really get work done for you. And that's where the new problems start.

Companies found that to really adopt agents, they have to solve these problems.

One: the agent doesn't know your systems or your projects, so someone still has to explain them every time.

Two: how do you keep its memory from one session to the next? If a session dies, how does a new one pick up the task?

Three: people only use the agent to change code, and still handle the tests, the CI-CD pipeline and the tickets themselves.

Four: it doesn't always follow the rules you agreed on.

Five: you don't dare give it access to your servers, in case it does something dangerous, like dropping a table.

Six: when it finishes a task, it's usually sure it got it right.

Seven: where did the time and money go, and how do you spend less? The plan, the logs, the steps it took: none of it gets recorded.

Eight: one person can keep an eye on five sessions at most, so human attention becomes the bottleneck.

Nine: on a long or complex task, the agent always stops partway through.

That's a lot of problems. Getting an agent to work well, and keep working well, is a craft of its own. It's called harness engineering.

There's a simple formula: agent equals model plus harness. Everything outside the model is the harness.

All of this used to be you, reminding it in the prompt, but now a program does it. A program is deterministic, it doesn't spend tokens, and it doesn't depend on the model behaving itself, so jobs with a fixed answer go to programs, and anything that needs judgment goes to the agent.

// picture: Agent = Model + Harness, five things around the model

## 5 My harness

I've built my own harness framework, on top of GitHub Copilot in VS Code.

If your company uses Microsoft, you're probably using two Copilots at once: M365 Copilot and GitHub Copilot. GitHub Copilot is what we call a coding agent, and my harness helps you steer it better.

Let's go back to those problems and see how my harness handles each one.

First: the agent doesn't know your systems or your projects, so someone has to explain them every time.

I built a standard framework that turns a codebase into a knowledge base. A set of tools studies your codebase, finds the hidden dependencies between files, and writes them up as cards. When it's done, it produces a summary file and an index. So the agent doesn't have to reread the code every time: it just loads the summary and a few cards, and it gets a rough picture of your codebase. And when it needs more, the index takes it straight to the right file.

Second: how do you keep its memory from one session to the next? If a session dies, how does a new one pick up the task?

Every task is a folder. It holds everything from the task's whole life: the plan, the history log, the status, the requirement doc, the test scripts, the changed code, and anything else the agent produces along the way. So if a session dies, a new one just scans the folder and carries on right away.

Third: people only use the agent to change code, and still handle the tests, the CI-CD pipeline and the tickets themselves. And you don't dare give it access to your servers, in case it does something dangerous, like dropping a table.

Give the agent access to your dev and test environments, and it can build things, write its own test scripts, run them, and fix what fails. To keep that safe, here's what I do: with a standard tool pack, the agent gets read-only access to the lower environments. Anything that writes or executes needs a person to approve it. Take Microsoft's SQL Server: I've tested my harness against thousands of injected dangerous commands. Between a blacklist, a whitelist, a human making the call, and the account's own permissions, the agent's access stays safe.

Fourth: when it finishes a task, it's usually sure it got it right.

I bring in an independent reviewer as a subagent. It reviews everything the agent did on the task and gives a test verdict. In practice, the reviewer catches lots of cases the main agent never thought of.

Fifth: where did the time and money go, and how do you spend less? The plan, the logs, the steps it took: none of it gets recorded.

I built a report panel that shows the numbers for the whole task: where the time went, where the money went, which tool calls failed. It's all there at a glance.

There are plenty of other problems too, but there's no time to go through them all here.

## 6 Summary

So, AI hasn't gotten dumber, it's the way we use it that's still stuck in 2024. We treat it as a chatbot, and people still do the copying and pasting, watch the process, and do the checks.

With an agent, a program does the copying and pasting. With a harness, a program also handles the process, the checks and the boundaries. And people can finally step back, and just make the calls and sign off.

If you're rolling out AI on your team, don't rush to ask, "Which stronger model should we switch to?" Ask this first: "What's missing around our AI?"

If you want to try it yourself, in the next video I'll walk you through installing this harness and starting your first task.
