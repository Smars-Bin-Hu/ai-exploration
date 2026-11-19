# Basic 01 · en → en-v2 changes

Verdict: the grammar is fine, but it reads like a careful translation, not like someone talking. Chinese calques ("really land", "trail of the task", "what depends on what before and after", "pushing AI on your team"), written-style colon lists and sentences that open with "Especially" or "Because", and the same list sentences re-read word for word in scene 5. For TTS: "80 to 90", "CI/CD", "Agent = Model + Harness" and the "..." trailing-off pauses.

## 0 Hook

- It's 2026, and a lot of teams want AI to really land in how they build software. → It's 2026, and a lot of teams want AI to be a real part of how they build software.
- Plenty of companies have bought their people an AI chat service or a coding agent, like Claude Code, Codex or GitHub Copilot. → Plenty of companies already pay for an AI chat tool or a coding agent, like Claude Code, Codex or GitHub Copilot.
- But in practice, we see that many teams still only use AI for a small slice of their daily work. → But what we actually see is that many teams still use it for only a small slice of their work.
- And lots of people still use AI the same old way: ask a question, get an answer, chat. → And lots of people still use it the same old way, as a chat. Ask a question, get an answer.
- Here's an example. → Here's what I mean.
- You've built lots of features like this before, and you know exactly what the best solution is. → You've built plenty of features like this, and you know the best way to do it.
- Which code to change, how to test it, what depends on what before and after, what it might affect: you've got the experience for all of it. → Which code to change, how to test it, what depends on what, what it might break. You've seen it all.
- Now someone makes you do it with AI. → Now you're told to do it with AI.
- First you dig out the code files you think matter, one by one, and hand them to the chat box. → First, you dig out the files you think matter, one by one, and paste them into the chat.
- Then you write a long explanation: what this code does, and how it all connects. → Then you write a long explanation of what the code does and how it all fits together.
- And last, a whole screen of "do this", "add that", "whatever you do, don't touch that". → And finally, a whole screen of "do this", "add that", "whatever you do, don't touch that".
- The AI hasn't written a single line of code, and you've already been busy for half an hour. → The AI hasn't written a single line yet, and you've already spent half an hour.
- Then you hit Enter, and hope it gives you the right result. → Then you hit Enter and hope it gets it right.
- But what you usually get is an answer you're maybe 80 to 90 percent happy with. → What you usually get is an answer you're maybe eighty or ninety percent happy with.
- You paste the code it wrote back in, run the tests yourself, check the results yourself... and find some parts are still wrong. → You paste its code back in, run the tests yourself, check the results yourself, and some of it's still wrong.
- So you spend even more time reviewing the code... → So you spend even longer reviewing it.
- In the end you feel it's faster to just write it yourself. → In the end, it feels faster to just write it yourself.
- AI can't understand your complex system, and it can't see the traps you know about. → The AI doesn't get your complex system, and it can't see the traps you know are there.
- This video wants to make three things clear: what's wrong with using AI this way, why it's so hard for development teams to make AI really land, and what the missing piece is called. → In this video I want to make three things clear. What's wrong with using AI this way. Why it's so hard for development teams to really adopt AI. And what the missing piece is called.

## 1 Your pain points

- If you've used AI like this, you've probably run into every one of these. → If you've used AI like this, you've probably hit every one of these.
- Two: it loses its memory. → Two: it forgets.
- You have to say it all again from the start. → You have to say it all again.
- And you'll notice that the longer one chat goes on, the worse it seems to do. → And the longer a chat goes on, the worse it seems to get.
- Things you agreed on early, it forgets later. → It forgets things you agreed on at the start.
- Three: you tell it lots of things to do and not to do, and it doesn't always do them. → Three: you give it a list of dos and don'ts, and it doesn't always follow them.
- Especially as the chat gets longer and the history piles up, the AI's attention drifts, and it remembers the older stuff less and less. → And the longer the chat gets, the more its attention drifts, and the less it remembers from earlier.
- Four: it's always confident when it checks itself. → Four: it's always sure of its own work.
- "It's done, and all the tests pass." → "Done, and all the tests pass."
- Then you get it back, take a look, and there's still a pile of mistakes. → Then you look for yourself, and there's still a pile of mistakes.
- Which files it changed, which commands it ran, why it changed things that way. → Which files did it change? Which commands did it run? Why did it do it that way?
- Afterwards, it's hard to say. → After the fact, it's hard to tell.

## 2 The root cause

