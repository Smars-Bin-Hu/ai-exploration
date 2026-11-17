#!/usr/bin/env python3
"""The demo workspace behind the board screenshots of the tutorials: harness 1.7.45, a made-up code repository and made-up tasks.

  python3 source/tutorials/shots/demo.py build [--fresh]   unpack 1.7.45 (git archive of ~/Developer/DE-agentic-harness), make repos/orders-service and the tasks
  python3 source/tutorials/shots/demo.py extra             add the states of the tour and tutorials 2 to 5 to a workspace built before (build does it too)
  python3 source/tutorials/shots/demo.py pack on|off       the demo tool pack and its connection on or off (capture.mjs turns it on for the outside screens)
  python3 source/tutorials/shots/demo.py kb on|off         the knowledge base registered or not (capture.mjs turns it off for a moment, for the yellow block)
  python3 source/tutorials/shots/demo.py hold              the held outside call of answer-ticket-t7 made again (it lives 10 minutes; the pack must be on)
  python3 source/tutorials/shots/demo.py start             start its board on 127.0.0.1:8845 in the background (`harness task board`, in a pseudo terminal)
  python3 source/tutorials/shots/demo.py pair              a new pairing link for a board that runs (a second `harness task board`, as a person would start it)
  python3 source/tutorials/shots/demo.py stop              stop the board
  python3 source/tutorials/shots/demo.py touch <task>      a fresh hook call in the task's session, so the board shows it as working (5 minutes)

The workspace is in DEMO (default `.claude/loops/2026-11-17-ai-exploration-map/demo/`, not in git). Everything in it is made up: no company, host or secret.
The board's browser is never opened: the board hands its pairing link to `opener.sh`, which writes it to `pair-url.txt` for capture.mjs.

How each state is made. The agent's side goes through the harness itself: the hook (`launch.py`, fed the payloads VS Code sends, as in
.harness/eval/fixtures/hooks/copilot-sdk/) and the agent's commands (`task new`, `fetch`, `diff`, `review start`, `promote`, `handoff`, `deliver`,
`intake convert`). The files the agent writes (REQ.md, PLAN.md, TODO.md, TASK.md, the DEV/ changes, COMMIT-MESSAGE.md) are written here. The person's
approvals (confirm-req, approve-plan, approve-promote) call the harness's own functions as a person at a terminal, typing the code they show. The
reviewer's answer goes through `taskreview.record`, what the hook calls when the reviewer stops. The one chat in VS Code (a task that waits for an
answer) is made from the board by capture.mjs --make-chat.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEMO = Path(os.environ.get("HARNESS_DEMO") or REPO / ".claude/loops/2026-11-17-ai-exploration-map/demo")
HARNESS_GIT = Path(os.environ.get("HARNESS_GIT") or Path.home() / "Developer/DE-agentic-harness")
VERSION = "1.7.45"
PORT = 8845
H = DEMO / "harness"
REPOS = DEMO / "repos"
ORDERS = REPOS / "orders-service"
TASKS = H / ".workspace/sandbox/tasks"


def run(args, cwd=H, stdin=None, check=True):
    done = subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True)
    if check and done.returncode != 0:
        sys.exit(f"failed: {' '.join(map(str, args))}\n{done.stdout}\n{done.stderr}")
    return done


def cli(*args, check=True):
    """An agent's command: `harness <args>`, its answer as JSON."""
    done = run([sys.executable, ".harness/engine/cli.py", *args, "--json"], check=check)
    try:
        return json.loads(done.stdout)
    except ValueError:
        return {"text": done.stdout, "error": done.stderr}


def session_id(number):
    return f"5e1f0c2a-0000-4000-8000-{number:012d}"


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())


def hook(event, session, **fields):
    """What VS Code hands the hook for one event of a Copilot chat."""
    payload = {"hook_event_name": event, "session_id": session, "timestamp": stamp(), "cwd": str(H), **fields}
    return run([sys.executable, ".harness/engine/launch.py"], stdin=json.dumps(payload)).stdout


def prompt(session, text, first=False):
    if first:
        hook("SessionStart", session, source="new", initial_prompt=text)
    hook("UserPromptSubmit", session, prompt=text)


def tool(session, command):
    hook("PostToolUse", session, tool_name="Bash", tool_input={"command": command, "description": "run"},
         tool_result={"result_type": "success", "text_result_for_llm": "<exited with exit code 0>"})


def stop(session):
    hook("Stop", session, transcript_path="<COPILOT_HOME>/session-state/events.jsonl", stop_reason="end_turn", stop_hook_active=False)


PERSON = r"""
import re, sys
from pathlib import Path
sys.path.insert(0, ".harness/engine")
from modules.task import task, taskreview
root = Path(".").resolve()
def reader(question):
    print(question)
    return re.search(r"type ([0-9A-F]{6}) \(", question).group(1)
what, name = sys.argv[1], sys.argv[2]
if what == "confirm-req":
    print(task.confirm_req(root, name, reader=reader, interactive=True))
elif what == "approve-plan":
    print(task.approve_plan(root, name, reader=reader, interactive=True))
elif what == "approve-promote":
    print(task.approve_promote(root, name, reader=reader, interactive=True))
elif what == "verdict":
    print(taskreview.record(root, ".workspace/sandbox/tasks/" + name, sys.stdin.read()))
"""


def person(what, name, stdin=None):
    """A person at a terminal (or, for `verdict`, the hook when the reviewer stops)."""
    return run([sys.executable, "-c", PERSON, what, name], stdin=stdin).stdout


def write(name, relative, text):
    path = TASKS / name / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n"), encoding="utf-8")


def task_md(name, kind, tier, status, now, nxt, decided="none"):
    write(name, "TASK.md", f"""
# TASK: {name}

> The handover file. A new session reads this file first, then what it points to. Keep it within one screen. Update it every time before you stop.

- **Kind**: {kind}
- **Tier**: {tier}
- **Created**: 2026-11-17
- **Updated**: 2026-11-17
- **Status**: {status}
- **Doing now**: {now}
- **Next step**: {nxt}

## Files to read

1. [REQ.md](REQ.md)
2. [PLAN.md](PLAN.md)

## Decided

{decided}

## Open questions

none
""")


def req_md(name, what, not_do, done_t, done_r="none", done_a="none", unclear="none"):
    write(name, "REQ.md", f"""
# REQ: {name}

> The requirement. The agent writes it from the conversation with the user. It counts only after the user has read it. When the requirement changes, change this file and add a line at the end.
> The user's own documents (BRD, emails, screenshots) go in `REQ/`. The agent reads them and never changes them.

- **User confirmed**: not yet

## What to do

{what}

## What not to do

{not_do}

## Done when

### Shown by the task files

{done_t}

### Shown by a run the user does before the promote

{done_r}

### Shown after the promote

{done_a}

## Source

Conversation

## Not clear yet

{unclear}

## Changes

none
""")


def plan_md(name, files, steps, check, risks):
    write(name, "PLAN.md", f"""
# PLAN: {name}

## Files to change

{files}

## Steps

{steps}

## How it will be checked

{check}

## Risks

{risks}
""")


def todo_md(name, items):
    write(name, "TODO.md", f"# TODO: {name}\n\n> The list of steps. Tick each step when it is done. Write \"<- now\" at the end of the line of the step in progress.\n\n" + "\n".join(items) + "\n")


