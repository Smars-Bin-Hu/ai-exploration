---
title: Write-back
subject: Write-back
layer: concept
file: 16 Write-back
harness_tag: 1.8.3
course: The book · 5.3 Two gates: where a person approves | https://smarshu.com/book/read/5-3-two-approvals.html
course: The book · 4.5 Some things you never hand over | https://smarshu.com/book/read/4-5-least-privilege.html
---
## Write-back: what it is and what problem it solves

The write-back (`harness task promote`, "promote" on the board) is the only way the harness itself puts a task's work into a target repository: a git repository of the team's code or knowledge base, set up in **Get ready**. The agent does not edit a target repository: the gate refuses its edit tools and the terminal commands that name it by its full path, and it changes copies in the task's `DEV/` folder instead; a dry run shows the exact change, a person approves that change with a typed code, and only then does the command write it, onto a new branch and without a commit {src:AGENTS.md#L48-L49} {src:.harness/engine/modules/task/promote_target.py#L1-L15}. So what reaches the repository is exactly the set of files a person approved, on a branch the person reviews and commits, not changes nobody read.

## Write-back: how files get into the task

The agent brings files into the task with `harness task fetch <repository>/<path>` (several files or a folder in one call, at most 200 files). Fetch needs the approved plan. It reads each file as the committed base branch (`main` by default) has it, not the working tree, copies it to `DEV/<repository>/<path>`, and keeps the base commit and the git blob of each file in `.task/task.json`, so the write-back can tell later whether the file moved on the base branch {src:.harness/engine/modules/task/task.py#L618-L673}. Before the first read of a repository in a round, the base branch is brought up to its remote (since 1.5.39) {src:.harness/engine/modules/task/basesync.py#L1-L14}.

Besides fetch into `DEV/`: `task fetch --read` (since 1.7.42) copies code only to be read into `READ/<repository>/<path>`, with no plan and never written back; `DEV/_manual/<path>` holds code the person runs by hand, never written back; `task delete <repository>/<path>` marks a fetched file to be deleted; a new file is written under `DEV/<repository>/<path>`; a file directly in `DEV/` belongs to no repository and is not written back {src:.harness/engine/modules/task/task.py#L676-L768}.

## Write-back: the dry run and what it checks

`harness task promote --dry-run` builds the write-back plan and writes nothing to any repository. It is refused unless the plan is approved as it is now and, when the person switched independent checks on, the work has enough passes in a row or the person waived them {src:.harness/engine/modules/task/task.py#L911-L940}. It brings each base branch up to its remote again, checks every repository, and refuses the whole plan, listing every problem, when any check fails {src:.harness/engine/modules/task/promote_target.py#L119-L223}:

- **Base commit:** the base branch must have one; the plan records it.
- **Dirty repository:** the working tree must be clean. When it sits on another task's write-back branch whose files are not committed yet, the refusal names that task (the promote queue) {src:.harness/engine/modules/task/taskqueue.py#L1-L9}.
- **Branch:** `feature/<task name>` by default, changed with `task set-branch`; it must not exist yet.
- **Files changed since fetch:** a changed or deleted file must still have, on the base branch, the blob the task fetched; a new file must not exist there yet {src:.harness/engine/modules/task/promote_target.py#L59-L92}.
- **Refused paths:** nothing under `.git/` or in the repository's `refused_paths`.

A file still as it was fetched was only read: it is left out, and its repository is not checked (since 1.7.42). When everything passes, the dry run takes a snapshot, records the plan digest, and writes the whole change as one diff to `PROMOTE-PLAN.diff`, which the agent links for the person to read.

![The write-back from fetch to close: the agent fetches and edits copies, the dry run checks, the person approves, the command writes a branch or a knowledge base commit, the person commits, the board closes the task](fig/write-back.svg)

## Write-back: what the person approves, and what the code covers

The person approves with **Approve promote** on the task page or `harness task approve-promote` in their own terminal; the gate refuses the command on the agent's command line, and the command checks for a person {src:.harness/policies/gate.json#L131-L137} {src:.harness/engine/modules/task/task.py#L984-L1024}. The screen lists each repository with its base commit and new branch, and every file with its action (create, modify, delete) and lines added and removed; the task page's Changes tab shows the diff side by side.

The code is six capitals taken from the plan digest: a sha256 over the branch name, the name and base commit of every repository, and the path, action and sha256 of every file {src:.harness/engine/modules/task/promote_target.py#L112-L116}. So the approval covers exactly that content; a changed file in `DEV/`, a moved base commit, another branch name or another file list is another digest, and `task promote` refuses unless the dry run and the approval are both for the plan as it is now {src:.harness/engine/modules/task/task.py#L941-L944}. A new dry run with the same digest keeps the approval; a fetch, a delete or a new branch name after the dry run drops it. The approval does not cover the knowledge base's commit message or what happens to the branch afterwards.

## Write-back: what the write itself does

After an approval on the board, the board sends the agent its "go on" message (after one in a terminal, the person tells the agent), and the agent runs `harness task promote`. The command checks the plan again under the task's lock, saves the whole change as `DEV/<task name>.patch` before the first repository is touched, then writes the repositories one by one. For a code repository it runs `git switch -c <branch> <base branch>`, copies each file into the working tree, checks that the written file has the approved sha256, and stops: it never commits, never resets and never switches back {src:.harness/engine/modules/task/promote_target.py#L399-L431}.

The commit message is the agent's, asked by text: the command's answer tells it to write `COMMIT-MESSAGE.md` in the task folder, a subject of at most 72 characters, a blank line and the body, one `## <repository>` section per repository when there are several {src:.harness/engine/core/messages.en.json#L1981}. The Changes tab shows it with the contributor line `Co-authored-by: GitHub Copilot Coding Agents` added by code (`commit.coauthor` in the task policy changes the name), warns about a long subject, and gives the commands to commit for macOS and Linux and for PowerShell; the person runs them {src:.harness/engine/modules/task/commitmsg.py#L1-L13}.

## Write-back: the knowledge base, committed by the harness

A repository registered with `knowledge_base: true` is the one exception: the write-back commits it. It must be on its base branch with a clean working tree and a git user name and e-mail set; it is written last, after every other repository; just before writing, the command checks again that the branch and its commit are the ones approved {src:.harness/engine/modules/task/promote_target.py#L95-L109} {src:.harness/engine/modules/task/promote_target.py#L399-L431}. The files go straight onto the base branch, with no new branch, in one commit that holds those files and nothing else, with the message `harness task <name>: <n> file(s)` and the approved plan digest; a failed commit leaves nothing staged {src:.harness/engine/modules/task/promote_target.py#L434-L452}. The harness does not push: the answer tells the person to push. The reason, in the code's own words: a knowledge base has one keeper, so a branch waiting for a review commit adds nothing; this came in 1.3.0 {src:.harness/engine/modules/task/promote_target.py#L1-L15}.

## Write-back: the git commands the agent may and may not run

When target repositories are set up, the gate reads every git command in a terminal call, in any folder {src:.harness/engine/modules/gate/gitcmd.py#L1-L9}:

- **Reads pass:** `status`, `diff`, `log`, `show`, `blame` and the like, and `branch` or `tag` with no change.
- **Writes wait for the person:** `commit`, a branch switch (`switch`, `checkout`), `merge`, `add` and any command not clearly a read are refused until the person approves that exact command with `harness approve-command` and its code; it may then run once, spelled the same, within 10 minutes {src:.harness/engine/modules/gate/handler.py#L154-L162}.
- **Never approved:** `git push`; `git clean` (a dry run, `-n` or `--dry-run` as the first argument, passes as a read); `git filter-branch`, `git filter-repo`, `git update-ref` and `git prune`; `git reset --hard`; `git gc` with an argument that starts `--prune`; `git reflog expire` and `git reflog delete`; `git branch -D`; any force (`--force`, `--force-with-lease`, `--force-if-includes`, `--discard-changes`, and a short `-f` in `add`, `checkout`, `switch`, `branch`, `tag`, `mv`, `rm`, `fetch`, `pull`, `worktree`, `submodule`, `clean` and `push`; `-f` of `config` and a capital `-F` are not force); and `gh pr`. A command line that holds one of these beside an approvable write is never as a whole {src:.harness/engine/modules/gate/gitcmd.py#L30-L37} {src:.harness/engine/modules/gate/gitcmd.py#L212-L218} {src:.harness/engine/modules/gate/gitcmd.py#L253-L296} {src:.harness/engine/modules/gate/gitcmd.py#L330-L341}.

The gate also refuses the agent's edit tools in a target repository's working tree and a terminal command that names it as a write target by its full path; a relative path into it is not caught {src:.harness/engine/modules/gate/handler.py#L36-L61} {src:.harness/engine/modules/gate/policy.py#L149-L156} {src:.harness/engine/modules/gate/handler.py#L117-L162}. **These rules, and the git rules above, hold only when target repositories are set up**; a write into any `.git` folder is refused always. Get ready writes the target repositories into `target.override.json` {src:.harness/engine/core/setup.py#L1-L3}. Without any, no repository is protected as a target, and only the ask list looks at git: `push`, `reset --hard`, `clean` and a few others ask for Copilot's confirmation, which does not show under Allow all (autorun's Start sets it), and a `commit` passes the gate {src:.harness/engine/modules/gate/handler.py#L815-L824} {src:.harness/policies/gate.json#L155-L160}. There is no write-back then either: the dry run says there is nowhere to promote, and the agent delivers the work in the task {src:.harness/engine/core/messages.en.json#L714}.

## Write-back: what happens after

A write-back is the person's acceptance of a development or knowledge base task. The agent is told to stop and never to run `task close`; the board closes the task once the agent has stopped and nothing else waits (a check, a question, a held call, a hand-over, autorun, a pause), without waiting for the commit {src:.harness/engine/modules/task/accept.py#L184-L218}. Closing writes the report, `.workspace/reports/tasks/<task name>/report.md`, with the write-back's state, the approval time, each file and action, a knowledge base commit and the patch {src:.harness/engine/modules/task/task_report.py#L55-L70}. A later change to the same goal is a new round, opened with `task open`: the old `DEV/` and plan move aside, and the round gets a new plan and a branch name ending `_r2` {src:.harness/engine/modules/task/task.py#L234-L251}.

## Write-back: conflicts and failure cases

- **Main changed since the fetch.** The dry run refuses that file, with the old and new blob. `task fetch <file> --rebase` takes it as main has it now and drops the change in `DEV/`; the agent makes the change again. The harness does not merge {src:.harness/engine/core/messages.en.json#L635-L636}.
- **The base branch cannot be brought up to its remote** (it diverged, or it is checked out with uncommitted changes while behind): the fetch or dry run stops and the person decides. A remote that cannot be reached is said, and the local branch is used.
- **A dirty tree, an existing branch, or a change after the dry run:** commit, stash or discard, or pick another branch name; after any change, run the dry run again.
- **A write that fails halfway.** There is no automatic undo across repositories. The task is marked `partial`, and the answer says which repositories were written, which failed, which were not touched, where the patch is, and the git commands that put each back {src:.harness/engine/modules/task/promote_target.py#L455-L538}. Putting back is the person's: **Recover the repository** on the task page or `harness task recover`, with a code. It restores written files, removes created ones, switches back and deletes the branch with `-d`, or reverts a knowledge base commit, only in a repository still on the write-back branch; a file edited there by hand is first copied to `REF/recovered-<time>/`. Until then a dry run, `task open` and `task close` are refused {src:.harness/engine/modules/task/task.py#L1027-L1061}.

## Write-back: what is enforced by code, and what is only an instruction

**Code:** the gate refuses `approve-promote` and `recover` on the agent's command line, and both need a person and a code; the dry run needs the approved plan and the passes; every repository and file is checked before anything is written; `task promote` writes only the approved digest, onto a new branch, never commits a code repository and commits a knowledge base once; edits, and terminal writes naming a target repository by its full path, are refused, and git writes wait for `approve-command` when target repositories are set up {src:.harness/engine/modules/task/task.py#L911-L957} {src:.harness/engine/modules/gate/handler.py#L117-L162}.

**Text only:** run the dry run and give the link, not the diff; run `task promote` only after the person approved (the command refuses anyway); write `COMMIT-MESSAGE.md` without the contributor line; stop after the write-back and never close the task; use `--read` for code only read {src:.harness/engine/core/messages.en.json#L722-L730}.

## Write-back: who decides what

The **person** sets up the target repositories, approves the plan and the write-back, approves each git write, recovers a failed write-back, commits and pushes. **Code** decides whether a dry run, an approval and a write may run, what is written, and when the board closes the task. The **agent** fetches, edits `DEV/`, runs the dry run and the write-back, and writes the commit message {src:.harness/engine/modules/task/task.py#L1-L14}.

## Write-back: why it is built this way, and what was tried before

**A copy in the task, not an edit in place.** The target repositories are data pipeline code stores: large, mixed files, nothing that runs on a laptop. So only the files the plan changes are fetched, the person's working tree, current branch and commits are left alone, the work is checked by reading the diff, and a mistake is put right with `task recover` or git {src:docs/05-design.md#L198-L202}. The task folder is the sandbox: the gate already keeps the edit tools of the task's chat in it, so no second sandbox is needed, and the recorded blob of each copy is what lets the dry run see that main moved. It is the idea of the book chapter "Some things you never hand over": no write access to the repository at all, rather than access with a guard on it; how strict a rule is follows the harm a mistake would do.

**What was tried before.** Version 1.0 already fetched from main, ran a dry run, took the approval in the terminal and wrote an uncommitted branch; its L3 level also had a request folder with its own `promote`, removed in 1.1.0 {src:docs/07-release-notes.md#L3699-L3706}. Later: the knowledge base commit and the promote queue (1.3.0); the agent's commit message (1.5.29); main brought up to its remote, after a clash with a merged pull request showed only in the pull request (1.5.39); recover that keeps a hand edit (1.6); the write-back as acceptance, with the board closing the task (1.7.38); read-only copies left out of the plan, after one held a whole write-back back (1.7.42).

**The second look after three seconds (1.7.43).** `approve-promote` builds the plan before it shows the screen. Before 1.7.43 it built it again after every code; since then only when the code came more than three seconds after the screen, as for a person reading in a terminal. A code typed on the board at once was read from the preview, and `task promote` checks the digest again before it writes, so the second look added only time: after the code, 2 git processes instead of 8 {src:.harness/engine/modules/task/task.py#L1014-L1020} {src:docs/07-release-notes.md#L136}.

## Write-back: where in the source

Under `.harness/engine/` {src:.harness/engine/modules/task/promote_target.py#L1-L15}: `modules/task/task.py` (fetch, delete, the plan, promote, approve-promote, recover); `modules/task/promote_target.py` (checks per repository, plan digest, the write, the knowledge base commit, recovery steps); `modules/task/common.py` and `basesync.py` (reading the base branch, bringing it up to its remote); `modules/task/commitmsg.py` (commit message and commands); `modules/task/accept.py` (the board's close); `modules/task/taskqueue.py` (the promote queue); `core/targets.py` (target repositories); `modules/gate/gitcmd.py` and `handler.py` (git rules, working-tree refusals).

## Write-back: common questions

**Q: When the work is written back, does the agent commit or push to our repository?** Not for a code repository: the write-back makes a new branch, writes the files and commits nothing; the person commits. A registered knowledge base is the exception, committed once on its base branch and never pushed by the harness. With target repositories set up, the agent's own `git commit` waits for the person's `approve-command`, and `git push` is never approved; without them only Copilot's confirmation asks about a push, and none shows under Allow all, which autorun sets {src:.harness/engine/modules/task/autorun_start.py#L1-L5}.

**Q: Can the agent write to the repository without my approval?** Not through the harness, when the repository is set up as a target repository in Get ready: `task promote` needs the approval of the same plan digest, and the gate refuses edit tools and terminal commands that name it by its full path. A relative path into it, a script or a path built at run time is not seen, and a git command you approve with `approve-command` runs. A repository not set up is not protected: only a chat that holds a task is kept in its folder, and only for its edit tools.

**Q: If the write-back goes wrong, can I go back?** Nothing is committed in a code repository, the patch is saved before the first write, and a write that fails halfway gives the commands that put each repository back, which **Recover the repository** runs. After a successful write-back, going back is ordinary git: delete the branch, or revert the knowledge base commit.

**Q: Does my approval hold if a file changes after I approved?** No. The code belongs to the plan digest, and `task promote` refuses a plan that differs from the approved one.

## Write-back: limits

- **The rules need target repositories set up;** without them git is checked only by the ask list {src:.harness/engine/modules/gate/handler.py#L815-L824}.
- **The gate reads command text.** A terminal write by a relative path, a script, an alias or a path made at run time can write a repository unseen {src:.harness/engine/modules/gate/policy.py#L149-L156}; a git command the person approves can also write there {src:.harness/engine/modules/gate/gitcmd.py#L1-L9}.
- **The harness runs `git fetch` and moves the base branch forward** at a first fetch and every dry run, by fast-forward only, although the design doc says "no automatic fetch or pull" {src:docs/05-design.md#L224}.
- **No undo across repositories,** and recovery acts only in a repository still on the write-back branch {src:.harness/engine/modules/task/promote_target.py#L13-L14} {src:.harness/engine/modules/task/promote_target.py#L350-L386}.
- **A person can approve without reading.** The digest stops a swap, not a careless yes; the dry run checks base versions, not whether the code is right.
- **One task per repository at a time:** the next write-back waits until the person commits the previous one.

## Write-back: related files

- Approvals and their codes: 14 Plans and approvals. The gate, `approve-command` and the ask list: 15 The gate and guardrails. The passes: 17 Independent checks. The task and its rounds: 11 Task. The knowledge base: 18 Knowledge base. Get ready: 24 Setup, doctor and upgrade.
- To do it step by step (approve the write-back, commit the branch), see the harness tutorial "1 A day with the harness" in `3 Courses/Harness tutorials/`.

The rule that a target repository is written only by an approved promote is in `AGENTS.md` {src:AGENTS.md#L48-L49}.