- Actually, this is how people used AI in 2024: as a chatbot. → Well, that's how people used AI in 2024. As a chatbot.
- In 2024, most people were still working out how to write a good prompt so the AI would do better, and people called it Prompt Engineering. → Back then, most people were busy learning to write better prompts to get better answers. That was called prompt engineering.
- Even if the AI model is smart enough, you're still treating it as someone who answers questions. → Even if the model is smart enough, you're still treating it like someone who just answers questions.
- Apart from answering your questions, every other job still lands on you: finding the code, sorting out the requirement, running the tests, remembering the context, watching it follow the process, checking its results. → It answers your questions, and everything else is still on you. Finding the code, sorting out the requirement, running the tests, remembering the context, making sure it follows the process, checking its results.
- And in the end, it's easy to hear the same old line: AI isn't reliable, AI makes mistakes, AI can only help with part of my work... → And in the end, you hear the same old lines. AI isn't reliable. AI makes mistakes. AI can only help with part of my work.

## 3 What is an agent

- So here, I have to explain what an AI agent is. → So let me explain what an AI agent is.
- When you chat with AI day to day, you're really talking straight to the large language model, the LLM. → When you chat with AI, you're talking straight to the large language model, the LLM.
- It thinks, then writes you a piece of text as an answer. → It thinks, then writes you an answer in text.
- An agent is an LLM with tool calling added: the ability to use tools. → An agent is an LLM plus tool calling, meaning it can use tools.
- Once it's thought things through, it can go and change the code files on your machine by itself, run commands, search the web, open a browser. → Once it's thought things through, it can go and change the code on your machine itself, run commands, search the web, open a browser.
- It calls a tool, takes a look at the result, then decides what to do next. → It calls a tool, looks at the result, and decides what to do next.
- Then it calls again, looks again, and keeps going until the job is done. → Then it calls again, looks again, and keeps going until the job's done.
- With hands, and a loop of its own, an agent is born. → Give an LLM hands and a loop of its own, and you've got an agent.
- It can get a piece of work done by itself. → It can finish a piece of work on its own.

## 4 What is a harness

- Once an agent can do work on its own, new problems come with it. → But once an agent can work on its own, you get a new set of problems.
- In 2025, people found you need good context engineering, managing the AI's context, before it performs consistently. → In 2025, people found that to get steady results, you have to manage the AI's context well. That's context engineering.
- By 2026, coding agents can really get work done for you, like Claude Code, Codex and GitHub Copilot. → And by 2026, coding agents like Claude Code, Codex and GitHub Copilot can really get work done for you.
- And being able to do work also brings new problems. → And that's where the new problems start.
- Companies found that to make agents really land, they have to solve these problems. → Companies found that to really adopt agents, they have to solve these.
- One: it doesn't know your systems and projects, so a person still has to introduce them every time. → One: it doesn't know your systems or your projects, so someone still has to explain them every time.
- Two: how do you keep memory across sessions? → Two: how do you keep its memory from one session to the next?
- If one session dies, how does another session pick up the task? → If a session dies, how does a new one pick up the task?
- Running the tests, the CI/CD pipeline, updating the tickets: people still do all of that. → Running tests, the CI-CD pipeline, updating tickets, people still do all of that.
- Four: rules you agreed on, it doesn't always follow. → Four: it doesn't always follow the rules you agreed on.
- Five: you don't dare open up your servers to it, because it might do something dangerous, like dropping a table. → Five: you don't dare give it access to your servers, in case it does something dangerous, like dropping a table.
- Six: when it finishes a task, it tends to confidently believe its result is right. → Six: when it finishes a task, it's usually sure it got it right.
- Seven: where did the money and the time go, and how do you cut them down? → Seven: where did the time and money go, and how do you spend less?
- The plan, the logs, the trail of the task: none of it is recorded. → The plan, the logs, the steps it took. None of it gets recorded.
- Eight: a person can keep an eye on five sessions at most, so human attention becomes the bottleneck for the agent's work. → Eight: one person can keep an eye on five sessions at most, so human attention becomes the bottleneck.
- Nine: on a long or complex task, the agent always ends up stopping partway. → Nine: on a long or complex task, the agent always stops partway through.
- There are just so many problems. → That's a lot of problems.
- Getting an agent to work steadily and well is a craft of its own, and it's called harness engineering. → Getting an agent to work well, and keep working well, is a craft of its own. It's called harness engineering.
- There's a formula: Agent = Model + Harness. → There's a simple formula: agent equals model plus harness.
- Because a program is deterministic: it doesn't spend tokens, and it doesn't rely on the model behaving itself. → A program is deterministic. It doesn't spend tokens, and it doesn't depend on the model behaving itself.
- We hand the deterministic jobs to programs, and the things that need judgment and thinking to the agent. → So jobs with a fixed answer go to programs, and anything that needs judgment goes to the agent.

## 5 My harness

