"""CLI sub-commands for archiving and retention management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from logslice.archiver import archive_by_size, archive_by_window, read_archive
from logslice.parser import iter_log_entries
from logslice.retention import apply_retention


def _cmd_archive(args: argparse.Namespace) -> int:
    """Read a log file and write compressed archives."""
    source = Path(args.source)
    if not source.exists():
        print(f"error: source file not found: {source}", file=sys.stderr)
        return 1

    with open(source, "r", encoding="utf-8") as fh:
        entries = list(iter_log_entries(fh))

    output_dir = Path(args.output_dir)

    if args.mode == "window":
        counts = archive_by_window(
            entries,
            output_dir,
            window=args.window,
            prefix=args.prefix,
        )
    else:
        counts = archive_by_size(
            entries,
            output_dir,
            max_entries=args.max_entries,
            prefix=args.prefix,
        )

    total = sum(counts.values())
    print(f"Archived {total} entries into {len(counts)} file(s) under {output_dir}")
    for path, count in sorted(counts.items()):
        print(f"  {path}: {count} entries")
    return 0


def _cmd_prune(args: argparse.Namespace) -> int:
    """Apply retention policy to an archive directory."""
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"error: not a directory: {directory}", file=sys.stderr)
        return 1

    removed = apply_retention(
        directory,
        max_age_days=args.max_age_days,
        keep=args.keep,
        dry_run=args.dry_run,
    )

    action = "Would remove" if args.dry_run else "Removed"
    print(f"{action} {len(removed)} archive file(s).")
    for path in removed:
        print(f"  {path}")
    return 0


def _cmd_read(args: argparse.Namespace) -> int:
    """Print entries from a compressed archive."""
    path = Path(args.archive)
    if not path.exists():
        print(f"error: archive not found: {path}", file=sys.stderr)
        return 1
    count = 0
    for entry in read_archive(path):
        print(entry)
        count += 1
    print(f"-- {count} entries --", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice-archive",
        description="Archive and manage compressed log files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # archive sub-command
    arc = sub.add_parser("archive", help="Archive a log file")
    arc.add_argument("source", help="Path to the source .log / .ndjson file")
    arc.add_argument("output_dir", help="Directory to write archives into")
    arc.add_argument("--mode", choices=["window", "size"], default="window")
    arc.add_argument("--window", choices=["hour", "day", "month"], default="day")
    arc.add_argument("--max-entries", type=int, default=10_000, dest="max_entries")
    arc.add_argument("--prefix", default="logslice")

    # prune sub-command
    prune = sub.add_parser("prune", help="Apply retention policy")
    prune.add_argument("directory", help="Archive directory")
    prune.add_argument("--max-age-days", type=float, default=None, dest="max_age_days")
    prune.add_argument("--keep", type=int, default=None)
    prune.add_argument("--dry-run", action="store_true", dest="dry_run")

    # read sub-command
    rd = sub.add_parser("read", help="Print entries from an archive")
    rd.add_argument("archive", help="Path to a .ndjson.gz archive file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {"archive": _cmd_archive, "prune": _cmd_prune, "read": _cmd_read}
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
