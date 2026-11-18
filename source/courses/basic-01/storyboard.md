# Basic 01 · Stop using AI the 2024 way · 分镜（待批）

// 这是给作者批的分镜，不是 scenes.md。批过以后，把每张表的「画面」和「英文句子」按顺序抄成 scenes.md：`@` 行在前，句子在后，`↑` 不写。
// 表格里的 `\|` 只是 Markdown 表格的转义，抄进 scenes.md 时写成 `|`。

## 总数

| 项 | 数 |
| --- | --- |
| 口播句（一口气一行） | 175 行，1786 词，约 12 分钟（按 150 词/分钟） |
| 画面变化（不是 `↑` 的行） | 161 次，平均约 4.5 秒换一次；同一画面最多停 3 行 |
| 要新画的图（`@ fig`） | 21 张，共 103 个步骤；上屏 103 次，其中 4 次是复用前面画过的步骤 |
| 用到的截图 | 17 处，15 张不同的截图（全是 `board/...` 和 `tutorials/...`，id 都在 catalog.md 里；不用旧文章的幻灯片） |
| 用到的模板 | 41 处：list 12、timeline 7、card 6、logos 6、loop 4、big 3、formula 2、quote 1 |

几条约定：

- 图都放在 `source/courses/basic-01/figs/<name>.html`，照 `source/video/samples-figs/process.html` 的写法：深灰底、Source Serif 4、青色 `--teal` 是「现在说到的」，橙色 `--orange` 是「出问题、要人管的」，灰色是「说过了」。
- 「你」在所有图里是同一个人形图标（Lucide `user`），AI 聊天是同一个气泡（`message-square`），agent 是同一个机器人（`bot`），这样观众一眼认得出谁是谁。
- 有些长句在逗号处切成两三行，好让每一截配上自己的画面；拼起来和 en.md 一字不差（已用脚本对过）。

---

## 0 Hook（31 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 1 | It's 2026, and a lot of teams want AI to be a real part of how they build software. | `@ card "Stop using AI the 2024 way" kicker="Basic 01"` | 开场 → 片名卡。 |
| 2 | Plenty of companies already pay for an AI chat tool or a coding agent, | `@ logos "claude\|Claude" "codex\|ChatGPT" m365-copilot` | 「AI 聊天工具」→ 三个聊天产品的官方标志。 |
| 3 | like Claude Code, Codex or GitHub Copilot. | `@ logos claude-code codex github-copilot` | 点名三个 coding agent → 正好这三个标志（中文稿要求它们出现）。 |
| 4 | But what we actually see is that many teams still use it for only a small slice of their work. | `@ fig small-slice step=1` | 只用了一小块 → 一条长长的开发工作条，只有一小段亮。 |
| 5 | And lots of people still use it the same old way, as a chat. | `@ fig small-slice step=2` | 老用法：聊天 → 工作条下面出现一个聊天窗口。 |
| 6 | Ask a question, get an answer. | `@ fig small-slice step=3` | 一问一答 → 窗口里一个问题气泡、一个回答气泡，依次亮。 |
| 7 | Here's what I mean. | ↑ | 过渡句。 |
| 8 | Say you're a software engineer, and you've got a huge legacy system on your hands. | `@ fig engineer step=1` | 你和一个庞大的老系统 → 人形图标旁边一个很大、很乱的系统方块。 |
| 9 | The business side gives you a requirement. | `@ fig engineer step=2` | 来了需求 → 一张需求单从右边飞到你手里。 |
| 10 | You've built plenty of features like this, and you know the best way to do it. | `@ fig engineer step=3` | 你做过很多次 → 你身后一叠打了勾的旧功能。 |
| 11 | Which code to change, how to test it, what depends on what, what it might break. | `@ fig engineer step=4` | 你心里有数的四件事 → 四个标签围着你：改哪、怎么测、依赖、影响面。 |
| 12 | You've seen it all. | ↑ | |
| 13 | Now you're told to do it with AI. | `@ fig engineer step=5` | 被要求用 AI → 橙色标签「do it with AI」和一个空聊天框。 |
| 14 | What do you do? | ↑ | 聊天框里一个问号（step 5 已有）。 |
| 15 | Probably something like this. | `@ fig hook-prompt step=1` | 开始准备 prompt → 一个空的大聊天输入框，右上角计时器 0 分钟。 |
| 16 | First, you dig out the files you think matter, one by one, and paste them into the chat. | `@ fig hook-prompt step=2` | 一个个找文件贴进去 → 文件小卡片一张张掉进输入框，计时器走到 8 分钟。 |
| 17 | Then you write a long explanation of what the code does and how it all fits together. | `@ fig hook-prompt step=3` | 写长解释 → 一大段灰色文字块，计时器 15 分钟。 |
| 18 | Then you paste in the requirement. | `@ fig hook-prompt step=4` | 贴需求 → 需求块，计时器 20 分钟。 |
| 19 | And finally, a whole screen of "do this", "add that", "whatever you do, don't touch that". | `@ fig hook-prompt step=5` | 满屏叮嘱 → 一墙「do this / add that / don't touch that」，最后一条橙色加粗。 |
| 20 | The AI hasn't written a single line yet, and you've already spent half an hour. | `@ fig hook-prompt step=6` | 半小时、零行代码 → 两个大数字：「30 min」和「0 lines」。 |
| 21 | Then you hit Enter and hope it gets it right. | `@ fig hook-prompt step=7` | 按回车、祈祷 → 回车键亮起，旁边一个交叉手指的小标记。 |
| 22 | What you usually get is an answer you're maybe eighty or ninety percent happy with. | `@ fig hook-answer step=1` | 八九成满意 → AI 回答气泡，下面一条满意度条停在 80–90%。 |
| 23 | You paste its code back in, run the tests yourself, check the results yourself, | `@ fig hook-answer step=2` | 全靠你自己 → 三个动作依次出现在「你」身边：贴回去、跑测试、查结果。 |
| 24 | and some of it's still wrong. | `@ fig hook-answer step=3` | 还是有错 → 代码上冒出几个红叉。 |
| 25 | So you spend even longer reviewing it. | `@ fig hook-answer step=4` | 花更久审查 → 计时器从 30 跳到 60+ 分钟，一个放大镜。 |
| 26 | In the end, it feels faster to just write it yourself. | `@ fig hook-answer step=5` | 不如自己写 → 「faster to write it myself」，你的图标变成崩溃的脸（中文稿：崩溃的你）。 |
| 27 | The AI doesn't get your complex system, and it can't see the traps you know are there. | `@ fig hook-answer step=6` | AI 看不到坑 → 老系统里几个橙色三角（坑），你看得见，AI 的眼睛是 `eye-off`。 |
| 28 | In this video I want to make three things clear. | `@ big "3" "things this video makes clear" icon=list-checks` | 三件事 → 大数字 3。 |
| 29 | What's wrong with using AI this way. | `@ list "This video" "What's wrong with using AI this way\|circle-alert" "Why it's so hard for teams to adopt AI\|users" "What the missing piece is called\|puzzle" lit=1` | 第一件 → 清单第 1 条。 |
| 30 | Why it's so hard for development teams to really adopt AI. | `@ list "This video" "What's wrong with using AI this way\|circle-alert" "Why it's so hard for teams to adopt AI\|users" "What the missing piece is called\|puzzle" lit=2` | 第二件 → 第 2 条亮。 |
| 31 | And what the missing piece is called. | `@ list "This video" "What's wrong with using AI this way\|circle-alert" "Why it's so hard for teams to adopt AI\|users" "What the missing piece is called\|puzzle" lit=3` | 第三件 → 第 3 条亮（拼图图标，留个悬念）。 |

