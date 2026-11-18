# en-v3: changes from en.md

30 rejoins: sentences that are one thought become one sentence again. Nothing else changes, except one word (marked ★). Each line is `old → new`.

## 0 Hook

- as a chat. Ask a question, get an answer. → as a chat: ask a question, get an answer.
- Here's what I mean. Say you're a software engineer, … → Here's what I mean: say you're a software engineer, …
- you know the best way to do it. Which code to change, how to test it, what depends on what, what it might break. → you know the best way to do it: which code to change, how to test it, what depends on what, what it might break.
- Probably something like this. First, you dig out the files … → Probably something like this: first, you dig out the files …
- and some of it's still wrong. So you spend even longer reviewing it. → and some of it's still wrong, so you spend even longer reviewing it.
- I want to make three things clear. What's wrong with using AI this way. Why it's so hard for development teams to really adopt AI. And what the missing piece is called. → I want to make three things clear: what's wrong with using AI this way, why it's so hard for development teams to really adopt AI, and what the missing piece is called.

## 1 Your pain points

- everything you said before is gone. You have to say it all again. → everything you said before is gone, so you have to say it all again.
- the worse it seems to get. It forgets things you agreed on at the start. → the worse it seems to get: it forgets things you agreed on at the start.
- Most of the time it listens. But every so often, it skips exactly the step you cared about most. → Most of the time it listens, but every so often it skips exactly the step you care about most. (★ cared → care, to match "listens", "skips")
- Which files did it change? Which commands did it run? Why did it do it that way? → Which files did it change, which commands did it run, why did it do it that way?

## 2 The root cause

- that's how people used AI in 2024. As a chatbot. → that's how people used AI in 2024: as a chatbot.
- But here's the problem. Even if the model is smart enough, … → But here's the problem: even if the model is smart enough, …
- everything else is still on you. Finding the code, … checking its results. → everything else is still on you: finding the code, … checking its results.
- you hear the same old lines. AI isn't reliable. AI makes mistakes. AI can only help with part of my work. → you hear the same old lines: AI isn't reliable, AI makes mistakes, AI can only help with part of my work.

## 3 What is an agent

- the large language model, the LLM. It thinks, then writes you an answer in text. → the large language model, the LLM: it thinks, then writes you an answer in text.
- Think of tools as its hands. Once it's thought things through, … → Think of tools as its hands: once it's thought things through, …
- But hands alone aren't enough. The key is that it loops. → But hands alone aren't enough; the key is that it loops.
- It doesn't just answer you anymore. It can finish a piece of work on its own. → It doesn't just answer you anymore; it can finish a piece of work on its own.

## 4 What is a harness

- Look back over the last few years. In 2024, people were figuring out … → Look back over the last few years: in 2024, people were figuring out …
- Seven: … The plan, the logs, the steps it took. None of it gets recorded. → The plan, the logs, the steps it took: none of it gets recorded.
- reminding it in the prompt. Now a program does it. → reminding it in the prompt, but now a program does it.
- A program is deterministic. It doesn't spend tokens, and it doesn't depend on the model behaving itself. → A program is deterministic, it doesn't spend tokens, and it doesn't depend on the model behaving itself.

## 5 My harness

- GitHub Copilot is what we call a coding agent. My harness helps you steer it better. → GitHub Copilot is what we call a coding agent, and my harness helps you steer it better.
- the agent doesn't have to reread the code every time. It just loads the summary … → the agent doesn't have to reread the code every time: it just loads the summary …
- everything from the task's whole life. The plan, the history log, … → everything from the task's whole life: the plan, the history log, …
- To keep that safe, here's what I do. With a standard tool pack, … → To keep that safe, here's what I do: with a standard tool pack, …
- Take Microsoft's SQL Server. I've tested my harness … → Take Microsoft's SQL Server: I've tested my harness …
- Fifth: … The plan, the logs, the steps it took. None of it gets recorded. → The plan, the logs, the steps it took: none of it gets recorded.
- the numbers for the whole task. Where the time went, where the money went, which tool calls failed. → the numbers for the whole task: where the time went, where the money went, which tool calls failed.

## 6 Summary

- So, AI hasn't gotten dumber. The way we use it is just stuck in 2024. → So, AI hasn't gotten dumber; the way we use it is just stuck in 2024.

## Left as they were, on purpose

- Naming lines stay their own sentence: "That was called prompt engineering." "That's context engineering." "It's called harness engineering."
- Questions: every question was already a real question with "?". The only change is the three in pain point Five, now one question.

## Paragraph breaks (a pause, and where the picture may rest)

Same as zh.md, one blank line in scenes-v3.md at each.

- **0 Hook** (6): It's 2026 · Here's what I mean · Probably something like this · The AI hasn't written · What you usually get · In this video
- **1 Your pain points** (6): If you've used AI · One · Two · Three · Four · Five
- **2 The root cause** (4): Is this how · Well, that's how · Back then · And in the end
- **3 What is an agent** (3): So let me explain · When you chat with AI · Give an LLM hands
- **4 What is a harness** (15): But once an agent · Look back · Companies found · One · Two · Three · Four · Five · Six · Seven · Eight · Nine · That's a lot of problems · There's a simple formula · All of this used to be you
- **5 My harness** (14): I've built my own · If your company · Let's go back · First · I built a standard framework · Second · Every task is a folder · Third · Give the agent access · Fourth · I bring in · Fifth · I built a report panel · There's a lot more
- **6 Summary** (4): So, AI hasn't gotten dumber · With an agent · If you're rolling out · If you want to try

To check: "The AI hasn't written" and "What you usually get" are one paragraph in zh.md with a line break between them (no blank line). I kept them as two paragraphs, as en.md has them, because the picture changes there and a pause before the result lands. Join them if you want them as one.
