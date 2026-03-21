"""Tests for the dotfiles install system.

Validates bash syntax, file existence for all linked sources,
and profile structure completeness.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

DOTFILES = Path(__file__).parent.parent
INSTALL_DIR = DOTFILES / "install"
LOCAL_D = DOTFILES / "shell" / "local.d"


def all_install_scripts() -> list[Path]:
    """Return install.sh plus all install/*.sh profile scripts."""
    scripts = [DOTFILES / "install.sh"]
    scripts.extend(sorted(INSTALL_DIR.glob("*.sh")))
    return scripts


def all_shell_scripts() -> list[Path]:
    """Return all shell local.d scripts."""
    return sorted(LOCAL_D.glob("*.sh")) if LOCAL_D.exists() else []


@pytest.mark.parametrize("script", all_install_scripts(), ids=lambda p: p.name)
def test_bash_syntax_install(script: Path) -> None:
    """All install scripts must pass bash -n syntax check."""
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Syntax error in {script.name}:\n{result.stderr}"
    )


@pytest.mark.parametrize("script", all_shell_scripts(), ids=lambda p: p.name)
def test_bash_syntax_local_d(script: Path) -> None:
    """All shell/local.d scripts must pass bash -n syntax check."""
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Syntax error in {script.name}:\n{result.stderr}"
    )


def _extract_dotfiles_sources(script: Path) -> list[str]:
    """Extract DOTFILES-relative source paths from link_path calls.

    Args:
        script: Path to a bash install script.

    Returns:
        List of relative paths (e.g. 'nvim', 'tmux/.tmux.conf').
    """
    pattern = re.compile(r'link_path\s+"\$DOTFILES/([^"]+)"')
    return pattern.findall(script.read_text())


@pytest.mark.parametrize("script", all_install_scripts(), ids=lambda p: p.name)
def test_link_path_sources_exist(script: Path) -> None:
    """Every $DOTFILES/... source in a link_path call must exist in the repo."""
    missing = []
    for rel in _extract_dotfiles_sources(script):
        target = DOTFILES / rel
        if not target.exists():
            missing.append(rel)
    assert not missing, (
        f"{script.name} references missing sources:\n"
        + "\n".join(f"  {r}" for r in missing)
    )


def test_profile_scripts_have_local_d() -> None:
    """Each install/<profile>.sh that links shell/local.d/<profile>.sh must have that file."""
    if not INSTALL_DIR.exists():
        pytest.skip("install/ directory does not exist yet")
    for profile_script in INSTALL_DIR.glob("*.sh"):
        profile = profile_script.stem
        content = profile_script.read_text()
        if f"shell/local.d/{profile}.sh" in content:
            expected = LOCAL_D / f"{profile}.sh"
            assert expected.exists(), (
                f"install/{profile}.sh references shell/local.d/{profile}.sh "
                f"but that file does not exist"
            )


def test_install_dir_exists() -> None:
    """install/ directory must exist."""
    assert INSTALL_DIR.is_dir()


def test_common_script_exists() -> None:
    """install/common.sh must exist."""
    assert (INSTALL_DIR / "common.sh").exists()


def test_known_profiles_exist() -> None:
    """Pi and edcloud profiles must exist."""
    for profile in ("pi", "edcloud"):
        assert (INSTALL_DIR / f"{profile}.sh").exists(), (
            f"install/{profile}.sh is missing"
        )