## 1 Your pain points（20 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 32 | If you've used AI like this, you've probably hit every one of these. | `@ list "Your pain points" "It doesn't know your project\|folder-search" "It forgets\|brain" "It doesn't always follow your rules\|list-x" "It's always sure of its own work\|badge-check" "You can't see what it did\|eye-off"` | 五个痛点先过一眼 → 不带 `lit=`，五条一起出现，都是平常色。 |
| 33 | One: it doesn't know your project. | `@ fig pain-context step=1` | 不知道你的项目 → 左边你的代码库，右边 AI 气泡带问号，中间隔着一道墙。 |
| 34 | Every single time, you have to find the code, paste the code, explain the code. | `@ fig pain-context step=2` | 每次都要找、贴、讲 → 三个箭头把文件搬过墙，旁边计数「×1 ×2 ×3 …」。 |
| 35 | Two: it forgets. | `@ fig pain-memory step=1` | 会丢记忆 → 一个聊满了的聊天窗口。 |
| 36 | Open a new chat, and everything you said before is gone. | `@ fig pain-memory step=2` | 新对话全没了 → 旧窗口变灰打叉，旁边一个空的新窗口。 |
| 37 | You have to say it all again. | `@ fig pain-memory step=3` | 从头再说 → 橙色箭头「again」，新窗口被你重新填满。 |
| 38 | And the longer a chat goes on, the worse it seems to get. | `@ fig pain-memory step=4` | 越聊越差 → 一个很长的对话，旁边一条往下走的表现曲线。 |
| 39 | It forgets things you agreed on at the start. | `@ fig pain-memory step=5` | 开头说好的忘了 → 对话顶上那条「agreed: …」变成虚线、淡出。 |
| 40 | Three: you give it a list of dos and don'ts, and it doesn't always follow them. | `@ fig pain-rules step=1` | 规则清单 → 五条 do / don't，其中一条带星（你最在意的）。 |
| 41 | Most of the time it listens. | `@ fig pain-rules step=2` | 大多照做 → 四条打上绿勾。 |
| 42 | But every so often, it skips exactly the step you cared about most. | `@ fig pain-rules step=3` | 偏偏跳过最在意的 → 带星那条变橙色虚线框，标签「skipped」。 |
| 43 | And the longer the chat gets, the more its attention drifts, and the less it remembers from earlier. | `@ fig pain-rules step=4` | 注意力漂走 → 一束「注意力」光从清单往下滑到对话末尾，上面的规则变暗。 |
| 44 | Four: it's always sure of its own work. | `@ fig pain-confident step=1` | 很自信 → agent 头像加一个大大的勾。 |
| 45 | "Done, and all the tests pass." | `@ fig pain-confident step=2` | 它的原话 → 绿色气泡「Done, and all the tests pass.」 |
| 46 | Then you look for yourself, and there's still a pile of mistakes. | `@ fig pain-confident step=3` | 自己一看一堆错 → 放大镜扫过代码，红叉一个个冒出来。 |
| 47 | Five: you can't see what it actually did. | `@ fig pain-blind step=1` | 看不到它做了什么 → 一个关着的黑盒子，agent 在里面，你在外面。 |
| 48 | Which files did it change? | `@ fig pain-blind step=2` | 改了哪些文件 → 盒子外第一个问号：文件图标。 |
| 49 | Which commands did it run? | `@ fig pain-blind step=3` | 跑了哪些命令 → 第二个问号：终端图标。 |
| 50 | Why did it do it that way? | `@ fig pain-blind step=4` | 为什么这么做 → 第三个问号：「why」。 |
| 51 | After the fact, it's hard to tell. | `@ fig pain-blind step=5` | 事后说不清 → 三个问号都变灰，盒子上一个时钟「later」。 |

## 2 The root cause（16 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 52 | Is this how you use AI right now? | `@ fig hook-prompt step=5` | 回到开头 → 复用 Hook 那一墙 prompt（不新画）。 |
| 53 | Well, that's how people used AI in 2024. | `@ fig human-carries step=1` | 这是 2024 的用法 → 中间一个聊天气泡，上方小字「2024」。 |
| 54 | As a chatbot. | ↑ | 气泡下标签「chatbot」（step 1 已有）。 |
| 55 | Back then, most people were busy learning to write better prompts to get better answers. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Coding agents at work" now=1` | 当年大家在研究 prompt → 时间线，2024 亮。 |
| 56 | That was called prompt engineering. | ↑ | 「Prompt engineering」字样正在亮处。 |
| 57 | But here's the problem. | ↑ | 过渡句。 |
| 58 | Even if the model is smart enough, you're still treating it like someone who just answers questions. | `@ fig human-carries step=2` | 只让它回答问题 → 气泡上只有一进一出两个箭头：问、答。 |
| 59 | You haven't let it get its hands on the work. | `@ fig human-carries step=3` | 没让它上手 → 气泡旁一只虚线的手，打着叉。 |
| 60 | It answers your questions, and everything else is still on you. | `@ fig human-carries step=4` | 其余都压在你身上 → 「你」出现在气泡旁边，橙色。 |
| 61 | Finding the code, sorting out the requirement, running the tests, | `@ fig human-carries step=5` | 前三件 → 三个任务块围到你身边：找代码、理需求、跑测试。 |
| 62 | remembering the context, making sure it follows the process, checking its results. | `@ fig human-carries step=6` | 后三件 → 再加三块：记上下文、盯流程、查结果。 |
| 63 | You do all of it by hand. | `@ fig human-carries step=7` | 全靠手工 → 六块都压在你身上，标签「by hand」，聊天气泡在旁边闲着。 |
| 64 | And in the end, you hear the same old lines. | `@ card "The same old lines" icon=messages-square` | 老论调 → 标题卡。 |
| 65 | AI isn't reliable. | `@ list "The same old lines" "AI isn't reliable.\|thumbs-down" "AI makes mistakes.\|circle-x" "AI can only help with part of my work.\|chart-pie" lit=1` | 第一句 → 清单第 1 条。 |
| 66 | AI makes mistakes. | `@ list "The same old lines" "AI isn't reliable.\|thumbs-down" "AI makes mistakes.\|circle-x" "AI can only help with part of my work.\|chart-pie" lit=2` | 第 2 条。 |
| 67 | AI can only help with part of my work. | `@ list "The same old lines" "AI isn't reliable.\|thumbs-down" "AI makes mistakes.\|circle-x" "AI can only help with part of my work.\|chart-pie" lit=3` | 第 3 条。 |

