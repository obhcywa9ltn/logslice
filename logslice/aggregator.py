"""Aggregator module for grouping and counting log entries by field values."""

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple


def group_by_field(
    entries: Iterable[dict],
    field: str,
    missing_label: str = "<missing>",
) -> Dict[str, List[dict]]:
    """Group log entries by the value of a given field.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field name to group by.
        missing_label: Label used when the field is absent in an entry.

    Returns:
        A dict mapping field values to lists of matching entries.
    """
    groups: Dict[str, List[dict]] = defaultdict(list)
    for entry in entries:
        key = str(entry.get(field, missing_label))
        groups[key].append(entry)
    return dict(groups)


def count_by_field(
    entries: Iterable[dict],
    field: str,
    missing_label: str = "<missing>",
) -> Dict[str, int]:
    """Count log entries grouped by the value of a given field.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field name to count by.
        missing_label: Label used when the field is absent in an entry.

    Returns:
        A dict mapping field values to occurrence counts.
    """
    counts: Dict[str, int] = defaultdict(int)
    for entry in entries:
        key = str(entry.get(field, missing_label))
        counts[key] += 1
    return dict(counts)


def top_values(
    counts: Dict[str, int],
    n: int = 10,
) -> List[Tuple[str, int]]:
    """Return the top-n field values by count, sorted descending.

    Args:
        counts: A dict of field values to counts (as returned by count_by_field).
        n: Maximum number of results to return.

    Returns:
        A list of (value, count) tuples sorted by count descending.
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]


def format_aggregation(
    counts: Dict[str, int],
    field: str,
    top: Optional[int] = None,
) -> str:
    """Format aggregation counts as a human-readable string.

    Args:
        counts: A dict of field values to counts.
        field: The field name (used in the header).
        top: If provided, only show the top-n values.

    Returns:
        A formatted multi-line string.
    """
    items = top_values(counts, n=top) if top else sorted(
        counts.items(), key=lambda x: x[1], reverse=True
    )
    lines = [f"Aggregation by '{field}':"]
    for value, count in items:
        lines.append(f"  {value}: {count}")
    return "\n".join(lines)
