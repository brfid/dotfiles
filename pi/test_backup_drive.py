"""Focused tests for pure backup-drive planning and rendering helpers."""

from __future__ import annotations

import json
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import backup_drive


class BackupDriveTests(unittest.TestCase):
    def test_load_config_requires_serial_and_both_labels(self) -> None:
        with mock.patch.dict(
            backup_drive.os.environ,
            {"PI_BACKUP_DISK_SERIAL": "TARGET"},
            clear=True,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "PI_BACKUP_BOOT_LABEL, PI_BACKUP_ROOT_LABEL required",
            ):
                backup_drive.load_config()

        with mock.patch.dict(
            backup_drive.os.environ,
            {
                "PI_BACKUP_DISK_SERIAL": "TARGET",
                "PI_BACKUP_BOOT_LABEL": "BOOT",
                "PI_BACKUP_ROOT_LABEL": "ROOT",
            },
            clear=True,
        ):
            config = backup_drive.load_config()
            self.assertEqual(config.boot_label, "BOOT")
            self.assertEqual(config.root_label, "ROOT")

    def test_parse_lsblk_selects_matching_whole_disk(self) -> None:
        payload = json.dumps(
            {
                "blockdevices": [
                    {"path": "/dev/sda", "type": "disk", "serial": "TARGET"},
                    {"path": "/dev/nvme0n1", "type": "disk", "serial": "BOOT"},
                ]
            }
        )
        self.assertEqual(backup_drive.parse_lsblk(payload, "TARGET"), Path("/dev/sda"))

    def test_parse_lsblk_rejects_missing_or_duplicate_serial(self) -> None:
        payload = json.dumps(
            {
                "blockdevices": [
                    {"path": "/dev/sda", "type": "disk", "serial": "DUP"},
                    {"path": "/dev/sdb", "type": "disk", "serial": "DUP"},
                ]
            }
        )
        with self.assertRaises(RuntimeError):
            backup_drive.parse_lsblk(payload, "DUP")
        with self.assertRaises(RuntimeError):
            backup_drive.parse_lsblk(payload, "MISSING")

    def test_replace_root_argument_replaces_and_deduplicates(self) -> None:
        cmdline = "console=tty1 root=/dev/old quiet root=UUID=also-old\n"
        rendered = backup_drive.replace_root_argument(cmdline, "new-uuid")
        self.assertEqual(
            rendered,
            "console=tty1 root=UUID=new-uuid quiet\n",
        )

    def test_render_fstab_uses_target_uuids(self) -> None:
        rendered = backup_drive.render_fstab("BOOT-UUID", "ROOT-UUID")
        self.assertIn("UUID=BOOT-UUID /boot/firmware vfat", rendered)
        self.assertIn("UUID=ROOT-UUID / ext4", rendered)

    def test_snapshot_names_and_retention_ignore_partial_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "2026-05-18T020000",
                "2026-05-25T020000",
                "2026-06-01T020000",
                "2026-06-08T020000.partial",
                "notes",
            ):
                (root / name).mkdir()
            names = backup_drive.snapshot_names(root.iterdir())
            self.assertEqual(
                names,
                [
                    "2026-05-18T020000",
                    "2026-05-25T020000",
                    "2026-06-01T020000",
                ],
            )
            self.assertEqual(
                backup_drive.retention_deletions(names, 2),
                ["2026-05-18T020000"],
            )

    def test_remove_partial_snapshots_keeps_completed_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            completed = root / "2026-06-01T020000"
            partial = root / "2026-06-08T020000.partial"
            completed.mkdir()
            partial.mkdir()
            (partial / "data").write_text("incomplete", encoding="utf-8")

            backup_drive.remove_partial_snapshots(root)

            self.assertTrue(completed.exists())
            self.assertFalse(partial.exists())

    def test_mount_action_mounts_reuses_and_rejects_conflicts(self) -> None:
        self.assertEqual(
            backup_drive.mount_action(
                target_identity="",
                expected_identity="8:2",
                other_targets=[],
            ),
            "mount",
        )
        self.assertEqual(
            backup_drive.mount_action(
                target_identity="8:2",
                expected_identity="8:2",
                other_targets=[],
            ),
            "reuse",
        )
        with self.assertRaisesRegex(RuntimeError, "unexpected device"):
            backup_drive.mount_action(
                target_identity="8:3",
                expected_identity="8:2",
                other_targets=[],
            )
        with self.assertRaisesRegex(RuntimeError, "already mounted"):
            backup_drive.mount_action(
                target_identity="",
                expected_identity="8:2",
                other_targets=[Path("/media/backup")],
            )

    def test_boot_mirror_args_avoid_unsupported_fat_metadata(self) -> None:
        args = backup_drive.boot_mirror_rsync_args(
            Path("/snapshot/boot"),
            Path("/target/boot"),
        )
        self.assertIn("-rt", args)
        self.assertNotIn("-aHAX", args)
        self.assertIn("--modify-window=1", args)

    def test_rsync_verbosity_levels(self) -> None:
        quiet = backup_drive.rsync_args(Path("/source"), Path("/target"))
        progress = backup_drive.rsync_args(
            Path("/source"),
            Path("/target"),
            verbosity="progress",
        )
        noisy = backup_drive.rsync_args(
            Path("/source"),
            Path("/target"),
            verbosity="noisy",
        )
        self.assertNotIn("--itemize-changes", quiet)
        self.assertNotIn("--human-readable", quiet)
        self.assertNotIn("--itemize-changes", progress)
        self.assertIn("--human-readable", progress)
        self.assertIn("--info=progress2,stats2", progress)
        self.assertIn("--itemize-changes", noisy)
        self.assertIn("--human-readable", noisy)
        self.assertIn("--info=progress2,stats2", noisy)

    def test_cli_verbosity_options(self) -> None:
        self.assertTrue(backup_drive.parse_args(["--noisy", "run"]).noisy)
        self.assertTrue(backup_drive.parse_args(["-v", "run"]).noisy)
        self.assertTrue(backup_drive.parse_args(["run", "--noisy"]).noisy)
        progress = backup_drive.parse_args(["run", "--progress"])
        self.assertTrue(progress.progress)
        self.assertFalse(progress.noisy)
        quiet = backup_drive.parse_args(["run"])
        self.assertFalse(quiet.progress)
        self.assertFalse(quiet.noisy)

    def test_nested_mount_excludes_cover_user_cloud_mounts(self) -> None:
        payload = json.dumps(
            {
                "filesystems": [
                    {
                        "target": "/",
                        "children": [
                            {"target": "/boot/firmware"},
                            {"target": "/home/example/Cloud"},
                        ],
                    }
                ]
            }
        )
        with mock.patch.object(backup_drive, "command_output", return_value=payload):
            excludes = backup_drive.nested_mount_excludes()
        self.assertIn("/boot/firmware/***", excludes)
        self.assertIn("/home/example/Cloud/***", excludes)
        self.assertNotIn("//***", excludes)

    def test_temporary_workstation_cache_policy_preserves_tooling(self) -> None:
        self.assertIn("/var/cache/apt/***", backup_drive.ROOT_EXCLUDES)
        self.assertIn("/home/*/.cache/***", backup_drive.ROOT_EXCLUDES)
        self.assertIn(
            "/home/*/.local/share/Trash/***",
            backup_drive.ROOT_EXCLUDES,
        )
        self.assertNotIn("/home/*/.cargo/registry/***", backup_drive.ROOT_EXCLUDES)
        self.assertNotIn("/home/*/.npm/***", backup_drive.ROOT_EXCLUDES)
        self.assertNotIn("/home/*/.rustup/***", backup_drive.ROOT_EXCLUDES)

    def test_run_rsync_accepts_only_success_and_vanished_source(self) -> None:
        success = subprocess.CompletedProcess(["rsync"], 0)
        vanished = subprocess.CompletedProcess(["rsync"], 24)
        partial_error = subprocess.CompletedProcess(["rsync"], 23)

        with mock.patch.object(backup_drive, "run_command", return_value=success):
            self.assertIsNone(
                backup_drive.run_rsync(["rsync"], context="root pass 1")
            )
        with mock.patch.object(backup_drive, "run_command", return_value=vanished):
            warning = backup_drive.run_rsync(
                ["rsync"],
                context="root pass 1",
            )
            self.assertIn("source files vanished", warning)
        with mock.patch.object(
            backup_drive,
            "run_command",
            return_value=partial_error,
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                backup_drive.run_rsync(["rsync"], context="root pass 1")

    def test_snapshot_is_verified_before_canonical_rename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                mount_root=root / "target",
            )
            seen: list[Path] = []

            def verify(path: Path) -> None:
                seen.append(path)
                self.assertTrue(path.name.endswith(".partial"))
                self.assertFalse(path.with_name(path.name.removesuffix(".partial")).exists())

            with (
                mock.patch.object(backup_drive, "run_rsync", return_value=None),
                mock.patch.object(
                    backup_drive,
                    "verify_staged_snapshot",
                    side_effect=verify,
                ),
            ):
                snapshot, warnings = backup_drive.create_snapshot(
                    config,
                    backup_drive.dt.datetime(2026, 6, 5, 20, 0, 0),
                    Path("/source"),
                    (),
                )

            self.assertEqual(len(seen), 1)
            self.assertEqual(snapshot.name, "2026-06-05T200000")
            self.assertTrue(snapshot.is_dir())
            self.assertEqual(warnings, [])

    def test_rejected_snapshot_is_deleted_immediately(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                mount_root=root / "target",
            )
            with (
                mock.patch.object(backup_drive, "run_rsync", return_value=None),
                mock.patch.object(
                    backup_drive,
                    "verify_staged_snapshot",
                    side_effect=RuntimeError("invalid capture"),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "invalid capture"):
                    backup_drive.create_snapshot(
                        config,
                        backup_drive.dt.datetime(2026, 6, 5, 20, 0, 0),
                        Path("/source"),
                        (),
                    )

            self.assertEqual(list(config.snapshots_dir.iterdir()), [])

    def test_pruning_keeps_configured_newest_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                retention=2,
                mount_root=Path(directory),
            )
            config.snapshots_dir.mkdir(parents=True)
            for name in (
                "2026-05-18T020000",
                "2026-05-25T020000",
                "2026-06-01T020000",
            ):
                (config.snapshots_dir / name).mkdir()

            backup_drive.prune_snapshots(config)

            self.assertEqual(
                backup_drive.snapshot_names(config.snapshots_dir.iterdir()),
                ["2026-05-25T020000", "2026-06-01T020000"],
            )

    def test_signal_handler_raises_cleanup_aware_interruption(self) -> None:
        old_term = signal.getsignal(signal.SIGTERM)
        old_int = signal.getsignal(signal.SIGINT)
        try:
            backup_drive.install_signal_handlers()
            with self.assertRaisesRegex(backup_drive.BackupInterrupted, "SIGTERM"):
                signal.raise_signal(signal.SIGTERM)
        finally:
            signal.signal(signal.SIGTERM, old_term)
            signal.signal(signal.SIGINT, old_int)

    def test_failed_run_unmounts_only_owned_mounts_and_records_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                state_dir=root / "state",
                mount_root=root / "mounts",
            )
            devices = backup_drive.Device(
                disk=Path("/dev/sda"),
                boot=Path("/dev/sda1"),
                root=Path("/dev/sda2"),
            )
            root_lease = backup_drive.MountLease(
                devices.root, config.root_mount, True
            )
            boot_lease = backup_drive.MountLease(
                devices.boot, config.boot_mount, False
            )
            source_lease = backup_drive.MountLease(
                Path("/"), backup_drive.DEFAULT_SOURCE_ROOT, True
            )

            with (
                mock.patch.object(backup_drive, "install_signal_handlers"),
                mock.patch.object(backup_drive, "resolve_devices", return_value=devices),
                mock.patch.object(
                    backup_drive,
                    "mount_device",
                    side_effect=[root_lease, boot_lease],
                ),
                mock.patch.object(
                    backup_drive,
                    "mount_source_view",
                    return_value=source_lease,
                ),
                mock.patch.object(backup_drive, "write_probe"),
                mock.patch.object(backup_drive, "verify_capacity"),
                mock.patch.object(backup_drive, "nested_mount_excludes", return_value=()),
                mock.patch.object(
                    backup_drive,
                    "create_snapshot",
                    side_effect=RuntimeError("rsync failed"),
                ),
                mock.patch.object(backup_drive, "run_command"),
                mock.patch.object(backup_drive, "unmount") as unmount,
            ):
                with self.assertRaisesRegex(RuntimeError, "rsync failed"):
                    backup_drive.run_backup(config)

            self.assertEqual(
                unmount.call_args_list,
                [
                    mock.call(backup_drive.DEFAULT_SOURCE_ROOT),
                    mock.call(config.root_mount),
                ],
            )
            state = json.loads((config.state_dir / "last-run.json").read_text())
            self.assertEqual(state["status"], "failed")
            self.assertEqual(state["phase"], "create-snapshot")
            self.assertIn("rsync failed", state["message"])

    def test_retention_runs_only_after_mirror_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                state_dir=root / "state",
                mount_root=root / "mounts",
            )
            devices = backup_drive.Device(
                disk=Path("/dev/sda"),
                boot=Path("/dev/sda1"),
                root=Path("/dev/sda2"),
            )
            leases = [
                backup_drive.MountLease(devices.root, config.root_mount, True),
                backup_drive.MountLease(devices.boot, config.boot_mount, True),
            ]
            snapshot = config.snapshots_dir / "2026-06-05T200000"
            events: list[str] = []

            with (
                mock.patch.object(backup_drive, "install_signal_handlers"),
                mock.patch.object(backup_drive, "resolve_devices", return_value=devices),
                mock.patch.object(
                    backup_drive,
                    "mount_device",
                    side_effect=leases,
                ),
                mock.patch.object(
                    backup_drive,
                    "mount_source_view",
                    return_value=backup_drive.MountLease(
                        Path("/"),
                        backup_drive.DEFAULT_SOURCE_ROOT,
                        True,
                    ),
                ),
                mock.patch.object(backup_drive, "write_probe"),
                mock.patch.object(backup_drive, "verify_capacity"),
                mock.patch.object(backup_drive, "nested_mount_excludes", return_value=()),
                mock.patch.object(
                    backup_drive,
                    "create_snapshot",
                    return_value=(snapshot, []),
                ),
                mock.patch.object(
                    backup_drive,
                    "refresh_mirror",
                    side_effect=lambda *_, **__: events.append("refresh"),
                ),
                mock.patch.object(
                    backup_drive,
                    "verify_mirror",
                    side_effect=lambda *_: events.append("verify"),
                ),
                mock.patch.object(
                    backup_drive,
                    "write_mirror_state",
                    side_effect=lambda *_, **__: events.append("mark"),
                ),
                mock.patch.object(
                    backup_drive,
                    "prune_snapshots",
                    side_effect=lambda *_: events.append("prune"),
                ),
                mock.patch.object(backup_drive, "offline_boot_check"),
                mock.patch.object(backup_drive, "run_command"),
                mock.patch.object(backup_drive, "unmount"),
            ):
                backup_drive.run_backup(config)

            self.assertEqual(events, ["refresh", "verify", "mark", "prune"])

    def test_status_fails_for_latest_non_successful_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                state_dir=Path(directory),
            )
            (config.state_dir / "last-run.json").write_text(
                json.dumps({"status": "interrupted"}) + "\n",
                encoding="utf-8",
            )
            with mock.patch("builtins.print"):
                self.assertEqual(backup_drive.status(config), 1)

            (config.state_dir / "last-run.json").write_text(
                json.dumps({"status": "success"}) + "\n",
                encoding="utf-8",
            )
            with mock.patch("builtins.print"):
                self.assertEqual(backup_drive.status(config), 0)


if __name__ == "__main__":
    unittest.main()
