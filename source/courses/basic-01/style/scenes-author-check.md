# scenes-author.md · check against zh.md

Read paragraph by paragraph against zh.md for meaning, logic (because / but / so), sentence breaks and referents (logic-brief step-3 rules). Fixes made:

| Scene | 中文 | What was wrong | Before → after |
| --- | --- | --- | --- |
| 0 Hook, the prompt paragraph | 先……；再写一大段解释……；然后……；最后…… | logic: the sequence step 再 was lost when "And then" (a lint split-thought) became "And," | "And, you have to write this long explanation…" → "And after that, you have to write this long explanation…" |
| 1 Pain points, two | 新开一个对话框，前面讲过的全都没了，你得从头再说一遍 | grammar: "if you open a new chat, and everything you told it is gone, and you have to…" has no main clause | "Like, if you open a new chat, and everything you told it is gone," → "Like, if you open a new chat, everything you told it is gone," |
| 4 Harness, the formula | 有一个公式：Agent = Model + Harness。模型之外的那些东西，都是 harness | logic: "so" made the definition sound like a consequence of the formula | "so everything outside the model, that's the harness." → "and everything outside the model, that's the harness." |
| 5 My harness, two Copilots | 大概率同时在用两个 Copilot | meaning: "I know you are most likely" says certain and likely at once | "I know you are most likely using…" → "I guess you are most likely using…" |
| 5 My harness, reviewer | 引入独立的 reviewer 作为 subagent | meaning: the added consequence "the main agent is not the one checking its own work" says more than the Chinese (the main agent may still check itself) | "so the main agent is not the one checking its own work anymore." → "so it's not just the main agent checking its own work anymore." |

Checked and left as they are:
- 0 Hook: "because the AI cannot understand our complex system… the traps I already know about" stays inside the quoted thought ("you feel, like, oh, …"), as 最后你觉得…… covers both clauses.
- 3 Agent: 但光有手还不够 is said "And the thing is, having hands is still not enough": "still" carries the contrast without a "But" after a full stop.
- 4 Harness: the nine gaps keep the Chinese order; signposts "number one is", "number two is", "the third thing is", "another thing is", "the last one is". "these problems" is named and the list is on screen.
- 5 My harness: the five list items are numbered as on screen ("number one" to "the last one"), and gap three keeps both halves (tests and pipelines, then server access), as the Chinese bullet does.
- Modules 1 and 2 are the approved examples. The only change is the grammar fix in pain point two above.

Lint flags kept (4): "follow them" (bare-referent, the dos and don'ts just named, as noted in the example); "But the problem is," (split-thought, the author's turn, as noted in the example); "So, the fixed, predictable stuff…" and "So, even if one session dies…" (split-thought on "So", intended by the style).
