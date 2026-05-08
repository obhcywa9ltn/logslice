"""Split a stream of log entries into named buckets based on a field value or predicate."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional


def split_by_field(
    entries: Iterable[dict],
    field: str,
    missing_label: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Partition *entries* into buckets keyed by the value of *field*.

    Entries that do not contain *field* are placed under *missing_label*.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for entry in entries:
        key = str(entry[field]) if field in entry else missing_label
        buckets[key].append(entry)
    return dict(buckets)


def split_by_predicate(
    entries: Iterable[dict],
    predicate: Callable[[dict], bool],
    true_label: str = "match",
    false_label: str = "no_match",
) -> Dict[str, List[dict]]:
    """Split *entries* into two buckets depending on *predicate*."""
    buckets: Dict[str, List[dict]] = {true_label: [], false_label: []}
    for entry in entries:
        label = true_label if predicate(entry) else false_label
        buckets[label].append(entry)
    return buckets


def split_by_rules(
    entries: Iterable[dict],
    rules: List[tuple[str, Callable[[dict], bool]]],
    default_label: Optional[str] = "__default__",
) -> Dict[str, List[dict]]:
    """Route each entry to the first rule whose predicate matches.

    *rules* is a list of ``(label, predicate)`` pairs evaluated in order.
    Unmatched entries go to *default_label*; if *default_label* is ``None``
    those entries are silently dropped.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for entry in entries:
        matched = False
        for label, predicate in rules:
            if predicate(entry):
                buckets[label].append(entry)
                matched = True
                break
        if not matched and default_label is not None:
            buckets[default_label].append(entry)
    return dict(buckets)
