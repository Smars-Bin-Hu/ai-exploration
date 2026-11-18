#!/usr/bin/env python3
"""A workspace of harness 1.7.45 to record videos in: made-up repositories, six made-up tasks in different states, the board.

  python3 source/demo/demo.py setup [--at FOLDER]    make the workspace (default /Users/Shared/harness-demo), keep its starting point, start the board
  python3 source/demo/demo.py reset [--at FOLDER]    stop the board, put the workspace back to its starting point, start the board again
  python3 source/demo/demo.py start [--at FOLDER]    start the board on 127.0.0.1:8846 in the background; it opens your browser, paired
  python3 source/demo/demo.py open  [--at FOLDER]    open the running board in your browser again (a new pairing link)
  python3 source/demo/demo.py stop  [--at FOLDER]    stop the board

  start, setup and reset also take --no-browser (the pairing link goes to FOLDER/pair-url.txt only) and --no-vscode (the board does not
  connect to VS Code, so no button on it can reach a chat: for a dry run or a test).

The tasks are made the way source/tutorials/shots/demo.py makes them (that file is imported, with HARNESS_DEMO set to FOLDER): the agent's side
through the harness's hook and commands, the person's approvals through the harness's own functions. No Copilot chat is made and nothing is spent.
Everything in the workspace is made up. See README.md next to this file.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOTS = HERE.parent / "tutorials/shots/demo.py"
DEFAULT = Path("/Users/Shared/harness-demo")  # not under the home folder: the board shows the workspace's paths, and this one names nobody
PORT = 8846  # not the 8845 of the screenshot rig, so both can run
MARK = ".harness-demo"  # in a folder this script made: the only kind of folder setup and reset delete
START = ".start.tar"  # the starting point: harness/ and repos/ just after setup
PARTS = ("harness", "repos")


def folder_of(argv):
    if "--at" in argv:
        at = argv.index("--at")
        if at + 1 >= len(argv):
            sys.exit("--at needs a folder")
        return Path(argv[at + 1]).expanduser().absolute()
    return DEFAULT


def shots(folder):
    """The screenshot rig, pointed at this folder: its helpers make the repositories and the tasks here."""
    os.environ["HARNESS_DEMO"] = str(folder)
    spec = importlib.util.spec_from_file_location("shots_demo", SHOTS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PORT = PORT
    return mod


def ours(folder):
    if folder.exists() and any(folder.iterdir()) and not (folder / MARK).exists():
        sys.exit(f"{folder} exists and was not made by this script: choose another folder with --at")


OPENER = """#!/bin/sh
# Stands in for the browser the board opens: it keeps the pairing link in pair-url.txt, then opens it in the default browser
# (not when HARNESS_DEMO_NO_BROWSER=1).
printf '%s\\n' "$1" > "$(dirname "$0")/pair-url.txt"
[ "${HARNESS_DEMO_NO_BROWSER:-}" = 1 ] || open "$1"
"""


def setup(folder, argv):
    ours(folder)
    mod = shots(folder)
    if folder.exists():
        if mod.board_pid():
            mod.stop_board()
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    (folder / MARK).write_text("Made by source/demo/demo.py of ai-exploration. setup and reset may delete this folder.\n", encoding="utf-8")
    H = mod.H
    H.mkdir()
    archive = subprocess.run(["git", "-C", str(mod.HARNESS_GIT), "archive", mod.VERSION], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(H)], input=archive, check=True)
    mod.REPOS.mkdir()
    mod.make_repo()
    policies = H / ".harness/policies"
    (policies / "target.override.json").write_text(json.dumps({"repos_root": "", "repos": {"orders-service": {"path": str(mod.ORDERS)}}}, indent=2) + "\n", encoding="utf-8")
    # the name an agent and the board use for the person: made up, never `git config user.name` of this computer
    (policies / "user.override.json").write_text(json.dumps({"language": "en", "name": "Alex", "setup_done": True}, indent=2) + "\n", encoding="utf-8")
    (folder / "opener.sh").write_text(OPENER, encoding="utf-8")
    (folder / "opener.sh").chmod(0o755)
    mod.make_kb()  # shop-dw and the knowledge base, registered
    mod.learn_orders()  # closed: the domain orders written back to the knowledge base
    mod.task_raise_stock_timeout()  # closed with changes
    mod.task_limit_order_items()  # ready to write back
    mod.task_cache_stock_counts()  # waits for your run on DEV
    mod.task_add_order_notes()  # waits for Approve plan
    mod.task_fix_total_rounding()  # waits for Confirm requirement
    for name in ("audit-answers.jsonl",):
        (folder / name).unlink(missing_ok=True)
    subprocess.run(["tar", "-c", "-f", START, *PARTS], cwd=folder, check=True)
    print(f"made: {folder}")
    start(folder, argv, mod)


def reset(folder, argv):
    if not (folder / MARK).exists() or not (folder / START).exists():
        sys.exit(f"no workspace of this script in {folder}: run setup first")
    mod = shots(folder)
    if mod.board_pid():
        mod.stop_board()
    for part in PARTS:
        target = folder / part
        if target.exists():
            for path in target.rglob("*"):  # a folder left read-only must not stop the delete
                if path.is_dir() and not path.is_symlink():
                    path.chmod(0o755)
            shutil.rmtree(target)
    for name in ("pair-url.txt", "board.log", "dev-result.txt"):
        (folder / name).unlink(missing_ok=True)
    subprocess.run(["tar", "-x", "-p", "-f", START], cwd=folder, check=True)
    print(f"back to the start: {folder}")
    start(folder, argv, mod)


def start(folder, argv, mod=None):
    if not (folder / MARK).exists():
        sys.exit(f"no workspace of this script in {folder}: run setup first")
    mod = mod or shots(folder)
    url = f"http://127.0.0.1:{PORT}/"
    if mod.board_pid():
        print(f"the board runs: {url} (open it again: demo.py open)")
        return
    (folder / "pair-url.txt").unlink(missing_ok=True)
    env = dict(os.environ, BROWSER=f"{folder / 'opener.sh'} %s")
    if "--no-browser" in argv:
        env["HARNESS_DEMO_NO_BROWSER"] = "1"
    if "--no-vscode" in argv:
        env["HARNESS_VSCODE_CLI"] = "off"  # the harness's own switch: the board does not link to VS Code at all
    log = open(folder / "board.log", "w")
    subprocess.Popen(["script", "-q", "/dev/null", "sh", ".harness/bin/harness", "task", "board", "--port", str(PORT)], cwd=mod.H, env=env,
                     stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    for _ in range(60):
        if (folder / "pair-url.txt").exists():
            print(f"the board runs: {url}" + (" (link to pair a browser: pair-url.txt)" if "--no-browser" in argv else ""))
            return
        time.sleep(0.5)
    sys.exit(f"the board did not start: see {folder / 'board.log'}")


def main():
    argv = sys.argv[1:]
    what = argv[0] if argv else ""
    folder = folder_of(argv)
    if what == "setup":
        setup(folder, argv)
    elif what == "reset":
        reset(folder, argv)
    elif what == "start":
        start(folder, argv)
    elif what == "open":
        if not (folder / MARK).exists():
            sys.exit(f"no workspace of this script in {folder}")
        shots(folder).pair()
    elif what == "stop":
        if not (folder / MARK).exists():
            sys.exit(f"no workspace of this script in {folder}")
        mod = shots(folder)
        mod.stop_board()
        print("the board is stopped")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