## 3 What is an agent（15 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 68 | So let me explain what an AI agent is. | `@ card "What is an AI agent?" icon=bot` | 章节卡。 |
| 69 | When you chat with AI, you're talking straight to the large language model, the LLM. | `@ fig llm-vs-agent step=1` | 你直接和 LLM 说话 → 你 ↔ 一个写着「LLM」的方块。 |
| 70 | It thinks, then writes you an answer in text. | `@ fig llm-vs-agent step=2` | 想完写文字 → LLM 方块里一个思考点点，吐出一张文字气泡。 |
| 71 | An agent is an LLM plus tool calling, meaning it can use tools. | `@ fig llm-vs-agent step=3` | LLM + tool calling → LLM 方块旁边加一个「+ tools」接口。 |
| 72 | Think of tools as its hands. | `@ fig llm-vs-agent step=4` | 工具是手 → 接口上长出两只手（`hand` 图标），标签「hands」。 |
| 73 | Once it's thought things through, it can go and change the code on your machine itself, run commands, search the web, open a browser. | `@ fig llm-vs-agent step=5` | 手能做的四件事 → 四个工具块亮起：改本地代码、跑命令、上网搜索、开浏览器。 |
| 74 | But hands alone aren't enough. | ↑ | |
| 75 | The key is that it loops. | `@ loop "LLM\|bot" "Tool\|square-terminal" "Result\|file-text" "Next step\|arrow-right"` | 关键是循环 → 循环图，不亮任何一格。 |
| 76 | It calls a tool, | `@ loop "LLM\|bot" "Tool\|square-terminal" "Result\|file-text" "Next step\|arrow-right" lit=2` | 调工具 → Tool 亮。 |
| 77 | looks at the result, | `@ loop "LLM\|bot" "Tool\|square-terminal" "Result\|file-text" "Next step\|arrow-right" lit=3` | 看结果 → Result 亮。 |
| 78 | and decides what to do next. | `@ loop "LLM\|bot" "Tool\|square-terminal" "Result\|file-text" "Next step\|arrow-right" lit=4` | 决定下一步 → Next step 亮。 |
| 79 | Then it calls again, looks again, and keeps going until the job's done. | `@ fig llm-vs-agent step=6` | 一圈圈做到完 → 右侧一串「call → look」小圈叠下去，最后一个绿勾「done」。 |
| 80 | Give an LLM hands and a loop of its own, and you've got an agent. | `@ formula "Agent" "LLM" "Hands + Loop"` | 公式 → Agent = LLM + Hands + Loop。 |
| 81 | It doesn't just answer you anymore. | `@ fig llm-vs-agent step=7` | 不只是回答 → 左边「answers you」的文字气泡变灰。 |
| 82 | It can finish a piece of work on its own. | `@ fig llm-vs-agent step=8` | 自己干完一件事 → 右边一张任务卡，盖上「done」青色章。 |