def edit(name, relative, old, new):
    path = TASKS / name / "DEV/orders-service" / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        sys.exit(f"{name}: {old!r} is not in {relative}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def new_task(number, name, kind, words, tier=""):
    session = session_id(number)
    prompt(session, words, first=True)
    cli("task", "new", name, "--kind", kind, "--session-id", session, *(["--tier", tier] if tier else []))
    tool(session, f"harness task new {name} --kind {kind}")
    return session


# --- the code repository ------------------------------------------------------------------------------------------------------------

ORDERS_FILES = {
    "README.md": """# orders-service

A small demo service: takes orders, checks stock and sends a confirmation.

- `orders/api.py`: the HTTP handlers
- `orders/client.py`: calls to the stock service
- `orders/settings.py`: timeouts and limits
- `orders/pricing.py`: order totals
""",
    "orders/__init__.py": "",
    "orders/settings.py": '''"""Settings of the orders service."""

STOCK_TIMEOUT_SECONDS = 5
MAX_ITEMS_PER_ORDER = 50
RETRY_COUNT = 0
''',
    "orders/client.py": '''"""Calls to the stock service."""

import json
import urllib.request

from . import settings


def stock_of(sku: str, base_url: str) -> int:
    """How many items of `sku` are in stock."""
    with urllib.request.urlopen(f"{base_url}/stock/{sku}", timeout=settings.STOCK_TIMEOUT_SECONDS) as answer:
        return int(json.load(answer)["count"])
''',
    "orders/api.py": '''"""HTTP handlers of the orders service."""

from . import client, pricing, settings


def create_order(items, base_url):
    """Check stock for every item, then accept the order."""
    if len(items) > settings.MAX_ITEMS_PER_ORDER:
        return {"ok": False, "error": "too many items"}
    for item in items:
        if client.stock_of(item["sku"], base_url) < item["count"]:
            return {"ok": False, "error": f"out of stock: {item['sku']}"}
    return {"ok": True, "total": pricing.total(items)}
''',
    "orders/pricing.py": '''"""Order totals."""


def total(items):
    """The sum of price times count, in cents."""
    return sum(int(item["price"] * 100) * item["count"] for item in items)
''',
    "tests/test_api.py": '''from unittest import mock

from orders import api


def test_too_many_items_is_refused():
    assert api.create_order([{"sku": "A1", "count": 1, "price": 1.0}] * 51, "http://stock.test")["ok"] is False


def test_in_stock_is_accepted():
    with mock.patch("orders.client.stock_of", return_value=10):
        assert api.create_order([{"sku": "A1", "count": 2, "price": 2.5}], "http://stock.test")["ok"] is True
''',
}


def make_repo():
    ORDERS.mkdir(parents=True)
    for relative, text in ORDERS_FILES.items():
        path = ORDERS / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git = ["git", "-C", str(ORDERS)]
    run(git + ["init", "-q", "-b", "main"], cwd=DEMO)
    run(git + ["config", "user.name", "Demo Developer"], cwd=DEMO)
    run(git + ["config", "user.email", "dev@example.com"], cwd=DEMO)
    run(git + ["add", "-A"], cwd=DEMO)
    run(git + ["commit", "-qm", "First version of the orders service"], cwd=DEMO)


# --- documents for the Intake tab ----------------------------------------------------------------------------------------------------


def docx(path, paragraphs):
    body = "".join(f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>' if style else
                   f'<w:p><w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>' for style, text in paragraphs)
    with zipfile.ZipFile(path, "w") as out:
        out.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        out.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        out.writestr("word/document.xml", '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                     f"<w:body>{body}</w:body></w:document>")


def xlsx(path, sheets):
    def cell(ref, value):
        if isinstance(value, (int, float)):
            return f'<c r="{ref}"><v>{value}</v></c>'
        return f'<c r="{ref}" t="inlineStr"><is><t>{value}</t></is></c>'

    with zipfile.ZipFile(path, "w") as out:
        out.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                     + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, len(sheets) + 1))
                     + "</Types>")
        out.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        out.writestr("xl/workbook.xml", '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                     'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                     + "".join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i, (name, _) in enumerate(sheets, 1)) + "</sheets></workbook>")
        out.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1))
                     + "</Relationships>")
        for i, (_, rows) in enumerate(sheets, 1):
            data = "".join(f'<row r="{r}">' + "".join(cell(f"{chr(65 + c)}{r}", v) for c, v in enumerate(row)) + "</row>" for r, row in enumerate(rows, 1))
            out.writestr(f"xl/worksheets/sheet{i}.xml", '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                         f"<sheetData>{data}</sheetData></worksheet>")


# --- the tasks ---------------------------------------------------------------------------------------------------------------------


def through_plan(number, name, words, req, plan, approve=True):
    """A development task up to an approved plan (or a plan that waits, approve=False)."""
    session = new_task(number, name, "dev", words)
    req_md(name, **req)
    task_md(name, "dev", "full", "waiting for the user to confirm the requirement", "The requirement is written.", "The user confirms REQ.md on the task page.")
    stop(session)
    person("confirm-req", name)
    prompt(session, "I confirmed the requirement. Go on.")
    plan_md(name, **plan)
    task_md(name, "dev", "full", "waiting for the user to approve the plan", "The plan is written.", "The user approves PLAN.md on the task page.",
            "2026-11-17: requirement confirmed by the user")
    tool(session, f"write .workspace/sandbox/tasks/{name}/PLAN.md")
    stop(session)
    if approve:
        person("approve-plan", name)
        prompt(session, "Plan approved. Go on.")
    return session


def build(fresh):
    if H.exists():
        if not fresh:
            sys.exit(f"{H} exists: use --fresh to make it again (the board is stopped first)")
        stop_board()
        shutil.rmtree(DEMO / "harness")
        shutil.rmtree(REPOS, ignore_errors=True)
    DEMO.mkdir(parents=True, exist_ok=True)
    H.mkdir()
    archive = subprocess.run(["git", "-C", str(HARNESS_GIT), "archive", VERSION], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(H)], input=archive, check=True)
    REPOS.mkdir(exist_ok=True)
    make_repo()
    # the repository by name rather than by repos_root, so the Enter screen says "1 repository" and no folder of this computer
    (H / ".harness/policies/target.override.json").write_text(json.dumps({"repos_root": "", "repos": {"orders-service": {"path": str(ORDERS)}}}, indent=2) + "\n", encoding="utf-8")
    (H / ".harness/policies/user.override.json").write_text(json.dumps({"language": "en", "name": "Alex", "setup_done": True}, indent=2) + "\n", encoding="utf-8")
    (DEMO / "opener.sh").write_text('#!/bin/sh\n# Stands in for the browser the board opens: it keeps the pairing link for capture.mjs.\nprintf \'%s\\n\' "$1" > "$(dirname "$0")/pair-url.txt"\n', encoding="utf-8")
    (DEMO / "opener.sh").chmod(0o755)

    # 1. Written back, then closed by the board: the Changes tab of a closed task, with the commit message.
    name = "raise-stock-timeout"
    session = through_plan(1, name, "Raise the timeout of the stock calls in orders-service from 5 to 10 seconds.", dict(
        what="Raise the timeout of the calls to the stock service in `orders-service` from 5 to 10 seconds. Orders fail at busy hours because the stock service answers in 6 to 8 seconds.",
        not_do="Do not change the retry count or the order limits.",
        done_t="- [T1] `STOCK_TIMEOUT_SECONDS` in `orders/settings.py` is 10.\n- [T2] Nothing else in `orders-service` changes."),
        dict(files="- `orders-service/orders/settings.py`: `STOCK_TIMEOUT_SECONDS` from 5 to 10.",
             steps="1. Fetch `orders/settings.py`.\n2. Change the value.\n3. Dry run of the write-back.",
             check="Read the diff: one line changes ([T1], [T2]).",
             risks="An order waits up to 10 seconds for the stock service before it fails."))
    cli("task", "fetch", "orders-service/orders/settings.py", "--task", name)
    edit(name, "orders/settings.py", "STOCK_TIMEOUT_SECONDS = 5", "STOCK_TIMEOUT_SECONDS = 10")
    todo_md(name, ["- [x] Fetch orders/settings.py", "- [x] Raise STOCK_TIMEOUT_SECONDS to 10", "- [x] Dry run of the write-back"])
    cli("task", "diff", "--task", name)
    cli("task", "promote", "--dry-run", "--task", name)
    stop(session)
    person("approve-promote", name)
    prompt(session, "Approved. Write it back.")
    cli("task", "promote", "--task", name)
    write(name, "COMMIT-MESSAGE.md", """
Raise the stock call timeout to 10 seconds

Orders failed at busy hours: the stock service answers in 6 to 8 seconds,
and the calls gave up after 5.
""")
    task_md(name, "dev", "full", "done", "Written back to feature/raise-stock-timeout.", "The user commits the branch.")
    stop(session)
    # the person commits the branch and goes back to main, so the next write-back finds a clean repository
    git = ["git", "-C", str(ORDERS)]
    run(git + ["add", "-A"], cwd=DEMO)
    run(git + ["commit", "-qm", "Raise the stock call timeout to 10 seconds"], cwd=DEMO)
    run(git + ["checkout", "-q", "main"], cwd=DEMO)

    # 2. The dry run is done: the Changes tab waits for Approve promote.
    name = "limit-order-items"
    session = through_plan(2, name, "Lower the item limit of an order in orders-service to 20.", dict(
        what="An order in `orders-service` may hold at most 20 items, not 50. The error says the limit.",
        not_do="Do not change the stock calls.",
        done_t="- [T1] `MAX_ITEMS_PER_ORDER` is 20.\n- [T2] The refusal says `at most 20 items`.\n- [T3] The test of the limit uses 21 items."),
        dict(files="- `orders-service/orders/settings.py`: the limit.\n- `orders-service/orders/api.py`: the words of the refusal.\n- `orders-service/tests/test_api.py`: the test of the limit.",
             steps="1. Fetch the three files.\n2. Change the limit, the refusal and the test.\n3. Dry run of the write-back.",
             check="Read the diff against [T1] to [T3].",
             risks="Orders of 21 to 50 items that worked before are refused."))
    cli("task", "fetch", "orders-service/orders/settings.py", "orders-service/orders/api.py", "orders-service/tests/test_api.py", "--task", name)
    edit(name, "orders/settings.py", "MAX_ITEMS_PER_ORDER = 50", "MAX_ITEMS_PER_ORDER = 20")
    edit(name, "orders/api.py", 'return {"ok": False, "error": "too many items"}', 'return {"ok": False, "error": f"at most {settings.MAX_ITEMS_PER_ORDER} items"}')
    edit(name, "tests/test_api.py", "* 51,", "* 21,")
    todo_md(name, ["- [x] Fetch the three files", "- [x] Lower MAX_ITEMS_PER_ORDER to 20", "- [x] Say the limit in the refusal", "- [x] Test with 21 items", "- [x] Dry run of the write-back"])
    cli("task", "diff", "--task", name)
    cli("task", "promote", "--dry-run", "--task", name)
    task_md(name, "dev", "full", "waiting for the user to approve the promote", "The dry run is done.", "The user approves the promote on the task page.")
    stop(session)

    # 3. Two independent checks wanted: one FAIL, then two passes. The Review tab.
    name = "validate-sku-format"
    session = session_id(3)
    prompt(session, "Refuse an order whose SKU is not two capital letters and four digits, in orders-service. [review]=2", first=True)
    cli("task", "new", name, "--kind", "dev", "--session-id", session)
    req_md(name, what="`orders-service` refuses an order line whose SKU is not two capital letters followed by four digits, such as `AB1234`, before it asks the stock service.",
           not_do="Do not change the stock calls or the limits.",
           done_t="- [T1] `orders/api.py` checks every SKU against `^[A-Z]{2}[0-9]{4}$` before the stock call.\n- [T2] The refusal names the SKU.\n- [T3] A test sends a wrong SKU.")
    task_md(name, "dev", "full", "waiting for the user to confirm the requirement", "The requirement is written.", "The user confirms REQ.md.")
    stop(session)
    person("confirm-req", name)
    prompt(session, "Confirmed. Go on.")
    plan_md(name, files="- `orders-service/orders/api.py`: the check.\n- `orders-service/tests/test_api.py`: a test of a wrong SKU.",
            steps="1. Fetch both files.\n2. Add the check before the stock call.\n3. Add the test.\n4. Two independent checks.", check="[T1] to [T3], by the reviewer.",
            risks="An SKU of another form that is in use today is refused.")
    stop(session)
    person("approve-plan", name)
    prompt(session, "Approved.")
    cli("task", "fetch", "orders-service/orders/api.py", "orders-service/tests/test_api.py", "--task", name)
    edit(name, "orders/api.py", '"""HTTP handlers of the orders service."""\n\nfrom . import client, pricing, settings\n',
         '"""HTTP handlers of the orders service."""\n\nimport re\n\nfrom . import client, pricing, settings\n\nSKU = re.compile(r"^[A-Z]{2}[0-9]{4}$")\n')
    edit(name, "orders/api.py", "    for item in items:\n        if client", '    for item in items:\n        if not SKU.match(item["sku"]):\n            return {"ok": False, "error": "wrong SKU"}\n        if client')
    todo_md(name, ["- [x] Fetch api.py and test_api.py", "- [x] Check the SKU before the stock call", "- [ ] Test a wrong SKU", "- [ ] Two independent checks"])
    cli("task", "diff", "--task", name)
    cli("task", "review", "start", "--task", name)
    line = next(i for i, text in enumerate((TASKS / name / "DEV/orders-service/orders/api.py").read_text().splitlines(), 1) if "wrong SKU" in text)
    person("verdict", name, stdin=f"VERDICT: FAIL\n- .workspace/sandbox/tasks/{name}/DEV/orders-service/orders/api.py:{line} the refusal does not name the SKU | basis: REQ.md [T2]\n"
                                  f"- .workspace/sandbox/tasks/{name}/DEV/orders-service/tests/test_api.py:1 no test sends a wrong SKU | basis: REQ.md [T3]\n")
    prompt(session, "(the agent goes on after the check)")
    edit(name, "orders/api.py", '"error": "wrong SKU"}', '"error": f"wrong SKU: {item[\'sku\']}"}')
    test = TASKS / name / "DEV/orders-service/tests/test_api.py"
    test.write_text(test.read_text() + '\n\ndef test_a_wrong_sku_is_refused():\n    assert api.create_order([{"sku": "ab12", "count": 1, "price": 1.0}], "http://stock.test") == {"ok": False, "error": "wrong SKU: ab12"}\n', encoding="utf-8")
    todo_md(name, ["- [x] Fetch api.py and test_api.py", "- [x] Check the SKU before the stock call", "- [x] Test a wrong SKU", "- [ ] Two independent checks <- now"])
    cli("task", "diff", "--task", name)
    api = (TASKS / name / "DEV/orders-service/orders/api.py").read_text().splitlines()
    check_line = next(i for i, text in enumerate(api, 1) if "SKU.match" in text)
    name_line = next(i for i, text in enumerate(api, 1) if "wrong SKU:" in text)
    test_line = len(test.read_text().splitlines()) - 1
    passed = (f"VERDICT: PASS\n- .workspace/sandbox/tasks/{name}/DEV/orders-service/orders/api.py:{check_line} the SKU is checked before the stock call | basis: REQ.md [T1]\n"
              f"- .workspace/sandbox/tasks/{name}/DEV/orders-service/orders/api.py:{name_line} the refusal names the SKU | basis: REQ.md [T2]\n"
              f"- .workspace/sandbox/tasks/{name}/DEV/orders-service/tests/test_api.py:{test_line} a test sends a wrong SKU | basis: REQ.md [T3]\n")
    for _ in range(2):
        cli("task", "review", "start", "--task", name)
        person("verdict", name, stdin=passed)
    todo_md(name, ["- [x] Fetch api.py and test_api.py", "- [x] Check the SKU before the stock call", "- [x] Test a wrong SKU", "- [x] Two independent checks", "- [ ] Dry run of the write-back"])
    task_md(name, "dev", "full", "in progress", "Two checks passed.", "Dry run of the write-back.")
    stop(session)

    # 4. A run on DEV before the write-back: the task waits for your run, with the form.
    name = "cache-stock-counts"
    session = through_plan(4, name, "Keep the stock counts for 30 seconds in orders-service, so a busy hour asks the stock service less.", dict(
        what="`orders-service` keeps each stock count it read for 30 seconds and asks the stock service again only after that.",
        not_do="Do not keep counts across a restart.",
        done_t="- [T1] `orders/client.py` keeps a count for 30 seconds.",
        done_r="- [R1] DEV: run `load-test --orders 500` against orders-service on DEV; the stock service gets fewer than 100 calls."),
        dict(files="- `orders-service/orders/client.py`: a small cache in memory.", steps="1. Fetch `client.py`.\n2. Add the cache.\n3. The user runs the load test on DEV.",
             check="[T1] in the diff; [R1] by the user's run.", risks="An order may see a count up to 30 seconds old."))
    cli("task", "fetch", "orders-service/orders/client.py", "--task", name)
    edit(name, "orders/client.py", "import json\nimport urllib.request\n", "import json\nimport time\nimport urllib.request\n")
    edit(name, "orders/client.py", 'def stock_of(sku: str, base_url: str) -> int:\n    """How many items of `sku` are in stock."""\n',
         'KEPT = {}\nKEEP_SECONDS = 30\n\n\ndef stock_of(sku: str, base_url: str) -> int:\n    """How many items of `sku` are in stock (a count is kept for 30 seconds)."""\n'
         '    kept = KEPT.get(sku)\n    if kept and time.monotonic() - kept[0] < KEEP_SECONDS:\n        return kept[1]\n')
    todo_md(name, ["- [x] Fetch client.py", "- [x] Keep each count for 30 seconds", "- [ ] The user runs the load test on DEV [R1] <- now", "- [ ] Dry run of the write-back"])
    cli("task", "diff", "--task", name)
    cli("task", "handoff", "run", "--env", "DEV", "--what", "Run load-test --orders 500 against orders-service on DEV and send back how many calls the stock service got.", "--task", name)
    task_md(name, "dev", "full", "waiting for the user's run on DEV", "The cache is written.", "The user runs the load test on DEV [R1].")
    stop(session)

    # 5. Working: the plan is approved, the TODO is half done (capture.mjs touches its session so the board shows it as working).
    name = "retry-stock-calls"
    session = through_plan(5, name, "Retry a stock call once when it times out, in orders-service.", dict(
        what="When a call to the stock service times out, `orders-service` tries it once more before it refuses the order.",
        not_do="No retry for an answer that came back with an error.",
        done_t="- [T1] `RETRY_COUNT` is 1.\n- [T2] `stock_of` retries a timeout once.\n- [T3] A test of a timeout, then an answer."),
        dict(files="- `orders-service/orders/settings.py`\n- `orders-service/orders/client.py`\n- `orders-service/tests/test_client.py` (new)",
             steps="1. Fetch the files.\n2. Set `RETRY_COUNT` to 1.\n3. Retry on a timeout.\n4. Add the test.\n5. Dry run.", check="[T1] to [T3] in the diff.", risks="A slow stock service now takes twice as long to refuse."))
    cli("task", "fetch", "orders-service/orders/settings.py", "orders-service/orders/client.py", "--task", name)
    edit(name, "orders/settings.py", "RETRY_COUNT = 0", "RETRY_COUNT = 1")
    todo_md(name, ["- [x] Fetch settings.py and client.py", "- [x] Set RETRY_COUNT to 1", "- [ ] Retry a timeout once in stock_of <- now", "- [ ] Add tests/test_client.py", "- [ ] Dry run of the write-back"])
    task_md(name, "dev", "full", "in progress", "Retrying a timeout in stock_of.", "Add the test.")
    tool(session, f"edit .workspace/sandbox/tasks/{name}/DEV/orders-service/orders/client.py")

    # 6. The plan waits for Approve plan.
    through_plan(6, "add-order-notes", "Let a customer add a short note to an order in orders-service.", dict(
        what="An order in `orders-service` may carry a note from the customer, at most 200 characters. The confirmation repeats it.",
        not_do="No change to totals or stock.",
        done_t="- [T1] `create_order` takes an optional `note`.\n- [T2] A note longer than 200 characters is refused.\n- [T3] The answer carries the note."),
        dict(files="- `orders-service/orders/api.py`: the `note` argument and its check.\n- `orders-service/tests/test_api.py`: two tests.",
             steps="1. Fetch `api.py` and `test_api.py`.\n2. Add `note` to `create_order`, refuse more than 200 characters.\n3. Put the note in the answer.\n4. Add a test of a long note and of a short one.\n5. Dry run of the write-back.",
             check="Each of [T1] to [T3] has a line in the diff and a test.",
             risks="A client that sends `note` today gets it back in the answer: none is known."), approve=False)

    # 7. The requirement waits for Confirm requirement.
    name = "fix-total-rounding"
    session = new_task(7, name, "dev", "Order totals in orders-service are a cent off for some prices. Fix it.")
    req_md(name, what="`pricing.total` in `orders-service` gives a total a cent too low for some prices, such as 19.99 (`int(19.99 * 100)` is 1998). It must round each price to whole cents.",
           not_do="Do not change how prices are stored or sent.",
           done_t="- [T1] `pricing.total` rounds each price to cents.\n- [T2] A test: two items at 19.99 make 3998.",
           unclear="none")
    task_md(name, "dev", "full", "waiting for the user to confirm the requirement", "The requirement is written.", "The user confirms REQ.md on the task page.")
    stop(session)

    # 8. Documents for the Intake tab.
    name = "import-price-list"
    session = new_task(8, name, "dev", "Prices should come from the price list the sales team sends. The documents follow.")
    docs = DEMO / "documents"
    docs.mkdir(exist_ok=True)
    docx(docs / "price-list-request.docx", [("Title", "Price list import"), ("", "Version 0.3, draft"),
         ("Heading1", "What we need"), ("", "Each Monday the sales team sends a price list. Orders should use these prices from the next day."),
         ("Heading1", "Rules"), ("", "A price is in euros with two decimals. A product missing from the list keeps its old price."),
         ("Heading1", "Revision history"), ("", "0.1 first draft; 0.2 rules added; 0.3 example added")])
    xlsx(docs / "price-list.xlsx", [("Prices", [["SKU", "Name", "Price"], ["AB1234", "Blue mug", 7.5], ["AB1235", "Red mug", 7.5], ["CD2001", "Tea towel", 4.25], ["CD2002", "Apron", 12.0]]),
                                   ("Notes", [["Note"], ["Prices valid from Tuesday"]])])
    cli("task", "intake", "convert", str(docs / "price-list-request.docx"), str(docs / "price-list.xlsx"), "--task", name)
    task_md(name, "dev", "full", "waiting for the user's documents", "The documents are converted.", "The user trims them and creates INTAKE.md.")
    stop(session)

    # 9. An RCA delivered: to accept.
    name = "why-orders-slow"
    session = new_task(9, name, "rca", "Find out why orders were slow on Monday morning and write an RCA.")
    req_md(name, what="Find out why creating an order took 6 to 8 seconds on Monday between 9:00 and 10:00, and write it as an RCA.",
           not_do="Change no code.", done_t="- [T1] `RCA.md` names the root cause with evidence.")
    write(name, "RCA.md", """
# RCA: slow orders on Monday morning

## What was seen

Creating an order took 6 to 8 seconds between 9:00 and 10:00; at other times under 1 second.

## Root cause

Each order line asks the stock service once (`orders/client.py`, `stock_of`). On Monday the price list import ran from 9:00 and kept the stock service busy, so each call took 1 to 2 seconds. An order of 5 lines waited up to 8 seconds.

## Evidence

- The stock service log: answer times of 1.2 to 1.9 s from 9:02 to 9:58.
- The import job ran from 9:00 to 9:57.

## What would help

Keep stock counts for a short time (a separate task), or move the import out of business hours.
""")
    task_md(name, "rca", "medium", "waiting for the user to accept", "The RCA is written.", "The user accepts the task.")
    cli("task", "deliver", "--task", name, "--summary", "The root cause: the Monday price list import kept the stock service busy, and each order line waits for one stock call. The evidence and two ways out are in RCA.md.")
    stop(session)
    extra()
    print(f"built: {H}")


