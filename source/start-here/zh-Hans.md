# AI Exploration：从这里开始

> 简中原稿第 4 版（2026-11-12；同日补上 Agent Performance Review，第 6 页和第 18 页各拆成两页，共 20 页）。三拍：共鸣 → 结论和根因 → 我的 harness 是解决方案（截图是证据）→ 下一步。按读者卡写（studio `skills/write-team-post/读者卡.md`）：读者是同组同事和 lead、manager，只用过 Copilot chat；harness 自己的词只留 harness、task、board、知识库，第一次出现讲清，其余换成大白话。图里的字只用英文，直接写在图位里。
>
> 这一版改了什么：
> - 第 2 页不再用“假如……我猜……第一步”的框架，按这一页的用处重写：让读者认出自己每天的样子（意见 4）。
> - 第 2 页（场景）和第 3 页（四个原因）分成两页；结论和根因也分成两页，和英文版一致。第 5 页的图是做英文时加的，现在写进中文稿，图里的字改成一句话，不用压缩的词（意见 3）。
> - 第 4 页先讲清 chat 和 agent 差在哪；第 6 页讲清 task 和 board。
> - 对照图按四个原因排，第 2 条同时对着纵向（知识库）和横向（不用写长 prompt），不再多出第五行。图里每一格都写成“谁做什么”。
> - 功能页去掉读者不懂的词：tool pack、skill、MCP、配对、promote、写回、fork、hook。“两次批准”改成“你批准计划，也批准结果”。
> - 第 10 页没有截图前，用一张环境规则的图，不放占位框。第 17 页“另一个 skill”的占位不进英文版和 PDF。
> - 最后一页从“目录”改成“看完以后：去哪里，找谁”，按读者卡的四个下一步写。

---

## 第 1 页 · 封面

**AI Exploration：从这里开始**

为什么 AI 在我们团队的实际工作里用不起来，缺的是什么，我给 Copilot 加的那一层（harness）怎么补上。

---

## 第 2 页 · 共鸣 · 今天我们怎么把一个任务交给 AI

一个普通的 intake，从拿到需求到关单，大概要做这几件事：读需求，找到要改的代码，改代码，在 DEV 上跑测试，查数据对不对，看 pipeline 有没有报错，更新工单，最后从头检查一遍。八件事里，Copilot 能帮上忙的只有“改代码”这一件。

为了这一件，你先得花半个小时准备：把相关的代码一段段找出来贴进 chat，讲清楚这些代码是干什么的、需求是怎么来的，再列一串要做的和不许做的，然后盼着它这次能一次做对。

它写完了，剩下的还是你的：登上 DEV 跑测试、查数据，打开 Azure DevOps 更新工单，再把它写的代码一行一行看一遍，因为你不敢直接信它。

【图：一个任务的八件事排成一排：Read the requirement · Find the code · Write the code · Run tests on DEV · Check the data · Check the pipeline · Update the ticket · Review every line。只有 Write the code 标 AI（橙色），其余都标 You。图下一句：Copilot writes the code. Everything else is still yours.】

---

## 第 3 页 · 共鸣 · AI 在我们团队用不起来，有四个原因

1. **AI 只会写代码，剩下的活还是我的。** 跑测试、查数据、看 pipeline 的报错、更新工单、查 incident，这些占了一个任务大半的时间，AI 一样都碰不到。
2. **它不懂我们的系统，教它比自己干还慢。** 每开一个新 chat，代码流、程序入口、表之间的关系、有哪些坑，都要写进 prompt 从头讲一遍。“我知道直接改哪里，它还要我教。等我把 prompt 写完，活我自己早干完了。”
3. **不敢放手。** 它会不会 push、删表、连错环境？它说“全部测试通过”，你一跑，全是红的。它道个歉：“对不起，是我的疏忽。” 你能怎么办？下次还得自己盯着。
4. **老板问不出答案。** “我们用 Copilot 到底省了多少时间？一个任务花了多少钱？卡在哪里？” 没人答得上来。值不值得在团队里推广，只能凭感觉。

