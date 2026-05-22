"""Update the daily streak log used by the scheduled GitHub Actions workflow."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_FILE = Path("activity/streak.md")
DEFAULT_TIMEZONE = "Asia/Shanghai"
HEADER = """# GitHub Streak Automation

This file is updated automatically by the scheduled GitHub Actions workflow.

## Daily Log

"""
TRUTHY_VALUES = {"1", "true", "yes", "y", "on"}
AUTOMATED_ENTRY_SUFFIX = " - automated streak update"
TIMEZONE_FALLBACKS: dict[str, tzinfo] = {
    "UTC": timezone.utc,
    "Asia/Shanghai": timezone(timedelta(hours=8), name="Asia/Shanghai"),
}


def is_truthy(value: str | None) -> bool:
    """Return whether an environment-style string represents true."""
    return value is not None and value.strip().lower() in TRUTHY_VALUES


def load_timezone(name: str) -> tzinfo:
    """Load an IANA timezone, with small fallbacks for common CI/local setups."""
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as error:
        fallback = TIMEZONE_FALLBACKS.get(name)
        if fallback is not None:
            return fallback
        message = (
            f"Unknown timezone '{name}'. Use UTC, Asia/Shanghai, "
            "or install the tzdata package."
        )
        raise SystemExit(message) from error


def format_entry(timestamp: datetime) -> str:
    """Format one append-only streak log entry."""
    return f"- {timestamp.strftime('%Y-%m-%d %H:%M:%S %z')}{AUTOMATED_ENTRY_SUFFIX}\n"


def has_automated_entry_for_date(content: str, date_key: str) -> bool:
    """Return whether the log already has an automated entry for a date."""
    entry_prefix = f"- {date_key} "
    return any(
        line.startswith(entry_prefix) and line.endswith(AUTOMATED_ENTRY_SUFFIX)
        for line in content.splitlines()
    )


def normalize_content(content: str) -> str:
    """Return existing file content in a safe appendable shape."""
    if not content.strip():
        return HEADER
    return content if content.endswith("\n") else f"{content}\n"


def update_streak_log(file_path: Path, timestamp: datetime, force: bool = False) -> bool:
    """Append today's log entry and return whether the file changed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    content = file_path.read_text(encoding="utf-8") if file_path.exists() else HEADER
    content = normalize_content(content)
    date_key = f"{timestamp:%Y-%m-%d}"

    if not force and has_automated_entry_for_date(content, date_key):
        print(f"Streak log already contains an entry for {date_key}.")
        return False

    file_path.write_text(f"{content}{format_entry(timestamp)}", encoding="utf-8")
    print(f"Updated {file_path} with an entry for {date_key}.")
    return True


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments and environment defaults."""
    parser = argparse.ArgumentParser(
        description="Append a daily GitHub streak entry to a markdown file."
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(os.environ.get("STREAK_FILE", DEFAULT_FILE)),
        help="Path to the streak log file.",
    )
    parser.add_argument(
        "--timezone",
        default=os.environ.get("STREAK_TIMEZONE", DEFAULT_TIMEZONE),
        help="IANA timezone used to calculate the local day.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=is_truthy(os.environ.get("FORCE_UPDATE")),
        help="Append an entry even if today's date already exists.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the streak log update."""
    args = parse_args()
    now = datetime.now(load_timezone(args.timezone))
    update_streak_log(args.file, now, force=args.force)


if __name__ == "__main__":
    main()