# --- more states, for the tour and the tutorials 2 to 5 (demo.py extra adds them to a workspace built before) -----------------------

KB = H / "knowledge-base"
SHOP = REPOS / "shop-dw"

SHOP_FILES = {
    "Shop/Shop.sqlproj": "<Project Sdk=\"Microsoft.Build.Sql\"><PropertyGroup><Name>Shop</Name></PropertyGroup></Project>\n",
    "Shop/dbo/Tables/order_lines.sql": "CREATE TABLE dbo.order_lines (\n    order_id INT NOT NULL,\n    sku CHAR(6) NOT NULL,\n    item_count INT NOT NULL,\n    price DECIMAL(9, 2) NOT NULL\n);\n",
    "Shop/dbo/Tables/orders.sql": "CREATE TABLE dbo.orders (\n    order_id INT NOT NULL PRIMARY KEY,\n    total DECIMAL(11, 2) NOT NULL,\n    loaded_at DATETIME2 NOT NULL\n);\n",
    "Shop/dbo/Tables/summary.sql": "CREATE TABLE dbo.summary (\n    day DATE NOT NULL PRIMARY KEY,\n    order_count INT NOT NULL,\n    total DECIMAL(13, 2) NOT NULL\n);\n",
    "Shop/dbo/Tables/stock.sql": "CREATE TABLE dbo.stock (\n    sku CHAR(6) NOT NULL PRIMARY KEY,\n    on_hand INT NOT NULL\n);\n",
    "Shop/dbo/Stored Procedures/usp_load_orders.sql": "CREATE PROCEDURE dbo.usp_load_orders\nAS\nBEGIN\n    -- one row per order, from its lines\n    INSERT INTO dbo.orders (order_id, total, loaded_at)\n    SELECT l.order_id, SUM(l.item_count * l.price), SYSDATETIME()\n    FROM dbo.order_lines AS l\n    WHERE NOT EXISTS (SELECT 1 FROM dbo.orders AS o WHERE o.order_id = l.order_id)\n    GROUP BY l.order_id;\nEND\nGO\n",
    "Shop/dbo/Stored Procedures/usp_build_summary.sql": "CREATE PROCEDURE dbo.usp_build_summary\nAS\nBEGIN\n    DELETE FROM dbo.summary WHERE day = CAST(SYSDATETIME() AS DATE);\n    INSERT INTO dbo.summary (day, order_count, total)\n    SELECT CAST(o.loaded_at AS DATE), COUNT(*), SUM(o.total)\n    FROM dbo.orders AS o\n    WHERE o.loaded_at >= CAST(SYSDATETIME() AS DATE)\n    GROUP BY CAST(o.loaded_at AS DATE);\nEND\nGO\n",
    "Shop/dbo/Stored Procedures/usp_count_stock.sql": "CREATE PROCEDURE dbo.usp_count_stock\nAS\nBEGIN\n    UPDATE s SET on_hand = s.on_hand - l.item_count\n    FROM dbo.stock AS s\n    JOIN dbo.order_lines AS l ON l.sku = s.sku;\nEND\nGO\n",
    "jobs/Shop_Orders.sql": "EXEC msdb.dbo.sp_add_job @job_name = N'Shop_Orders', @enabled = 1;\nEXEC msdb.dbo.sp_add_jobstep @job_name = N'Shop_Orders', @step_name = N'Load orders', @subsystem = N'TSQL', @database_name = N'Shop', @command = N'EXEC dbo.usp_load_orders';\nEXEC msdb.dbo.sp_add_jobstep @job_name = N'Shop_Orders', @step_name = N'Summary', @subsystem = N'TSQL', @database_name = N'Shop', @command = N'EXEC dbo.usp_build_summary';\nEXEC msdb.dbo.sp_add_jobschedule @job_name = N'Shop_Orders', @name = N'Hourly', @freq_type = 4, @freq_interval = 1, @freq_subday_type = 8, @freq_subday_interval = 1;\n",
    "jobs/Shop_Stock.sql": "EXEC msdb.dbo.sp_add_job @job_name = N'Shop_Stock', @enabled = 1;\nEXEC msdb.dbo.sp_add_jobstep @job_name = N'Shop_Stock', @step_name = N'Count stock', @subsystem = N'TSQL', @database_name = N'Shop', @command = N'EXEC dbo.usp_count_stock';\nEXEC msdb.dbo.sp_add_jobschedule @job_name = N'Shop_Stock', @name = N'Nightly', @freq_type = 4, @freq_interval = 1;\n",
}