## 4 What is a harness（32 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 83 | But once an agent can work on its own, you get a new set of problems. | `@ card "New problems" kicker="Once an agent works on its own" icon=triangle-alert` | 新问题 → 章节卡，橙色警示图标。 |
| 84 | Look back over the last few years. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Coding agents at work"` | 回头看 → 时间线三格，都不亮。2026 先写「Coding agents at work」，「Harness engineering」留到第 106 行揭晓。 |
| 85 | In 2024, people were figuring out how to write good prompts. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Coding agents at work" now=1` | 2024 亮。 |
| 86 | In 2025, people found that to get steady results, you have to manage the AI's context well. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Coding agents at work" now=2` | 2025 亮。 |
| 87 | That's context engineering. | ↑ | |
| 88 | And by 2026, coding agents like Claude Code, Codex and GitHub Copilot can really get work done for you. | `@ logos claude-code codex github-copilot` | 点名三个 coding agent → 三个标志。 |
| 89 | And that's where the new problems start. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Coding agents at work" now=3` | 2026 亮：能干活了，问题也来了。 |
| 90 | Companies found that to really adopt agents, they have to solve these. | `@ fig nine-gaps step=1` | 企业要解决的 → 3×3 九个虚线空格，编号 1–9。 |
| 91 | One: it doesn't know your systems or your projects, so someone still has to explain them every time. | `@ fig nine-gaps step=2` | 第 1 格亮：不懂你的系统。 |
| 92 | Two: how do you keep its memory from one session to the next? | `@ fig nine-gaps step=3` | 第 2 格：跨会话记忆。 |
| 93 | If a session dies, how does a new one pick up the task? | ↑ | 第 2 格里的小图：一个会话断开、另一个接不上（step 3 已有）。 |
| 94 | Three: people only use the agent to change code. | `@ fig nine-gaps step=4` | 第 3 格：只拿来改代码。 |
| 95 | Running tests, the CI-CD pipeline, updating tickets, people still do all of that. | ↑ | 第 3 格里列着：测试、CI/CD、工单，都挂在人身上。 |
| 96 | Four: it doesn't always follow the rules you agreed on. | `@ fig nine-gaps step=5` | 第 4 格：不守约定的规则。 |
| 97 | Five: you don't dare give it access to your servers, in case it does something dangerous, like dropping a table. | `@ fig nine-gaps step=6` | 第 5 格：不敢开放服务器，小字「DROP TABLE」。 |
| 98 | Six: when it finishes a task, it's usually sure it got it right. | `@ fig nine-gaps step=7` | 第 6 格：做完很自信。 |
| 99 | Seven: where did the time and money go, and how do you spend less? | `@ fig nine-gaps step=8` | 第 7 格：钱和时间去哪了。 |
| 100 | The plan, the logs, the steps it took. | ↑ | 第 7 格里三个小文件：plan、log、steps。 |
| 101 | None of it gets recorded. | ↑ | 三个文件是虚线（没记下来）。 |
| 102 | Eight: one person can keep an eye on five sessions at most, so human attention becomes the bottleneck. | `@ big "5" "sessions at most, before human attention is the bottleneck" icon=messages-square` | 第 8 条单独给大数字 5，换个节奏。 |
| 103 | Nine: on a long or complex task, the agent always stops partway through. | `@ fig nine-gaps step=10` | 第 9 格：长任务半路停（第 8 格此时已作为「说过的」显示）。 |
| 104 | That's a lot of problems. | `@ fig nine-gaps step=11` | 太多了 → 九格一起变橙。 |
| 105 | Getting an agent to work well, and keep working well, is a craft of its own. | ↑ | |
| 106 | It's called harness engineering. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Harness engineering" now=3` | 揭晓名字 → 同一条时间线，2026 换成「Harness engineering」并亮起。 |
| 107 | There's a simple formula: agent equals model plus harness. | `@ formula "Agent" "Model" "Harness"` | 公式，Harness 青色。 |
| 108 | Everything outside the model is the harness. | `@ fig harness-around step=1` | 模型之外都是 harness → 中间「Model」，外面一圈青色环「Harness」，环上五件事（中文稿：五件事围着模型）。 |
| 109 | All of this used to be you, reminding it in the prompt. | `@ fig program-vs-agent step=1` | 以前靠你在 prompt 里叮嘱 → 左边「你」和一张写满叮嘱的 prompt（呼应 Hook 那一墙）。 |
| 110 | Now a program does it. | `@ fig program-vs-agent step=2` | 交给程序 → 叮嘱一条条移进一个齿轮方块「program」。 |
| 111 | A program is deterministic. | `@ fig program-vs-agent step=3` | 确定性 → 程序方块下「same input → same result」。 |
| 112 | It doesn't spend tokens, and it doesn't depend on the model behaving itself. | `@ fig program-vs-agent step=4` | 两个好处 → 两个标签：「0 tokens」「no model needed」。 |
| 113 | So jobs with a fixed answer go to programs, | `@ fig program-vs-agent step=5` | 有标准答案的给程序 → 画面一分为二，左栏 program 收进三件事：挡危险命令、查文件清单、算测试数。 |
| 114 | and anything that needs judgment goes to the agent. | `@ fig program-vs-agent step=6` | 要判断的给 agent → 右栏 agent 收进三件事：设计方案、写代码、读失败原因。 |

