"""Tests for the gdrive_backup script.

Validates config parsing, rclone filter generation, and command assembly.
Does not mock or call rclone itself.
"""

from __future__ import annotations

import sys
import textwrap
from datetime import date, timedelta
from pathlib import Path

import pytest

# Allow importing scripts/ as modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import gdrive_backup


DOTFILES = Path(__file__).resolve().parent.parent


# -- Config loading ----------------------------------------------------------


def test_load_config_valid(tmp_path: Path) -> None:
    """Valid TOML produces a Config with correct fields."""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        textwrap.dedent("""\
        [defaults]
        remote = "gdrive:backups/pi"
        retain_days = 30
        notify_email = "test@example.com"

        [[backup]]
        name = "stuff"
        mode = "archive"
        source = "/tmp/stuff"
        include = ["docs/**"]
        exclude = ["cache/**"]
        """)
    )
    config = gdrive_backup.load_config(cfg)
    assert config.defaults.remote == "gdrive:backups/pi"
    assert config.defaults.retain_days == 30
    assert config.defaults.notify_email == "test@example.com"
    assert len(config.backups) == 1
    assert config.backups[0].name == "stuff"
    assert config.backups[0].mode == "archive"
    assert config.backups[0].include == ["docs/**"]
    assert config.backups[0].exclude == ["cache/**"]


def test_load_config_expands_tilde(tmp_path: Path) -> None:
    """Source paths with ~ are expanded to absolute paths."""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        textwrap.dedent("""\
        [defaults]
        remote = "gdrive:test"

        [[backup]]
        name = "home"
        mode = "bisync"
        source = "~/Documents"
        """)
    )
    config = gdrive_backup.load_config(cfg)
    source = config.backups[0].source
    assert "~" not in str(source)
    assert source.is_absolute()


def test_load_config_missing_remote(tmp_path: Path) -> None:
    """Config without [defaults].remote raises SystemExit."""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        textwrap.dedent("""\
        [defaults]
        retain_days = 30

        [[backup]]
        name = "x"
        mode = "archive"
        source = "/tmp"
        """)
    )
    with pytest.raises(SystemExit, match="remote"):
        gdrive_backup.load_config(cfg)


def test_load_config_invalid_mode(tmp_path: Path) -> None:
    """Invalid mode raises SystemExit."""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        textwrap.dedent("""\
        [defaults]
        remote = "gdrive:test"

        [[backup]]
        name = "bad"
        mode = "mirror"
        source = "/tmp"
        """)
    )
    with pytest.raises(SystemExit, match="mirror"):
        gdrive_backup.load_config(cfg)


def test_load_config_no_backups(tmp_path: Path) -> None:
    """Config with no [[backup]] sections raises SystemExit."""
    cfg = tmp_path / "config.toml"
    cfg.write_text('[defaults]\nremote = "gdrive:test"\n')
    with pytest.raises(SystemExit, match="no \\[\\[backup\\]\\]"):
        gdrive_backup.load_config(cfg)


def test_load_config_missing_file(tmp_path: Path) -> None:
    """Missing config file raises SystemExit."""
    with pytest.raises(SystemExit, match="Config not found"):
        gdrive_backup.load_config(tmp_path / "nope.toml")


def test_load_config_defaults_are_optional(tmp_path: Path) -> None:
    """retain_days and notify_email default when omitted."""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        textwrap.dedent("""\
        [defaults]
        remote = "gdrive:test"

        [[backup]]
        name = "x"
        mode = "archive"
        source = "/tmp"
        """)
    )
    config = gdrive_backup.load_config(cfg)
    assert config.defaults.retain_days == 90
    assert config.defaults.notify_email == ""


def test_load_config_per_set_remote_override(tmp_path: Path) -> None:
    """A backup set can override the default remote."""
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        textwrap.dedent("""\
        [defaults]
        remote = "gdrive:default"

        [[backup]]
        name = "custom"
        mode = "bisync"
        source = "/tmp"
        remote = "gdrive:custom"
        """)
    )
    config = gdrive_backup.load_config(cfg)
    assert gdrive_backup.resolve_remote(
        config.backups[0], config.defaults
    ) == "gdrive:custom"


# -- Filter file generation --------------------------------------------------


def test_build_filter_include_exclude() -> None:
    """Filter file includes + rules, - rules, and a catch-all exclude."""
    path = gdrive_backup.build_filter_file(
        include=["worlds/**", "minetest.conf"],
        exclude=["cache/**"],
    )
    assert path is not None
    content = path.read_text()
    lines = content.strip().splitlines()
    assert lines[0] == "+ worlds/**"
    assert lines[1] == "+ minetest.conf"
    assert lines[2] == "- cache/**"
    assert lines[3] == "- **"
    path.unlink()


def test_build_filter_exclude_only() -> None:
    """Exclude-only filter has no catch-all since nothing is included."""
    path = gdrive_backup.build_filter_file(
        include=[],
        exclude=[".git/**", "node_modules/**"],
    )
    assert path is not None
    content = path.read_text()
    lines = content.strip().splitlines()
    assert lines == ["- .git/**", "- node_modules/**"]
    path.unlink()


