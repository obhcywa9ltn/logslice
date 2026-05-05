"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime
from typing import Optional, Tuple

from logslice.filter import filter_entries
from logslice.formatter import format_entries, SUPPORTED_FORMATS
from logslice.parser import iter_log_entries


def parse_datetime(value: str) -> datetime:
    """Parse a datetime string in ISO 8601 format."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Invalid datetime '{value}'. Expected format: YYYY-MM-DDTHH:MM:SS"
    )


def parse_pattern(value: str) -> Tuple[str, str]:
    """Parse a field=pattern argument into a (field, pattern) tuple."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"Invalid pattern '{value}'. Expected format: field=pattern"
        )
    field, _, pattern = value.partition("=")
    if not field:
        raise argparse.ArgumentTypeError(
            f"Invalid pattern '{value}': field name cannot be empty."
        )
    return field, pattern


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Extract and filter structured JSON logs by time range and field patterns.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to the log file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--start",
        type=parse_datetime,
        metavar="DATETIME",
        help="Include entries at or after this datetime (ISO 8601).",
    )
    parser.add_argument(
        "--end",
        type=parse_datetime,
        metavar="DATETIME",
        help="Include entries at or before this datetime (ISO 8601).",
    )
    parser.add_argument(
        "--match",
        type=parse_pattern,
        action="append",
        metavar="FIELD=PATTERN",
        dest="patterns",
        help="Filter by field value using a regex pattern. Can be repeated.",
    )
    parser.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        default="json",
        dest="fmt",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--fields",
        nargs="+",
        metavar="FIELD",
        help="Fields to include in compact output.",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    """Entry point for the logslice CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        try:
            source = open(args.file, "r", encoding="utf-8")
        except OSError as exc:
            print(f"logslice: error: {exc}", file=sys.stderr)
            return 1
    else:
        source = sys.stdin

    try:
        entries = list(iter_log_entries(source))
        patterns = dict(args.patterns) if args.patterns else None
        filtered = filter_entries(
            entries,
            start=args.start,
            end=args.end,
            field_patterns=patterns,
        )
        for line in format_entries(filtered, fmt=args.fmt, fields=args.fields):
            print(line)
    finally:
        if args.file:
            source.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
