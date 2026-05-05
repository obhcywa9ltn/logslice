"""Core JSON log parser for logslice."""

import json
from datetime import datetime
from typing import Iterator, Optional


DEFAULT_TIMESTAMP_FIELD = "timestamp"
DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_timestamp(value: str, fmt: str = DEFAULT_TIMESTAMP_FORMAT) -> Optional[datetime]:
    """Parse a timestamp string into a datetime object."""
    for format_str in (fmt, "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, format_str)
        except (ValueError, TypeError):
            continue
    return None


def parse_log_line(line: str) -> Optional[dict]:
    """Parse a single log line as JSON. Returns None if parsing fails."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def iter_log_entries(
    lines: Iterator[str],
    timestamp_field: str = DEFAULT_TIMESTAMP_FIELD,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Iterator[dict]:
    """
    Iterate over log lines, yielding parsed JSON entries filtered by time range.

    Args:
        lines: Iterable of raw log line strings.
        timestamp_field: The JSON key used for the timestamp.
        start: Inclusive start datetime filter.
        end: Inclusive end datetime filter.

    Yields:
        Parsed log entry dicts within the specified time range.
    """
    for line in lines:
        entry = parse_log_line(line)
        if entry is None:
            continue

        if start is None and end is None:
            yield entry
            continue

        raw_ts = entry.get(timestamp_field)
        if raw_ts is None:
            continue

        ts = parse_timestamp(str(raw_ts))
        if ts is None:
            continue

        if start and ts < start:
            continue
        if end and ts > end:
            continue

        yield entry
