---
title: Tool packs, connections and MCP
subject: Tool packs
layer: concept
file: 19 Tool packs, connections and MCP
harness_tag: 1.8.3
course: The book · 1.3 What should you think through before connecting an MCP server? | https://smarshu.com/book/read/1-3-mcp.html
course: The book · 4.5 Some things you never hand over | https://smarshu.com/book/read/4-5-least-privilege.html
course: The book · 4.6 Text the agent reads can give it orders | https://smarshu.com/book/read/4-6-untrusted-input.html
---
## Tool packs: what they are and what problem they solve

A tool pack is one folder that teaches the agent one outside tool (a database, a ticket board, a pipeline service): the program it calls, the gate's rules for that program, and the skills that say how the team uses it. A connection is one place the tool reaches, such as one database on DEV, with the person's own sign-in {src:.harness/contracts/toolpack/README.md#L1-L30}. The harness knows no tool and no server itself; every connection type is a file a pack brings {src:.harness/engine/core/connections.py#L1-L17}. The problem: once the agent can reach a database with the person's account, a rule in a prompt cannot stop a write. So the gate turns each terminal call to a listed system into an action `{system, env, verb, target}` and decides by the company's rules whether it runs, waits for the person, or is refused {src:.harness/engine/modules/gate/external.py#L1-L22}.

## Tool packs: what files make one, and the three that ship

A pack holds `toolpack.json` (name, version, programs it needs, ticket link types, MCP tool rules), `types/<type>.json` (connection types: fields, ways to sign in, a test, and the gate's verbs, lists and rules), and optionally `rules.json` (rules for programs no type covers), `skills/`, `bin/` (its own small program, put on the PATH VS Code gets), `launch/` and `mcp.json` {src:.harness/contracts/toolpack/README.md#L1-L30}.

| Pack | Tool and program | Sign-in | Ticket links | MCP |
|---|---|---|---|---|
| `ado` | Azure DevOps through its own program `ado`: work items, pipeline runs, releases | Azure CLI sign-in or a personal access token | `ado:<id>` | none |
| `sqlserver` | SQL Server through `sqlcmd`, a jobs skill, a Windows launch script | a Windows account held by the VS Code window, or a SQL account | none | none |
| `demotracker` | a made-up ticket board, to try the whole path | the program's own sign-in | `demo:<id>` | a sample server, only where MCP is allowed |

A factory pack is off until the knowledge base names it in `company/tools/packs.json` (`{"use": ["ado"]}`); a pack the company wrote in `company/tools/packs/<name>/` is always on; a person may try a folder with `harness toolpack add`, a person-only command {src:.harness/toolpacks/README.md#L7-L31}. Only a pack's skills are copied, into `.github/skills/`. Turning a pack off takes back its skills and its `bin/` on the PATH, not its guard: while a connection uses one of its types, the gate still judges that program by the pack's rules {src:.harness/engine/core/toolpacks.py#L340-L358}. `.harness/toolpacks/**` is a guardrail path the agent cannot change {src:.harness/policies/gate.json#L4-L19}.

## Tool packs: connections, environments and where the sign-in is kept

A connection has a name, a type, an environment (`dev`, `ist`, `qat`, `prod`, or `none` for a tool with none, such as a ticket board) and the type's fields (`host`, `port`, `database`; `org`, `project`). The team's list is `company/tools/connections.json` in the knowledge base, copied in by `harness company sync`; it may lower how far a connection opens and set its own rules, and holds no account or password. A person may also add a connection of their own on the board's Get ready page (Tools, Connections & sign-ins) {src:.harness/contracts/toolpack/connections.md#L1-L30}.

The person signs in once per connection on the board; the sign-in is saved to `.harness/.env` when the type's test passes (or kept as "not tested yet" when the test never reached the server) {src:.harness/engine/core/connections.py#L1053-L1090}. `.harness/.env` is a plain text file on the person's computer, readable only by its owner on macOS and Linux, in `.gitignore`, and a guardrail path {src:.harness/engine/core/connections.py#L272-L297} {src:.gitignore#L16-L18} {src:.harness/policies/gate.json#L4-L19}. The gate refuses a tool whose path (its `filePath` or `path` input) is `.harness/.env`, a terminal command that names the file or dumps the environment, and a command that names a sign-in variable unless every call in it goes to that variable's own connection; a tool that names the file another way is not checked, and an MCP tool a pack names is decided before this check runs {src:.harness/engine/modules/gate/handler.py#L624-L672} {src:.harness/engine/adapters/tool_kinds.json#L1-L10} {src:.harness/engine/modules/gate/handler.py#L758-L836}.

The sign-in reaches the program through the process, not the command line: the board opens VS Code with the chosen identities in its environment, or under a Windows account as `runas /netonly` does; an identity the window cannot also hold is used through `harness as <name> -- <command>`, which refuses any command that is not a call of that connection {src:.harness/engine/core/connections.py#L1239-L1331}. The agent is told at each chat start only the kinds and counts of connections, and finds one with `harness connections find <words>` {src:.harness/engine/modules/gate/handler.py#L695-L720}.

## Tool packs: how the gate judges a call through a tool pack

The gate splits a terminal line into commands and turns each call of a listed program into an action; the strictest part decides {src:.harness/engine/modules/gate/handler.py#L213-L256}. The rules give each verb (`read`, `write`, `exec`, `destroy`) in each environment one of five decisions {src:.harness/engine/core/systems.py#L1-L38}:

- `allow`: it runs.
- `task`: it runs only in an open task whose plan the person approved (or a test task whose environment the person gave the agent); otherwise it is refused {src:.harness/engine/modules/gate/handler.py#L273-L314}.
- `outbox`: held. The person approves that exact command on its card with a code, and it runs once (the file 14 Plans and approvals).
- `human`: the agent hands the command to the person.
- `deny`: refused {src:.harness/engine/modules/gate/handler.py#L405-L433}.

With no rule written, a read passes, a write is held, a run is the person's, a destroy is refused, and on `prod` only a read passes; a call no verb rule names counts as a write, and an environment no rule names as prod {src:.harness/engine/core/systems.py#L1-L38} {src:.harness/engine/modules/gate/external.py#L1-L22}. On `prod` the gate takes only a rule written for `prod` by name: a company's catch-all rule (`"*"`) applies to the other environments and can never loosen prod {src:.harness/engine/modules/gate/external.py#L108-L114}. So after the plan is approved, only `task` calls and calls on a connection the person opened pass without a further approval; each held write still needs its own code. A subagent's call that is not a pass is refused, and so is, during autorun, any call that would wait for the person {src:.harness/engine/modules/gate/handler.py#L273-L314} {src:.harness/engine/modules/gate/handler.py#L405-L433}.

A type whose program takes statements as text (`sqlserver`) is judged by three lists: a statement on `refuse` (`KILL`, `RESTORE`, sqlcmd's `!!`, `:connect`, `xp_...`) is refused at once with the right way; a call whose every statement is on `reads` passes; the rest asks {src:.harness/contracts/toolpack/README.md#L97-L113}. Since 1.7.38 a call must name exactly one server that matches a connection, a pack's program with no connection of its type is refused (except `--help`, `--version`), and when the gate fails or a pack's file or connection list cannot be read, a line naming a pack's program is refused or held {src:docs/07-release-notes.md#L216-L273} {src:.harness/engine/modules/gate/failclosed.py#L1-L7}.

## Tool packs: what each sample type lets through, and SQL Server's destroy on DEV and IST

| Type | Read | Write | Run | Destroy | Open for a task |
|---|---|---|---|---|---|
| `sqlserver` DEV, IST | if on the read list | held | held | held | the whole connection |
| `sqlserver` QAT | if on the read list | held | the person's | refused | never |
| `sqlserver` PROD | if on the read list | refused | refused | refused | never |
| `azure-devops` (`ado`) | passes | held | held | refused | the linked work items |
| `demotracker` | passes | held | the person's | refused | the linked tickets |

The rows come from each type's `rules` and `open` keys and the prod default {src:.harness/toolpacks/sqlserver/types/sqlserver.json#L254-L279} {src:.harness/toolpacks/ado/types/azure-devops.json#L94-L102} {src:.harness/toolpacks/demotracker/types/demotracker.json#L49-L56} {src:.harness/engine/core/connections.py#L644-L654}. A company changes the lists in its own copy of the pack; a connection can only lower its scope and set rules. On SQL Server DEV and IST, `DROP TABLE` and `TRUNCATE TABLE` are a destroy that is held, not refused, and they are on the type's write list, so on a connection the person opened they pass without asking. The 1.7.38 notes give the reason: ETL tests on DEV drop and refill tables, and a refusal left the agent no way on. A drop of a temporary table, procedure or view is an ordinary write; `EXEC('...')` and `sp_executesql` always ask {src:.harness/engine/modules/gate/handler.py#L273-L314} {src:docs/07-release-notes.md#L216-L273}.

## Tool packs: opening a connection for one task (`task allow`)

Opening a connection lets the agent's held writes and runs on that one connection pass, in that one task, with no code each time. `task allow --conn <name> --on|--off` and `task allow --links --on|--off` (the task's linked tickets) are the person's: the command checks for a person at a terminal, and since 1.8.0 the gate refuses every spelling of `task allow` on the agent's command line {src:.harness/engine/modules/task/tasklife.py#L520-L595} {src:.harness/policies/gate.json#L131-L137}. From 1.7.38 to 1.7.46 the gate's pattern still matched only the old `--env`, so `--conn` and `--links` were not refused by the gate {src:docs/07-release-notes.md#L83}.

On the board, a held call's card offers **Open** *connection* **for this task**; it needs the code of a held call of this task that offers that connection, and it does not approve the call: the agent runs the command again and it passes {src:.harness/engine/modules/task/boardserve.py#L774-L792}. How far it opens is the type's `open` word, lowered by the company: `all`, `items` (only the tickets the task is linked to) or `no`; prod never opens {src:.harness/engine/core/connections.py#L644-L654}. Even when open, a statement on no list, a script the gate cannot read, or a destroy the type's write list does not name still waits each time (a destroy on a type with no lists never passes, even when open) {src:.harness/engine/modules/gate/handler.py#L273-L314}. On SQL Server, an `UPDATE` or `DELETE` with no `WHERE`, or with one that is always true (`WHERE 1=1`, `WHERE id = id`, an `OR 1=1`), is on neither list, so it waits for the person each time even on a DEV connection the person opened {src:.harness/toolpacks/sqlserver/types/sqlserver.json#L124-L127} {src:.harness/engine/modules/gate/handler.py#L299-L308}. An opening lasts until the person closes it on the task page or with `--off`; the gate reads it only while the task is open, and every call it let through is noted in the task {src:.harness/engine/modules/gate/handler.py#L336-L390} {src:.harness/engine/modules/gate/handler.py#L758-L836}.

## Tool packs: tickets linked to a task

A task can name items of an outside tool (`ado:300100`, `demo:T-7`): in **New task**, on the task page, or with `harness task link add <type>:<id>`. The board shows each as a chip that opens the item. The board refuses a type no installed pack gives; `task link add` keeps it with a warning {src:.harness/engine/modules/task/tasklife.py#L597-L640} {src:.harness/engine/modules/task/boardserve.py#L774-L792}. For a type that says which item a write names (`ado`, `demotracker`), a write to an item the task is not linked to is refused; to a linked item it is held; after the person opens the linked items it passes; a new item is still held {src:.harness/engine/modules/gate/handler.py#L273-L314} {src:.harness/engine/modules/gate/handler.py#L336-L390}. `task link add` is not person-only: the agent may link a ticket, but an item it links is not opened, while one the person links on the board while the linked items are open is opened at once {src:.harness/engine/modules/task/tasklife.py#L597-L640}. Ticket text is written by other people and can steer the agent, one reason writes are held.

## Tool packs: MCP servers

A pack may carry `mcp.json`. Where the person allowed MCP on this computer (Get ready, or `harness tools mcp --allow`, person-only; blocked by default), turning the pack on adds its servers to `.vscode/mcp.json`; blocking MCP or turning the pack off takes them out {src:.harness/engine/core/toolpacks.py#L1089-L1127} {src:.harness/engine/modules/gate/commands.py#L317-L323}. `.vscode/mcp.json` is a guardrail path, so the agent cannot add a server with its edit tools {src:.harness/policies/gate.json#L4-L19}. A team adds a guarded server through a pack: its `mcp.json`, and its tools named with a verb in `mcp.tools`, as in `demotracker` {src:.harness/toolpacks/demotracker/toolpack.json#L22-L33}.

No MCP tool is listed in `tool_kinds.json`, so every MCP tool, like any unlisted tool, has the kind `other` {src:.harness/engine/adapters/tool_kinds.json#L1-L10}. For such a tool the gate only refuses an input that names the board's port, judges an MCP tool a pack names, and applies the `.env` check: no path check, no terminal rules {src:.harness/engine/modules/gate/handler.py#L758-L836}. A named MCP tool: a read passes, a write or exec asks (Copilot's own confirmation), a destroy is refused, a subagent may only read {src:.harness/engine/modules/gate/handler.py#L317-L333}. An MCP tool no pack names is not judged; it is only noted for `harness doctor` {src:.harness/engine/modules/gate/handler.py#L758-L836}. So a pack's MCP route is weaker than its program route: no card, no code, no linked-ticket check, and the harness docs say Copilot's box does not show under Allow all, the permission every chat the board makes starts with {src:docs/02-features.md#L50} {src:.harness/engine/modules/task/chatnew.py#L25-L26}.

## Tool packs: the tool calling check

The tool calling check (`docs/11-tool-calling-check.md`) is not a harness feature; no harness code runs it. It is a manual probe a person runs once on a work computer, in an empty folder with an echo MCP server and a logging hook, to learn whether hooks run and whether MCP, extension and terminal calls reach a hook with full input and can be refused {src:docs/11-tool-calling-check.md#L1-L14}.

## Tool packs: what is enforced by code, what is only an instruction, and who decides

Code: the judgement of every terminal call of a listed program and of every MCP tool a pack names; the `.env` refusal; the refusal of `task allow` to the agent; the code a held call needs; the linked-ticket check; fail closed for pack programs {src:.harness/engine/modules/gate/handler.py#L758-L836}. Instruction only: the pack's skills (find the connection with `harness connections find`, ask when two fit) and the `AGENTS.md` rule not to do a held or refused call another way {src:.harness/toolpacks/sqlserver/skills/sqlserver-jobs/SKILL.md#L10} {src:AGENTS.md#L56-L59}.

Who decides: the company writes types, rules and connections and can only lower how far a connection opens; the person signs in, approves held calls, opens and closes connections per task, and allows MCP on their computer; the code applies the rules; the agent picks the call and may link a ticket, but opens nothing {src:.harness/contracts/toolpack/README.md#L125-L133}.

## Tool packs: why they are built this way, and what was tried before

Many companies switch MCP off by policy, and a SQL Server sign-in can follow the process (`runas /netonly`), so the agent never sees a password; but a DEV account that can write leaves the gate as the only check. So a pack works through a plain program in the terminal, with MCP optional; and a pack exists beside MCP because a server cannot say which call is a write, which item it changes, or whether the task is linked to it {src:docs/13-tool-packs-and-mcp.md#L1-L31}. Opening began in 1.7.4 as a switch per environment (`task allow --env dev`), with no global switch on purpose; 1.7.38 replaced it with opening one connection on the card of a held call, since with several systems "the task's DEV" names nothing exact {src:docs/07-release-notes.md#L741} {src:.harness/engine/modules/gate/handler.py#L336-L390}. The same release made the lists name what may pass rather than chase what to stop, and failed closed after a red team found calls the gate let through {src:docs/12-guardrails-and-gate.md#L22-L38}.

## Tool packs: where in the source

`.harness/contracts/toolpack/`: the protocol and connection list. Under `.harness/engine/`: `core/toolpacks.py` (packs, skills, links, MCP), `core/connections.py` (types, connections, `.env`, sign-in, `harness as`), `core/systems.py` and `modules/gate/external.py` (verbs, decisions, reading a command), `modules/gate/handler.py` (judging, held calls, openings, MCP, secrets), `modules/task/tasklife.py` (`task allow`, `task link`). Tests: `test_open_connection.py`, `test_toolpacks.py`, `test_gate_sqlserver.py` {src:.harness/engine/core/toolpacks.py#L340-L358}.

## Tool packs: common questions

**How does the agent reach SQL Server or Azure DevOps, and who decides what it may do?** Through a pack's program in the terminal, signed in through the VS Code process; the company's rules decide, and by default a read passes, a write waits for the person's code, a run is the person's, a destroy is refused {src:.harness/engine/core/systems.py#L1-L38}. The person may open one connection for one task; its writes then pass without asking.

**Can the agent read our passwords?** Not by the read and edit tools or a terminal command that names `.harness/.env`, nor by printing a sign-in variable: the gate refuses these {src:.harness/engine/modules/gate/handler.py#L624-L672}. A sign-in carried by variables, such as a SQL account's password, is plain text in that file and in the VS Code process's environment, so the real limit is the account's rights.

**How do I let the agent query our SQL Server?** Turn on the `sqlserver` pack, add the connection and sign in on Get ready, open VS Code from the board {src:.harness/toolpacks/README.md#L7-L31}. Step by step: tutorial 5 Outside systems and connections.

**Does an approved plan approve database writes?** Only calls the rules mark `task`; the sample packs mark none, so each held write needs its code or an opened connection {src:.harness/toolpacks/sqlserver/types/sqlserver.json#L254-L279}.

## Tool packs: limits

- **Unnamed MCP tools and unlisted tools are not judged,** and a named MCP write only asks, which the docs say shows no box under Allow all {src:.harness/engine/modules/gate/handler.py#L758-L836}.
- **`task allow --conn X --off` leaves a ticket board's linked items open (still so at 1.8.3).** For a type that opens only linked items, `--on` opens the linked items, but `--off` only takes X off the opened connections, where it never was, and says X is closed; `--links --off` or **Close** on the linked-items row closes them {src:.harness/engine/modules/task/tasklife.py#L520-L595}.
- **An opening is not cleared when the task closes;** it is ignored while closed and in force again when the same task is opened again, a new round included {src:.harness/engine/modules/task/task.py#L174-L182}.
- **Docs say a destroy is never opened; the code opens `DROP TABLE` and `TRUNCATE TABLE` on SQL Server DEV and IST.** The CLI help and the protocol still say "a destroy is still refused"; the newer messages say it right {src:.harness/engine/modules/task/commands.py#L358} {src:.harness/contracts/toolpack/README.md#L125-L133} {src:.harness/engine/core/messages.en.json#L3852}.
- **The gate reads text:** a program name built at run time, a script changed after the check or remote execution is not seen; for stronger isolation the protocol advises an operating-system sandbox {src:.harness/contracts/toolpack/README.md#L147-L158}.
- **The refuse list is best effort,** and `.harness/.env` is protected by file rights only on macOS and Linux {src:.harness/contracts/toolpack/README.md#L97-L113}.

## Tool packs: related files

15 The gate and guardrails; 14 Plans and approvals (approving a held call); 11 Task (where openings and links are kept); 20 Autorun; 23 Skills; 24 Setup, doctor and upgrade; 35 Known limits; 34 Version history. To do this step by step, see tutorial 5 Outside systems and connections in 3 Courses/Harness tutorials/ {src:.harness/toolpacks/README.md#L7-L31}.
