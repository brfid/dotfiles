#!/usr/bin/env python3
"""
General-purpose Git sync controller.
- Supports syncing multiple project directories
- Pulls if remote is ahead
- Pushes if local is ahead
- Commits local changes with timestamp + change preview
- Handles merge conflicts by renaming conflicted files
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# === Configuration Constants ===
SYNC_INTERVAL_MINUTES = 1440  # e.g. once per day
LOGFILE = Path("/tmp/multi_git_sync.log")
DEFAULT_BRANCH = "main"

# Define projects as a list of dicts
PROJECTS = [
    {
        "name": "dotconfig",
        "path": Path.home() / ".config",
        "remote_url": "https://github.com/brfid/config.git",
        "token": os.getenv("GITHUB_TOKEN_SYNC"),
        "branch": "main"
    },
    # Add more projects here
]

# === Utility Functions ===

def log(msg: str, also_print: bool = False) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    with LOGFILE.open("a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    if also_print:
        print(msg)

def run_git(args: list[str], cwd: Path, allow_fail=False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=not allow_fail,
        capture_output=True,
        text=True
    )

def set_authenticated_remote(project: dict) -> None:
    url = project["remote_url"]
    token = project["token"]
    if not url or not token:
        log(f"[ERROR] Missing remote or token for {project['name']}", also_print=True)
        return
    auth_url = url.replace("https://", f"https://{token}@")
    run_git(["remote", "set-url", "origin", auth_url], cwd=project["path"], allow_fail=True)

def has_changes(path: Path) -> bool:
    result = run_git(["status", "--porcelain"], cwd=path, allow_fail=True)
    return bool(result.stdout.strip())

def get_commit_delta(path: Path, branch: str) -> tuple[int, int]:
    run_git(["fetch"], cwd=path)
    ahead = int(run_git(["rev-list", "--count", f"origin/{branch}..{branch}"], cwd=path).stdout.strip())
    behind = int(run_git(["rev-list", "--count", f"{branch}..origin/{branch}"], cwd=path).stdout.strip())
    return ahead, behind

def stash_changes(path: Path) -> None:
    run_git(["stash", "--include-untracked", "-m", "autosync stash"], cwd=path, allow_fail=True)

def pop_stash(path: Path) -> None:
    stash_list = run_git(["stash", "list"], cwd=path, allow_fail=True).stdout
    for line in stash_list.splitlines():
        if "autosync stash" in line:
            stash_ref = line.split(":")[0]
            run_git(["stash", "pop", stash_ref], cwd=path, allow_fail=True)
            break

def handle_conflicts(path: Path) -> None:
    status = run_git(["status", "--porcelain"], cwd=path, allow_fail=True).stdout
    for line in status.splitlines():
        if line.startswith("UU "):
            file = line[3:].strip()
            src = path / file
            dest = src.with_name(src.stem + "_conflicted" + src.suffix)
            if src.exists():
                src.rename(dest)
                run_git(["add", str(dest)], cwd=path)

def commit_local_changes(path: Path) -> None:
    run_git(["add", "-A"], cwd=path)
    diff = run_git(["diff", "--cached", "--unified=0"], cwd=path).stdout
    sample = next((l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")), "").strip()
    msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} sync: {sample[:60] if sample else 'update'}"
    try:
        run_git(["commit", "-m", msg], cwd=path)
    except subprocess.CalledProcessError:
        log(f"[{path.name}] Nothing to commit.")


def sync_project(project: dict) -> None:
    name = project["name"]
    path = project["path"]
    branch = project.get("branch", DEFAULT_BRANCH)

    log(f"--- Syncing {name} ---", also_print=True)

    if not path.exists() or not (path / ".git").exists():
        log(f"[{name}] Skipped: Not a valid git repo at {path}")
        return

    set_authenticated_remote(project)

    if has_changes(path):
        log(f"[{name}] Committing local changes")
        commit_local_changes(path)
        run_git(["push", "origin", branch], cwd=path)

    ahead, behind = get_commit_delta(path, branch)
    log(f"[{name}] Ahead: {ahead}, Behind: {behind}")

    if behind > 0:
        stash_changes(path)
        try:
            run_git(["pull", "--rebase", "origin", branch], cwd=path)
        except subprocess.CalledProcessError:
            log(f"[{name}] Merge conflict detected; renaming conflicted files")
            handle_conflicts(path)

    ahead, _ = get_commit_delta(path, branch)
    if ahead > 0:
        run_git(["push", "origin", branch], cwd=path)

    pop_stash(path)
    log(f"[{name}] Sync complete")


def main():
    for project in PROJECTS:
        try:
            sync_project(project)
        except Exception as e:
            log(f"[{project['name']}] ERROR: {e}", also_print=True)

if __name__ == "__main__":
    main()
