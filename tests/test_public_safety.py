"""Tests for public-repo safety guardrails."""
from __future__ import annotations

import subprocess
from pathlib import Path

DOTFILES = Path(__file__).parent.parent


def test_public_safety_script_exists() -> None:
    """Repo should provide a public-safety scan entry point."""
    script = DOTFILES / "scripts" / "check_public_safety.sh"
    assert script.is_file()


def test_public_safety_script_passes() -> None:
    """Tracked files should not contain private paths or direct identifiers."""
    result = subprocess.run(
        ["bash", "scripts/check_public_safety.sh"],
        cwd=DOTFILES,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_global_pre_commit_fails_closed_and_runs_public_safety() -> None:
    """The tracked global pre-commit hook should fail closed and run safety scans."""
    hook = (DOTFILES / "git" / "hooks" / "pre-commit").read_text()
    assert "exit 1" in hook
    assert "scripts/check_secrets.sh" in hook
    assert "scripts/check_public_safety.sh" in hook
