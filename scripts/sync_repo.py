#!/usr/bin/env python3
"""
Sync a git repository bidirectionally.

Behavior:
- commit + push local changes (if present)
- pull --rebase when remote is ahead
- rename conflicted files with a "_conflicted" suffix
- push again if local is ahead after pull
- send macOS notification on error

Required env vars:
- (none — SSH auth assumed)

Optional env vars:
- REPO_DIR (default: ~/repo)
- BRANCH (default: main)
- LOGFILE (default: ~/Library/Logs/repo-sync.log)
"""

from __future__ import annotations

import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(os.getenv("REPO_DIR", str(Path.home() / "repo")))
BRANCH = os.getenv("BRANCH", "main")
LOGFILE = Path(os.getenv("LOGFILE", str(Path.home() / "Library/Logs/repo-sync.log")))


def log(message: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with LOGFILE.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")


def notify_error(message: str) -> None:
    if platform.system() == "Darwin":
        subprocess.run(
            [
                "osascript", "-e",
                f'display notification "{message}" with title "Repo Sync Error" sound name "Basso"',
            ],
            capture_output=True,
        )


def run_git(args: list[str], allow_fail: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=REPO_DIR,
        check=not allow_fail,
        text=True,
        capture_output=True,
    )


def fail(message: str, code: int = 1) -> None:
    log(f"[ERROR] {message}")
    notify_error(message)
    raise SystemExit(code)


def ensure_repo() -> None:
    if not REPO_DIR.exists():
        fail(f"REPO_DIR does not exist: {REPO_DIR}")
    if not (REPO_DIR / ".git").exists():
        fail(f"REPO_DIR is not a git repository: {REPO_DIR}")


def has_uncommitted_changes() -> bool:
    result = run_git(["status", "--porcelain"], allow_fail=True)
    return bool(result.stdout.strip())


def get_commit_delta() -> tuple[int, int]:
    run_git(["fetch"])
    ahead = int(run_git(["rev-list", "--count", f"origin/{BRANCH}..{BRANCH}"]).stdout.strip())
    behind = int(run_git(["rev-list", "--count", f"{BRANCH}..origin/{BRANCH}"]).stdout.strip())
    return ahead, behind


def handle_merge_conflicts() -> None:
    status = run_git(["status", "--porcelain"], allow_fail=True).stdout
    for line in status.splitlines():
        if line.startswith("UU "):
            file_path = line[3:].strip()
            src = REPO_DIR / file_path
            dst = src.with_name(src.stem + "_conflicted" + src.suffix)
            if src.exists():
                src.rename(dst)
                run_git(["add", str(dst)])


def build_commit_message() -> str:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return f"sync [{timestamp}]"


def sync() -> None:
    log("=== Starting sync ===")
    ensure_repo()

    if has_uncommitted_changes():
        log("Uncommitted changes found; committing and pushing...")
        run_git(["add", "-A"])
        try:
            run_git(["commit", "-m", build_commit_message()])
        except subprocess.CalledProcessError:
            log("Nothing to commit.")
        run_git(["push", "origin", BRANCH])
        log("Push completed.")

    ahead, behind = get_commit_delta()
    log(f"Commits ahead: {ahead}, behind: {behind}")

    if behind > 0:
        log("Pulling from remote...")
        try:
            run_git(["pull", "--rebase", "origin", BRANCH])
        except subprocess.CalledProcessError:
            log("Merge conflict during pull. Renaming conflicted files.")
            handle_merge_conflicts()

    ahead, _ = get_commit_delta()
    if ahead > 0:
        log("Pushing after pull...")
        run_git(["push", "origin", BRANCH])
        log("Push completed.")

    log("=== Sync complete ===\n")


def main() -> int:
    try:
        sync()
    except SystemExit:
        raise
    except Exception as exc:
        fail(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