每一条都不大，但每一条都在折损团队用 AI 的信心。最后大家退回舒适区：代码自己写，AI 当一个会思考的 Google。心里还有一个说不出口的担心：要是全交给 AI，那人干什么？

**AI 依旧是一个聊天机器人。**

---

## 第 4 页 · 结论 · 缺的是两种能力

这几个月下来，我的结论是：团队用 AI 没信心，是因为缺了两种能力。

先分清 chat 和 agent。chat 只会回答你，读文件、跑命令、改工单都得你自己来。agent 会自己动手：读文件、跑命令、用工具，一步一步把活往下做。Copilot 的 agent mode 就是一个 agent。但光把 chat 换成 agent 还不够，还缺两种能力：

- **纵向能力：agent 能干多少活、懂多少。** 它懂我们的系统，读得懂需求；能读、能更新 Azure DevOps 上的工单，能看 pipeline 的报错；能去 DEV 和 IST 跑测试、查数据；出了问题，能查出原因。它解决第 1、2 条。
- **横向能力：agent 用起来有多放心、多省事。** 开一个任务不用写长 prompt；它动手之前，你批准它的计划；它把代码写进代码库、写工单、改数据之前，都先等你批准；危险的操作由代码拦下；另一个 agent 检查它的活；每个任务的进度、时间和花费都看得见。它解决第 3、4 条，也省掉第 2 条里那段长 prompt。

【图：两条轴。竖轴 What it can do and knows，横轴 How safe and easy it is to use。左下：Chat: answers you; you do the rest。左上：Agent alone: does more by itself, but you watch every step。右上（橙色）：Agent + harness: takes the whole task, and you can trust it。】

---

## 第 5 页 · 根因 · 这两种能力都不在模型里

很多人的第一反应是模型不够聪明：换 Opus，把 thinking 开到最高。账单涨了，问题还在。

因为这两种能力都不在模型里，而在模型外面那一层：agent 能连到哪些系统、能读到哪些资料，谁来管它、谁来查它。业界把这一层叫 harness，有一个说法：**Agent = Model + Harness**。

那人干什么？人不再每一步都亲手做，而是做只有人能做的决定：定目标，回答它的问题，批准计划，批准结果。

【图：三个框排成一个等式。Model（thinks and writes; Opus, Sonnet, GPT…）+ Harness（Vertical: what the agent can reach and know · Horizontal: what keeps it safe and easy to use）= An agent you can hand a whole task to。图下一句：A bigger model changes only the first box. The bill goes up; the problems stay.】

---

## 第 6 页 · 解决方案 · 我的 harness 把这两种能力加进 Copilot

我做了一套 harness，装在 GitHub Copilot 外面。它是一个文件夹，放在你自己的电脑上：从 `Harness/` 解压，照安装指南装一次，在 VS Code 里打开它，之后 Copilot 就按它的规则干活。里面有两样东西：写给 Copilot 的规则（Copilot 打开一个文件夹时，本来就会读这类文件）；一组小程序，在 agent 每一步的前后自动运行，检查它、记录它（这也是 Copilot 本来就支持的）。只需要 Python，不需要服务器。模型还是那个模型，变的是 agent 能干的活、懂的东西，和管它、查它的那一层。

后面每页都会用到两个词：
- **task**：在 harness 里，一件活就是一个 task。它是一个文件夹，需求、计划、进度和结果都存成文件，不在聊天记录里。
- **board（看板）**：harness 在你自己电脑上、在浏览器里打开的一个页面。你在上面开 task、做批准、看每个 task 走到了哪一步。

【图：harness 是什么。上：You →（start tasks · approve）→ The board: a page in your browser。中间橙框：Harness: a folder on your computer，里面三格：Rules Copilot reads · Checks before and after every step · One folder per task。下：Copilot agent in VS Code →（reads and writes, through the checks）→ Azure DevOps · DEV and IST · your code。图下一句：No server. It needs only Python.】

