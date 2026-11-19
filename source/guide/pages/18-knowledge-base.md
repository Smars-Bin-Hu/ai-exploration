---
title: Knowledge base
subject: Knowledge base
layer: concept
file: 18 Knowledge base
harness_tag: 1.8.3
course: The book · 8.1 A knowledge base: an honest index of the code | https://smarshu.com/book/read/8-1-why-a-knowledge-base.html
course: The book · 3.5 What an agent should remember | https://smarshu.com/book/read/3-5-memory.html
---
## Knowledge base: what it is and what problem it solves

The knowledge base is the team's own notebook about its code: Markdown and JSON files in a git repository of their own, which the agent is told to read before the code, because reading them costs less than reading the code and gives a better answer {src:.github/instructions/knowledgebase.instructions.md#L6-L8}. The harness carries none of the team's knowledge: it ships no knowledge base, and the team plugs its own in, as it plugs in skills and target repositories {src:AGENTS.md#L11-L15}. It is the folder `knowledge-base/` in the harness folder, or a repository registered with `knowledge_base: true` {src:.harness/engine/core/targets.py#L1-L10}. It answers two problems of large code stores: no agent can read all the code for every task, and what the code does not show (what runs where, why something failed) is lost when a chat ends {src:docs/08-knowledge-base.md#L11-L15}.

## Knowledge base: where it lives, next to the target repositories

A knowledge base that tasks may update is a target repository of its own kind, beside the code repositories in the target policy, by default `knowledge-base/` with its own `.git` {src:docs/03-configure.md#L124-L140}. Like every target repository, its working tree is closed to the agent's edit tools, and to a terminal command that names a path in it as a write target by its full path; a relative path such as `knowledge-base/domains/…` is not caught {src:.harness/engine/modules/gate/handler.py#L36-L52} {src:.harness/engine/modules/gate/policy.py#L149-L156}.

The board's **Get ready** form has a Knowledge base section: a package (a zip), a folder, or not yet. On Finish it puts the content into `knowledge-base/`, runs `target init-kb` (a git repository on its base branch, with a first commit), registers it as `kb` in the target override, copies the company content and runs `doctor` {src:.harness/engine/modules/task/setupjob.py#L88-L137}.

## Knowledge base: what a domain holds

A knowledge base is cut into domains, one folder each, in a fixed form, the knowledge base standard v1, so that scripts can check it and find what went stale {src:.harness/engine/core/kbstd.py#L1-L13}. Its entry is `README.md`, a table of the domains with the glossary. Per domain {src:.harness/contracts/kb/README.md#L1-L26}:

- `architecture.md`: purpose, flows, key data, where to start for each kind of task, traps, limits; at most 300 lines.
- `domain.yaml`: the commit of each repository it was learned at, entry points, boundaries, open questions; no object list.
- `objects/index.jsonl`: one line per object: id, source path, the git blob sha of the source when the card was written, the card as `file#section`, a level.
- `objects/<type>.md`: the cards, one `## <id>` section each, at most 120 lines (longer for a long object); each names the commit it was read at, and each rule cites its source lines.
- `environment.md` (facts of one environment, only from results a person gave), `requests.md` (what a person must still give), `discovery/` (inputs, not facts), `skills/` (the domain's skills).

Every fact has a level: `verified`, `supported`, `inferred`, `unknown` or `conflict`; a research note or an old document is `supported` at best {src:.github/instructions/knowledgebase.instructions.md#L23-L41}.

## Knowledge base: how the agent finds and reads it

The order of reading is an instruction: `copilot-instructions.md`, loaded with every prompt, points the agent at `knowledgebase.instructions.md` {src:.github/copilot-instructions.md#L6}. That file says: name the task's domain (`task set-domain`) or ask; read `architecture.md` and `domain.yaml` and stop when they answer; then find one object in `objects/index.jsonl` and read only its card; then only that object's sources, with `task fetch`; ask the map who else uses it (`kb near`); log each step deeper in `LOG.md`; run `kb stale` before relying on cards {src:.github/instructions/knowledgebase.instructions.md#L12-L21}.

Code adds hints and blocks nothing. When the knowledge base has domains and a task names none, `task new` and `task open` list them {src:.harness/engine/modules/task/tasklife.py#L148-L151}. For a task that names its domains, the hook names their skills at every prompt; these live in the knowledge base under `domains/<domain>/skills/`, not in Copilot's `/` menu {src:.harness/engine/modules/task/tasklife.py#L255-L263} {src:.harness/engine/core/domainskills.py#L1-L8}. `task fetch` and `task fetch --read` answer with the cards that describe the fetched files and mark those written from an older version {src:.harness/engine/modules/task/task.py#L666-L672}.

What is recorded as read: after each read, search or terminal call, the hook keeps the knowledge base paths the call named, never their content {src:.harness/engine/core/kbreads.py#L1-L9}. From that log, `harness kb reads` lists which files each task read and which nobody read, and the board's knowledge base window shows when each domain was last read {src:.harness/engine/core/kbreads.py#L138-L148}. `knowledge_base_reads: false` in `observe.json` turns it off.

## Knowledge base: how it is built from the code

`harness kb status` works out from the files where a build stands, in eight steps: code repositories, knowledge base repository, toolkit, map, audit, domains, learning, keeping it true {src:.harness/engine/core/kbstatus.py#L1-L20}. Scripts do the structure; the model does the meaning {src:docs/08-knowledge-base.md#L11-L15}.

- **Toolkit**, once per code base: the extractors that read the team's stack. `generic-kb-toolkit-design` writes the design; `/generic-kb-toolkit-build`, which only the person starts, builds it until `kb map --toolkit` finds every use a person listed as known {src:.harness/contracts/kb/map.md#L1-L23}.
- **Map**: `kb map` lists every object and every use into a cache under `.harness/runtime/kbmap/`, which is not knowledge {src:.harness/engine/core/kbmap.py#L1-L15}.
- **Audit**: the agent reads a sample blind, and `kb audit` scores the map per type, recall and precision, against a bar of 0.95 {src:.harness/engine/core/kbaudit.py#L1-L24}.
- **Domains**: `kb split` proposes a cut, the person confirms it once (`generic-kb-domains`).
- **Learning**: one `kb` task per domain, `learn-<domain>`. `generic-kb-learn-plan` orders the objects bottom up in batches (`kb order`, 20 objects or 1,500 lines by default) and the person approves the plan once; `generic-kb-learn-batch` writes each batch's cards and checks them with `kb cardcheck`; `generic-kb-learn-synthesize` writes `architecture.md`; then the whole domain is written back once {src:.github/skills/generic-kb-learn-plan/SKILL.md#L16-L67}.

`/harness-rookie-new-knowledgebase` leads a beginner: it runs `kb status`, explains the next step, asks for what only the person knows, and does the step with its skill {src:.github/skills/harness-rookie-new-knowledgebase/SKILL.md#L16-L62}. On the board, the knowledge base window (the book button) shows the steps and each domain with its cards, stale cards and last read; **Learn** opens a chat with a new `kb` task `learn-<domain>` and `generic-kb-learn-plan`, **Refresh cards** one `refresh-<domain>` with `generic-kb-refresh` {src:.harness/engine/modules/task/web/dock.js#L315-L325}. While a registered knowledge base has no domain learned, the agent is told once per session, at a stop of a task that is not a `kb` task and not in autorun, to offer the next step; `kb_offer: false` in `task.json` turns it off {src:.harness/engine/modules/task/handler.py#L462-L483}. `generic-kb-migrate` and `generic-kb-translate` convert old forms and translate.

## Knowledge base: how it is kept true

Staleness is found by code. Each index line keeps the git blob of its source when the card was written; `kb stale --domain <d>` compares it with the base branch and lists the cards whose source changed or is gone, `--diff` with only the change {src:.harness/engine/core/kbstd.py#L207-L209}. `generic-kb-refresh` fixes, in a `kb` task, only the lines a change touches, and stamps the checked cards (`kb stamp`) {src:.github/skills/generic-kb-refresh/SKILL.md#L16-L53}.

What a task teaches is asked of the agent by text: note wrong, stale or missing knowledge in `LOG.md`; at the next stop ask the person in two or three lines; on a yes, draft it with `generic-capture-knowledge` (which writes only `KB-DRAFT.md` in the task) and write it through a `kb` task; on a no, do not ask again in that task {src:.github/instructions/knowledgebase.instructions.md#L23-L41}. What only an environment can tell goes into `requests.md` for a person to run, and its answer into `environment.md`, dated {src:.harness/contracts/kb/README.md#L89-L116}.

## Knowledge base: writing back, committed by the harness

A change reaches a knowledge base as code reaches a code repository: a `kb` task fetches the files into `DEV/<kb repository>/`, the person approves the plan, the dry run shows the change, the person approves the write-back, and `task promote` writes it {src:.github/skills/harness-my-task/SKILL.md#L81}. The difference is in `promote_target.py`: a code repository gets a new branch and no commit, while a registered knowledge base, which has one keeper, gets its files written straight onto its base branch and committed once, with only those files in the commit {src:.harness/engine/modules/task/promote_target.py#L1-L15}. The command requires the base branch checked out, a clean working tree and a git name and e-mail, checks the branch and commit again just before the write, and writes knowledge bases after every code repository; the commit message names the task and the approved plan {src:.harness/engine/modules/task/promote_target.py#L95-L109} {src:.harness/engine/modules/task/promote_target.py#L399-L452}. The harness never pushes; sharing is the person's, by git or **Pack for colleagues** (a zip) {src:docs/03-configure.md#L152}.

A knowledge base that is not a git repository, or not registered, can be read by a task but not updated by a write-back; `doctor` warns and names the fix. It is not closed to the agent as a target repository is (see the section "Knowledge base: limits") {src:.harness/engine/core/messages.en.json#L1059-L1060}. The commands that write knowledge base files, `kb index`, `kb stamp` and `kb migrate`, write only inside a task's `DEV/` {src:.harness/engine/core/kbstd.py#L315-L321} {src:.harness/engine/core/kblearn.py#L235-L246}.

## Knowledge base: toolkits

The toolkit knows the team's stack: what an object and a use look like in its files. It lives in the knowledge base at `toolkit/`: `toolkit.json`, the `extract_*.py` extractors, `facts.jsonl` (uses a person knows) and `declared.jsonl` (uses no extractor can see, with their evidence line) {src:.harness/contracts/kb/map.md#L1-L23}. The harness ships no toolkit, only two samples in `.harness/examples/kb-toolkits/`: `sqlserver` (procedures, SQL Agent jobs, SSIS packages) and `spring` (a Spring Boot service) {src:.harness/INDEX.md#L66}. `kb map` loads the extractors as Python modules and runs them per file; a toolkit being built can be tried with `--toolkit` only from a task folder {src:.harness/engine/core/kbextract.py#L36-L49} {src:.harness/engine/core/kbmap.py#L151-L160}.

## Knowledge base: what is enforced by code, and what is only an instruction

Enforced by code:

- Through a task, the harness writes a registered knowledge base only by a write-back a person approved, of any task kind, committed once. Outside tasks, the person's board actions write it too, with a paired click and no code: Get ready imports a package or folder, and the **Commit** button offered when Pack for colleagues finds uncommitted files commits all of them (`git add -A`) without showing their content; a git command approved with `approve-command` can as well. The agent's edit tools are refused in its working tree, and so is a terminal command that names a path there by its full path; a terminal write by a relative path is not refused {src:.harness/engine/modules/gate/policy.py#L149-L156} {src:.harness/engine/modules/gate/handler.py#L36-L52} {src:.harness/engine/core/company.py#L555-L571} {src:.harness/engine/modules/task/boardserve.py#L2026-L2033} {src:.harness/engine/modules/gate/handler.py#L153-L162}.
- `kb index`, `kb stamp` and `kb migrate` write only in a task's `DEV/`; `kb index` takes only ids the map has {src:.harness/engine/core/kblearn.py#L235-L246}.
- The form (`kb check`), staleness (`kb stale`), the card relations against the map (`kb cardcheck`) and the audit score are computed by script, with no model {src:.harness/engine/core/kbstd.py#L1-L13}.
- **Pack for colleagues** refuses uncommitted files and `kb check` errors, then offers that one-click Commit, so look at what the files are first {src:.harness/engine/core/company.py#L529-L542}. The read log, the domain skills named at each prompt, the cards listed by `task fetch` and the offer at a stop are hints: they block nothing.

Only an instruction to the agent: reading the knowledge base at all, and in what order; naming the domain; running `kb stale` before relying on cards; running `kb check` and `kb cardcheck` before a write-back (the write-back itself does not run them); noting wrong knowledge and asking at a stop; never stamping a card it did not read; never editing the knowledge base from a task of another kind {src:.github/instructions/knowledgebase.instructions.md#L12-L41}. So reading the knowledge base is not enforced: an agent that skips it is not stopped, and the read log is how a person finds out.

## Knowledge base: who decides what

The person imports or registers the knowledge base, gives the known uses, the entry points and the boundaries, confirms the domains, approves each plan and write-back, starts `/generic-kb-toolkit-build`, answers the requests and shares the commits {src:.github/skills/harness-rookie-new-knowledgebase/SKILL.md#L16-L62}. Code decides what can be checked (objects and uses, order, form, staleness); the agent writes the words, from the code {src:docs/08-knowledge-base.md#L62-L68}.

## Knowledge base: why it is built this way, and what was tried before

**A repository of its own.** The harness is general and replaced by each upgrade; the knowledge is the team's. So it lives where an upgrade never writes {src:docs/08-knowledge-base.md#L173}. Git gives each card an "as of", the commit it was read at, which is what lets a script tell a stale card. And a knowledge base has one keeper, so a reviewed change is committed at once instead of left on a branch {src:.harness/engine/modules/task/promote_target.py#L1-L15}.

**Files, not the model or the prompt.** The model does not know the team's code, and a chat forgets. A prompt costs context on every turn; files are read step by step, the index first {src:docs/05-design.md#L145}. Files in a fixed form can be checked by scripts, dated by git and logged when read; a model's memory cannot. The test of every page: reading it must cost less than reading the code {src:.harness/contracts/kb/README.md#L1-L26}. The aim is a base, not a finished book: every gap is written where the next reader sees it {src:docs/08-knowledge-base.md#L11-L15}.

**What was tried before.** 1.3.0 let a task update a registered knowledge base and logged the reads {src:docs/07-release-notes.md#L3503-L3504}. 1.4.8 brought the standard v1, replacing a form whose `domain.yaml` listed the objects, which `kb migrate` still converts {src:docs/07-release-notes.md#L3290}. 1.4.37 brought learning from zero in three skills, 1.5.0 the wizard and the offer at a stop, and 1.5.4 one task per domain with one write-back, in place of one task per batch {src:docs/07-release-notes.md#L2761-L2871}.

## Knowledge base: where in the source

Under `.harness/engine/` {src:.harness/engine/core/kbstd.py#L1-L13}: `core/kbstd.py` (form, `stale`, `stamp`); `core/kbmap.py`, `kbextract.py`, `kbgraph.py`, `kbaudit.py`, `kblearn.py` (map, audit, learning); `core/kbstatus.py` (the steps); `core/kbreads.py` (the read log); `core/targets.py` and `modules/task/kbsetup.py` (registration); `modules/task/promote_target.py` (the commit); `modules/task/kbview.py` and `web/dock.js` (the window). Contracts: `.harness/contracts/kb/`.

## Knowledge base: common questions

**Q: What is the knowledge base, and how does the agent use it?** The team's own notes about its code, in `knowledge-base/` or a repository registered with `knowledge_base: true`, in a fixed form per domain. The agent is told to read `architecture.md` and `domain.yaml` first, then one card from the index, then only the code that card names {src:.github/instructions/knowledgebase.instructions.md#L12-L21}.

**Q: Is the agent forced to read the knowledge base?** No. Reading it, and the order, are instructions; code names the domain skills, lists the cards of fetched files and logs which files were read {src:.harness/engine/core/kbreads.py#L1-L9}.

**Q: Can the agent change the knowledge base on its own?** Not a registered one by its edit tools or by a terminal command that names the knowledge base's full path: through the harness, a change goes in only by a task whose plan and write-back a person approved. A terminal write by a relative path (`echo … > knowledge-base/…`), a script or a path made at run time is not refused {src:.harness/engine/modules/gate/policy.py#L149-L156}. That it is a `kb` task is only an instruction: `task promote` does not check the kind {src:.harness/engine/modules/task/task.py#L911-L930} {src:.harness/engine/modules/task/promote_target.py#L1-L15}.

**Q: Why give the agent a knowledge base instead of letting it read the code?** Reading it costs less and answers better; scripts check its form and find what went stale, the map's accuracy is measured, and the read log shows what nobody reads {src:.harness/engine/core/kbaudit.py#L1-L24}.

## Knowledge base: limits

- **The read log sees named paths only**: a search over a folder records the folder. "Last read" counts a read in any chat, also one that holds no task {src:.harness/engine/core/kbreads.py#L1-L9} {src:.harness/engine/core/kbreads.py#L138-L148}.
- **The write-back does not run `kb check` or `kb cardcheck`**; `doctor` only warns {src:.harness/engine/doctor.py#L559-L571}.
- **A registered knowledge base is closed to the terminal only by its full path.** A terminal write by a relative path, or after a `cd` to a relative folder, is not refused, domain skills included {src:.harness/engine/modules/gate/policy.py#L149-L156}.
- **An unregistered `knowledge-base/` is not a target repository**, so the gate's target refusal does not cover it, and a chat that holds no task is not kept out of it {src:.harness/engine/modules/gate/handler.py#L64-L72}.
- **A stamp is trusted**: the code cannot tell whether a stamped card was read {src:.github/skills/generic-kb-refresh/SKILL.md#L16-L53}.
- **The map is blind to some uses**: SQL built at run time, a package chosen by a variable, rows only in production become `dynamic` or `outside` and requests; a card names only uses the map has {src:docs/08-knowledge-base.md#L96}.
- **`kb map` runs the toolkit's Python in its own process**, with no sandbox; a trial toolkit in a task folder runs before anyone reviewed it {src:.harness/engine/core/kbextract.py#L36-L49}.
- **A domain being learned is not in the knowledge base** until its learn task is written back {src:.github/skills/generic-kb-learn-plan/SKILL.md#L16-L67}.

## Knowledge base: related files

- The write-back: 16 Write-back. Tasks and the `kb` kind: 11 Task. Domain and company skills: 23 Skills. The gate's target refusal: 15 The gate and guardrails. Get ready and `doctor`: 24 Setup, doctor and upgrade. The ideas: 41 Ideas behind the harness {src:.harness/engine/modules/task/promote_target.py#L1-L15}.
- To import or build a knowledge base step by step, see the harness tutorial "6 Knowledge base" in `3 Courses/Harness tutorials/`.