FACTS = [
    {"from": "job:Shop_Orders", "kind": "calls", "to": "sp:Shop.dbo.usp_load_orders"},
    {"from": "sp:Shop.dbo.usp_load_orders", "kind": "writes", "to": "table:Shop.dbo.orders"},
    {"from": "sp:Shop.dbo.usp_build_summary", "kind": "reads", "to": "table:Shop.dbo.orders"},
]


def git_repo(folder, files, message):
    folder.mkdir(parents=True, exist_ok=True)
    for relative, text in files.items():
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git = ["git", "-C", str(folder)]
    if not (folder / ".git").exists():
        run(git + ["init", "-q", "-b", "main"], cwd=DEMO)
        run(git + ["config", "user.name", "Demo Developer"], cwd=DEMO)
        run(git + ["config", "user.email", "dev@example.com"], cwd=DEMO)
    run(git + ["add", "-A"], cwd=DEMO)
    run(git + ["commit", "-qm", message], cwd=DEMO)


def edit_dev(name, relative, old, new):
    path = TASKS / name / "DEV" / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        sys.exit(f"{name}: {old!r} is not in {relative}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def pre(session, tool_name, tool_input):
    """A tool call the agent is about to make: the gate's answer (allow, deny, or held)."""
    return hook("PreToolUse", session, tool_name=tool_name, tool_input=tool_input)


def read(session, path):
    """The agent read a file: the gate let it through, and the read finished (a read of the knowledge base is kept for its Last read)."""
    pre(session, "Read", {"path": str(path)})
    hook("PostToolUse", session, tool_name="Read", tool_input={"path": str(path)}, tool_result={"result_type": "success", "text_result_for_llm": "(the file)"})


def make_kb():
    """A made-up SQL repository (shop-dw), and a knowledge base for it: the sample toolkit, the company's content, two domains listed."""
    git_repo(SHOP, SHOP_FILES, "Shop data warehouse: tables, procedures and jobs")
    kit = H / ".harness/examples/kb-toolkits/sqlserver"
    files = {
        "README.md": "# Knowledge base\n\nWhat our code does, learned from the code. Made up for a demo.\n\n## Domains\n\n| Domain | What it does | Entry points | Status |\n| --- | --- | --- | --- |\n"
                     "| orders | Loads orders from their lines and builds the daily summary | `job:Shop_Orders` | learned |\n"
                     "| inventory | Counts stock against the order lines each night | `job:Shop_Stock` | not started |\n\n## Shared\n\nnone\n\n## Glossary\n\n[glossary.md](glossary.md)\n",
        "glossary.md": "# Glossary\n\n| Term | Meaning |\n| --- | --- |\n| order line | one product of an order, with its count and price |\n| summary | one row per day: how many orders, and their total |\n",
        "toolkit/toolkit.json": (kit / "toolkit.json").read_text(),
        "toolkit/extract_sqlserver.py": (kit / "extract_sqlserver.py").read_text(),
        "toolkit/facts.jsonl": "".join(json.dumps(fact) + "\n" for fact in FACTS),
        "company/company.json": json.dumps({"schema_version": 1, "name": "Demo company", "skill_prefix": "demo"}, indent=2) + "\n",
        "domains/.gitkeep": "",
    }
    git_repo(KB, files, "Knowledge base: toolkit, company content, the list of domains")
    policy = H / ".harness/policies/target.override.json"
    data = json.loads(policy.read_text())
    data["repos"]["shop-dw"] = {"path": str(SHOP)}
    data["repos"]["kb"] = {"path": "knowledge-base", "knowledge_base": True}
    policy.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    # the toolkit is for shop-dw only (orders-service is Python), then the map, then a blind reading against it (kb audit)
    kit_file = KB / "toolkit/toolkit.json"
    kit_data = json.loads(kit_file.read_text())
    kit_data["repos"] = ["shop-dw"]
    kit_file.write_text(json.dumps(kit_data, indent=2) + "\n", encoding="utf-8")
    cli("kb", "map", "--fresh")
    answers = DEMO / "audit-answers.jsonl"
    answers.write_text("".join(json.dumps(item) + "\n" for item in [
        {"from": "job:Shop_Stock", "kind": "calls", "to": "dbo.usp_count_stock", "line": 2},
        {"from": "job:Shop_Orders", "kind": "calls", "to": "dbo.usp_load_orders", "line": 2},
        {"from": "job:Shop_Orders", "kind": "calls", "to": "dbo.usp_build_summary", "line": 3},
        {"from": "sp:Shop.dbo.usp_count_stock", "kind": "writes", "to": "dbo.stock", "line": 4},
        {"from": "sp:Shop.dbo.usp_count_stock", "kind": "reads", "to": "dbo.order_lines", "line": 6},
        {"from": "sp:Shop.dbo.usp_build_summary", "kind": "writes", "to": "dbo.summary", "line": 4},
        {"from": "sp:Shop.dbo.usp_build_summary", "kind": "reads", "to": "dbo.orders", "line": 7},
        {"from": "sp:Shop.dbo.usp_load_orders", "kind": "writes", "to": "dbo.orders", "line": 5},
        {"from": "sp:Shop.dbo.usp_load_orders", "kind": "reads", "to": "dbo.order_lines", "line": 7}]), encoding="utf-8")
    scored = cli("kb", "audit", "--answers", str(answers))
    signature = json.loads((H / ".harness/runtime/kbmap/shop-dw.json").read_text())["signature"]
    rows = "".join(f"| {item['type']} | {item['objects']} | {item['recall']:.2f} | {item['precision']:.2f} |\n" for item in scored.get("types", []))
    (KB / "toolkit/audit.md").write_text(f"# Audit of the map\n\nToolkit `sqlserver`, signature `{signature}`. A blind reading of every object, scored by `harness kb audit --answers`.\n\n"
                                         f"| Type | Objects | Recall | Precision |\n| --- | --- | --- | --- |\n{rows}\nResult: pass\n", encoding="utf-8")
    git_repo(KB, {}, "Toolkit for shop-dw, and its audit")


ORDERS_DOMAIN = {
    "domain.yaml": """schema_version: 1
domain: orders
description: Loads each order from its lines every hour, and builds the summary of the day.
updated: 2026-11-17
generated_by: generic-kb-learn-synthesize, harness 1.7.45
sources:
  - repo: shop-dw
    branch: main
    commit: {commit}
entry_points: ["job:Shop_Orders"]
boundaries:
  - name: stock
    note: usp_count_stock reads the same order lines; it belongs to the domain inventory.
shared: []
excluded: []
files:
  architecture: architecture.md
open_questions:
  - id: late-lines
    level: unknown
    note: What happens to a line that arrives after its order was loaded; the code does not say.
""",
    "architecture.md": """# Architecture: orders

## Purpose

Order lines come in; one row per order and one summary row per day come out.

## Flows

- Hourly: `job:Shop_Orders` runs `sp:Shop.dbo.usp_load_orders`, then `sp:Shop.dbo.usp_build_summary`.

## Key data

- `table:Shop.dbo.order_lines`: what comes in.
- `table:Shop.dbo.orders`: one row per order, with its total.
- `table:Shop.dbo.summary`: one row per day.

## Where to start

- RCA of a wrong total: `sp:Shop.dbo.usp_load_orders`.
- A change to the summary: `sp:Shop.dbo.usp_build_summary`.

## Traps

- An order is loaded once: a line that comes later is never added to its total.

## Limits

- What sends the order lines is outside this repository.
""",
    "environment.md": "# Environment: orders\n\n| Environment | Seen | Object | Code then | Fact | From | Level |\n| --- | --- | --- | --- | --- | --- | --- |\n",
    "requests.md": "# Requests: orders\n\n| Id | Object | Kind | Why | How to get it | Status |\n| --- | --- | --- | --- | --- | --- |\n"
                   "| req-0001 | `job:Shop_Orders` | runtime | Whether the job is enabled in PROD, and its schedule | In PROD: `SELECT enabled FROM msdb.dbo.sysjobs WHERE name = 'Shop_Orders'` | open |\n",
    "exam.md": "# Exam: orders\n\n1. A line arrives after its order was loaded. Is it in the total? No: an order is loaded once.\n",
    "discovery/learn-plan.md": "# Learn plan: orders\n\nEntry point `job:Shop_Orders`. One batch: the job, two procedures, three tables.\n",
    "objects/job.md": """# Jobs

## job:Shop_Orders

- What: the hourly load of orders and the summary.
- Reads: none · Writes: none · Called by: none · Calls: sp:Shop.dbo.usp_build_summary, sp:Shop.dbo.usp_load_orders
- Level: verified (read in shop-dw at {commit})

Step 1 loads the orders (L2), step 2 builds the summary (L3). Runs hourly (L4).
""",
    "objects/sp.md": """# Procedures

## sp:Shop.dbo.usp_load_orders

- What: one row per new order, its total from its lines.
- Reads: table:Shop.dbo.order_lines, table:Shop.dbo.orders · Writes: table:Shop.dbo.orders · Called by: job:Shop_Orders · Calls: none
- Level: verified (read in shop-dw at {commit})

Sums count times price of each line (L6). Skips an order already loaded (L8).

Traps: a late line is never added.

## sp:Shop.dbo.usp_build_summary

- What: the summary row of today, made again.
- Reads: table:Shop.dbo.orders · Writes: table:Shop.dbo.summary · Called by: job:Shop_Orders · Calls: none
- Level: verified (read in shop-dw at {commit})

Deletes today's row (L4), then counts and sums today's orders (L5-L9).
""",
    "objects/table.md": """# Tables

## table:Shop.dbo.order_lines

- What: the lines of each order as they come in.
- Reads: none · Writes: none · Called by: sp:Shop.dbo.usp_load_orders · Calls: none
- Level: verified (read in shop-dw at {commit})

## table:Shop.dbo.orders

- What: one row per order.
- Reads: none · Writes: none · Called by: sp:Shop.dbo.usp_build_summary, sp:Shop.dbo.usp_load_orders · Calls: none
- Level: verified (read in shop-dw at {commit})

## table:Shop.dbo.summary

- What: one row per day.
- Reads: none · Writes: none · Called by: sp:Shop.dbo.usp_build_summary · Calls: none
- Level: verified (read in shop-dw at {commit})
""",
    "objects/index.jsonl": "",
}

ORDERS_IDS = ["job:Shop_Orders", "sp:Shop.dbo.usp_build_summary", "sp:Shop.dbo.usp_load_orders", "table:Shop.dbo.order_lines", "table:Shop.dbo.orders", "table:Shop.dbo.summary"]


def learn_orders():
    """A knowledge base task that learns the domain orders and writes it back (committed on the knowledge base's main branch)."""
    name = "learn-orders"
    session = new_task(20, name, "kb", "Learn the domain orders of shop-dw from zero; the entry point is the job Shop_Orders.")
    req_md(name, what="Learn the domain `orders` of `shop-dw` from its code, from the entry point `job:Shop_Orders`, and write it into the knowledge base.",
           not_do="Do not learn the stock count: it is the domain inventory.", done_t="- [T1] Every object the job reaches has a card.\n- [T2] `harness kb cardcheck` passes.")
    stop(session)
    person("confirm-req", name)
    prompt(session, "Confirmed.")
    plan_md(name, files="- `kb/domains/orders/` (new): domain.yaml, architecture.md, the cards, the index.", steps="1. One batch: the job, two procedures, three tables.\n2. Architecture.\n3. Write back.",
            check="`kb cardcheck`, `kb check`.", risks="none")
    stop(session)
    person("approve-plan", name)
    prompt(session, "Approved.")
    commit = run(["git", "-C", str(SHOP), "rev-parse", "--short", "HEAD"], cwd=DEMO).stdout.strip()
    folder = TASKS / name / "DEV/kb/domains/orders"
    for relative, text in ORDERS_DOMAIN.items():
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.replace("{commit}", commit), encoding="utf-8")
    where = f".workspace/sandbox/tasks/{name}/DEV/kb/domains/orders"
    for item in ORDERS_IDS:
        cli("kb", "index", "--path", where, "--id", item, "--level", "verified")
    cli("kb", "stamp", "--path", where)
    print("cardcheck:", json.dumps(cli("kb", "cardcheck", "--path", where, check=False))[:600])
    todo_md(name, ["- [x] Batch 1: the job, two procedures, three tables", "- [x] Architecture", "- [x] Write back"])
    cli("task", "diff", "--task", name)
    cli("task", "promote", "--dry-run", "--task", name)
    stop(session)
    person("approve-promote", name)
    prompt(session, "Approved. Write it back.")
    cli("task", "promote", "--task", name)
    task_md(name, "kb", "full", "done", "The domain orders is written back.", "none")
    stop(session)