---

## 第 7 页 · 解决方案 · 每个原因对上哪个功能

下面这张图把四个原因对上 harness 的功能。后面每页讲一个功能，截图是 harness 的真实界面，数据是测试用的。

【图：对照图，三列：The problem → The ability → In my harness
- 1. AI only writes code → Vertical → It reads and updates tickets · It finds why a pipeline failed · It runs tests on DEV and IST
- 2. It does not know our systems → Vertical → It learns our systems once and keeps what it learned
  　　　　　　　　　　　　　　 → Horizontal → You start a task from a short form, not a long prompt
- 3. I do not dare to let go → Horizontal → You approve the plan and the result · You approve every write to a ticket or a database · Code blocks dangerous actions · A second agent checks the work
- 4. The boss gets no answers → Horizontal → One page shows every task · Reports show where the time and money went】

---

## 第 8 页 · 纵向 · 懂我们的系统，读得懂需求

- **解决什么**：agent 不懂我们的系统，每开一个新 chat 都要重新讲一遍；读需求只能照字面理解，需求里的坑要等代码写完才发现。
- **怎么做到**：agent 把一块业务（比如订单、退货）学一次，存进知识库：每个对象（一张表、一个存储过程……）一张小卡片，写它是干什么的、有什么规则、用到了谁、坑在哪里。程序先从代码里算出结构（有哪些对象、谁调用谁），模型再写每个对象的意思。读需求时，它拿需求对着知识库查一遍，把说不清、对不上的地方列出来问你。业务给的 Word、Excel 也能读：程序先把它们转成文本，不花 token。
- **关键性质**：学一块业务本身就是一个 task：你先批准它要学哪些对象，它再一批一批写卡。卡上写的调用关系，要和程序从代码里算出来的一致，对不上就写不进去；代码里看不出来的，它列出来等人补。每张卡都记着它是从哪个版本的代码读来的，代码改了，过期的卡能列出来重新学。
- **你能拿它做什么**：新人、新 chat、新 agent 都从同一份知识开始，不用你再讲一遍；需求里的问题在写代码之前就列出来，你直接拿去问 business。

【截图：知识库总览，裁到数字和业务列表：5 块业务（界面上叫 Domains）、305 张卡、5 张过期】

---

## 第 9 页 · 纵向 · 读写 Azure DevOps 的工单，看 pipeline

- **解决什么**：工单和 pipeline 都在 Azure DevOps 上，agent 碰不到。读工单、贴结果、看 pipeline，还得你自己去。
- **怎么做到**：harness 自带一个连 Azure DevOps 的程序，agent 直接调用，不用自己拼命令。它能读工单、评论和历史，看 pipeline 的运行、日志和测试结果；能加评论、改字段、建工单、把工单关联起来。连接和登录在 board 上设一次，每个系统一行：连没连上、用哪个身份登录、上次检查是什么时候。
- **关键性质**：不能删除；只有关联到这个 task 的工单才写得进去；每次写都先等你批准（第 14 页）。很多公司为了安全关掉了 Copilot 的插件（MCP）。这个程序不是插件，是 agent 在终端里运行的一个普通命令，而终端 Copilot 本来就能用，所以公司电脑上也能用。
- **你能拿它做什么**：开 task 时关联工单，agent 自己去读需求，做完自己把结果写回工单。

【截图：board 上的连接和登录，裁到表格：ado 一行是绿的】

---

## 第 10 页 · 纵向 · pipeline 挂了，它自己查出原因

- **解决什么**：pipeline 挂了、出了 incident，人要自己翻日志、对 commit，一查就是半天。
- **怎么做到**：agent 自己读 pipeline 的运行记录、日志和这次的 commit，把结论写成一份 RCA，分五段：看到了什么；证据，每一条都指向跑出它的那条命令；原因；怎么验证的；下一步。
- **关键性质**：查原因的 task 只读，不改任何东西；每条证据都能照着那条命令再跑一遍，不是 agent 一句“我觉得”。
- **你能拿它做什么**：把 RCA 发给同事，或者附到工单上；再从它开一个修复的 task，结论和材料一起带过去。

