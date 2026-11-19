# 视频生成工作流 · Harness 教程

一支教程视频从想法到成片的全过程。**人**负责想清楚、写、听、拍板；**AI** 负责改写、检查、配画面、出声音、合成；**代码**负责可重复的部分，不花钱，改一处只重做一处。

所有命令在 `ai-exploration` 根目录运行；`<video>` 是课程文件夹名，例如 `basic-01`。

---

## 一图看全流程

```
 ① 提纲      人 + AI brainstorm                  outline.md
 ② 中文稿    人写                                zh.md
 ③ 英文稿    AI：直译 → 母语口语化 → 对照中文    en.md
 ④ 你的风格  AI：按“说话风格规则”改写，加停顿   scenes-author.md
 ⑤ 分镜      AI 出分镜 → 人批 → AI 画图           storyboard.md · figs/
 ⑥ 声音      Qwen3 合成（默认）  或  人自己录    audio/
 ⑦ 成片      一条命令：画面 + 声音 + 字幕 + 头像  rough.mp4 · fcpxml · srt
 ⑧ 收尾      人在 Final Cut Pro 里看、微调、导出
```

---

## ① 提纲 · 人 + AI

- 人先说要讲什么；AI 按“痛点 → harness 管的事 → 真实场景”的结构挑战一轮，指出逻辑不通、少了一步的地方。
- 不纠结小细节（年份、措辞）；只改会改变观众理解的地方。
- 产出：`source/courses/<video>/outline.md`

## ② 中文稿 · 人写

- 写法：像跟同事讲话，一段一个意思；〔画面：…〕写给自己看，不念。
- 用写稿台改：在 Claude Code 里输入 `/script-desk`，左边 AI 初稿、右边你的稿，自动保存、按段估时长、长句标黄。
- 产出：`zh.md`

## ③ 英文稿 · AI，四步，每步换一个 agent

| 步 | 谁 | 做什么 |
| --- | --- | --- |
| 直译 | agent A | 只看中文，完整、准确，不加修饰 |
| 口语化 | agent B（母语者的耳朵） | 改成同事间聊天的说法；词准确、常用；语法不重要 |
| 对照中文 | agent C | 逐段逐句查：**意思**、**逻辑**（因果/转折/并列）、**断句**、**指代**（these 指什么？“下面这几件事”还在不在） |
| 脚本检查 | 代码 | `python3 source/video/lint_script.py <video>`：一个意思被拆两句、孤立短句、没分段、问句不像问句、光秃秃的 these |

- 每步的改动都列成清单（原句 → 新句，为什么），人只看清单。
- 产出：`en.md`

## ④ 你的风格 · AI

- 依据：`style/author-style.md`——从你自己录的模块量出来的说话习惯：每 100 词约 5 次 “And”、2 次 “So”、每段一次 “right?”；“number one is,” 式的列举；关键词前停 0.3 秒；语速 175 词/分。
- 把英文稿按这些规则改写：语气词写进去，停顿写成 `[.3]`（秒），句末和段末不加。
- 你每多录一个模块，就重新量一次，规则越来越准。
- 产出：`scenes-author.md`（带画面的最终讲稿）

## ⑤ 分镜与画面 · AI 出，人批

1. AI 写分镜表 `storyboard.md`：每句配什么画面、哪张图要画、每张图分几步亮起。
2. 人批分镜。
3. AI 画图：`figs/<name>.html`，深灰底、Source Serif 4、青绿 = 正在说的、橙红 = 出问题的；一句推进一步。
4. 真实画面：harness 看板截图（`source/video/catalog.md` 里的 `board/...`）；缺的用演示工作区补拍（`source/demo/`）。
5. 官方 Logo 放在本地素材夹；**画面不留空缺**，找不到就找替代品。
- 检查画面：`.venv/bin/python source/video/build.py <video> --scenes source/courses/<video>/scenes-author.md --frames-only`

## ⑥ 声音 · 两条路

**A. Qwen3 合成（默认，接近真人）**
- 模型：Qwen3-TTS 1.7B；参考音频：从你真实讲话里截的 10–15 秒（`talk-a`）。
- 稿子写成你的风格（第 ④ 步）是关键：模型负责音色，稿子负责“像你在讲”。
- 停顿用房间底噪填，不留纯静音；每段声音的头尾加淡入淡出。
- 音量统一到 −18 LUFS。

**B. 你自己录**
1. `/script-desk rec`：一屏一个模块，关键短语加粗，①② 标出换图的地方；R 录、S 停、P 听；数字键选一段单独补录。
2. 录完自动检查：每个要点讲到没有、顺序对不对。
3. 修音预览：`build.py <video> --polish-preview <sid>` → 降噪、剪 um/uh/结巴/重说、缩长停顿、统一音量。
4. AI 剪辑：`--edit-draft <sid>` → agent 读原话，整句重讲取最好的一遍、剪口误、恢复剪过头的；每一刀列清单，可撤回。
5. 字幕校对：`--subs-draft <sid>` → agent 按原意改听错的词（read → write、Cloud → Claude）。
6. 人听修好的音频，点头。

## ⑦ 成片 · 一条命令

```
.venv/bin/python source/video/build.py <video> --scenes source/courses/<video>/scenes-author.md
```
（自己录的加 `--voice rec`）

自动完成：
- 声音按段合成，按词对齐；画面在对应的词前 0.3 秒淡入，讲完停一下再换。
- 交叉淡入淡出；同一张图逐步亮起。
- 字幕（`.srt` + 烧进画面 + FCP 字幕轨），去掉语气词。
- 右下角头像，随声音呼吸、说话时有涟漪。
- 输出：`.claude/loops/video-out/<video>/`：`<video>-rough.mp4`（预览）、`<video>.fcpxml`（FCP 工程）、`<video>.en.srt`。
- 改一句话或一张图：同一条命令，只重做那一处。
- 某一句合成得不满意（或报 `never passed`）：加 `--redo "<那句里的几个词>"` 或 `--redo <行号>`，重说 3 遍（`--takes N`），每遍都过检查，旧的不删；最好的一遍自动进时间线。

## ⑧ 收尾 · 人

- 在 Final Cut Pro 里打开 `.fcpxml`：画面、每段声音、字幕、头像各在自己的轨道上，可单独调。
- 微调转场、个别停顿，导出。
- 不喜欢的那句：`--redo` 之后到 `redo/` 里听每一遍（`redo/README.md` 列出行号、检查结果、哪一遍在时间线上）；用 `--keep-take <行号>:<第几遍>` 选定再跑一次（记在稿子旁的 `takes*.json`，以后都用它），或直接把那遍的 wav 拖进 FCP 盖住原来的。
- 反馈给 AI：说“第几分钟”或“哪一句”，AI 只改那一处。

---

## 规矩

- **不花钱**：全部开源、本地跑；声音模型、降噪、对齐都在本机。
- **隐私**：你的声音、照片、录音、生成的音频视频都不进 git；截图里不出现你的名字和本机路径。
- **一次一个改动可追溯**：每一步的产物都在 git 里，改动有清单。
- **不满意的模型就删**：试过的 Chatterbox、F5、VoxCPM2、Kokoro+Seed-VC、VibeVoice、GPT-SoVITS 都已删除，记录在 `source/video/tts/README.md`。