## 5 My harness（50 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 115 | I've built my own harness framework, | `@ board/tour-list crop=0,0,1,0.42` | 我的 harness → 真实看板：顶上的数字（15 个任务、13 个等你）和前几行任务。 |
| 116 | on top of GitHub Copilot in VS Code. | `@ logos github-copilot vscode` | 基于什么 → 两个官方标志。 |
| 117 | If your company uses Microsoft, you're probably using two Copilots at once: M365 Copilot and GitHub Copilot. | `@ logos m365-copilot github-copilot` | 两个 Copilot → 两个标志。 |
| 118 | GitHub Copilot is what we call a coding agent. | `@ logos "m365-copilot\|chat, mail, documents" "github-copilot\|coding agent"` | GitHub Copilot 是 coding agent → 同两个标志，标签换成各自是干什么的。 |
| 119 | My harness helps you steer it better. | `@ fig harness-around step=2` | 我的 harness 驾驭它 → 复用第 108 行的环：中间换成 GitHub Copilot 标志，环上写「my harness」，五件事换成具体的名字。 |
| 120 | Let's go back to those problems and see how my harness handles each one. | `@ fig nine-gaps step=12` | 回到那些问题 → 复用九格：这次要讲的 1、2、3、5、6、7 亮青色，4、8、9 变暗标「more」。 |
| 121 | First: it doesn't know your systems or your projects, so someone has to explain them every time. | `@ list "How my harness handles them" "It doesn't know your systems\|folder-search" "Memory across sessions\|history" "Tests, pipelines, tickets · server access\|server" "Sure it got it right\|badge-check" "Time and money, not recorded\|receipt" lit=1` | 第一个问题 → 本场的目录清单，第 1 条亮。之后每个问题回到这张清单，一条条往下亮。 |
| 122 | I built a standard framework that turns a codebase into a knowledge base. | `@ fig kb-build step=1` | 代码库 → 知识库 → 左边代码库（一堆文件），箭头，右边一个空的知识库书架。 |
| 123 | A set of tools studies your codebase, | `@ fig kb-build step=2` | 一套工具读代码 → 扳手/放大镜图标在文件上扫过。 |
| 124 | finds the hidden dependencies between files, | `@ fig kb-build step=3` | 找隐藏依赖 → 文件之间亮起青色虚线连线。 |
| 125 | and writes them up as cards. | `@ fig kb-build step=4` | 写成卡片 → 连线收拢成一张张卡片，进到书架。 |
| 126 | When it's done, it produces a summary file and an index. | `@ fig kb-build step=5` | 总结和目录 → 书架顶上一份 SUMMARY，旁边一份 INDEX。 |
| 127 | So the agent doesn't have to reread the code every time. | `@ fig kb-build step=6` | 不用每次重读代码 → agent 出现，指向代码库的箭头打叉。 |
| 128 | It just loads the summary and a few cards, | `@ fig kb-build step=7` | 只加载总结和几张卡 → agent 拿走 SUMMARY 和两张卡（青色箭头）。 |
| 129 | and it gets a rough picture of your codebase. | `@ tutorials/6_kb/kb-go-on-docs box=0.025,0.315,0.95,0.4 text="The knowledge base: 5 domains, 74 cards"` | 大概了解代码库 → 真实知识库总览：5 个领域、74 张卡、每个领域学到哪。 |
| 130 | And when it needs more, the index takes it straight to the right file. | `@ board/kb-lookup crop=0,0.03,0.7,0.42 box=0.015,0.2,0.45,0.245 text="Look up: who uses it, what it uses, which file"` | 目录直达文件 → 真实「Look up」：一个存储过程被谁用、用了谁、在哪个文件。 |
| 131 | Second: how do you keep its memory from one session to the next? | `@ list "How my harness handles them" "It doesn't know your systems\|folder-search" "Memory across sessions\|history" "Tests, pipelines, tickets · server access\|server" "Sure it got it right\|badge-check" "Time and money, not recorded\|receipt" lit=2` | 第 2 条亮。 |
| 132 | If a session dies, how does a new one pick up the task? | `@ fig task-folder step=1` | 会话断了怎么接 → 会话 A 打叉，会话 B 一脸问号。 |
| 133 | Every task is a folder. | `@ fig task-folder step=2` | 每个任务是一个文件夹 → 中间一个大文件夹「show-delivery-date/」。 |
| 134 | It holds everything from the task's whole life. | `@ fig task-folder step=3` | 全生命周期 → 文件夹下一条时间轴：需求 → 计划 → 动手 → 检查 → 结束。 |
| 135 | The plan, the history log, the status, | `@ fig task-folder step=4` | 第一批文件 → PLAN.md、LOG.md、TASK.md（状态）飞进文件夹。 |
| 136 | the requirement doc, the test scripts, the changed code, | `@ fig task-folder step=5` | 第二批 → REQ.md、TEST/、DEV/ 飞进去。 |
| 137 | and anything else the agent produces along the way. | `@ board/tour-tab-files crop=0,0.31,0.75,0.69 box=0.03,0.475,0.27,0.52 text="The Files tab: the whole task folder"` | 还有别的产物 → 真实「Files」页：REQ/、REF/、DEV/、TEST/、LOG.md 一整棵树。 |
| 138 | So if a session dies, a new one just scans the folder and carries on right away. | `@ board/go-on-new-chat box=0.13,0.72,0.8,0.2 text="A new chat picks the task up from its files"` | 新会话接着做 → 真实按钮「Go on in a new chat」，旁边一行「picks the task up from its files」。 |
| 139 | Third: people only use the agent to change code, and still handle the tests, the CI-CD pipeline and the tickets themselves. | `@ list "How my harness handles them" "It doesn't know your systems\|folder-search" "Memory across sessions\|history" "Tests, pipelines, tickets · server access\|server" "Sure it got it right\|badge-check" "Time and money, not recorded\|receipt" lit=3` | 第 3 条亮。 |
| 140 | And you don't dare give it access to your servers, in case it does something dangerous, like dropping a table. | `@ big "DROP TABLE" "the one command nobody wants an agent to run" icon=database-zap` | 怕删表 → 大字「DROP TABLE」。 |
| 141 | Give the agent access to your dev and test environments, | `@ fig tool-pack step=1` | 开放开发、测试环境 → agent 连向 DEV、TEST 两个环境方块；PROD 灰着、上锁。 |
| 142 | and it can build things, write its own test scripts, run them, and fix what fails. | `@ fig tool-pack step=2` | 自己闭环 → DEV 旁一个小循环亮起：build → 写测试 → run → fix。 |
| 143 | To keep that safe, here's what I do. | `@ fig tool-pack step=3` | 安全怎么办 → 箭头外面罩上一层盾牌。 |
| 144 | With a standard tool pack, the agent gets read-only access to the lower environments. | `@ fig tool-pack step=4` | 标准 tool pack、只读 → 箭头分成两条道：「read」畅通（青），「write / execute」前面一道门（橙）。 |
| 145 | Anything that writes or executes needs a person to approve it. | `@ board/outside-held-card box=0.045,0.845,0.72,0.1 text="A write waits for a person and a typed code"` | 写和执行要人批 → 真实卡片：agent 要往工单系统写一条评论，停着等你输入批准码。 |
| 146 | Take Microsoft's SQL Server. | `@ board/outside-tools-packs crop=0,0,1,0.56 box=0.027,0.405,0.946,0.12 text="The sqlserver tool pack ships with the harness"` | 以 SQL Server 为例 → 真实「Tool packs」对话框，框出 sqlserver 这一包。 |
| 147 | I've tested my harness against thousands of injected dangerous commands. | `@ fig guard-layers step=1` | 几千种危险命令 → 左边一串红色命令（DROP TABLE、TRUNCATE、DELETE … xp_cmdshell）涌向右边的数据库（SQL Server 标志），计数「thousands」。 |
| 148 | Between a blacklist, a whitelist, | `@ fig guard-layers step=2` | 前两层 → 黑名单、白名单两道墙亮起，大部分红命令被挡下。 |
| 149 | a human making the call, and the account's own permissions, | `@ fig guard-layers step=3` | 后两层 → 「人」和「账号权限」两道墙亮起，剩下的也被挡下。 |
| 150 | the agent's access stays safe. | `@ board/stop-agent-actions box=0.04,0.495,0.92,0.49 text="What the gate stopped, kept on the task's record"` | 访问是安全的 → 真实「Agent actions」：4 个被拦下的调用（删工单、git checkout、git push、改目标库）和原因。 |
| 151 | Fourth: when it finishes a task, it's usually sure it got it right. | `@ list "How my harness handles them" "It doesn't know your systems\|folder-search" "Memory across sessions\|history" "Tests, pipelines, tickets · server access\|server" "Sure it got it right\|badge-check" "Time and money, not recorded\|receipt" lit=4` | 第 4 条亮。 |
| 152 | I bring in an independent reviewer as a subagent. | `@ fig reviewer step=1` | 独立 reviewer 子 agent → 主 agent 一个机器人，旁边另一个独立的机器人「reviewer」，各自一个框（不同的上下文）。 |
| 153 | It reviews everything the agent did on the task | `@ fig reviewer step=2` | 审全部 → 需求、计划、改动、测试结果四份东西流进 reviewer。 |
| 154 | and gives a test verdict. | `@ board/review crop=0,0.57,1,0.43 box=0.035,0.805,0.93,0.185 text="Each round: a verdict and its reasons"` | 给出判定 → 真实「Review」页：round-002 PASS，round-001 FAIL 被框出，带理由。 |
| 155 | In practice, the reviewer catches lots of cases the main agent never thought of. | `@ board/checks-used-review crop=0,0.46,1,0.54 box=0.04,0.79,0.92,0.2 text="Caught: capital letters and digits were never checked"` | 发现主 agent 没想到的 → 真实三轮 FAIL，框出「only measured, not checked against capital letters or digits」。 |
| 156 | Fifth: where did the time and money go, and how do you spend less? | `@ list "How my harness handles them" "It doesn't know your systems\|folder-search" "Memory across sessions\|history" "Tests, pipelines, tickets · server access\|server" "Sure it got it right\|badge-check" "Time and money, not recorded\|receipt" lit=5` | 第 5 条亮。 |
| 157 | The plan, the logs, the steps it took. | `@ fig task-report step=1` | 计划、日志、步骤 → 一张报表的轮廓，三块都是虚线空白。 |
| 158 | None of it gets recorded. | ↑ | 空白上标「not recorded」。 |
| 159 | I built a report panel that shows the numbers for the whole task. | `@ board/tour-report crop=0,0.03,1,0.37 box=0.012,0.17,0.975,0.2 text="Task analysis: the whole task in numbers"` | 报告面板 → 真实「Task analysis」顶上一排数字。 |
| 160 | Where the time went, | `@ board/tour-report crop=0,0.78,1,0.2 box=0.035,0.805,0.93,0.15 text="Where the time went"` | 时间 → 同一页下面的「Where the time went」时间条。 |
| 161 | where the money went, | `@ board/tour-performance crop=0,0.37,1,0.32 box=0.01,0.39,0.98,0.28 text="Credits, prompt by prompt"` | 钱 → 真实「Agent Performance Review」每个 prompt 的 Credits。 |
| 162 | which tool calls failed. | `@ board/stop-agent-actions crop=0,0.36,1,0.64 box=0.655,0.385,0.305,0.09 text="Blocked and failed calls, counted"` | 失败的调用 → 「blocked by a hook」「tool calls failed」两个计数被框出。 |
| 163 | It's all there at a glance. | `@ fig task-report step=2` | 一目了然 → 第 157 行那张轮廓被填满：时间条、钱、失败调用，青色。 |
| 164 | There's a lot more, but no time to cover it all here. | `@ board/tour-lobby crop=0,0,1,0.62` | 还有很多 → 真实大厅：一屋子机器人，各自在等你或在干活。 |