def test_build_filter_empty() -> None:
    """No include or exclude returns None."""
    assert gdrive_backup.build_filter_file([], []) is None


# -- Command assembly --------------------------------------------------------


def _make_set(
    name: str = "test",
    mode: str = "archive",
    source: str = "/tmp/test",
    remote: str = "",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> gdrive_backup.BackupSet:
    return gdrive_backup.BackupSet(
        name=name,
        mode=mode,
        source=Path(source),
        remote=remote,
        include=include or [],
        exclude=exclude or [],
    )


_DEFAULTS = gdrive_backup.Defaults(remote="gdrive:backups/pi")


def test_build_archive_cmd() -> None:
    """Archive command includes sync, --backup-dir, and correct paths."""
    backup = _make_set(name="minetest")
    cmd = gdrive_backup.build_archive_cmd(backup, _DEFAULTS, "2026-03-24")
    assert cmd[0:3] == ["rclone", "sync", "/tmp/test"]
    assert cmd[3] == "gdrive:backups/pi/minetest/current"
    assert "--backup-dir" in cmd
    idx = cmd.index("--backup-dir")
    assert cmd[idx + 1] == "gdrive:backups/pi/minetest/archive/2026-03-24"
    assert "--dry-run" not in cmd


def test_build_archive_cmd_dry_run() -> None:
    """Archive command includes --dry-run when requested."""
    backup = _make_set(name="minetest")
    cmd = gdrive_backup.build_archive_cmd(
        backup, _DEFAULTS, "2026-03-24", dry_run=True
    )
    assert "--dry-run" in cmd


def test_build_archive_cmd_with_filters() -> None:
    """Archive command includes --filter-from when filters are present."""
    backup = _make_set(
        name="minetest",
        include=["worlds/**"],
        exclude=["cache/**"],
    )
    cmd = gdrive_backup.build_archive_cmd(backup, _DEFAULTS, "2026-03-24")
    assert "--filter-from" in cmd
    idx = cmd.index("--filter-from")
    filter_path = Path(cmd[idx + 1])
    assert filter_path.exists()
    filter_path.unlink()


def test_build_bisync_cmd() -> None:
    """Bisync command includes bisync, --resilient, and correct paths."""
    backup = _make_set(
        name="myproject", mode="bisync", remote="gdrive:myproject"
    )
    cmd = gdrive_backup.build_bisync_cmd(backup, _DEFAULTS)
    assert cmd[0:3] == ["rclone", "bisync", "/tmp/test"]
    assert cmd[3] == "gdrive:myproject"
    assert "--resilient" in cmd
    assert "--dry-run" not in cmd


def test_build_bisync_cmd_dry_run() -> None:
    """Bisync command includes --dry-run when requested."""
    backup = _make_set(name="myproject", mode="bisync")
    cmd = gdrive_backup.build_bisync_cmd(backup, _DEFAULTS, dry_run=True)
    assert "--dry-run" in cmd


def test_build_bisync_cmd_uses_default_remote() -> None:
    """Bisync with no per-set remote uses the default."""
    backup = _make_set(name="stuff", mode="bisync")
    cmd = gdrive_backup.build_bisync_cmd(backup, _DEFAULTS)
    assert cmd[3] == "gdrive:backups/pi"


# -- Resolve remote ----------------------------------------------------------


def test_resolve_remote_per_set_override() -> None:
    """Per-set remote takes precedence over default."""
    backup = _make_set(remote="gdrive:custom")
    assert gdrive_backup.resolve_remote(backup, _DEFAULTS) == "gdrive:custom"


def test_resolve_remote_falls_back_to_default() -> None:
    """Empty per-set remote falls back to default."""
    backup = _make_set(remote="")
    assert (
        gdrive_backup.resolve_remote(backup, _DEFAULTS) == "gdrive:backups/pi"
    )


# -- CLI parsing -------------------------------------------------------------


def test_parse_args_defaults() -> None:
    """Default args parse correctly."""
    args = gdrive_backup.parse_args([])
    assert args.config == gdrive_backup.DEFAULT_CONFIG
    assert args.only is None
    assert args.mode is None
    assert args.dry_run is False
    assert args.prune_only is False
    assert args.list_sets is False


def test_parse_args_all_flags() -> None:
    """All flags are recognized."""
    args = gdrive_backup.parse_args(
        ["--only", "mine", "--mode", "archive", "--dry-run"]
    )
    assert args.only == "mine"
    assert args.mode == "archive"
    assert args.dry_run is True


# -- Example config ----------------------------------------------------------


def test_example_config_is_valid() -> None:
    """The shipped config.toml.example parses without error."""
    example = DOTFILES / "scripts" / "config.toml.example"
    assert example.exists(), "config.toml.example is missing"
    config = gdrive_backup.load_config(example)
    assert len(config.backups) >= 1
    modes = {b.mode for b in config.backups}
    assert modes == {"archive", "bisync"}