def kb_card_task():
    """A knowledge base task whose dry run waits for Approve promote; and, after it was learned, a change in shop-dw that makes two cards stale."""
    name = "fix-orders-card"
    session = new_task(21, name, "kb", "The card of usp_load_orders should say that a late order line is never added. Fix it in the knowledge base.")
    req_md(name, what="The card of `sp:Shop.dbo.usp_load_orders` in the domain `orders` says, with its line, that a line which arrives after its order was loaded is never added to the total.",
           not_do="No other card.", done_t="- [T1] The card says it, with the line (L8).")
    stop(session)
    person("confirm-req", name)
    prompt(session, "Confirmed.")
    for path in ("domains/orders/architecture.md", "domains/orders/objects/sp.md", "domains/orders/objects/index.jsonl"):
        read(session, KB / path)  # what the board shows as "last read by a task"
    plan_md(name, files="- `kb/domains/orders/objects/sp.md`: the card of usp_load_orders.", steps="1. Fetch the card.\n2. Add the sentence, with its line.\n3. Dry run.", check="Read the diff.", risks="none")
    stop(session)
    person("approve-plan", name)
    prompt(session, "Approved.")
    cli("task", "fetch", "kb/domains/orders/objects/sp.md", "--task", name)
    edit_dev(name, "kb/domains/orders/objects/sp.md", "Traps: a late line is never added.", "Traps: a line that arrives after its order was loaded is never added to the total (L8: the order is skipped once it exists).")
    todo_md(name, ["- [x] Fetch the card", "- [x] Add the sentence", "- [x] Dry run"])
    cli("task", "diff", "--task", name)
    cli("task", "promote", "--dry-run", "--task", name)
    task_md(name, "kb", "full", "waiting for the user to approve the promote", "The dry run is done.", "The user approves the promote.")
    stop(session)
    # shop-dw moves on after the domain was learned: kb stale finds the cards learned from the old code
    proc = SHOP / "Shop/dbo/Stored Procedures/usp_load_orders.sql"
    proc.write_text(proc.read_text().replace("    GROUP BY l.order_id;", "      AND l.item_count > 0\n    GROUP BY l.order_id;"), encoding="utf-8")
    git_repo(SHOP, {}, "usp_load_orders: leave out lines with no items")
    cli("kb", "map")


