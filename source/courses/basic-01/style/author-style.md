# 作者的说话风格 (author's speaking style)

Measured on the two modules the author talked through and approved: "0 Hook" (scene `4a4aac372946`) and "1 Your pain points" (`c4a7fea25f36`). "Script" is what they talked from (`scenes.md`); "spoken" is what stays after the automatic polish, the editorial cuts (`edit/<sid>.json`) and the subtitle proofread (`subs-fix/<sid>.json`): the version the author approved. Um and uh are not counted; they are cut anyway.

How it was measured: the kept words come from the edit drafts (`build.py basic-01 --edit-draft <sid>`, every word with its cuts); pauses and rate from the polished audio (`preview/<sid>-polished.mp3`), with mlx-whisper word times on that audio (large-v3-turbo) and the silences found from loudness (10 ms frames more than 28 dB under the voice's 95th percentile; a run of at least 0.1 s, blips under 50 ms bridged). Each silence is given to the nearest word boundary, so a pause can sit one word off; the totals and medians are sound, single cases less so. The polish shortens a pause over 0.8 s to 0.4 s and keeps up to 0.35 s around a cut filler, so the pause numbers are what the approved audio sounds like, not the raw take.

Data: 752 spoken words in 258 s of polished audio (Hook 440 words, 151 s; pain points 312 words, 107 s), from 571 script words.

## 1 口头标记 (fillers and discourse markers kept)

Per 100 spoken words; the script's own rate in brackets.

| Marker | Per 100 words | Where |
| --- | --- | --- |
| **And** opening a clause | **4.9** (3.0) | after a comma, chaining the next point onto the last: "…from scratch, and another thing is, …". Half of them carry a comma of their own: "And, the third thing is," |
| **So** opening a clause | **1.6** (0.5) | first word of a paragraph or a turn: "So, number one is," "So, every single time," "right, so, what do you do?" |
| But opening a clause | 0.9 (0.7) | as in the script |
| **right** as a tag | **0.8** (0) | 6 times in 11 paragraphs, always at the end of a consequence, once a paragraph at most: "…80 or 90 percent happy with, right," "…the worse performance it gets, right?" |
| like (hedge, not comparison) | 0.7 (0.2) | before a number ("like, 80 or 90 percent"), before an example or a list ("like, which code files", "like… if you open a new chat"), before quoted thought ("you feel, like, oh, AI is not reliable") |
| numbering phrase | 0.8 (0) | every numbered point: "number one is," "number two is," "the third thing is," "number four is," "the last one is," "another thing is," |
| I know / I guess / as I said | 0.4 (0) | stance at a clause start: "and I know a lot of companies…", "I guess, pretty much like that," "and as I said, the longer the chat is…" |
| that means / this is because | 0.3 (0) | to state a consequence or a reason as its own clause |
| sometimes | 0.4 (0) | softens a claim: "sometimes, it still has a lot of mistakes" |
| hey / oh / yeah | 0.1 each | hey opens quoted speech ("AI will say, hey, I have done all the work"), oh opens quoted thought, "Yeah, so," opens a paragraph |
| you know | 0.1 (0.2) | only where the script had it |

Not kept or rare: "well" (never), "I mean" (never), "basically" (never), "you know" beyond the script. The markers are plain and few; the style is in the chaining (And, So) and in the numbering, not in fillers.

## 2 停顿 (pauses in the polished audio)

All pauses of 0.1 s or more: **25 per 100 words** (one every 4 words), **median 0.21 s, IQR 0.13–0.32**. Of 0.2 s or more: 13 per 100 words (one every 7); of 0.3 s or more: 8 per 100 (one every 12); of 0.5 s or more: 3 per 100. Pause time is 19% of the audio.

| Place | Share of such places with a pause | Length of those pauses: median (IQR) |
| --- | --- | --- |
| paragraph end | 78% | 0.36 (0.32–0.39), the polish's 0.4 s cap shows |
| a dangling "and…" / "still…" | 57% | 0.38 (0.26–0.48) |
| after an opener: "So," "And," "But," | 50% | 0.27 (0.13–0.43) |
| inside a phrase, before the content word: "the ‖ different sessions", "a ‖ lot of errors", "after you ‖ complete a task" | 17% | 0.30 (0.16–0.44) |
| sentence end (. ? !) | 67% | 0.23 (0.18–0.30) |
| comma: between clauses or list items | 60% | 0.23 (0.16–0.33) |
| after the numbering phrase "number one is," | 50% | 0.19 (0.17–0.21) |
| inside a phrase, elsewhere | 13% | 0.17 (0.12–0.28) |

So: short pauses, many of them, and in odd places. The sentence end is not longer than a comma (both about 0.23 s), because the author does not end sentences so much as chain them. The longest regular pauses are the hesitations: before the word that carries the point (0.3) and after a trailing "and…" (0.4); many of them are where an um was cut, which the author heard and approved.

## 3 改写方式 (how the script becomes speech)

Words: spoken is **1.32 times** the script (Hook 1.20, pain points 1.53; "Four" 2.48, "Five" 1.90: the short scripted points grow most). Sentences: **21.5 words** from one full stop to the next, against 14.3 in the script; **19 commas per 100 words**, against 7.5. Rate: **175 words a minute** overall in both modules, **4.8 syllables a second** on voiced time (Hook 4.6, pain points 5.1), 1.26 syllables a word.

The rewrites, paragraph by paragraph, in kinds:

- **A number becomes a phrase.** "One: it doesn't know your project." → "So, number one is, it doesn't know your project." "Two:" → "And, number two is," "Three:" → "And, the third thing is," "Four:" → "And number four is," "Five:" → "And the last one is,". A second point inside one is "another thing is,": "And you'll notice" → "and another thing is, you'll probably notice that".
- **Sentences chained with ", and" and ", so".** The hook's paragraph 1 (8 script sentences) is said as one; "…there are still a lot of errors, and you have to spend a lot of time to review that and change that, right?".
- **A consequence or a reason added after the point, often closed by "right?"** "Then you look, and there are still tons of errors." → "…there are still a lot of errors, and you have to spend a lot of time to review that and change that, right?" "And it gets worse the longer the chat goes: the more history…" → "And it gets worse, and as I said, the longer the chat is, the worse performance it gets, right? This is because the more history there is…".
- **Restatement.** The point is said, then said again in other words: "you have to find the code, paste the code, explain the code yourself"; "the longer the chat is… right? This is because…"; in the hook the author pulls module 2's "same old lines" forward: "you feel, like, oh, AI is not reliable, AI still makes mistakes, AI only helped me do a tiny slice of work".
- **Quoted speech and thought, introduced with "say, hey," / "feel, like, oh,".** "\"Done, all tests pass.\"" → "sometimes AI will say, hey, I have done all the work, everything is completed and it looks good".
- **Imperatives become situations.** "Open a new chat, and…" → "like… if you open a new chat, and…"; "say you're a software engineer" → "let's say, you are a software engineer".
- **"You have to"** for what the listener must do (1.1 per 100 words, script 0.5): "first, you dig up the code files" → "the first, you have to find all the code files"; "you paste in the request" → "then you have to paste in the request".
- **"The AI"** with an article where the script has "it" or bare "AI" (0.7 against 0.35): "it forgets" → "the AI forgets", "Most of the time it listens" → "most of the time, the AI will listen".
- **A bridging question at the end of a section:** "So, what's the problem?" (hook, before the three things); "So, where'd the time and money go?" (pain point five, added).
- **Plain intensifiers:** "every single one", "a lot of" (for "tons of", "lots of"), "really hard", "so much experience".
- **Contractions half spelled out:** 2.7 contractions and 2.7 full forms per 100 words (script 4.4 and 0.7): "you have", "you are", "cannot", "is not".
- **What stays:** the order of the points and the key phrases ("a tiny slice of work", "find the code, paste the code, explain the code", "the more history there is, the more its attention drifts"); "But here's the thing" and "In this video I want to make three things clear" are said word for word.

## 4 语法习惯 (grammar habits)

What the subtitle proofread had to correct (`subs-fix/`): 50 changes in 258 s, 28 of them grammar (some only capitals or commas after a cut), 11 misheard words, 10 fragments, 1 name:

| Habit | Examples | Reproduce? |
| --- | --- | --- |
| "the AI" with an article; "behind the scene(s)" | "the AI forgets", "the AI will listen" | **Yes**: clear and it is the author's sound |
| Embedded question in question word order | "you know exactly, what's the best solution", "where is this way of using AI goes wrong" | **Lightly**: "you know exactly what's the best fix" reads fine; never with a second verb ("where is … goes") |
| To-infinitive for purpose or result | "spend a lot of time to review that" | **Yes**: clear |
| Full forms for contractions | "you have done", "you cannot see" | **Yes**, half of the time |
| Dropped plural -s | "a lot of team", "a lot of company", "which code file need", "different session" | **No**: the proofread put them back, so the approved subtitles do not have them, and a synthetic voice says them clearly, so they sound like mistakes, not like an accent |
| Missing or wrong verb, tense slip | "teams still using AI", "AI still mistake", "something you agree on earlier", "why it's made those changes", "the worse performance AI is get" | **No**: unclear |
| "to come" for "that comes"; "the first," for "first," | "a request to come from the business side" | **No** |

## 5 写作规则 (rules a writer can apply)

1. **Keep every point, in the script's order, and its key phrase.** Add, never drop: the spoken text runs about 1.3 times the script (short numbered points up to 2 times).
2. **Number points as phrases:** "So, number one is," "And number two is," "And the third thing is," "And the last one is,"; a second idea inside a point: "and another thing is,".
3. **Chain.** Join sentences with ", and" and ", so" until a sentence runs about 20 words (up to 40 in a list or story); start a clause with "And" about 5 times and "So" about 1.5 times per 100 words. Start a paragraph or a turn with "So," (or "Yeah, so," once in a module).
4. **After a point, add its consequence or reason as its own clause** ("and that means, …", "this is because …", "and you have to …"), and close the paragraph's main consequence with **", right?"**: about once a paragraph, never twice.
5. **Say it twice** where the point matters: the claim, then the same in other words or as an example.
6. **"like," (0.7 per 100 words)** only before a number, an example, a list or a quoted thought; never as a stall between ordinary words.
7. **Quoted speech** with "will say, hey," and quoted thought with "feel, like, oh,".
8. **Stance once or twice a module:** "I know", "I guess", "as I said", "sometimes".
9. **Plain words:** "you have to", "the AI", "a lot of", "every single", "really"; contractions spelled out about half the time ("you have", "is not", "cannot").
10. **Grammar:** keep it correct. Of the author's slips keep only "the AI", the question-order embedded question when it stays clear, and "spend time to …".
11. **No um, uh, I mean, well, basically.**
12. **Pause marks** (`[.3]`, seconds; the build tops the voice's own pause up to this, so a mark the voice already makes costs nothing). About 13 marks per 100 words, one every 7 or 8 words:
    - after an opener "So," "And," "But," (every other one): `[.3]`;
    - after "number one is," and "the thing is,": `[.2]`;
    - between list items and at clause commas (every other one): `[.2]`, `[.3]` before the last item or before a turn;
    - before the word that carries the point, inside the phrase, about once in 25 words: `[.3]` ("what people called [.3] Prompt Engineering", "there are still [.3] a lot of errors");
    - after a dangling "and…": `[.4]`;
    - none at sentence ends or paragraph ends: the voice makes 0.3 s at a sentence end (as the author's 0.23), and the timeline sets the time between paragraphs.
13. **Rate:** the author speaks 175 words a minute with pauses, 4.8 syllables a second when voiced. A voice slower than that sounds like reading; check the made clip's words per minute against 175.