【截图：RCA 页。截图下一句：测试 task，连的是一个模拟的 Azure DevOps】

---

## 第 11 页 · 纵向 · 在 DEV 和 IST 上跑测试、查数据

- **解决什么**：代码写完，测试还得你自己登 server 跑，数据还得你自己查、自己对。
- **怎么做到**：agent 在终端里用 sqlcmd 连到 DEV 和 IST 的数据库，跑测试、查数据，每条命令和返回的结果都记在 task 里。
- **关键性质**：只读的查询直接跑。改数据的语句先等你批准这一条；你也可以在那张等你批准的卡上按一下，给这个 task 打开 DEV 或 IST，之后它在这里改数据就不用每次问你。QAT 默认打不开。PROD 永远只读，谁也不能为 task 打开它的写。
- **你能拿它做什么**：让 agent 自己跑完测试、核对完数据，再把结果交给你看。

【图（真实截图到公司电脑上再补）：四个环境排成一排。DEV、IST：Reads run · Changes wait for your approval, or run after you open it for this task。QAT：Not opened by default。PROD：Read only. Never opened for changes。】

---

## 第 12 页 · 横向 · 不用写长 prompt：填一张表开 task

- **解决什么**：开一个任务，要写一大段 prompt 交代背景、规则和步骤，比自己干还慢。
- **怎么做到**：新 task 从 board 上的一张表开始：名字、task 的种类、用哪个知识库、关联哪些工单、要做什么、用哪个模型、想得多深。board 替你写好第一条消息，发给 agent。
- **关键性质**：流程和规则在 harness 里，不在你的 prompt 里。task 的种类决定流程有多重：问个问题很轻，开发最完整。随时开一个新 chat，task 都从上次停下的地方接着做，因为需求、计划和进度都在 task 的文件夹里。
- **你能拿它做什么**：只填只有你知道的东西，几句话开一个 task。

【截图：New task 表单】

---

## 第 13 页 · 横向 · 你批准计划，也批准结果

- **解决什么**：AI 一上来就改代码，改了哪里你事后才知道；改动进代码库之前，也没人把关。
- **怎么做到**：agent 只能写自己的 task 文件夹。你批准计划之前，它连 task 里放代码的文件夹都写不进去（界面上叫 DEV/，和 DEV 环境无关）。代码先写在 task 里；做完以后，要写进代码库之前，你再批准一次。
- **关键性质**：批准在 board 上按，再输入它给出的一个短码；这个码只对这份计划有效，计划改了，就要重新批准。agent 自己做不了。写进代码库时，它新建一个 branch，把改动写进去，但不 commit，也不 push：你看过以后自己 commit、push。
- **你能拿它做什么**：动手之前看清它要改什么，写进去之前看清它改了什么。

【截图：计划等你批准】

---

## 第 14 页 · 横向 · 写工单、改数据之前，先等你批准

- **解决什么**：敢让 agent 读工单，不敢让它写：怕它写错工单、写错内容；改数据就更不敢了。
- **怎么做到**：agent 每一次往外部系统写东西（加评论、改字段、改数据），都先被拦下来，变成 board 上的一张卡：写到哪里、做什么、要写进去的原文。
- **关键性质**：你输入卡上的码，按 Approve。这次批准只管这一条命令，10 分钟内有效。批准以后 agent 再执行一次同一条命令，这一次才放行、真正写进去；agent 要是没在等，卡上有个按钮通知它。agent 自己批准不了。卡上还有一个按钮，可以给这个 task 打开它关联的工单；之后 agent 写这些工单就不再每次问你。
- **你能拿它做什么**：放心让 agent 写工单，最后一步由你来按。

【截图：等你批准的卡，和批准后的绿卡】

---

## 第 15 页 · 横向 · 围栏（Guardrails）

