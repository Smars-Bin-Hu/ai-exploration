# Basic 01 · English plain translation

## 0 Hook

In 2026, many teams want AI to take hold in their development work, and many companies have subscribed their employees to AI chat services or coding agents, such as Claude Code, Codex, or GitHub Copilot. However, in practice, we have found that many teams still use AI for only a very small part of their daily work, and many people even still use AI as question-and-answer chat.

// picture: Claude Code, Codex, and GitHub Copilot must appear

For example, say you are a software engineer, and you have a very large legacy system in your hands. You get a requirement from the business side, and you have already built many similar features before. You know clearly what the best solution is: for example, which code you need to change, how to test it, the dependencies before and after the code, and the impact area; you have experience with all of it. Now you are forced to use AI to do it. What would you do?

It goes roughly like this: first, you find the code files you think are relevant, one by one, and pass them to the chat box; then you write a long explanation telling it what this code does and how it fits together; then you paste in the requirement; finally, you write a full screen of "do this", "add that", "never touch that".

The AI has not written a single line of code yet, and you have already been busy for half an hour. Then you press Enter and hope it gives you a correct result.
But the result is often this: the AI most likely gives you an answer you are 80% to 90% satisfied with. You paste the code it wrote back in, run the tests yourself, check the results yourself... and find that some parts are still wrong, so you spend even more time reviewing the code... In the end you feel that using AI is slower than writing it yourself, because AI cannot understand your complex system and cannot see your pitfalls.

// picture: a long prompt, the AI's answer, you breaking down

This video wants to make three things clear: where this way of using AI goes wrong, why it is hard for development teams to put AI into real use, and what the missing piece is called.

## 1 Your pain points

If you have used AI this way, you have probably run into all of the following things.

First, it does not know your project. Every time, you have to find the code, paste the code, and explain the code.

Second, it loses its memory. When you open a new chat, everything you said before is gone, and you have to say it all again from the start. Also, you will find that the longer you chat in the same conversation, the worse it seems to perform; things you agreed on earlier, it forgets later.

Third, you tell it many things to do and not to do, but it does not always follow them. Most of the time it listens, but there are always a few times when it skips exactly the step you care about most. This is especially true the longer the chat goes on: the more history there is, the more the AI's attention drifts, and the less it remembers the older content.

Fourth, it is always very confident when it checks itself. "It's done, and all tests pass." When you get it and look, there are still lots of errors.

Fifth, you cannot see what it actually did. Which files it changed, which commands it ran, and why it made those changes are hard to explain afterwards.

// picture: one image per pain point

## 2 Root cause

Is this how you use AI now?

In fact, this is how people used AI in 2024: treating it as a chatbot.

In 2024, most people were still studying how to write a good prompt so that the AI would perform better, and so people called this Prompt Engineering. But the problem is that even if the AI model is smart enough, you are still treating the AI as someone who answers questions; you have not let it actually do the work. Apart from answering your questions, all the other tasks are still on you: finding the code, organizing the requirement, running tests, remembering the context, watching it to make sure it follows the process, and checking its results are all done by hand, by you.

In the end, it is easy to hear a common view: AI is not reliable, AI makes mistakes, AI can only help with part of my work...

## 3 What is an agent

Here, we have to explain what an AI agent is.

When you usually chat with AI, you are actually talking directly to the large model, that is, the LLM: it thinks, and then writes a piece of text to answer you. An agent adds tool calling to the LLM, that is, the ability to call tools. You can think of tools as its hands: once it has thought things through, it can change the code files on your local machine by itself, run commands, search the web, and open a browser. But having hands is not enough. The key is that it loops: it calls a tool, looks at the result, and then decides what to do next; then it calls again, looks again, and keeps going until the job is done.

With hands, and the ability to loop on its own, an agent is born. It no longer just answers you; it can finish a task by itself.

// picture: LLM → tool → result → next step, in a circle

## 4 What is a harness

Now that agents can do work by themselves, new problems come with them.

Look back over the past few years: in 2024, people studied how to write prompts well; in 2025, people found that they needed to do context engineering well, managing the AI's context, so that it could perform consistently; by 2026, coding agents, such as Claude Code, Codex, and GitHub Copilot, can really do work for you. Being able to do work also means bringing new problems.

