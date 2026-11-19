# Basic 01 · English casual script

## 0 Hook

You know, it's 2026, and a lot of teams want AI to really stick in their dev work. Lots of companies have already paid for AI chat or coding agents for their people, like Claude Code, Codex, or GitHub Copilot. But here's the thing: what we keep seeing is, most teams still use AI for just a tiny slice of their day. And a lot of people are still using it like a Q&A chat.

// picture: Claude Code, Codex, and GitHub Copilot must appear

So, say you're a software engineer, and you've got this huge legacy system on your hands. A request comes in from the business side, and you've built a bunch of features like it before. You know exactly what the best fix is: which code to change, how to test it, what it depends on before and after, what it might affect. You've done all of it before. Now you're told you have to use AI for it. What do you do?

Pretty much this: first, you dig up the code files you think matter, one by one, and drop them into the chat box. Then you write this long explanation of what the code does and how it all fits together. Then you paste in the request. And finally, you write a whole screen of "do this", "add that", "never touch that".

The AI hasn't written a single line of code yet, and you've already spent half an hour. Then you hit Enter and hope it gets it right.
But what usually happens? The AI gives you something you're, like, 80 to 90% happy with. You paste its code back in, run the tests yourself, check the results yourself... and some of it's still wrong. So now you're spending even more time reviewing the code... And in the end you're thinking, using AI is slower than just writing it myself. Because it can't understand your complex system, and it can't see the traps you already know about.

// picture: a long prompt, the AI's answer, you breaking down

So in this video I want to make three things clear: where this way of using AI goes wrong, why it's so hard for dev teams to really put AI to work, and what the missing piece is called.

## 1 Your pain points

If you've used AI like this, you've probably hit every one of these.

One: it doesn't know your project. Every single time, you have to find the code, paste the code, explain the code.

Two: it forgets. Open a new chat, and everything you told it is gone. You have to say it all again from scratch. And you'll notice, the longer you chat in the same conversation, the worse it seems to get. Stuff you agreed on earlier, it forgets later.

Three: you give it a bunch of dos and don'ts, but it doesn't always follow them. Most of the time it listens, but every now and then it skips exactly the step you care about most. And it gets worse the longer the chat goes: the more history there is, the more its attention drifts, and the less it remembers the older stuff.

Four: it's always super confident when it checks its own work. "Done, all tests pass." Then you look, and there are still tons of errors.

Five: you can't see what it actually did. Which files it changed, which commands it ran, why it made those changes... it's hard to explain any of that afterwards.

// picture: one image per pain point

## 2 Root cause

So, is this how you use AI right now?

Well, this is how people used AI back in 2024: treating it like a chatbot.

In 2024, most people were still figuring out how to write a good prompt so the AI would do better. That's why people called it Prompt Engineering. But the problem is, even if the model is smart enough, you're still treating it as someone who just answers questions. You haven't let it actually do the work. Apart from answering you, everything else is still on you: finding the code, sorting out the request, running the tests, remembering the context, watching it to make sure it sticks to the process, checking its results. All of that, you do by hand.

And so in the end, you hear the same thing everywhere: AI isn't reliable, AI makes mistakes, AI can only help with part of my work...

## 3 What is an agent

So here we've got to explain what an AI agent is.

When you normally chat with AI, you're really talking straight to the large model, the LLM. It thinks, then writes some text back to answer you. An agent adds tool calling on top of the LLM, basically, the ability to use tools. Think of tools as its hands: once it's thought things through, it can change code files on your machine by itself, run commands, search the web, open a browser. But having hands isn't enough. Here's the key: it loops. It calls a tool, looks at the result, then decides what to do next. Then it calls again, looks again, and keeps going until the job's done.

Hands, plus the ability to loop on its own, and that's when you get an agent. It doesn't just answer you anymore. It can finish a task by itself.

// picture: LLM → tool → result → next step, in a circle

## 4 What is a harness

OK, so now agents can do work on their own. But that brings new problems.

Look back at the last few years. In 2024, people were working on how to write good prompts. In 2025, people figured out they needed to get context engineering right, you know, managing what's in the AI's context, so it'd perform consistently. And by 2026, coding agents like Claude Code, Codex, and GitHub Copilot can really do work for you. And being able to do work brings new problems too.

