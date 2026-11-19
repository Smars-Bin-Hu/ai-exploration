# Basic 01 · 骨架（人写，2026-11-17）

0 Hook：你想开发一个东西，你还在上传给很多代码文件到 chatbox，写一大堆代码内容的解释，然后是你要做的事情（需求），写满很多要做什么，要加什么。期望 AI 能给你正确的结果。

1 你的痛点：不知道你的项目，每次需要你寻找和解释很多代码文件；AI 会丢失记忆，重新开一个对话框，就要重新说一遍，而且你发现随着对话越来越多，一个会话里的 agent 表现似乎开始下降；你说了很多要做什么，不做什么，它不一定照做；它自己检查自己总是很自信，交给你的时候，你会发现还有很多错误……

2 根因：这是不是你用 AI 的方式？这也是 2024 年使用 AI 的方式，总结就是，你限制了 AI 的发挥。

3 什么是 Agent：你日常和 AI 交流的方式，其实是直接和 LLM 对话，LLM 思考并写作，回答你的问题。但是 Agent 是 LLM 加了 Tool Calling，我们可以理解 tool 就是手，现在 LLM 思考后就可以去调用这些 Tool，比如修改你本地的代码文件、运行命令、web search、使用浏览器等等。这样 Agent 就诞生了。

4 什么是 harness：2024 年，人们是研究如何写好 prompt 才能提高表现；2025 年，人们发现要做好 context engineering，保护好 AI 的上下文，AI 才能发挥稳定；2026 年，随着 coding agent，比如 codex，claude code，github copilot 的诞生，agent 可以帮你干活了，但是也意味着 agent 可能会做很多危险的事情，所以如何让 agent 更稳定高效的工作，就是所谓 harness engineering。一个公式：Agent = Model + Harness，模型外面那些内容，比如上下文怎么管理、怎么拦住危险操作、怎么设计工作流、怎么批准 agent 的操作、如何使用子 agent、如何后续审计我们的 agent 的 performance，这些都是 harness engineering。

5 我的 harness 是什么？我开发了一款框架，它是基于 VS Code copilot 的，如果你的团队是微软的客户，那么大概率会同时使用 M365 copilot 和 github copilot 这两款软件，其中 github copilot 就是我们所谓的 coding agent，和大名鼎鼎的 Claude Code 和 Codex 都是异曲同工的。那我的 harness 就是来帮助用户更好驾驭 github copilot 的，它会提供你更好的驾驭 agent 的体验。包括：……（设计几个场景）

6 总结
