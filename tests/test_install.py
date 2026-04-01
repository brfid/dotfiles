"""Tests for the dotfiles repo structure.

Validates bash syntax for all shell scripts and verifies that every source
path declared in mapping.yaml exists in the repo.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

DOTFILES = Path(__file__).parent.parent
MAPPING = DOTFILES / "mapping.yaml"


def all_shell_scripts() -> list[Path]:
    """Return all .sh files in the repo (excluding .git)."""
    return sorted(
        p for p in DOTFILES.rglob("*.sh")
        if ".git" not in p.parts
    )


def all_bash_configs() -> list[Path]:
    """Return bash config files that should pass syntax check."""
    candidates = [
        DOTFILES / "shell" / "bashrc",
        DOTFILES / "shell" / "aliases",
    ]
    candidates.extend((DOTFILES / "shell" / "local").glob("*.sh"))
    return [p for p in candidates if p.exists()]


def mapping_sources() -> list[Path]:
    """Return all source paths declared in mapping.yaml."""
    with MAPPING.open() as f:
        data = yaml.safe_load(f)
    sources = []
    for profile in data.values():
        for src in profile:
            sources.append(DOTFILES / src)
    return sources


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
    """Bash config files (bashrc, aliases, local/) must pass syntax check."""
    result = subprocess.run(
        ["bash", "-n", str(config)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Syntax error in {config.name}:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "source", mapping_sources(), ids=lambda p: str(p.relative_to(DOTFILES))
)
def test_mapping_sources_exist(source: Path) -> None:
    """Every source path in mapping.yaml must exist in the repo."""
    assert source.exists(), f"mapping.yaml references missing path: {source}"


