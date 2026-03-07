#!/usr/bin/env python3
"""
Sync an Obsidian vault git repository.

Behavior:
- commit + push local changes (if present)
- pull --rebase when remote is ahead
- rename conflicted files with a "_conflicted" suffix
- push again if local is ahead after pull

Required env vars:
- GITHUB_URL
- GITHUB_TOKEN

Optional env vars:
- VAULT_DIR (default: ~/vault)
- BRANCH (default: main)
- LOGFILE (default: /tmp/vault_git_sync.log)
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

VAULT_DIR = Path(os.getenv("VAULT_DIR", str(Path.home() / "vault")))
LOGFILE = Path(os.getenv("LOGFILE", "/tmp/vault_git_sync.log"))
GITHUB_URL = os.getenv("GITHUB_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BRANCH = os.getenv("BRANCH", "main")


def log(message: str, also_print: bool = False) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    with LOGFILE.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")
    if also_print:
        print(message)


def run_git(args: list[str], allow_fail: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=VAULT_DIR,
        check=not allow_fail,
        text=True,
        capture_output=True,
    )


def fail(message: str, code: int = 1) -> None:
    log(f"[ERROR] {message}", also_print=True)
    raise SystemExit(code)


def ensure_repo() -> None:
    if not VAULT_DIR.exists():
        fail(f"VAULT_DIR does not exist: {VAULT_DIR}")
    if not (VAULT_DIR / ".git").exists():
        fail(f"VAULT_DIR is not a git repository: {VAULT_DIR}")


def set_authenticated_remote() -> None:
    if not GITHUB_URL or not GITHUB_TOKEN:
        fail("GITHUB_URL and GITHUB_TOKEN must be set.")
    authenticated_url = GITHUB_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
    run_git(["remote", "set-url", "origin", authenticated_url])


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
            src = VAULT_DIR / file_path
            dst = src.with_name(src.stem + "_conflicted" + src.suffix)
            if src.exists():
                src.rename(dst)
                run_git(["add", str(dst)])


def first_staged_added_line() -> str:
    diff = run_git(["diff", "--cached", "--unified=0"], allow_fail=True).stdout
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content:
                return content
    return ""


def build_commit_message() -> str:
    first_line = first_staged_added_line()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")
    if first_line:
        return f"{first_line} [{timestamp}]"
    return f"vault sync [{timestamp}]"


def sync_vault() -> None:
    log("=== Starting vault sync ===", also_print=True)
    ensure_repo()
    set_authenticated_remote()

    if has_uncommitted_changes():
        log("Uncommitted changes found; committing and pushing...", also_print=True)
        run_git(["add", "-A"])
        try:
            run_git(["commit", "-m", build_commit_message()])
        except subprocess.CalledProcessError:
            log("Nothing to commit.", also_print=True)
        run_git(["push", "origin", BRANCH])
        log("Push completed.", also_print=True)

    ahead, behind = get_commit_delta()
    log(f"Commits ahead: {ahead}, behind: {behind}", also_print=True)

    if behind > 0:
        log("Pulling from remote...", also_print=True)
        try:
            run_git(["pull", "--rebase", "origin", BRANCH])
        except subprocess.CalledProcessError:
            log("Merge conflict during pull. Renaming conflicted files.", also_print=True)
            handle_merge_conflicts()

    ahead, _ = get_commit_delta()
    if ahead > 0:
        log("Pushing new commits after pull...", also_print=True)
        run_git(["push", "origin", BRANCH])
        log("Push completed.", also_print=True)

    log("=== Vault sync complete ===\n", also_print=True)
    print(f"See log file for details: {LOGFILE}")


def main() -> int:
    try:
        sync_vault()
    except Exception as exc:
        log(f"[ERROR] {exc}", also_print=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