## 6 Summary（11 行）

| # | 英文句子（一口气一行，已切好） | 画面 | 说明（这句的核心 → 画面上看到什么） |
| --- | --- | --- | --- |
| 165 | So, AI hasn't gotten dumber. | `@ card "AI hasn't gotten dumber" icon=brain` | 总结卡。 |
| 166 | The way we use it is just stuck in 2024. | `@ timeline "2024\|Prompt engineering" "2025\|Context engineering" "2026\|Harness engineering" now=1` | 卡在 2024 → 同一条时间线，亮在 2024。 |
| 167 | We treat it as a chatbot, and people still do the copying and pasting, watch the process, and do the checks. | `@ fig who-does-what step=1` | 人在搬运、盯流程、做检查 → 一张三栏表：2024 chatbot / agent / harness；行是搬运、流程、检查、边界；第一栏每行都是「你」（橙）。 |
| 168 | With an agent, a program does the copying and pasting. | `@ fig who-does-what step=2` | agent 接走搬运 → 第二栏「搬运」行换成齿轮（青）。 |
| 169 | With a harness, a program also handles the process, the checks and the boundaries. | `@ fig who-does-what step=3` | harness 接走流程、检查、边界 → 第三栏四行全是齿轮。 |
| 170 | And people can finally step back, | `@ fig who-does-what step=4` | 人退后一步 → 「你」移到表下面一行，标签「judge · sign off」。 |
| 171 | make the calls, and sign off. | `@ board/accept box=0.045,0.85,0.135,0.11 text="You make the call: Accept and close"` | 把关 → 真实「to accept」卡片，框出「Accept and close」按钮。 |
| 172 | If you're rolling out AI on your team, don't rush to ask, "Which stronger model should we switch to?" | `@ quote "Which stronger model should we switch to?" by="Don't ask this first"` | 先别问换模型 → 引语卡。 |
| 173 | Ask this first: "What's missing around our AI?" | `@ fig harness-around step=3` | 我们的 AI 周围缺了什么 → 复用环：中间模型，外圈变成虚线环，环上一个大问号。 |
| 174 | If you want to try it yourself, | `@ board/one-01-new-task box=0.02,0.54,0.47,0.165 text="Your first task starts here"` | 想试试 → 真实「New task」对话框，框出「What to do」。 |
| 175 | in the next video I'll walk you through installing this harness and starting your first task. | `@ card "Install the harness, start your first task" kicker="Next video" icon=play` | 下一集预告卡。 |

---

## 要新画的图

21 张，放在 `source/courses/basic-01/figs/`。每张一句话说布局，然后列每一步亮什么、哪几行用。没写的规则照 FORMAT.md：`data-step="k"` 的元素 k>N 时隐藏、k=N 时青色、k<N 时平常色；要「变掉」以前的东西就用 `.at-N`。

### small-slice（开场：AI 只用了一小块）
布局：上面一条横向长条，分成 8 段：需求、设计、写代码、测试、CI/CD、工单、评审、上线；下面一个小聊天窗口。
- step 1：长条出现，只有「写代码」里的一小段青色，其余灰。标注「AI」。→ 第 4 行
- step 2：下面出现一个聊天窗口，标题「chat」。→ 第 5 行
- step 3：窗口里一个问题气泡（你），一个回答气泡（AI），一问一答。→ 第 6–7 行

### engineer（你和老系统）
布局：左边「你」，右边一个很大、线条交错的系统方块「legacy system」。
- step 1：你 + 老系统。→ 第 8 行
- step 2：一张需求单从右上飞来，标「from the business」。→ 第 9 行
- step 3：你身后一叠打勾的旧功能卡「done before」。→ 第 10 行
- step 4：四个标签围着你：which code / how to test / what depends / what breaks。→ 第 11–12 行
- step 5：橙色标签「do it with AI」，旁边一个空聊天框，里面一个问号。→ 第 13–14 行

### hook-prompt（半小时的准备）
布局：中间一个很高的聊天输入框，右上角一个计时器，右下角「Enter」键。
- step 1：空输入框，计时 0 min。→ 第 15 行
- step 2：三四张文件小卡（orders.py、api.py …）一张张进框，计时 8 min。→ 第 16 行
- step 3：一大段灰色解释文字，计时 15 min。→ 第 17 行
- step 4：需求块，计时 20 min。→ 第 18 行
- step 5：一墙叮嘱「do this / add that / don't touch that」，最后一条橙色。→ 第 19 行，第 52 行复用
- step 6：两个大数字「30 min」「0 lines」。→ 第 20 行
- step 7：Enter 键亮，旁边交叉手指的小标记「hope」。→ 第 21 行

