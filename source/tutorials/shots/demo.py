#!/usr/bin/env python3
"""The demo workspace behind the board screenshots of the tutorials: harness 1.7.45, a made-up code repository and made-up tasks.

  python3 source/tutorials/shots/demo.py build [--fresh]   unpack 1.7.45 (git archive of ~/Developer/DE-agentic-harness), make repos/orders-service and the tasks
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

import io
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
    print(f"built: {H}")


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
