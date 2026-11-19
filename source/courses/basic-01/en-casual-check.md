# Basic 01 · casual script check (en-casual.md → en-casual-v2.md)

18 changes, all small; the casual tone, the scenes and the paragraphs are kept, and nothing is added. Main fixes: "many" had become "most", the stiff words (deterministic, lower environments, injection cases) are now common words, and a few vague "it / them / that" now name what they point to.

- 0 Hook · 很多团队依然只是用AI完成…很小的一部分工作 · meaning · "most teams still use AI for just a tiny slice of their day" → "a lot of teams still only use AI for a tiny slice of their work"
- 0 Hook · 甚至很多人使用AI的方式依旧是一问一答的聊天 · logic · "And a lot of people are still using it like a Q&A chat." → "And plenty of people are even still using it like a Q&A chat."
- 0 Hook · 代码前后的依赖，影响面 · meaning · "what it depends on before and after, what it might affect" → "what it depends on and what depends on it, and what else it could break"
- 1 Your pain points · 下面这几件事你应该都碰到过 · signpost · "you've probably hit every one of these." → "you've probably hit every one of the things I'm about to list."
- 2 Root cause · 于是大家叫这个所谓 Prompt Engineering · logic · "That's why people called it Prompt Engineering." → "So that's what people called Prompt Engineering."
- 3 What is an agent · no change
- 4 What is a harness · 一个长任务、复杂任务，agent 总是会停下来 · meaning · "the agent always ends up stopping." → "the agent always stops partway through."
- 4 What is a harness · 怎么让 agent 干得又稳又好，这门功夫，就叫 harness engineering · referent · "So how do you get an agent to work both steadily and well? That skill is called harness engineering." → "And the skill of getting an agent to work both steadily and well, that's called harness engineering."
- 4 What is a harness · 因为程序是确定性的 · word · "Because programs are deterministic, they don't cost tokens, and they don't depend on…" → "Because a program does the same thing every time, it doesn't cost tokens, and it doesn't depend on…"
- 4 What is a harness · 我们把确定性的任务交给程序 · word · "So the deterministic stuff goes to programs" → "So the fixed, predictable stuff goes to programs"
- 5 My harness · 还是对着那些缺口 · referent · "So let's go back to those gaps and see" → "So let's go back to the gaps on that list and see"
- 5 My harness · 找到文件之间潜在的依赖关系，形成卡片 · referent · "find the hidden dependencies between files, and turn them into cards." → "find the hidden dependencies between files, and write what it finds into cards."
- 5 My harness · 给Agent访问开发环境和测试环境的权限 · referent · "Give the agent access to the dev and test environments," → "So I give the agent access to the dev and test environments,"
- 5 My harness · 访问 lower enviornment 的只读权限 · word · "read-only access to the lower environments" → "read-only access to the non-prod environments"
- 5 My harness · 我的harness前后跑了几千种危险命令的注入情况 · word · "my harness has been run against thousands of dangerous-command injection cases." → "I've tested my harness against thousands of attempts to sneak in dangerous commands."
- 5 My harness · 通过黑名单、白名单和给人决策…保证了Agent的安全访问 · referent · "And with a blacklist, … permissions, it keeps the agent's access safe." → "And between a blacklist, … permissions, the agent's access stays safe."
- 5 My harness · 让subagent来review agent的全部任务 · referent · "The subagent reviews all of the agent's work" → "The subagent reviews everything the main agent did"
- 5 My harness · 还有很多别的，在这里由于时间问题，就不再一一列举 · signpost · "There are a bunch of others too, but for time, I won't go through them all here." → "And there's a lot more, but to save time, I won't list it all here."
- 5 My harness · (kept) each gap line repeats module 4 word for word; kept, because the listener hears the same line and knows which problem is being answered
- 6 Summary · 如果你在团队里推 AI · word · "If you're pushing AI on your team," → "If you're trying to get your team using AI," ("pushing on" sounds like forcing it on people)