def gate_task():
    """A development task at work whose agent tried things the gate refused: an edit of the code repository itself, a git push, a ticket deleted."""
    name = "add-order-export"
    session = through_plan(22, name, "Add a CSV export of the orders of one day to orders-service.", dict(
        what="`orders-service` can export the orders of one day as CSV.", not_do="No change to how orders are stored.",
        done_t="- [T1] `orders/export.py` writes the CSV.\n- [T2] A test of one day with two orders."),
        dict(files="- `orders-service/orders/export.py` (new)\n- `orders-service/tests/test_export.py` (new)", steps="1. Write the export.\n2. Write the test.\n3. Dry run.",
             check="[T1], [T2] in the diff.", risks="none"))
    pre(session, "Edit", {"path": str(ORDERS / "orders/api.py"), "old_str": "from . import client", "new_str": "from . import client, export"})
    pre(session, "Bash", {"command": "git -C ../repos/orders-service push origin main", "description": "push"})  # never approved
    pre(session, "Bash", {"command": "git -C ../repos/orders-service checkout -b try-export", "description": "a branch to try"})  # the person may approve it (harness approve-command)
    pre(session, "Bash", {"command": "demotracker --project DEMO delete T-12", "description": "delete the old ticket"})
    pre(session, "Read", {"path": str(ORDERS / "orders/api.py")})
    todo_md(name, ["- [ ] Write orders/export.py <- now", "- [ ] Write the test", "- [ ] Dry run of the write-back"])
    task_md(name, "dev", "full", "in progress", "Writing the export.", "Write the test.")


