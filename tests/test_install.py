"""Tests for the dotfiles repo structure.

Validates bash syntax for shell scripts (excluding vendored plugins) and
verifies that every tool in the README.md profile table exists as a directory.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

DOTFILES = Path(__file__).parent.parent
README = DOTFILES / "README.md"

# Directories containing third-party code — not ours to test.
_VENDORED = {"plugins", ".tmux"}


def _is_vendored(path: Path) -> bool:
    """Return True if path is inside a vendored directory."""
    return bool(_VENDORED & set(path.relative_to(DOTFILES).parts))


def all_shell_files() -> list[Path]:
    """Return shell files we own: *.sh scripts plus bashrc/aliases."""
    scripts = [
        p
        for p in DOTFILES.rglob("*.sh")
        if ".git" not in p.parts and not _is_vendored(p)
    ]
    for name in ("bashrc", "aliases"):
        p = DOTFILES / "shell" / name
        if p.exists():
            scripts.append(p)
    return sorted(scripts)


def profile_tools() -> list[str]:
    """Parse tool names from the profile table in README.md."""
    text = README.read_text()
    tools: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Tool "):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("| "):
            match = re.match(r"\|\s*(\S+)\s*\|", line)
            if match:
                tools.append(match.group(1))
        elif in_table:
            break
    return tools


def tracked_text_files() -> list[Path]:
    """Return tracked text-like files we should scan for merge markers."""
    extensions = {
        ".md",
        ".py",
        ".sh",
        ".json",
        ".toml",
        ".yml",
        ".yaml",
        ".conf",
        ".service",
        ".timer",
        ".rules",
    }
    files: list[Path] = []
    for path in DOTFILES.rglob("*"):
        if not path.is_file() or ".git" in path.parts or _is_vendored(path):
            continue
        if path.name in {"aliases", "bashrc", "mailcap", "neomuttrc", "zshrc"}:
            files.append(path)
            continue
        if path.suffix in extensions:
            files.append(path)
    return sorted(files)


@pytest.mark.parametrize(
    "script",
    all_shell_files(),
    ids=lambda p: str(p.relative_to(DOTFILES)),
)
def test_bash_syntax(script: Path) -> None:
    """Our shell files must pass bash -n syntax check."""
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Syntax error in {script.name}:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "tool",
    profile_tools(),
    ids=lambda t: t,
)
def test_profile_tools_exist(tool: Path) -> None:
    """Every tool in the README profile table must exist as a directory."""
    assert (DOTFILES / tool).is_dir(), (
        f"README.md profile table references missing directory: {tool}"
    )


@pytest.mark.parametrize(
    "path",
    tracked_text_files(),
    ids=lambda p: str(p.relative_to(DOTFILES)),
)
def test_no_merge_conflict_markers(path: Path) -> None:
    """Tracked text files must not contain unresolved merge markers."""
    text = path.read_text()
    assert re.search(r"^(<<<<<<< |=======|>>>>>>> )", text, re.MULTILINE) is None, (
        f"Unresolved merge conflict marker found in {path}"
    )