- I've built a harness framework myself, based on GitHub Copilot in VS Code. → I've built my own harness framework, on top of GitHub Copilot in VS Code.
- If your team is a Microsoft customer, you're most likely using two Copilots at the same time: M365 Copilot and GitHub Copilot. → If your company uses Microsoft, you're probably using two Copilots at once: M365 Copilot and GitHub Copilot.
- My harness is there to help you steer GitHub Copilot better. → My harness helps you steer it better.
- Let's go back to those gaps, and see what each one looks like in my harness. → Let's go back to those problems and see how my harness handles each one.
- First: it doesn't know your systems and projects, so a person still has to introduce them every time. → First: it doesn't know your systems or your projects, so someone has to explain them every time.
- When the learning is done, it produces a summary file and an index. → When it's done, it produces a summary file and an index.
- The agent doesn't have to read the code again every time. → So the agent doesn't have to reread the code every time.
- It only loads the summary file and a few cards, and it has a rough idea of your codebase. → It just loads the summary and a few cards, and it gets a rough picture of your codebase.
- And if it needs to, it can go straight to the right file through the index. → And when it needs more, the index takes it straight to the right file.
- Second: how do you keep memory across sessions? If one session dies, how does another session pick up the task? → Second: how do you keep its memory from one session to the next? If a session dies, how does a new one pick up the task?
- It holds the files for the task's whole life: the task plan, the history log, the status, the requirement document, the test scripts, the changed code, and anything else the agent produces while it works. → It holds everything from the task's whole life. The plan, the history log, the status, the requirement doc, the test scripts, the changed code, and anything else the agent produces along the way.
- It's all saved in there. → (cut, repeats the line before)
- So even if one session dies, another session only has to scan this task folder, and it can carry on right away. → So if a session dies, a new one just scans the folder and carries on right away.
- Third: people only use the agent to change code, and running the tests, the CI/CD pipeline and updating the tickets are still done by people. → Third: people only use the agent to change code, and still handle the tests, the CI-CD pipeline and the tickets themselves.
- And you don't dare open up your servers to it, because it might do something dangerous, like dropping a table. → And you don't dare give it access to your servers, in case it does something dangerous, like dropping a table.
- Give the agent access to the development and test environments, and it can build things itself, write its own test scripts, run them itself, and fix them itself. → Give the agent access to your dev and test environments, and it can build things, write its own test scripts, run them, and fix what fails.
- For safety, here's what I do. → To keep that safe, here's what I do.
- Through a standard tool pack, the agent gets read-only access to the lower environments. → With a standard tool pack, the agent gets read-only access to the lower environments.
- Write and execute access has to be approved by a person. → Anything that writes or executes needs a person to approve it.
- Take Microsoft's SQL Server: I've run my harness against thousands of cases of dangerous commands being injected. → Take Microsoft's SQL Server. I've tested my harness against thousands of injected dangerous commands.
- With a blacklist, a whitelist, a person making the call, and the account's own permissions, the agent's access stays safe. → Between a blacklist, a whitelist, a human making the call, and the account's own permissions, the agent's access stays safe.
- Fourth: when it finishes a task, it tends to confidently believe its result is right. → Fourth: when it finishes a task, it's usually sure it got it right.
- The subagent reviews everything the agent did on the task, and gives a test verdict. → It reviews everything the agent did on the task and gives a test verdict.
- In practice, the reviewer finds lots of cases the main agent never thought of. → In practice, the reviewer catches lots of cases the main agent never thought of.
- Fifth: where did the money and the time go, and how do you cut them down? The plan, the logs, the trail of the task: none of it is recorded. → Fifth: where did the time and money go, and how do you spend less? The plan, the logs, the steps it took. None of it gets recorded.
- I built a task report panel just for the whole task's numbers: where the time went, where the money went, which tool calls failed. → I built a report panel that shows the numbers for the whole task. Where the time went, where the money went, which tool calls failed.
- Every conclusion, clear at a glance. → It's all there at a glance.
- And there's a lot more, but there isn't time to go through it all here. → There's a lot more, but no time to cover it all here.

## 6 Summary

- It's that the way we use it is still stuck in 2024: treating it as a chatbot, with people doing the copying and pasting, watching the process, and doing the checks. → The way we use it is just stuck in 2024. We treat it as a chatbot, and people still do the copying and pasting, watch the process, and do the checks.
- Agents hand the copying and pasting to a program. → With an agent, a program does the copying and pasting.
- A harness hands the process, the checks and the boundaries to a program too. → With a harness, a program also handles the process, the checks and the boundaries.
- People can finally step back, and just make the calls and sign off. → And people can finally step back, make the calls, and sign off.
- If you're pushing AI on your team, don't rush to ask "which stronger model should we switch to?" → If you're rolling out AI on your team, don't rush to ask, "Which stronger model should we switch to?"
- First, ask one question: "What's missing around our AI?" → Ask this first: "What's missing around our AI?"
- If you want to try it yourself, in the next video I'll help you install this harness and start your first task. → If you want to try it yourself, in the next video I'll walk you through installing this harness and starting your first task.
