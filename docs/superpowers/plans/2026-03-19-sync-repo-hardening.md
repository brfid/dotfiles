# sync_repo.py Hardening Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix critical reliability bugs in `scripts/sync_repo.py` and make the script robust for months of unattended operation syncing iCloud-hosted git repos.

**Architecture:** Single-file rewrite of `sync_repo.py`. Replace rebase with merge for conflict handling, add lockfile/timeout/iCloud-eviction guards, fetch once instead of per-call, generalize notification title. Minor fixes to `install.sh` (deprecated launchctl commands, `which` → `command -v`).

**Tech Stack:** Python 3 stdlib only (subprocess, fcntl, pathlib). No external dependencies.

**Context:** This is a dotfiles repo with no test infrastructure. Verification is manual — run the script against a real git repo and check log output. The script runs as a macOS LaunchAgent every 15 minutes.

---

### Task 1: Replace rebase with merge and fix conflict handling

The most critical fix. `pull --rebase` leaves the repo stuck in a mid-rebase state on conflict. Switch to `pull` (merge), and handle all conflict types (`UU`, `AA`, `DU`, `UD`, `DD`), not just `UU`.

**Files:**
- Modify: `scripts/sync_repo.py` — `sync()`, `handle_merge_conflicts()`

- [ ] **Step 1: Rewrite `handle_merge_conflicts()` to detect all unmerged files**

Use `git diff --name-only --diff-filter=U` instead of parsing porcelain status for `UU`. For each conflicted file: check out "ours" version, save "theirs" as `_conflicted`, stage both.

```python
def handle_merge_conflicts() -> None:
    """Resolve merge conflicts by keeping ours and saving theirs as _conflicted."""
    result = run_git(["diff", "--name-only", "--diff-filter=U"], allow_fail=True)
    if not result.stdout.strip():
        return
    for file_path in result.stdout.strip().splitlines():
        file_path = file_path.strip()
        src = REPO_DIR / file_path
        dst = src.with_name(src.stem + "_conflicted" + src.suffix)
        # Save theirs as _conflicted
        theirs = run_git(["show", f":3:{file_path}"], allow_fail=True)
        if theirs.returncode == 0 and theirs.stdout:
            dst.write_text(theirs.stdout)
            run_git(["add", str(dst)])
        # Keep ours
        run_git(["checkout", "--ours", file_path], allow_fail=True)
        run_git(["add", file_path])
    log(f"Resolved {len(result.stdout.strip().splitlines())} conflict(s) — theirs saved as _conflicted files.")
```

- [ ] **Step 2: Change `sync()` to use merge instead of rebase**

Replace:
```python
run_git(["pull", "--rebase", "origin", BRANCH])
```
With:
```python
run_git(["pull", "--no-rebase", "origin", BRANCH])
```

In the except block, after calling `handle_merge_conflicts()`, commit the merge resolution:
```python
try:
    run_git(["pull", "--no-rebase", "origin", BRANCH])
except subprocess.CalledProcessError:
    log("Merge conflict during pull. Resolving conflicts.")
    handle_merge_conflicts()
    run_git(["commit", "--no-edit"], allow_fail=True)
```

- [ ] **Step 3: Verify manually**

Run against `~/homeschool`:
```bash
REPO_DIR=~/homeschool python3 ~/src/dotfiles/scripts/sync_repo.py
```
Check log output shows "Sync complete" with no errors.

- [ ] **Step 4: Commit**

```bash
cd ~/src/dotfiles
git add scripts/sync_repo.py
git commit -m "Fix conflict handling: merge instead of rebase, all conflict types"
```

---

### Task 2: Add lockfile to prevent concurrent runs

If the LaunchAgent fires while a previous run is still going (slow network, sleep resume), two instances will corrupt the repo.

**Files:**
- Modify: `scripts/sync_repo.py` — add `acquire_lock()`, call it in `main()`

- [ ] **Step 1: Add lockfile logic**

```python
import fcntl

LOCKFILE = REPO_DIR / ".sync_repo.lock"

def acquire_lock() -> int:
    """Acquire an exclusive lock. Returns fd on success, exits 0 if already locked."""
    fd = os.open(str(LOCKFILE), os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        log("Another sync is already running. Skipping.")
        os.close(fd)
        raise SystemExit(0)
```

- [ ] **Step 2: Call `acquire_lock()` at the start of `sync()`**

```python
def sync() -> None:
    log("=== Starting sync ===")
    ensure_repo()
    lock_fd = acquire_lock()
    try:
        # ... existing sync logic ...
    finally:
        os.close(lock_fd)
```

- [ ] **Step 3: Commit**

```bash
git add scripts/sync_repo.py
git commit -m "Add lockfile to prevent concurrent sync runs"
```

---

### Task 3: Add timeout to git operations

A hung SSH connection blocks the process forever. Add a timeout to `run_git`.

**Files:**
- Modify: `scripts/sync_repo.py` — `run_git()`

- [ ] **Step 1: Add timeout parameter**

```python
GIT_TIMEOUT = 120  # seconds

def run_git(args: list[str], allow_fail: bool = False) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=REPO_DIR,
            check=not allow_fail,
            text=True,
            capture_output=True,
            timeout=GIT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        fail(f"git {' '.join(args)} timed out after {GIT_TIMEOUT}s")
```