def checks_used_task():
    """One independent check asked; three FAILs: the checks are used up and wait for the person."""
    name = "check-coupon-codes"
    session = session_id(23)
    prompt(session, "Refuse a coupon code that is not 8 capital letters or digits, in orders-service. [review]=1", first=True)
    cli("task", "new", name, "--kind", "dev", "--session-id", session)
    req_md(name, what="`orders-service` refuses an order whose coupon code is not 8 capital letters or digits.", not_do="No change to prices.",
           done_t="- [T1] `orders/api.py` checks the code against `^[A-Z0-9]{8}$`.\n- [T2] The refusal names the code.\n- [T3] A test sends a wrong code.")
    stop(session)
    person("confirm-req", name)
    prompt(session, "Confirmed.")
    plan_md(name, files="- `orders-service/orders/api.py`\n- `orders-service/tests/test_api.py`", steps="1. The check.\n2. The test.\n3. One independent check.", check="By the reviewer.", risks="none")
    stop(session)
    person("approve-plan", name)
    prompt(session, "Approved.")
    cli("task", "fetch", "orders-service/orders/api.py", "orders-service/tests/test_api.py", "--task", name)
    edit_dev(name, "orders-service/orders/api.py", "def create_order(items, base_url):\n", "def create_order(items, base_url, coupon=None):\n")
    edit_dev(name, "orders-service/orders/api.py", '    """Check stock for every item, then accept the order."""\n',
             '    """Check stock for every item, then accept the order."""\n    if coupon is not None and len(coupon) != 8:\n        return {"ok": False, "error": "wrong coupon"}\n')
    todo_md(name, ["- [x] The check", "- [ ] The test", "- [ ] One independent check <- now"])
    api = f".workspace/sandbox/tasks/{name}/DEV/orders-service/orders/api.py"
    findings = [f"VERDICT: FAIL\n- {api}:7 the code is only measured, not checked against capital letters or digits | basis: REQ.md [T1]\n- {api}:8 the refusal does not name the code | basis: REQ.md [T2]\n",
                f"VERDICT: FAIL\n- {api}:8 the refusal does not name the code | basis: REQ.md [T2]\n",
                f"VERDICT: FAIL\n- {api}:7 a code of 8 small letters passes | basis: REQ.md [T1]\n"]
    fixes = [('len(coupon) != 8', 'not coupon.isalnum() or len(coupon) != 8'), ('"wrong coupon"', 'f"wrong coupon: {coupon}"'), (None, None)]
    for verdict, (old, new) in zip(findings, fixes):
        cli("task", "diff", "--task", name)
        cli("task", "review", "start", "--task", name)
        person("verdict", name, stdin=verdict)
        prompt(session, "(the agent goes on after the check)")
        if old:
            edit_dev(name, "orders-service/orders/api.py", old, new)
    task_md(name, "dev", "full", "waiting for the user: the checks are used up", "Three checks failed.", "The user decides: more checks, or waive them.")
    stop(session)


def outside_task():
    """A task linked to a ticket of the demo tracker: a comment waits for the person's approval (a held outside call)."""
    name = "answer-ticket-t7"
    session = new_task(24, name, "qa", "Read demo ticket T-7, link it to this task, and comment on it: checked, the fix is on its branch.")
    cli("task", "link", "add", "demo:T-7", "--task", name)
    pre(session, "Bash", {"command": "demotracker --project DEMO get T-7", "description": "read the ticket"})
    write(name, "TASK.md", (TASKS / name / "TASK.md").read_text().replace("<one sentence>", "The comment waits for the user's approval.").replace("<the one thing to do next>", "The user approves the comment."))
    hold()


def hold():
    """The comment of answer-ticket-t7, held for the person. A held call lives 10 minutes (gate.json, approval_minutes), so capture.mjs calls this
    again (with the pack on) before it takes the outside screens. The agent waits on it with `harness wait --approval`; the wait runs out, the agent
    ends its turn, as the gate tells it to: the card then says the call waits for the person."""
    session = session_id(24)
    pre(session, "Bash", {"command": 'demotracker --project DEMO comment T-7 --text "Checked: the fix is on branch feature/raise_stock_timeout."', "description": "comment on the ticket"})
    listing = ("import sys\nsys.path.insert(0, '.harness/engine')\nfrom pathlib import Path\nfrom core import approvals\n"
               "print(' '.join(str(i.get('code')) for i in approvals.pending(Path('.').resolve(), 10, file=approvals.ACTIONS) if str(i.get('task', '')).endswith('answer-ticket-t7')))")
    for code in run([sys.executable, "-c", listing]).stdout.split()[-1:]:
        run([sys.executable, ".harness/engine/cli.py", "wait", "--approval", code, "--timeout", "10", "--task", "answer-ticket-t7"], check=False)
    stop(session)