- **解决什么**：怕它 push、reset、删文件、改错仓库，甚至改掉管它的规则。在 prompt 里写“不要”拦不住。
- **怎么做到**：agent 每一次动手（改文件、跑命令），执行之前都先过同一个检查程序（界面上叫 gate）。危险的 git 命令、直接改目标代码库、改这个检查程序自己的规则、计划批准前写代码，都被它拒绝，并写明原因。
- **关键性质**：拦它的是代码，不是 prompt 里的一句话。每一次拦截都有记录，算进报告。
- **你能拿它做什么**：放心让 agent 多干活，不用担心它越界。

【截图：5 次被拒的操作，每次都有原因，裁到列表】

---

## 第 16 页 · 横向 · 独立检查（Independent review）

- **解决什么**：agent 检查自己的活，总给自己打高分：“全部测试通过”，一跑全红。
- **怎么做到**：做完的活交给另一个 agent 检查。它没看过写代码的那个 agent 是怎么想的，只看需求、结果和改动；它不能改文件；每条意见都要指到文件和行，第一行写 PASS 或 FAIL。
- **关键性质**：检查要连续通过几次，你在 task 页上选（关，或者 1 到 5），只有你能打开。比如选 2：要连着两次 PASS 才算过，中间一次 FAIL，agent 改完重新查。每次都是一个新的检查者；通过几次由代码数，不是 agent 自己报。每多查一轮多一份花费，board 会提醒你。
- **你能拿它做什么**：把“它说做完了”，变成“另一个 agent 按需求查过了”。

【截图：检查结果，裁到一次 PASS 和一次 FAIL（FAIL 指到文件和行）】

---

## 第 17 页 · 横向 · 看板（The board）：所有 task 一眼看清

- **解决什么**：开了好几个 chat、好几个任务，不知道哪个在干活、哪个在等你、等了多久。
- **怎么做到**：所有没关闭的 task 都在 board 上：在干什么、在等你什么、等了多久。agent 一停下来，harness 就记下“在等你”，不用你一个 chat 一个 chat 地去翻。
- **关键性质**：board 上的状态来自 harness 自己的记录，不是 agent 说的。
- **你能拿它做什么**：每天打开 board，先处理等你的那几件；一个按钮就能在新 chat 里接着做。

【截图：board 列表：4 个 task、谁在等你、等了多久】

---

## 第 18 页 · 横向 · 可审计（Auditability）

- **解决什么**：很多团队不知道一个复杂的 AI 任务，时间和钱到底花在了哪里。
- **怎么做到**：harness 读 Copilot 自己存的对话记录和 harness 的日志，算出每一段花的时间、用掉的 token 和 Copilot 的用量（界面上叫 Credits）、agent 做了多少次操作、被拦下几次、独立检查的结果。
- **关键性质**：报告全部由程序算出来，不是 agent 写的总结；看报告不花 token。
- **你能拿它做什么**：每份报告都能存成一个 HTML 文件，分享给团队，或者拿去向 leader 汇报。
- **再往下**：还有两个复盘，见下一页。

【截图：任务分析页，裁到 Key points 和 Where the time went】

---

## 第 19 页 · 横向 · 可审计：两个复盘

- **背后还有什么**：两个复盘，都只有你能启动：在 Copilot chat 里输入命令，或者在 board 上按对应的按钮。
  - `/harness-task-report` 读报告里的数字，说出时间和用量花在哪里、为什么。
  - Agent Performance Review（`/harness-agent-performance-review`）读得更深：agent 的每一次操作、被拦下时检查程序说了什么、每一步之前它在想什么。程序先标出像是绕了远路的地方，agent 再逐个拿证据判断原因：harness 的限制、agent 自己的错、环境的问题、缺了知识，还是围栏在正常拦截；最后指出该改哪个文件。
  - 它单独开一个 task，只读，不改被复盘的那个 task；它要读完整份记录，所以比平常问一个问题花得多。
  - 原因在 harness 自己，就交给维护 harness 的人（现在是我）去改。这样 harness 改在真正出问题的地方，有证据。

