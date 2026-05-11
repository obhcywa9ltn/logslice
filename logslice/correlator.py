"""Correlate log entries by a shared field value (e.g. request_id, trace_id)."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional


def group_by_correlation_id(
    entries: Iterable[dict],
    field: str = "request_id",
    missing_label: str = "__no_id__",
) -> Dict[str, List[dict]]:
    """Group entries into buckets keyed by *field* value.

    Entries that lack the field are grouped under *missing_label*.
    """
    groups: Dict[str, List[dict]] = defaultdict(list)
    for entry in entries:
        key = str(entry.get(field, missing_label))
        groups[key].append(entry)
    return dict(groups)


def iter_correlated(
    entries: Iterable[dict],
    field: str = "request_id",
    min_entries: int = 1,
    missing_label: str = "__no_id__",
) -> Iterator[List[dict]]:
    """Yield lists of entries that share the same *field* value.

    Only groups with at least *min_entries* entries are yielded.
    """
    if min_entries < 1:
        raise ValueError("min_entries must be >= 1")
    groups = group_by_correlation_id(entries, field=field, missing_label=missing_label)
    for group in groups.values():
        if len(group) >= min_entries:
            yield group


def find_by_correlation_id(
    entries: Iterable[dict],
    correlation_id: str,
    field: str = "request_id",
) -> List[dict]:
    """Return all entries whose *field* matches *correlation_id* exactly."""
    return [
        entry for entry in entries if str(entry.get(field, "")) == correlation_id
    ]


def correlation_summary(
    groups: Dict[str, List[dict]],
    label_field: Optional[str] = None,
) -> List[dict]:
    """Return a summary list with id, count, and optional label sample per group."""
    summary = []
    for correlation_id, group_entries in groups.items():
        record: dict = {"correlation_id": correlation_id, "count": len(group_entries)}
        if label_field:
            sample = next(
                (e[label_field] for e in group_entries if label_field in e), None
            )
            record["label_sample"] = sample
        summary.append(record)
    return summary
