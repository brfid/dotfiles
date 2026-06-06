"""Focused tests for destructive backup-drive provisioning guards."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import prepare_backup_drive


class PrepareBackupDriveTests(unittest.TestCase):
    def test_environment_file_supplies_required_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pi-backup.conf"
            path.write_text(
                "\n".join(
                    (
                        "PI_BACKUP_DISK_SERIAL=TARGET",
                        'PI_BACKUP_BOOT_LABEL="BOOT"',
                        "PI_BACKUP_ROOT_LABEL=ROOT",
                        "PI_BACKUP_RETENTION=4",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            config = prepare_backup_drive.load_config(path)

        self.assertEqual(config.disk_serial, "TARGET")
        self.assertEqual(config.boot_label, "BOOT")
        self.assertEqual(config.root_label, "ROOT")

    def test_target_requires_one_unmounted_usb_removable_disk(self) -> None:
        payload = json.dumps(
            {
                "blockdevices": [
                    {
                        "path": "/dev/sda",
                        "type": "disk",
                        "serial": "TARGET",
                        "tran": "usb",
                        "rm": True,
                        "size": 128 * 1024**3,
                        "mountpoints": [None],
                        "children": [
                            {"path": "/dev/sda1", "mountpoints": [None]},
                            {"path": "/dev/sda2", "mountpoints": [None]},
                        ],
                    }
                ]
            }
        )
        with mock.patch.object(
            prepare_backup_drive,
            "command_output",
            return_value=payload,
        ):
            target = prepare_backup_drive.resolve_target("TARGET")
        self.assertEqual(target.path, Path("/dev/sda"))

        mounted = payload.replace(
            '"mountpoints": [null]',
            '"mountpoints": ["/media"]',
            1,
        )
        with (
            mock.patch.object(
                prepare_backup_drive,
                "command_output",
                return_value=mounted,
            ),
            self.assertRaisesRegex(RuntimeError, "mounted target"),
        ):
            prepare_backup_drive.resolve_target("TARGET")

        non_usb = payload.replace('"tran": "usb"', '"tran": "sata"')
        with (
            mock.patch.object(
                prepare_backup_drive,
                "command_output",
                return_value=non_usb,
            ),
            self.assertRaisesRegex(RuntimeError, "non-USB"),
        ):
            prepare_backup_drive.resolve_target("TARGET")

    def test_provision_requires_exact_serial_before_resolution(self) -> None:
        config = prepare_backup_drive.Config(
            disk_serial="TARGET",
            boot_label="BOOT",
            root_label="ROOT",
        )
        with (
            mock.patch.object(prepare_backup_drive, "resolve_target") as resolve,
            self.assertRaisesRegex(RuntimeError, "confirm-erase"),
        ):
            prepare_backup_drive.provision(config, "wrong")
        resolve.assert_not_called()

    def test_main_holds_shared_backup_lock_while_provisioning(self) -> None:
        config = prepare_backup_drive.Config(
            disk_serial="TARGET",
            boot_label="BOOT",
            root_label="ROOT",
        )
        with (
            mock.patch.object(prepare_backup_drive, "require_root"),
            mock.patch.object(prepare_backup_drive, "load_config", return_value=config),
            mock.patch.object(prepare_backup_drive, "backup_lock") as backup_lock,
            mock.patch.object(prepare_backup_drive, "provision") as provision,
        ):
            prepare_backup_drive.main(["--confirm-erase", "TARGET"])

        backup_lock.assert_called_once_with()
        provision.assert_called_once_with(config, "TARGET")

    def test_provisioner_uses_the_backup_run_lock(self) -> None:
        import backup_drive

        self.assertEqual(prepare_backup_drive.LOCK_PATH, backup_drive.LOCK_PATH)


if __name__ == "__main__":
    unittest.main()
