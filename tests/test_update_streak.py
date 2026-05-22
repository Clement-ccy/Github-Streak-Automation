"""Tests for the streak log updater."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.update_streak import HEADER, is_truthy, load_timezone, update_streak_log


class UpdateStreakLogTest(unittest.TestCase):
    def test_creates_log_with_entry(self) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "activity" / "streak.md"
            timestamp = datetime(
                2026,
                5,
                22,
                8,
                10,
                tzinfo=timezone(timedelta(hours=8)),
            )

            changed = update_streak_log(file_path, timestamp)

            self.assertTrue(changed)
            content = file_path.read_text(encoding="utf-8")
            self.assertIn("# GitHub Streak Automation", content)
            self.assertIn("- 2026-05-22 08:10:00 +0800", content)

    def test_skips_duplicate_date_by_default(self) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "activity" / "streak.md"
            timestamp = datetime(2026, 5, 22, 8, 10, tzinfo=timezone.utc)

            first_changed = update_streak_log(file_path, timestamp)
            original_content = file_path.read_text(encoding="utf-8")
            second_changed = update_streak_log(file_path, timestamp)

            self.assertTrue(first_changed)
            self.assertFalse(second_changed)
            self.assertEqual(original_content, file_path.read_text(encoding="utf-8"))

    def test_force_allows_duplicate_date(self) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "activity" / "streak.md"
            timestamp = datetime(2026, 5, 22, 8, 10, tzinfo=timezone.utc)

            update_streak_log(file_path, timestamp)
            changed = update_streak_log(file_path, timestamp, force=True)
            content = file_path.read_text(encoding="utf-8")

            self.assertTrue(changed)
            self.assertEqual(content.count("- 2026-05-22"), 2)

    def test_unrelated_date_text_does_not_skip_update(self) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "activity" / "streak.md"
            file_path.parent.mkdir(parents=True)
            file_path.write_text(
                f"{HEADER}- 2026-05-22 project planning note\n",
                encoding="utf-8",
            )
            timestamp = datetime(2026, 5, 22, 8, 10, tzinfo=timezone.utc)

            changed = update_streak_log(file_path, timestamp)
            content = file_path.read_text(encoding="utf-8")

            self.assertTrue(changed)
            self.assertIn("- 2026-05-22 project planning note", content)
            self.assertIn("- 2026-05-22 08:10:00 +0000", content)

    def test_truthy_values(self) -> None:
        self.assertTrue(is_truthy("true"))
        self.assertTrue(is_truthy("YES"))
        self.assertTrue(is_truthy("1"))
        self.assertFalse(is_truthy("false"))
        self.assertFalse(is_truthy(None))

    def test_load_timezone_has_common_fallbacks(self) -> None:
        utc_datetime = datetime(2026, 5, 22, tzinfo=load_timezone("UTC"))
        shanghai_datetime = datetime(
            2026,
            5,
            22,
            tzinfo=load_timezone("Asia/Shanghai"),
        )

        self.assertEqual(utc_datetime.utcoffset(), timedelta(0))
        self.assertEqual(
            shanghai_datetime.utcoffset(),
            timedelta(hours=8),
        )


if __name__ == "__main__":
    unittest.main()