Note: `fail()` calls `notify_error()` so the user gets a macOS notification on timeout.

- [ ] **Step 2: Commit**

```bash
git add scripts/sync_repo.py
git commit -m "Add 120s timeout to git operations"
```

---

### Task 4: Fetch once, not per call

`get_commit_delta()` calls `git fetch` every invocation (2-3 times per run). Fetch once at the top of `sync()`.

**Files:**
- Modify: `scripts/sync_repo.py` — `sync()`, `get_commit_delta()`

- [ ] **Step 1: Extract fetch from `get_commit_delta()`**

Rename to just compare cached refs:
```python
def get_commit_delta() -> tuple[int, int]:
    ahead = int(run_git(["rev-list", "--count", f"origin/{BRANCH}..{BRANCH}"]).stdout.strip())
    behind = int(run_git(["rev-list", "--count", f"{BRANCH}..origin/{BRANCH}"]).stdout.strip())
    return ahead, behind
```

- [ ] **Step 2: Add a single fetch at the top of sync logic**

In `sync()`, after the initial commit+push block, add:
```python
    run_git(["fetch", "origin"])
```
Then the existing `get_commit_delta()` calls work off cached refs.

- [ ] **Step 3: Commit**

```bash
git add scripts/sync_repo.py
git commit -m "Fetch once per sync run instead of per delta check"
```

---

### Task 5: iCloud eviction guard

If iCloud evicts files to cloud-only stubs, `git add -A` will commit the stubs and destroy real content in git history.

**Files:**
- Modify: `scripts/sync_repo.py` — add `download_icloud_files()`, call before `git add`

- [ ] **Step 1: Add brctl download call**

```python
def download_icloud_files() -> None:
    """Force-download any iCloud-evicted files before git operations."""
    if platform.system() != "Darwin":
        return
    try:
        subprocess.run(
            ["brctl", "download", str(REPO_DIR)],
            capture_output=True,
            timeout=300,
        )
        log("iCloud download check completed.")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        log("brctl not available or timed out; skipping iCloud download check.")
```

- [ ] **Step 2: Call it in `sync()` before `has_uncommitted_changes()`**

```python
    download_icloud_files()

    if has_uncommitted_changes():
        ...
```

- [ ] **Step 3: Commit**

```bash
git add scripts/sync_repo.py
git commit -m "Guard against iCloud file eviction with brctl download"
```

---

### Task 6: Generalize notification title

Hardcoded "Homeschool Sync Error" breaks multi-repo use. Derive from `REPO_DIR.name`.

**Files:**
- Modify: `scripts/sync_repo.py` — `notify_error()`

- [ ] **Step 1: Update `notify_error` to use REPO_DIR name**

```python
def notify_error(message: str) -> None:
    if platform.system() == "Darwin":
        title = f"{REPO_DIR.name} Sync Error"
        subprocess.run(
            [
                "osascript", "-e",
                f'display notification "{message}" with title "{title}" sound name "Basso"',
            ],
            capture_output=True,
        )
```

- [ ] **Step 2: Commit**

```bash
git add scripts/sync_repo.py
git commit -m "Derive notification title from REPO_DIR name"
```

---

### Task 7: Fix install.sh minor issues

`which` → `command -v`, deprecated `launchctl load/unload` → `bootstrap/bootout`.

**Files:**
- Modify: `install.sh` — `--mac` block

- [ ] **Step 1: Fix `which` to `command -v`**

Change line 119:
```bash
PYTHON3="$(command -v python3)"
```

- [ ] **Step 2: Replace launchctl load/unload with bootstrap/bootout**

Replace:
```bash
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"
```
With:
```bash
    launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
```

- [ ] **Step 3: Commit**

```bash
git add install.sh
git commit -m "Fix which to command -v, use launchctl bootstrap/bootout"
```

---

### Task 8: Update docs and verify

Update README and docstring to reflect the new behavior, then do a final manual run.

**Files:**
- Modify: `README.md`, `scripts/sync_repo.py` docstring

- [ ] **Step 1: Update docstring at top of sync_repo.py**

```python
"""
Sync a git repository bidirectionally.

Behavior:
- force-download any iCloud-evicted files
- commit + push local changes (if present)
- pull (merge) when remote is ahead
- on conflict: keep ours, save theirs as _conflicted files
- push again if local is ahead after pull
- send macOS notification on error

Env vars (set via LaunchAgent plist):
- REPO_DIR (default: ~/homeschool)
- BRANCH (default: main)
- LOGFILE (default: ~/Library/Logs/homeschool-sync.log)
"""
```

- [ ] **Step 2: Update README conflict description**

Change "renames conflicted files" to:
> On conflict it keeps the local version, saves the remote version as `_conflicted`, and commits the merge resolution automatically.

- [ ] **Step 3: Final manual run**

```bash
REPO_DIR=~/homeschool python3 ~/src/dotfiles/scripts/sync_repo.py
tail -10 ~/Library/Logs/homeschool-sync.log
```

Verify log shows: iCloud download check, fetch, delta counts, sync complete.

- [ ] **Step 4: Commit and push**

```bash
git add scripts/sync_repo.py README.md
git commit -m "Update docs for hardened sync behavior"
git push
```

- [ ] **Step 5: Reload LaunchAgent**

```bash
cd ~/src/dotfiles && bash install.sh --mac
```