### hook-answer（八九成的答案，然后你崩溃）
布局：左边 AI 回答气泡，中间「你」，右边老系统缩略图。
- step 1：回答气泡，下面满意度条停在 80–90%。→ 第 22 行
- step 2：你身边依次三个动作：paste back、run tests、check results（都标「you」）。→ 第 23 行
- step 3：代码上冒出红叉。→ 第 24 行
- step 4：计时器 30 → 60+ min，一个放大镜。→ 第 25 行
- step 5：「faster to write it myself」，你的头像换成崩溃的脸（Lucide `frown` 或 `angry`）。→ 第 26 行
- step 6：右边老系统里几个橙色三角（坑）；你这边看得见，AI 那边是 `eye-off`。→ 第 27 行

### pain-context（痛点 1：不知道你的项目）
每张痛点图左上角都有一排五个小圆点，当前这个亮，作为进度。
布局：左边你的代码库，右边 AI 气泡带问号，中间一道竖墙。
- step 1：代码库、墙、问号气泡。→ 第 33 行
- step 2：三个箭头把文件搬过墙：find、paste、explain，旁边计数「×1 ×2 ×3 …」。→ 第 34 行

### pain-memory（痛点 2：会丢记忆）
布局：两个并排的聊天窗口，右侧留一条竖向的「表现」曲线位置。
- step 1：左窗口聊满了。→ 第 35 行
- step 2：左窗口变灰打叉，右边一个空的新窗口。→ 第 36 行
- step 3：橙色「again」箭头，新窗口被重新填满。→ 第 37 行
- step 4：换成一个很长的对话，旁边表现曲线往下走。→ 第 38 行
- step 5：对话顶上那条「agreed: …」变虚线淡出。→ 第 39 行

### pain-rules（痛点 3：不一定照做）
布局：左边五条 do / don't 清单，其中一条带星；右边一条长对话。
- step 1：清单出现。→ 第 40 行
- step 2：四条绿勾。→ 第 41 行
- step 3：带星那条变橙色虚线框，标签「skipped」。→ 第 42 行
- step 4：一束「attention」光从清单滑到对话末尾，清单变暗。→ 第 43 行

### pain-confident（痛点 4：很自信）
布局：左边 agent 和它的气泡，右边一段代码。
- step 1：agent 头像加一个大勾。→ 第 44 行
- step 2：绿色气泡「Done, and all the tests pass.」→ 第 45 行
- step 3：放大镜扫过右边代码，红叉一个个冒出来。→ 第 46 行

### pain-blind（痛点 5：看不到它做了什么）
布局：中间一个黑盒子（agent 在里面），盒外三个问号位置。
- step 1：黑盒子，你在外面。→ 第 47 行
- step 2：问号 1：文件图标「which files?」。→ 第 48 行
- step 3：问号 2：终端图标「which commands?」。→ 第 49 行
- step 4：问号 3：「why?」。→ 第 50 行
- step 5：三个问号都变灰，盒子上一个时钟「after the fact」。→ 第 51 行

### human-carries（根因：人在扛所有事）
布局：中间偏左一个聊天气泡「chatbot」，右边是「你」的位置，六个任务块围着你。
- step 1：气泡 + 小字「2024」+ 标签「chatbot」。→ 第 53–54 行
- step 2：气泡上只有「question → answer」一进一出。→ 第 58 行
- step 3：气泡旁一只虚线的手，打叉「no hands on the work」。→ 第 59 行
- step 4：「你」出现，橙色。→ 第 60 行
- step 5：三块围上来：find the code、sort the requirement、run the tests。→ 第 61 行
- step 6：再三块：remember context、follow the process、check results。→ 第 62 行
- step 7：六块压在你身上，标签「by hand」；气泡在一旁闲着。→ 第 63 行

### llm-vs-agent（LLM 和 agent）
布局：左半边「你 ↔ LLM → 文字」；右半边同一个 LLM 长出手和工具；最右一列是循环的记录。
- step 1：你 ↔ LLM 方块。→ 第 69 行
- step 2：LLM 吐出一张文字气泡「answer」。→ 第 70 行
- step 3：LLM 旁加「+ tool calling」接口。→ 第 71 行
- step 4：接口上两只手（`hand`），标签「hands」。→ 第 72 行
- step 5：四个工具块：edit your code、run commands、search the web、open a browser。→ 第 73–74 行
- step 6：最右一串「call → look」小圈往下叠，最后一个绿勾「done」。→ 第 79 行
- step 7：左边的文字气泡变灰，标「just answers」。→ 第 81 行
- step 8：右边一张任务卡，盖上青色「done」章，标「finishes the work」。→ 第 82 行

### nine-gaps（企业要补的九个缺口）
布局：3×3 九格，每格一个图标加一行短标签，先是虚线空格带编号。九格的内容：
1 doesn't know your systems（`folder-search`） · 2 memory across sessions（`unplug`，小图：会话断开） · 3 only changes code（`workflow`，小字 tests / CI-CD / tickets） · 4 doesn't follow the rules（`list-x`） · 5 no server access（`database-zap`，小字 DROP TABLE） · 6 sure it's right（`badge-check`） · 7 time & money?（`receipt`，三个虚线小文件 plan / log / steps） · 8 5 sessions at most（`messages-square`） · 9 stops partway（`circle-pause`）
- step 1：九个虚线空格。→ 第 90 行
- step 2 … step 8：第 1 … 7 格依次亮。→ 第 91、92–93、94–95、96、97、98、99–101 行
- step 9：第 8 格（这一步不单独上屏，第 102 行用大数字 5；到 step 10 时它作为「说过的」出现）
- step 10：第 9 格亮。→ 第 103 行
- step 11：九格一起变橙（`.at-11`）。→ 第 104–105 行
- step 12：1、2、3、5、6、7 亮青色，4、8、9 变暗，角上小字「and more」（`.at-12`）。→ 第 120 行

### harness-around（模型外面那一圈）
布局：中间一个圆「Model」，外面一圈环「Harness」，环上均匀五个小块。
- step 1：Model + 青色环「Harness」+ 五块通用名：knowledge、memory、limits、checks、records。→ 第 108 行
- step 2：中间换成 GitHub Copilot 标志（`<img data-logo="github-copilot">`），环标「my harness」，五块换成具体名：knowledge base、task folder、tool pack、reviewer、task report（`.at-2`）。→ 第 119 行
- step 3：五块消失，环变成橙色虚线，环上一个大问号「what's missing?」（`.at-3`）。→ 第 173 行