【图：两个复盘。上：One task’s records: every action, what the gate said, the thinking before each step。左：/harness-task-report — reads the numbers, and says where the time and usage went, and why。右（橙框）：Agent Performance Review — 1. A program marks spots that look like detours. 2. An agent judges each one with evidence: harness limit · agent mistake · environment · missing knowledge · guardrails working. 3. It names the file to change。图下：Only you can start either one. Neither changes the task it reviews. A cause in the harness goes to the person who maintains it.】

---

## 第 20 页 · 下一步 · 看完以后：去哪里，找谁

这份文档在 OneDrive 的 AI Exploration 文件夹里。看完以后，按你想做的事走：

- **想自己试一试**：去 `Harness/`。安装包、我们团队的知识库、要装的程序（比如 Python）、安装和使用教程都在里面。
- **想先看我演示**：找我（Smars Hu）约一次 demo，用一个真实的任务从头走到尾。
- **想在团队里试点**（lead、manager）：找我一起挑几个真实的 intake，交给 harness 从头做到尾，用报告看省了多少时间、花了多少钱。
- **想先多了解一点**：去 `Harness Engineering 101/` 读 Basic；去 `Showcase/Real Tasks/` 看真实 task 花了多少时间、多少钱、哪里被拦下；`Showcase/Lessons/` 是我一路踩过的坑。

【图：目录树，每个文件夹旁一句它是什么：Start Here (you are here) · Harness Engineering 101/ — short courses: Basic, Advanced, Mindset · Showcase/ — Real Tasks: real task pages, each with a one-page note; Lessons: wrong turns I took · Harness/ — install package, our knowledge base, the programs it needs, and the guides】

---

## 核对清单

