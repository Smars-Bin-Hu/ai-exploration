Checked all 81 Chinese sentences against en-v5 as a viewer who hears each one once: does every this / these / it / them point to something just said or on screen, and did the Chinese signposts (下面, 这几件事, 第一…, 这就是, 也就是, 还有) survive?
Changed 7: referent 6, signpost 1 (meaning 0, logic 0, break 0). Spoken words only; every `@` line, paragraph and line break is unchanged.

- 0 Hook · 然而在实践过程中，我们发现很多团队依然只是用AI完成它们日常工作中很小的一部分工作 · referent (right after "Claude Code, Codex or GitHub Copilot", "it" sounds like GitHub Copilot) · "many teams still use it for only a small slice of their work." → "many teams still use AI for only a small slice of their work."
- 1 Your pain points · 如果你这样用过 AI，下面这几件事你应该都碰到过。 · signpost (下面这几件事 was lost; "these" pointed at nothing yet said) · "you've probably hit every one of these." → "you've probably run into every one of the following problems."
- 1 Your pain points · 而且你会发现，同一个对话聊得越久，它的表现好像越差 · referent ("the worse it seems to get" sounds like the chat gets worse; 同一个对话 was lost, which is what sets this apart from opening a new chat) · "And the longer a chat goes on, the worse it seems to get:" → "And the longer you stay in the same chat, the worse the AI seems to do:"
- 4 What is a harness · 企业发现，Agent落地需要解决这些问题： · referent ("solve these" — these what?) · "they have to solve these." → "they have to solve these problems."
- 4 What is a harness · 它不知道你们的系统项目，每次还是需要人来介绍 · referent (just before it, "they" is the companies and "agents" is plural, so a lone "it" has nothing to land on) · "One: it doesn't know your systems…" → "One: the agent doesn't know your systems…"
- 5 My harness · 它不知道你们的系统项目，每次还是需要人来介绍 · referent (right after "how my harness handles each one", "it" sounds like the harness doesn't know your systems) · "First: it doesn't know your systems…" → "First: the agent doesn't know your systems…"
- 5 My harness · 还有很多别的，在这里由于时间问题，就不再一一列举。 · referent (a lot more what? 还有很多别的 is the last item of the problem list) · "There's a lot more, but no time to cover it all here." → "There are plenty of other problems too, but there's no time to go through them all here."

Kept on purpose:
- 1 · "…a list of dos and don'ts, and it doesn't always follow them." — lint flags "them", but it comes straight after "dos and don'ts".
- 2 · "Is this how you use AI right now?" — the Chinese has the same 这, and the screen shows the long prompt from the hook again.
- Lint flags that were already passed under items 1–3 and that these fixes don't touch: the split-thought flags at scenes-v6 lines 124, 163, 283 and 307, and the short-alone flag at line 26. Line 11 ("But what we actually see…") is touched, but its sentence break follows the Chinese 。然而, so it stays.
