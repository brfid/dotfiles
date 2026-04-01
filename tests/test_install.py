"""Tests for the dotfiles repo structure.

Validates bash syntax for all shell scripts and verifies stow package
directory conventions.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

DOTFILES = Path(__file__).parent.parent
PACKAGES = DOTFILES / "packages"

# Directories that are stow packages (contents mirror $HOME)
STOW_PACKAGES = [
    "bash",
    "shell",
    "nvim",
    "tmux",
    "git",
    "gh",
    "claude",
    "copilot",
    "vscode",
    "neomutt",
    "systemd-user",
    "x11",
    "yazi",
]


def all_shell_scripts() -> list[Path]:
    """Return all .sh files in the repo (excluding .git)."""
    return sorted(
        p for p in DOTFILES.rglob("*.sh")
        if ".git" not in p.parts
    )


def all_bash_configs() -> list[Path]:
    """Return bash config files that should pass syntax check."""
    candidates = [
        PACKAGES / "bash" / ".bashrc",
        PACKAGES / "shell" / ".config" / "shell" / "aliases",
    ]
    candidates.extend(
        (PACKAGES / "shell" / ".config" / "shell" / "local.d").glob("*.sh")
    )
    return [p for p in candidates if p.exists()]


@pytest.mark.parametrize(
    "script", all_shell_scripts(), ids=lambda p: str(p.relative_to(DOTFILES))
)
def test_bash_syntax(script: Path) -> None:
    """All .sh files must pass bash -n syntax check."""
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Syntax error in {script.name}:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "config", all_bash_configs(), ids=lambda p: str(p.relative_to(DOTFILES))
)
def test_bash_config_syntax(config: Path) -> None:
    """Bash config files (bashrc, aliases, local.d) must pass syntax check."""
    result = subprocess.run(
        ["bash", "-n", str(config)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Syntax error in {config.name}:\n{result.stderr}"
    )


def test_stow_packages_exist() -> None:
    """All declared stow packages must exist as directories."""
    missing = [p for p in STOW_PACKAGES if not (PACKAGES / p).is_dir()]
    assert not missing, f"Missing stow packages: {missing}"


