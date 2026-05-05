"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime, timezone
from typing import List, Optional

from logslice.filter import filter_entries
from logslice.parser import iter_log_entries


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_datetime(value: str) -> datetime:
    """Parse an ISO-like datetime string and attach UTC timezone."""
    try:
        dt = datetime.strptime(value, DATETIME_FORMAT)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime '{value}'. Expected format: {DATETIME_FORMAT}"
        ) from exc


def parse_pattern(value: str):
    """Parse a field=pattern argument into a (field, pattern) tuple."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"Pattern '{value}' must be in field=regex format."
        )
    field, _, pattern = value.partition("=")
    return (field.strip(), pattern.strip())


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Extract and filter structured JSON logs by time range and field patterns.",
    )
    p.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Log file to read (default: stdin).",
    )
    p.add_argument("--start", type=parse_datetime, metavar="DATETIME", help="Start of time range.")
    p.add_argument("--end", type=parse_datetime, metavar="DATETIME", help="End of time range.")
    p.add_argument(
        "--match",
        dest="patterns",
        type=parse_pattern,
        action="append",
        metavar="FIELD=PATTERN",
        help="Field pattern filter (repeatable).",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.file == "-":
        source = sys.stdin
    else:
        try:
            source = open(args.file, "r", encoding="utf-8")  # noqa: WPS515
        except OSError as exc:
            print(f"logslice: error opening file: {exc}", file=sys.stderr)
            return 1

    try:
        entries = iter_log_entries(source)
        results = filter_entries(
            entries,
            patterns=args.patterns,
            start=args.start,
            end=args.end,
        )
        import json
        for entry in results:
            print(json.dumps(entry, default=str))
    finally:
        if args.file != "-":
            source.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