### program-vs-agent（确定的事给程序，要判断的给 agent）
布局：先是左边「你 + 一张写满叮嘱的 prompt」，然后画面分成左右两栏：program（齿轮）和 agent（机器人）。
- step 1：你和那张叮嘱 prompt（「don't touch X」「run the tests」「follow the plan」）。→ 第 109 行
- step 2：叮嘱一条条移进齿轮方块「program」。→ 第 110 行
- step 3：齿轮下「same input → same result」。→ 第 111 行
- step 4：两个标签「0 tokens」「no model needed」。→ 第 112 行
- step 5：左栏「fixed answer → program」：block dangerous commands、check the file list、count the tests。→ 第 113 行
- step 6：右栏「judgment → agent」：choose a design、write the code、read why it failed。→ 第 114 行

### kb-build（代码库 → 卡片 → 总结 + 目录）
布局：左边代码库（一叠文件），中间工具，右边知识库书架。
- step 1：代码库 → 箭头 → 空书架「knowledge base」。→ 第 122 行
- step 2：工具图标（`scan-search`）扫过文件。→ 第 123 行
- step 3：文件之间亮起青色虚线连线「hidden dependencies」。→ 第 124 行
- step 4：连线收成卡片，一张张进书架。→ 第 125 行
- step 5：书架顶上 SUMMARY，旁边 INDEX。→ 第 126 行
- step 6：agent 出现，指向代码库的箭头打叉「no rereading」。→ 第 127 行
- step 7：agent 拿走 SUMMARY 和两张卡（青色箭头）。→ 第 128 行

### task-folder（每个任务是一个文件夹）
布局：左上两个会话（A、B），中间一个大文件夹，文件夹下一条生命周期时间轴。
- step 1：会话 A 打叉，会话 B 带问号。→ 第 132 行
- step 2：大文件夹「show-delivery-date/」。→ 第 133 行
- step 3：时间轴：requirement → plan → work → review → closed。→ 第 134 行
- step 4：PLAN.md、LOG.md、TASK.md（status）飞进文件夹。→ 第 135 行
- step 5：REQ.md、TEST/、DEV/ 飞进去。→ 第 136 行
- （第 138 行直接用真实截图「Go on in a new chat」，不再加步。）

### tool-pack（开放环境，但分道）
布局：左边 agent，右边三个环境方块 DEV、TEST、PROD（PROD 灰色上锁），中间是连线。
- step 1：agent 连向 DEV、TEST。→ 第 141 行
- step 2：DEV 旁一个小循环：build → write tests → run → fix。→ 第 142 行
- step 3：连线外罩上一个盾牌。→ 第 143 行
- step 4：连线分两条道：「read」畅通（青），「write / execute」前一道门，门边一个「你」（橙），标「tool pack」。→ 第 144 行

### guard-layers（四道防线）
布局：左边一串红色危险命令往右冲，中间四道竖墙，右边数据库（`<img data-logo="sql-server">`）。
- step 1：红命令（DROP TABLE、TRUNCATE、DELETE FROM、xp_cmdshell …）和计数「thousands, injected」；四道墙只是虚线位置。→ 第 147 行
- step 2：「blacklist」「whitelist」两道墙亮，大部分命令碎在墙上。→ 第 148 行
- step 3：「a human decides」「account permissions」两道墙亮，剩下的也停住，数据库安然无恙。→ 第 149 行

### reviewer（独立 reviewer 子 agent）
布局：左边主 agent 和它的框，右边另一个机器人 reviewer 和它自己的框。
- step 1：两个机器人，各自一个框，中间一道隔线「separate context」。→ 第 152 行
- step 2：需求、计划、改动、测试结果四份东西从左流进 reviewer，reviewer 下面一个空的「verdict」位。→ 第 153 行
（判定本身由第 154 行的真实 Review 截图来出。）

### task-report（钱和时间都去哪了）
布局：一张报表轮廓，三块：time、money、failed calls。
- step 1：三块都是虚线空白，标「not recorded」。→ 第 157–158 行
- step 2：三块被填满：时间条、按 prompt 的 credits 条、几条红色失败调用，青色（`.at-2` 去掉「not recorded」）。→ 第 163 行

### who-does-what（谁在干活）
布局：一张表，三栏：2024 chatbot / agent / harness；四行：copy & paste、process、checks、boundaries。格子里是「你」（橙）或齿轮（青）。
- step 1：第一栏四行全是「你」。→ 第 167 行
- step 2：第二栏「copy & paste」是齿轮，其余仍是你。→ 第 168 行
- step 3：第三栏四行全是齿轮。→ 第 169 行
- step 4：「你」挪到表下面单独一行「make the calls · sign off」。→ 第 170 行

---

## 截图要补的

现有截图都用上了，但下面这些在演示工作区里重拍会更有说服力（按重要性排）：

1. **SQL Server 被拦下的危险命令**（第 147–150 行）：一个真实任务的「Agent actions」，里面是 sqlserver 包拦下的 DROP TABLE / TRUNCATE，和一条等人批准的写语句。现在只有 demotracker 和 git 的例子，而这段口播说的就是 SQL Server。
2. **有真实数字的任务报告**（第 159–162 行）：`board/tour-report` 现在是 5 秒、credits 是「-」；`board/tour-performance` 每个 prompt 的条是空的；`tool calls failed` 是 0。需要一个真跑过 Copilot 的任务，时间、credits、失败调用都有值。
3. **agent 自己在 DEV 跑测试并改到通过**（第 142 行）：一个 Test 页或 Agent actions 页，runner 是 agent、DEV 先 FAIL 再 PASS。现在的 `board/tour-tab-test` 里 IST 的 runner 是 person，所以这行暂时只用了图。
4. **知识库的总结文件和一张卡片打开的样子**（第 126–128 行）：知识库仓库里的 SUMMARY 和一张卡，现在只能靠图来画。顺带一张有好几个领域、有连线的 Map（现在 `board/kb-map` 只有一个点）。
5. **任务文件夹顶层文件展开**（第 135–137 行）：Files 页把 PLAN.md、LOG.md、TASK.md、REQ.md、TEST/、DEV/ 都露出来；现在 `board/tour-tab-files` 被 REQ/originals 占了大半，顶层文件在底部被截断。
