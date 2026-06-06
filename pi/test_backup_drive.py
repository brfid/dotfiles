"""Focused tests for the direct bootable-mirror workflow."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import backup_drive


class BackupDriveTests(unittest.TestCase):
    def test_load_config_requires_serial_and_labels(self) -> None:
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
                "PI_BACKUP_RETENTION": "obsolete",
            },
            clear=True,
        ):
            config = backup_drive.load_config()
        self.assertEqual(config.disk_serial, "TARGET")

    def test_parse_lsblk_selects_exactly_one_matching_disk(self) -> None:
        payload = json.dumps(
            {
                "blockdevices": [
                    {"path": "/dev/sda", "type": "disk", "serial": "TARGET"},
                    {"path": "/dev/nvme0n1", "type": "disk", "serial": "SOURCE"},
                ]
            }
        )
        self.assertEqual(backup_drive.parse_lsblk(payload, "TARGET"), Path("/dev/sda"))
        with self.assertRaises(RuntimeError):
            backup_drive.parse_lsblk(payload, "MISSING")

    def test_replace_root_argument_replaces_and_deduplicates(self) -> None:
        rendered = backup_drive.replace_root_argument(
            "console=tty1 root=/dev/old quiet root=UUID=also-old\n",
            "new-uuid",
        )
        self.assertEqual(rendered, "console=tty1 root=UUID=new-uuid quiet\n")

    def test_render_fstab_uses_target_uuids(self) -> None:
        rendered = backup_drive.render_fstab("BOOT-UUID", "ROOT-UUID")
        self.assertIn("UUID=BOOT-UUID /boot/firmware vfat", rendered)
        self.assertIn("UUID=ROOT-UUID / ext4", rendered)

    def test_mount_device_requires_exclusive_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "backup"
            with (
                mock.patch.object(
                    backup_drive, "device_identity", return_value="8:2"
                ),
                mock.patch.object(
                    backup_drive, "mounted_identity", return_value="8:3"
                ),
                mock.patch.object(backup_drive, "mounted_targets", return_value=[]),
                self.assertRaisesRegex(RuntimeError, "mountpoint already in use"),
            ):
                backup_drive.mount_device(Path("/dev/sda2"), target)

    def test_nested_mount_excludes_cover_user_mounts(self) -> None:
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

    def test_root_rsync_is_direct_destructive_mirror(self) -> None:
        args = backup_drive.rsync_args(
            Path("/source"),
            Path("/target"),
            excludes=backup_drive.MIRROR_EXCLUDES,
        )
        self.assertIn("--delete-excluded", args)
        self.assertIn("protect /lost+found", args)
        self.assertIn("protect /etc/fstab", args)
        self.assertIn("/etc/fstab", backup_drive.MIRROR_EXCLUDES)
        self.assertIn("-aHAXS", args)
        self.assertNotIn("--link-dest", args)
        self.assertEqual(args[-2:], ["/source/", "/target/"])

    def test_root_rsync_excludes_reproducible_dependency_trees(self) -> None:
        expected = (
            "/home/*/.bun/install/cache/***",
            "/home/*/.npm/_cacache/***",
            "/home/*/.npm/_npx/***",
            "/home/*/src/**/.venv/***",
            "/home/*/src/**/node_modules/***",
            "/home/*/src/**/target/***",
        )
        for pattern in expected:
            self.assertIn(pattern, backup_drive.MIRROR_EXCLUDES)
        self.assertNotIn("/home/*/src/**/dist/***", backup_drive.MIRROR_EXCLUDES)
        self.assertNotIn("/home/*/src/**/build/***", backup_drive.MIRROR_EXCLUDES)

    def test_direct_mirror_deletes_legacy_and_excluded_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            (source / "etc").mkdir(parents=True)
            (source / "etc" / "issue").write_text("current\n")
            (source / "etc" / "fstab").write_text("source root\n")
            (source / "home" / "user" / "src" / "project").mkdir(parents=True)
            (
                source
                / "home"
                / "user"
                / "src"
                / "project"
                / "source.txt"
            ).write_text("keep\n")
            node_modules = (
                source
                / "home"
                / "user"
                / "src"
                / "project"
                / "node_modules"
            )
            node_modules.mkdir()
            (node_modules / "dependency").write_text("exclude\n")

            (target / "backup" / "snapshots" / "old").mkdir(parents=True)
            (target / "backup" / "snapshots" / "old" / "payload").write_text(
                "legacy\n"
            )
            (target / "lost+found").mkdir()
            (target / "lost+found" / "inode").write_text("preserve\n")
            (target / "etc").mkdir(exist_ok=True)
            (target / "etc" / "fstab").write_text("usb root\n")
            stale_modules = (
                target
                / "home"
                / "user"
                / "src"
                / "project"
                / "node_modules"
            )
            stale_modules.mkdir(parents=True)
            (stale_modules / "stale").write_text("delete\n")

            subprocess.run(
                backup_drive.rsync_args(
                    source,
                    target,
                    excludes=backup_drive.MIRROR_EXCLUDES,
                ),
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertEqual((target / "etc" / "issue").read_text(), "current\n")
            self.assertEqual((target / "etc" / "fstab").read_text(), "usb root\n")
            self.assertFalse((target / "backup").exists())
            self.assertFalse(stale_modules.exists())
            self.assertTrue((target / "lost+found" / "inode").exists())

    def test_progress_mode_shows_aggregate_progress(self) -> None:
        args = backup_drive.rsync_args(
            Path("/source"),
            Path("/target"),
            verbosity="progress",
        )
        self.assertIn("--info=progress2,stats2", args)
        self.assertNotIn("--itemize-changes", args)

    def test_noisy_mode_lists_changed_paths(self) -> None:
        args = backup_drive.rsync_args(
            Path("/source"),
            Path("/target"),
            verbosity="noisy",
        )
        self.assertIn("--itemize-changes", args)

    def test_boot_args_use_fat_compatible_metadata(self) -> None:
        args = backup_drive.boot_rsync_args(
            Path("/boot/firmware"),
            Path("/target/boot"),
        )
        self.assertIn("-rt", args)
        self.assertNotIn("-aHAX", args)
        self.assertIn("--modify-window=1", args)
        self.assertIn("protect /cmdline.txt", args)
        self.assertIn("/cmdline.txt", args)

    def test_boot_copy_preserves_target_cmdline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            (source / "config.txt").write_text("arm_64bit=1\n")
            (source / "cmdline.txt").write_text("root=SOURCE\n")
            (target / "cmdline.txt").write_text("root=USB\n")

            subprocess.run(
                backup_drive.boot_rsync_args(source, target),
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertEqual((target / "config.txt").read_text(), "arm_64bit=1\n")
            self.assertEqual((target / "cmdline.txt").read_text(), "root=USB\n")

    def test_package_database_lock_rejects_an_active_package_manager(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "dpkg.lock"
            with (
                mock.patch.object(
                    backup_drive.fcntl,
                    "lockf",
                    side_effect=BlockingIOError,
                ),
                self.assertRaisesRegex(RuntimeError, "package manager is active"),
            ):
                with backup_drive.package_database_lock((lock_path,)):
                    self.fail("lock should not have been acquired")

    def test_run_rsync_accepts_only_success_and_vanished_source(self) -> None:
        with mock.patch.object(
            backup_drive,
            "run_command",
            return_value=subprocess.CompletedProcess(["rsync"], 24),
        ):
            warning = backup_drive.run_rsync(["rsync"], context="root")
        self.assertIn("source files vanished", warning)

        with (
            mock.patch.object(
                backup_drive,
                "run_command",
                return_value=subprocess.CompletedProcess(["rsync"], 23),
            ),
            self.assertRaisesRegex(RuntimeError, "rsync status 23"),
        ):
            backup_drive.run_rsync(["rsync"], context="root")

    def test_expected_target_config_uses_live_boot_cmdline(self) -> None:
        devices = backup_drive.Device(
            disk=Path("/dev/sda"),
            boot=Path("/dev/sda1"),
            root=Path("/dev/sda2"),
        )
        with (
            mock.patch.object(
                backup_drive,
                "filesystem_uuid",
                side_effect=["BOOT-UUID", "ROOT-UUID"],
            ),
            mock.patch.object(
                backup_drive.Path,
                "read_text",
                return_value="console=tty1 root=SOURCE quiet\n",
            ),
        ):
            generated = backup_drive.expected_target_config(devices)
        self.assertIn("root=UUID=ROOT-UUID", generated.cmdline)

    def test_atomic_write_flushes_file_and_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            with mock.patch.object(
                backup_drive.os,
                "fsync",
                wraps=os.fsync,
            ) as fsync:
                backup_drive.atomic_write(path, '{"status": "success"}\n')
            self.assertGreaterEqual(fsync.call_count, 2)
            self.assertEqual(json.loads(path.read_text()), {"status": "success"})

    def test_runtime_directories_copy_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            for relative in backup_drive.RUNTIME_DIRECTORIES:
                path = source / relative
                path.mkdir(parents=True)
                path.chmod(0o751)

            backup_drive.ensure_runtime_directories(source, target)

            for relative in backup_drive.RUNTIME_DIRECTORIES:
                self.assertEqual(
                    (target / relative).stat().st_mode & 0o777,
                    0o751,
                )

    def test_verify_mirror_checks_config_and_rejects_legacy_snapshots(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                mount_root=root / "mounts",
            )
            devices = backup_drive.Device(
                disk=Path("/dev/sda"),
                boot=Path("/dev/sda1"),
                root=Path("/dev/sda2"),
            )
            generated = backup_drive.TargetConfig(
                fstab="target fstab\n",
                cmdline="root=UUID=ROOT\n",
            )
            (config.root_mount / "etc").mkdir(parents=True)
            modules = (
                config.root_mount / "lib" / "modules" / os.uname().release
            )
            modules.mkdir(parents=True)
            config.boot_mount.mkdir(parents=True)
            (config.root_mount / "etc" / "fstab").write_text(generated.fstab)
            (config.root_mount / "etc" / "debian_version").write_text("13\n")
            (config.boot_mount / "config.txt").write_text("arm_64bit=1\n")
            (config.boot_mount / "cmdline.txt").write_text(generated.cmdline)

            def mounted_source(target):
                return str(
                    devices.root if target == config.root_mount else devices.boot
                )

            with (
                mock.patch.object(
                    backup_drive,
                    "mounted_source",
                    side_effect=mounted_source,
                ),
                mock.patch.object(
                    backup_drive.shutil,
                    "disk_usage",
                    return_value=mock.Mock(free=20 * 1024**3),
                ),
            ):
                backup_drive.verify_mirror(config, devices, generated)
                (config.root_mount / "backup").mkdir()
                with self.assertRaisesRegex(RuntimeError, "legacy snapshot"):
                    backup_drive.verify_mirror(config, devices, generated)

    def test_capacity_uses_target_total_not_incremental_free_space(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                mount_root=Path(directory),
            )

            def disk_usage(path):
                if Path(path) == Path("/source"):
                    return mock.Mock(used=20 * 1024**3)
                return mock.Mock(total=40 * 1024**3, free=1 * 1024**3)

            with mock.patch.object(
                backup_drive.shutil,
                "disk_usage",
                side_effect=disk_usage,
            ):
                backup_drive.verify_capacity(config, Path("/source"))

            def undersized(path):
                if Path(path) == Path("/source"):
                    return mock.Mock(used=20 * 1024**3)
                return mock.Mock(total=29 * 1024**3)

            with (
                mock.patch.object(
                    backup_drive.shutil,
                    "disk_usage",
                    side_effect=undersized,
                ),
                self.assertRaisesRegex(RuntimeError, "insufficient backup capacity"),
            ):
                backup_drive.verify_capacity(config, Path("/source"))

    def test_success_state_commits_last_run_after_last_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                state_dir=Path(directory),
            )
            now = backup_drive.dt.datetime.now().astimezone()
            with mock.patch.object(backup_drive, "atomic_write") as atomic_write:
                backup_drive.write_state(
                    config,
                    status="success",
                    started=now,
                    finished=now,
                )
        self.assertEqual(
            [call.args[0].name for call in atomic_write.call_args_list],
            ["last-success.json", "last-run.json"],
        )

    def test_failed_run_unmounts_all_owned_mounts_and_records_state(self) -> None:
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
            mounts = [
                config.root_mount,
                config.boot_mount,
                backup_drive.DEFAULT_SOURCE_ROOT,
            ]
            with (
                mock.patch.object(backup_drive, "install_signal_handlers"),
                mock.patch.object(backup_drive, "package_database_lock"),
                mock.patch.object(
                    backup_drive,
                    "resolve_devices",
                    return_value=devices,
                ),
                mock.patch.object(
                    backup_drive,
                    "mount_device",
                    side_effect=mounts[:2],
                ),
                mock.patch.object(
                    backup_drive,
                    "mount_source_view",
                    return_value=mounts[2],
                ),
                mock.patch.object(backup_drive, "write_probe"),
                mock.patch.object(backup_drive, "verify_capacity"),
                mock.patch.object(
                    backup_drive,
                    "nested_mount_excludes",
                    return_value=(),
                ),
                mock.patch.object(
                    backup_drive,
                    "run_rsync",
                    side_effect=RuntimeError("rsync failed"),
                ),
                mock.patch.object(backup_drive, "run_command") as run_command,
                mock.patch.object(backup_drive, "unmount") as unmount,
            ):
                with self.assertRaisesRegex(RuntimeError, "rsync failed"):
                    backup_drive.run_backup(config)

            self.assertEqual(
                unmount.call_args_list,
                [
                    mock.call(backup_drive.DEFAULT_SOURCE_ROOT),
                    mock.call(config.boot_mount),
                    mock.call(config.root_mount),
                ],
            )
            state = json.loads((config.state_dir / "last-run.json").read_text())
            self.assertEqual(state["status"], "failed")
            self.assertEqual(state["phase"], "mirror-root")
            self.assertNotIn(
                mock.call(["sync"], check=False),
                run_command.call_args_list,
            )

    def test_cleanup_attempts_every_mount_after_an_unmount_failure(self) -> None:
        config = backup_drive.Config("TARGET", "BOOT", "ROOT")
        context = backup_drive.RunContext(
            config=config,
            started=backup_drive.dt.datetime.now().astimezone(),
            verbosity="quiet",
            mounts=[Path("/one"), Path("/two")],
        )
        failure = subprocess.CalledProcessError(1, ["umount", "/two"])
        with mock.patch.object(
            backup_drive,
            "unmount",
            side_effect=[failure, None],
        ) as unmount:
            errors = backup_drive.cleanup_mounts(context)

        self.assertEqual(
            unmount.call_args_list,
            [mock.call(Path("/two")), mock.call(Path("/one"))],
        )
        self.assertEqual(len(errors), 1)

    def test_backup_lock_reports_contention(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "backup.lock"
            with (
                mock.patch.object(backup_drive, "LOCK_PATH", lock_path),
                mock.patch.object(
                    backup_drive.fcntl,
                    "flock",
                    side_effect=BlockingIOError,
                ),
                self.assertRaisesRegex(RuntimeError, "already running"),
            ):
                with backup_drive.backup_lock():
                    self.fail("lock should not have been acquired")

    def test_signal_handler_raises_cleanup_aware_interruption(self) -> None:
        old_term = signal.getsignal(signal.SIGTERM)
        old_int = signal.getsignal(signal.SIGINT)
        try:
            backup_drive.install_signal_handlers()
            with self.assertRaisesRegex(backup_drive.BackupInterrupted, "SIGTERM"):
                signal.raise_signal(signal.SIGTERM)
            self.assertEqual(signal.getsignal(signal.SIGTERM), signal.SIG_DFL)
            self.assertEqual(signal.getsignal(signal.SIGINT), signal.SIG_DFL)
        finally:
            signal.signal(signal.SIGTERM, old_term)
            signal.signal(signal.SIGINT, old_int)

    def test_cli_verbosity_options(self) -> None:
        self.assertTrue(backup_drive.parse_args(["--noisy", "run"]).noisy)
        self.assertTrue(backup_drive.parse_args(["run", "--progress"]).progress)

    def test_interactive_wrapper_uses_private_mount_namespace(self) -> None:
        wrapper = Path(__file__).with_name("pi-backup").read_text(encoding="utf-8")
        self.assertIn("unshare --mount --propagation private", wrapper)

    def test_status_fails_for_non_successful_latest_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = backup_drive.Config(
                disk_serial="TARGET",
                boot_label="BOOT",
                root_label="ROOT",
                state_dir=Path(directory),
            )
            (config.state_dir / "last-run.json").write_text(
                json.dumps({"status": "interrupted"}) + "\n"
            )
            with mock.patch("builtins.print"):
                self.assertEqual(backup_drive.status(config), 1)


if __name__ == "__main__":
    unittest.main()