def test_and_design_tasks():
    name = "test-sku-check"
    session = new_task(25, name, "test", "Test the SKU check of validate-sku-format on DEV and IST.")
    write(name, "TEST-GUIDE.md", """
# Test guide: test-sku-check

Written for: Alex. Change under test: an order with a wrong SKU is refused, branch `feature/validate_sku_format` of `orders-service`, written back by task `validate-sku-format`.

Order: DEV, then IST. Start the next only when the one before passed.

## DEV

Runner: person

### Steps

1. Send an order with the SKU `ab12`.

   ```
   curl -s -X POST http://orders-dev.example.test/orders -d '{"items": [{"sku": "ab12", "count": 1, "price": 1.0}]}'
   ```

   - Expect: `{"ok": false, "error": "wrong SKU: ab12"}`

### Pass when

- [ ] A wrong SKU is refused, and the refusal names it.

### Send back

- The output of step 1.

## IST

Runner: person

### Steps

1. The same order on IST.

   ```
   curl -s -X POST http://orders-ist.example.test/orders -d '{"items": [{"sku": "ab12", "count": 1, "price": 1.0}]}'
   ```

### Pass when

- [ ] A wrong SKU is refused, and the refusal names it.

### Send back

- The output of step 1.
""")
    given = DEMO / "dev-result.txt"
    given.write_text('{"ok": false, "error": "wrong SKU: ab12"}\n', encoding="utf-8")
    cli("task", "test", "record", "--task", name, "--env", "DEV", "--given-file", str(given), "--run-by", "Alex, 2026-11-17",
        "--row", "A wrong SKU is refused, and the refusal names it.::step 1 returned the refusal with the SKU::PASS", "--follow-up", "Run IST.")
    stop(session)

    name = "design-order-events"
    session = new_task(26, name, "design", "Design how orders-service tells other services that an order was accepted.")
    write(name, "DESIGN.md", """
# Design: order events

## Options

| Option | How | For | Against |
| --- | --- | --- | --- |
| A. A table others read | `order_events`, read every minute | Simple | Readers poll; a minute late |
| B. A message queue | one message per accepted order | At once; readers decoupled | A queue to run |

## Proposal

B, with the table of A kept for a replay.

## Open

- Who runs the queue.
""")
    stop(session)


CONNECTIONS = {"connections": {"demo": {"type": "demotracker", "env": "none", "auth": "signin", "project": "DEMO", "label": "Demo tracker"}}}


def pack(on):
    """The demo tool pack (demotracker, a made-up ticket board that ships with the harness) and its connection, on or off for this company.
    On, the board wants VS Code started with the pack's program folder: the VS Code that runs here was not, so the Enter screen says Not ready
    and capture.mjs skips it. Off (the state the demo is left in), every line is green. The held call and the links stay in the tasks either way."""
    tools = KB / "company/tools"
    tools.mkdir(parents=True, exist_ok=True)
    (tools / "packs.json").write_text(json.dumps({"use": ["demotracker"] if on else []}, indent=2) + "\n", encoding="utf-8")
    if on:
        (tools / "connections.json").write_text(json.dumps(CONNECTIONS, indent=2) + "\n", encoding="utf-8")
    else:
        (tools / "connections.json").unlink(missing_ok=True)
    git = ["git", "-C", str(KB)]
    run(git + ["add", "-A"], cwd=DEMO)
    if run(git + ["diff", "--cached", "--quiet"], cwd=DEMO, check=False).returncode:
        run(git + ["commit", "-qm", "Demo tracker pack " + ("on" if on else "off")], cwd=DEMO)
    run([sys.executable, ".harness/engine/cli.py", "company", "sync"])


def left_alone():
    """A task no session holds: its chat opened another task after it (the Lobby's Left alone)."""
    session = new_task(30, "tidy-readme", "other", "Tidy the README of orders-service: one line per module.")
    new_task(30, "list-endpoints", "qa", "Which endpoints does orders-service have?")  # the same chat picks up another task: tidy-readme is left
    stop(session)


RUN_BLOCK = """
## Check it yourself

The answer times of the stock service on Monday morning, from its log:

```bash
grep "GET /stock" stock-service.log | awk '$2 >= "09:00" && $2 < "10:00" {print $NF}' | sort -n | tail -5
```
"""


def run_block():
    """A shell code block in a delivered file: the task page gives it Ask agent and Run (the person's own run)."""
    path = TASKS / "why-orders-slow" / "RCA.md"
    if "Check it yourself" not in path.read_text(encoding="utf-8"):
        path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n" + RUN_BLOCK, encoding="utf-8")


def kb_registered(on):
    """The knowledge base registered as a target repository, or not (for a moment: the board's yellow block says there is none)."""
    policy = H / ".harness/policies/target.override.json"
    data = json.loads(policy.read_text())
    if on:
        data["repos"]["kb"] = {"path": "knowledge-base", "knowledge_base": True}
    else:
        data["repos"].pop("kb", None)
    policy.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def extra():
    if not KB.exists():
        make_kb()
    if not (TASKS / "learn-orders").exists():
        learn_orders()
    pack(True)
    for name, make in (("fix-orders-card", kb_card_task), ("add-order-export", gate_task), ("check-coupon-codes", checks_used_task),
                       ("answer-ticket-t7", outside_task), ("test-sku-check", test_and_design_tasks)):
        if not (TASKS / name).exists():
            make()
    if not (TASKS / "tidy-readme").exists():
        left_alone()
    run_block()
    pack(False)
    print(f"extra states made in {H}")


# --- the board ---------------------------------------------------------------------------------------------------------------------


def board_pid():
    found = run(["pgrep", "-f", f"{H}/.harness/engine/cli.py task board"], check=False).stdout.split()
    return [int(pid) for pid in found]


def start_board():
    if board_pid():
        print(f"the board runs: http://127.0.0.1:{PORT}/")
        return
    (DEMO / "pair-url.txt").unlink(missing_ok=True)
    env = dict(os.environ, BROWSER=f"{DEMO / 'opener.sh'} %s")
    log = open(DEMO / "board.log", "w")
    subprocess.Popen(["script", "-q", "/dev/null", "sh", ".harness/bin/harness", "task", "board", "--port", str(PORT)], cwd=H, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    for _ in range(60):
        if (DEMO / "pair-url.txt").exists():
            print(f"the board runs: http://127.0.0.1:{PORT}/")
            return
        time.sleep(0.5)
    sys.exit("the board did not start: see board.log")


def pair():
    """A second start of the board: the one that runs opens its page with a new code, which opener.sh keeps."""
    (DEMO / "pair-url.txt").unlink(missing_ok=True)
    env = dict(os.environ, BROWSER=f"{DEMO / 'opener.sh'} %s")
    subprocess.run(["script", "-q", "/dev/null", "sh", ".harness/bin/harness", "task", "board", "--port", str(PORT)], cwd=H, env=env, stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
    for _ in range(40):
        if (DEMO / "pair-url.txt").exists():
            print((DEMO / "pair-url.txt").read_text().strip().split("#")[0])
            return
        time.sleep(0.25)
    sys.exit("no pairing link: is the board running? (demo.py start)")


def stop_board():
    """Ctrl+C, as a person stops it; a board that does not hear it (started in the background by a shell, which ignores Ctrl+C there) is ended."""
    for sig in (signal.SIGINT, signal.SIGTERM):
        for pid in board_pid():
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        for _ in range(40):
            if not board_pid():
                return
            time.sleep(0.25)
    sys.exit("the board did not stop")


def touch(name):
    path = TASKS / name / ".task/task.json"
    data = json.loads(path.read_text()) if path.exists() else None
    session = (data or {}).get("session_id") or ""
    if not session:
        sys.exit(f"no session for {name}")
    tool(session, f"edit .workspace/sandbox/tasks/{name}/DEV")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "build":
        build("--fresh" in sys.argv)
    elif what == "extra":
        extra()
    elif what == "pack" and len(sys.argv) > 2 and sys.argv[2] in ("on", "off"):
        pack(sys.argv[2] == "on")
    elif what == "kb" and len(sys.argv) > 2 and sys.argv[2] in ("on", "off"):
        kb_registered(sys.argv[2] == "on")
    elif what == "hold":
        hold()
    elif what == "start":
        start_board()
    elif what == "pair":
        pair()
    elif what == "stop":
        stop_board()
    elif what == "touch" and len(sys.argv) > 2:
        touch(sys.argv[2])
    else:
        sys.exit(__doc__)