| 说法 | 依据 |
|---|---|
| 知识库：每个对象一张卡、记代码版本、过期可列、重新学 | `docs/02-features.md` 第 194–197 行；`kb-overview.png` |
| 学一块业务是一个 task，你批准一次计划，一批一批写卡；卡上的关系对不上程序算出的就被拒；代码看不出的写进 requests 等人补 | `docs/02-features.md` 第 196 行（`kb cardcheck`、`requests.md`） |
| harness 是本地一个文件夹，装好后在 VS Code 里打开；Copilot 读它的规则文件（AGENTS.md、instructions）；每一步前后的小程序是 Copilot 的 hooks；只要 Python 3.9+（标准库），不需要服务器 | `AGENTS.md`；`.harness/INDEX.md`；`docs/01-quickstart.md` 第 9–10 行 |
| 需求对着知识库查、列出不清楚的地方；Word、Excel 由程序转成文本，不花 token | `docs/02-features.md` 第 30 行（`generic-req-review`、`task intake convert`） |
| 连 Azure DevOps 的程序：读工单、评论、历史、pipeline 运行和日志、测试；写评论、改字段、建工单、关联；不能删除；没关联的工单写不进；写等批准 | `.harness/toolpacks/ado/README.md`（0.4.13） |
| 走终端，公司关了 MCP 也能用 | `docs/13-tool-packs-and-mcp.md` |
| board 上的连接和登录：状态、身份、上次检查 | 截图 `img/reach.png`（v1.7.38） |
| RCA 五段；查原因的 task 只读；从 RCA 开修复 task，带走结论和材料 | 截图 `img/rca.png`；`docs/02-features.md` 第 28 行 |
| sqlcmd 连 DEV、IST；读直接跑；写等批准这一条，或为 task 打开连接后不再每次问；QAT 默认打不开；PROD 只读、永远打不开 | `docs/12-guardrails-and-gate.md` 第 40–55 行（写等批准；打开连接；sample 类型开 DEV、IST 不开 QAT；prod 只读、never opened） |
| New task 表单字段；board 写第一条消息；task 种类定流程轻重；新 chat 接着做 | 截图 `img/new-task.png`；`docs/02-features.md` tier 表 |
| 只能写 task 文件夹；计划批准前写不进放代码的地方；批准码绑定计划；写进代码库：新建 branch（`feature/<task>`），写入改动，不 commit | `docs/02-features.md` 第 33、45、69、76 行 |
| 检查要连续通过 n 次；每次一个新的检查者 | `docs/02-features.md` 第 93–95 行 |
| 在等批准的卡上按 Open，给 task 打开 DEV、IST（要码） | `docs/12-guardrails-and-gate.md` 第 52–56 行 |
| 批准只能人在 board 上按，agent 按不了 | Basic 06 已核对（`approve-plan.png`，配对的浏览器） |
| 外部写被拦成卡；输码批准；只管这一条、10 分钟；卡上 Open linked items 为 task 打开关联工单，之后写它们不再问（`docs/12-guardrails-and-gate.md` 第 55 行）；批准后 agent 再执行一次才写进去；没在等时卡上按钮通知它 | `docs/03-configure.md` 第 292 行；`docs/07-release-notes.md` 第 546 行；截图 `img/held-write*.png` |
| 检查程序管每一次动手；5 种被拒 | Basic 06 已核对（`refusals.png`） |
| 另一个 agent 检查：不能改文件、指到文件和行、PASS/FAIL；次数只有人能开；代码数次数；花费提醒 | `AGENTS.md`；`docs/02-features.md` 第 93 行；`img/new-task-2.png` |
| board 列出没关闭的 task、等你什么、等了多久；agent 停下 harness 记“在等你” | `docs/02-features.md` 第 34 行；`img/board-list.png` |
| 规则太紧这类原因交给维护 harness 的人 | `references/reasons.md`（“tell whoever maintains it”） |
| 报告读 Copilot 的记录和 harness 日志；程序算出；看报告不花 token；存 HTML | `docs/02-features.md` 第 83–84 行 |
| `/harness-task-report` 从数字找弯路：被拦后换路、反复试、对话太长被压缩（规则可能丢）；原因指向工具、规则、资料；规则太紧告诉维护的人 | `.github/skills/harness-task-report/SKILL.md`；`references/reasons.md` |
| Agent Performance Review：单独开一个 rca task，只读，不改被复盘的 task；花费高（board-cost: high）；只有人能启动；读每次调用、gate 的回答、每次调用前的思考；代码标出候选，agent 按证据判断（harness 限制、agent 错误、环境、知识缺口、围栏生效）；建议点名要改的文件 | `.github/skills/harness-agent-performance-review/SKILL.md` |

## 英文时要先定的词

- “用不起来”：use AI in real work，不用 land、take hold。
- “纵向能力 / 横向能力”：Vertical ability / Horizontal ability（你定的名字）。
- “系统”：our systems（不用 our domain；知识库页讲清界面上的 Domains 是一块业务）。
- “围栏”：Guardrails。“检查程序”：a check program（the gate）。“写进代码库”：write the change into the repository（不用 promote、write-back）。
- task、board、knowledge base 第一次出现时讲清，后面一直用同一个词。
- 环境：测试在 DEV 和 IST；QAT 是用户测的；PROD 只有 incident 才看。

## 标题清单

AI Exploration：从这里开始 · 今天我们怎么把一个任务交给 AI · AI 在我们团队用不起来，有四个原因 · 缺的是两种能力 · 这两种能力都不在模型里 · 我的 harness 把这两种能力加进 Copilot · 每个原因对上哪个功能 · 懂我们的系统，读得懂需求 · 读写 Azure DevOps 的工单，看 pipeline · pipeline 挂了，它自己查出原因 · 在 DEV 和 IST 上跑测试、查数据 · 不用写长 prompt：填一张表开 task · 你批准计划，也批准结果 · 写工单、改数据之前，先等你批准 · 围栏（Guardrails） · 独立检查（Independent review） · 看板（The board）：所有 task 一眼看清 · 可审计（Auditability） · 可审计：两个复盘 · 看完以后：去哪里，找谁