Companies found that putting agents into real use requires solving these problems:

- It does not know your systems and projects, so a person still has to introduce them every time;
- How is memory kept across sessions? When one session breaks, how does another session continue the task?
- People only use the agent to change code; the rest, such as running tests, the CI/CD pipeline, and updating tickets, is still done by people;
- It does not always follow the rules you agreed on;
- People do not dare to open servers to it, because it might do something dangerous (such as dropping a table);
- When it finishes a task, it tends to confidently believe its result is correct;
- Where did the money and time go, and how can they be optimized; the plan, logs, and traces of the task process are not recorded at all;
- A person's attention can manage at most 5 sessions, so human attention becomes the bottleneck for the agent's work;
- On a long or complex task, the agent always ends up stopping;

There are far too many problems. How to make an agent work both steadily and well: this skill is called harness engineering.

There is a formula: Agent = Model + Harness. Everything outside the model is the harness.

In the past, all of these things depended on you reminding it in the prompt; now they are handed over to programs. Because programs are deterministic, cost no tokens, and do not depend on the model's own discipline, we hand deterministic tasks to programs, and we give the things that need judgment and thinking to the agent.

// picture: Agent = Model + Harness, five things around the model

## 5 My harness

I have developed a harness framework myself, and it is based on GitHub Copilot in VS Code.

If your team is a Microsoft customer, you are most likely using two Copilots at the same time: M365 Copilot and GitHub Copilot. Of these, GitHub Copilot is what we call a coding agent, and my harness helps you drive GitHub Copilot better.

Let's go back to those gaps and see what each of them looks like in my harness.

- It does not know your systems and projects, so a person still has to introduce them every time;

I built a standard framework that turns a codebase into a knowledge base. It uses a set of tools to learn your codebase, find hidden dependencies between files, and turn them into cards; when the learning is finished, it generates a summary file and an index. The agent does not need to re-read the code each time; it only needs to load the summary file and some of the cards to get a rough understanding of your codebase, and if needed, it can find the relevant files directly through the index.

- How is memory kept across sessions? When one session breaks, how does another session continue the task?

Each task is a folder that holds the files for the task's whole life cycle: the task plan, history logs, status, requirement documents, test scripts, the changed code, and any results the agent produces while working are all saved in it. This way, even if one session dies, another session only needs to scan this task folder to continue right away.

- People only use the agent to change code; the rest, such as running tests, the CI/CD pipeline, and updating tickets, is still done by people; people do not dare to open servers to it, because it might do something dangerous (such as dropping a table);

Give the agent access to the development and test environments, so the agent can develop on its own, write test scripts on its own, run them on its own, and fix things on its own. For safety, this is how I did it: through a standard Toolpack, the agent is given read-only access to the lower environments, and write and execute permissions must be approved by a person. For example, for Microsoft's SQL Server, my harness has been run against thousands of dangerous-command injection cases, and through a blacklist, a whitelist, decisions made by a person, and the account's own permissions, it keeps the agent's access safe.

- When it finishes a task, it tends to confidently believe its result is correct;

I bring in an independent reviewer as a subagent, and the subagent reviews all of the agent's work and gives a test verdict. In practice, the reviewer finds many cases that the main agent did not consider.

- Where did the money and time go, and how can they be optimized; the plan, logs, and traces of the task process are not recorded at all;

I built a task report dashboard just for looking at the statistics of a whole task: where the time went, where the money went, and which tool calls failed. All the conclusions are clear at a glance.

- There are many others as well; because of time, I will not list them one by one here.

## 6 Summary

So, AI has not become dumber; it is that our way of using it is still stuck in 2024: treating it as a chatbot, with people carrying things back and forth, watching the process, and doing the checks.

The agent hands the carrying over to programs, and the harness hands the process, the checks, and the boundaries over to programs as well. People can finally step back and only make judgments and act as gatekeepers.

If you are pushing AI in your team, don't rush to ask "which stronger model should we switch to?"; first ask: "What is missing around our AI?"

If you want to try it yourself, in the next video I will help you install this harness and start your first task.
