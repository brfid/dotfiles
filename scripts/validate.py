#!/usr/bin/env python3
"""Validate dotfiles repo invariants.

Checks every <tool>/sync.toml at the repo root against the v2 schema:

* Top-level keys: version (==2), tool (matches dirname), live_root (str).
* [[managed]] entries: name (str), repo (str), live (str). No other keys.
* No [[unmanaged]] or [[verify]] tables (those were removed in v2).

Also runs ``bash -n`` on tracked shell scripts (*.sh, shell/bashrc,
shell/aliases) to catch syntax errors.

Usage: python scripts/validate.py
Exits 0 on success, 1 on any violation. Prints all failures, not just the
first.
"""
from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 2
MANAGED_KEYS = {"name", "repo", "live"}


def check_sync_toml(path: Path) -> list[str]:
    errs: list[str] = []
    tool_dir = path.parent.name
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        return [f"{path}: invalid TOML ({e})"]

    if data.get("version") != SCHEMA_VERSION:
        errs.append(f"{path}: version must be {SCHEMA_VERSION}, got {data.get('version')!r}")
    if data.get("tool") != tool_dir:
        errs.append(f"{path}: tool field {data.get('tool')!r} must match dirname {tool_dir!r}")
    live_root = data.get("live_root")
    if not isinstance(live_root, str) or not live_root:
        errs.append(f"{path}: live_root must be a non-empty string")

    managed = data.get("managed", [])
    if not isinstance(managed, list):
        errs.append(f"{path}: managed must be a list")
        managed = []
    for i, entry in enumerate(managed):
        ctx = f"{path} managed[{i}]"
        if not isinstance(entry, dict):
            errs.append(f"{ctx}: must be a table")
            continue
        for k in MANAGED_KEYS:
            if k not in entry:
                errs.append(f"{ctx}: missing {k!r}")
            elif not isinstance(entry[k], str) or not entry[k]:
                errs.append(f"{ctx}: {k} must be a non-empty string")
        extra = set(entry) - MANAGED_KEYS
        if extra:
            errs.append(f"{ctx}: unexpected keys {sorted(extra)} (v2 dropped actions/unmanaged/verify)")

    for legacy in ("unmanaged", "verify"):
        if legacy in data:
            errs.append(f"{path}: {legacy!r} table not allowed in v{SCHEMA_VERSION}")

    return errs


def check_shell_syntax() -> list[str]:
    errs: list[str] = []
    targets = sorted(p for p in REPO.rglob("*.sh") if ".git" not in p.parts)
    for name in ("bashrc", "aliases"):
        p = REPO / "shell" / name
        if p.exists():
            targets.append(p)
    for p in targets:
        result = subprocess.run(
            ["bash", "-n", str(p)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errs.append(f"{p}: bash -n failed: {result.stderr.strip()}")
    return errs


def main() -> int:
    errs: list[str] = []
    sync_files = sorted(REPO.glob("*/sync.toml"))
    if not sync_files:
        errs.append("no sync.toml files found at repo root")
    for p in sync_files:
        errs.extend(check_sync_toml(p))
    errs.extend(check_shell_syntax())

    if errs:
        for e in errs:
            print(e, file=sys.stderr)
        print(f"\n{len(errs)} validation error(s)", file=sys.stderr)
        return 1
    print(f"ok: {len(sync_files)} sync.toml files, shell syntax clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
