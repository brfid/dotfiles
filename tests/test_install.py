"""Tests for the dotfiles repo structure.

Validates bash syntax for shell scripts (excluding vendored plugins) and
verifies that every tool in the README.md profile table exists as a directory.
"""
from __future__ import annotations

import re
import subprocess
import tomllib
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
    """Parse tool names from the root config inventory table in README.md."""
    text = README.read_text()
    tools: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Path "):
            in_table = True
            continue
        if in_table and set(line.replace("|", "").strip()) <= {"-", ":", " "}:
            continue
        if in_table and line.startswith("|"):
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


def structured_tool_dirs() -> list[Path]:
    """Return top-level tool dirs that opt into the sync.toml convention."""
    return sorted(
        path.parent
        for path in DOTFILES.glob("*/sync.toml")
        if path.parent.is_dir()
    )


def test_secret_scan_script_exists() -> None:
    """Repo should provide a visible local secret-scan entry point."""
    assert (DOTFILES / "scripts" / "check_secrets.sh").is_file()


def test_secret_scan_workflow_exists() -> None:
    """Repo should provide CI secret scanning."""
    workflow = DOTFILES / ".github" / "workflows" / "secret-scan.yml"
    assert workflow.is_file()
    text = workflow.read_text()
    assert "gitleaks" in text
    assert "git/.gitleaks.toml" in text


def test_markdown_check_script_exists() -> None:
    """Repo should provide a visible local Markdown check entry point."""
    assert (DOTFILES / "scripts" / "check_markdown.sh").is_file()


def test_markdown_workflow_exists() -> None:
    """Repo should provide CI Markdown formatting checks."""
    workflow = DOTFILES / ".github" / "workflows" / "markdown.yml"
    assert workflow.is_file()
    text = workflow.read_text()
    assert "mdformat" in text
    assert "./scripts/check_markdown.sh" in text


def test_pyproject_declares_markdown_tools() -> None:
    """Dev dependencies should include Markdown format tooling."""
    with (DOTFILES / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)
    dev = pyproject["project"]["optional-dependencies"]["dev"]
    assert any(dep.startswith("mdformat") for dep in dev)
    assert any(dep.startswith("mdformat-gfm") for dep in dev)
    assert any(dep.startswith("mdformat-frontmatter") for dep in dev)


@pytest.mark.parametrize(
    "tool_dir",
    structured_tool_dirs(),
    ids=lambda p: str(p.relative_to(DOTFILES)),
)
def test_structured_tool_has_agents_and_sync_manifest(tool_dir: Path) -> None:
    """A tool using sync.toml must also provide a local AGENTS.md guide."""
    assert (tool_dir / "AGENTS.md").is_file(), (
        f"{tool_dir.relative_to(DOTFILES)}/AGENTS.md is missing"
    )


@pytest.mark.parametrize(
    "tool_dir",
    structured_tool_dirs(),
    ids=lambda p: str(p.relative_to(DOTFILES)),
)
def test_structured_tool_sync_manifest_parses(tool_dir: Path) -> None:
    """Per-tool sync manifests must be valid TOML and self-identifying."""
    sync_path = tool_dir / "sync.toml"
    with sync_path.open("rb") as handle:
        manifest = tomllib.load(handle)
    assert manifest["version"] == 1
    assert manifest["tool"] == tool_dir.name


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