Companies found that to really put agents to work, they have to solve these problems:

- It doesn't know your systems and projects, so someone still has to walk it through them every time.
- How do you keep memory across sessions? If one session breaks, how does another one pick up the task?
- People only use the agent to change code. Everything else, like running tests, the CI/CD pipeline, updating tickets, people still do themselves.
- It doesn't always follow the rules you agreed on.
- People don't dare give it access to servers, because it might do something dangerous, like dropping a table.
- When it finishes a task, it tends to be totally sure its result is right.
- Where did the money and time go, and how do you cut them down? The plan, the logs, the traces of how the task went... none of it gets recorded.
- One person can keep an eye on five sessions, tops. So human attention becomes the bottleneck for the agent's work.
- On a long or complex task, the agent always ends up stopping.

That's way too many problems. So how do you get an agent to work both steadily and well? That skill is called harness engineering.

There's a formula: Agent = Model + Harness. Everything outside the model is the harness.

Before, all of this depended on you reminding it in the prompt. Now it's handed over to programs. Because programs are deterministic, they don't cost tokens, and they don't depend on the model behaving itself. So the deterministic stuff goes to programs, and the stuff that needs judgment and thinking goes to the agent.

// picture: Agent = Model + Harness, five things around the model

## 5 My harness

So I built a harness framework myself, and it runs on GitHub Copilot in VS Code.

If your team's a Microsoft customer, you're most likely using two Copilots at once: M365 Copilot and GitHub Copilot. GitHub Copilot is the one we call a coding agent, and my harness helps you drive GitHub Copilot better.

So let's go back to those gaps and see what each one looks like in my harness.

- It doesn't know your systems and projects, so someone still has to walk it through them every time.

I built a standard framework that turns a codebase into a knowledge base. It uses a set of tools to learn your codebase, find the hidden dependencies between files, and turn them into cards. Once it's done learning, it generates a summary file and an index, kind of like a table of contents. So the agent doesn't have to re-read the code every time. It just loads the summary file and a few of the cards, and it gets a rough picture of your codebase. And if it needs to, it can jump straight to the right files through the index.

- How do you keep memory across sessions? If one session breaks, how does another one pick up the task?

Each task is a folder. It holds the files for the task's whole life: the task plan, history logs, status, requirement docs, test scripts, the changed code, and anything the agent produces while it works. It all gets saved in there. So even if one session dies, another session just scans that task folder and picks right up.

- People only use the agent to change code. Everything else, like running tests, the CI/CD pipeline, updating tickets, people still do themselves. And people don't dare give it access to servers, because it might do something dangerous, like dropping a table.

Give the agent access to the dev and test environments, so it can develop on its own, write test scripts on its own, run them on its own, and fix things on its own. For safety, here's how I did it: through a standard Toolpack, the agent gets read-only access to the lower environments, and anything that writes or executes needs a person to approve it. For example, with Microsoft's SQL Server, my harness has been run against thousands of dangerous-command injection cases. And with a blacklist, a whitelist, a person making the call, and the account's own permissions, it keeps the agent's access safe.

- When it finishes a task, it tends to be totally sure its result is right.

I bring in an independent reviewer as a subagent. The subagent reviews all of the agent's work and gives a test verdict. And in practice, the reviewer catches a lot of cases the main agent didn't think of.

- Where did the money and time go, and how do you cut them down? The plan, the logs, the traces of how the task went... none of it gets recorded.

I built a task report dashboard just for looking at the stats of a whole task: where the time went, where the money went, which tool calls failed. All the conclusions, right there at a glance.

- There are a bunch of others too, but for time, I won't go through them all here.

## 6 Summary

So, AI hasn't gotten dumber. It's that the way we use it is still stuck in 2024: treating it like a chatbot, with people doing all the legwork in between, watching the process, and doing the checks.

The agent hands that legwork over to programs, and the harness hands the process, the checks, and the boundaries over to programs too. So people can finally step back, and just make the calls and be the gatekeepers.

If you're pushing AI on your team, don't rush to ask "which stronger model should we switch to?" First ask: "What's missing around our AI?"

And if you want to try it yourself, in the next video I'll help you install this harness and kick off your first task.
