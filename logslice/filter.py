"""Field pattern filtering for structured JSON log entries."""

import re
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple


LogEntry = Dict[str, Any]
FieldPattern = Tuple[str, str]  # (field_name, regex_pattern)


def match_field_patterns(entry: LogEntry, patterns: List[FieldPattern]) -> bool:
    """Return True if all field patterns match the given log entry.

    Each pattern is a (field, regex) tuple. A missing field is treated
    as a non-match.
    """
    for field, pattern in patterns:
        value = entry.get(field)
        if value is None:
            return False
        if not re.search(pattern, str(value)):
            return False
    return True


def filter_by_time_range(
    entries: Iterator[LogEntry],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    timestamp_field: str = "timestamp",
) -> Iterator[LogEntry]:
    """Yield entries whose timestamp falls within [start, end].

    Either bound may be None (open-ended). Entries missing the
    timestamp field are skipped.
    """
    for entry in entries:
        ts = entry.get(timestamp_field)
        if ts is None:
            continue
        if not isinstance(ts, datetime):
            continue
        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue
        yield entry


def filter_entries(
    entries: Iterator[LogEntry],
    patterns: Optional[List[FieldPattern]] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    timestamp_field: str = "timestamp",
) -> Iterator[LogEntry]:
    """Combine time-range and field-pattern filtering in a single pass."""
    effective_patterns: List[FieldPattern] = patterns or []

    for entry in entries:
        # Time range check
        ts = entry.get(timestamp_field)
        if start is not None or end is not None:
            if not isinstance(ts, datetime):
                continue
            if start is not None and ts < start:
                continue
            if end is not None and ts > end:
                continue

        # Field pattern check
        if effective_patterns and not match_field_patterns(entry, effective_patterns):
            continue

        yield entry
