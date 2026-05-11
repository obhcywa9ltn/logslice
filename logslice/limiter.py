"""Field-value based entry limiter: stop yielding after N entries per key."""

from __future__ import annotations

from collections import defaultdict
from typing import Generator, Iterable, Optional


def limit_by_field(
    entries: Iterable[dict],
    field: str,
    max_per_value: int,
    missing_label: str = "__missing__",
) -> Generator[dict, None, None]:
    """Yield at most *max_per_value* entries for each distinct value of *field*.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field whose value is used as the grouping key.
        max_per_value: Maximum number of entries to yield per distinct value.
        missing_label: Label used when *field* is absent from an entry.

    Yields:
        Entries that have not yet exceeded the per-value cap.

    Raises:
        ValueError: If *max_per_value* is less than 1.
    """
    if max_per_value < 1:
        raise ValueError(f"max_per_value must be >= 1, got {max_per_value}")

    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        key = str(entry.get(field, missing_label))
        if counts[key] < max_per_value:
            counts[key] += 1
            yield entry


def limit_total(
    entries: Iterable[dict],
    max_entries: int,
) -> Generator[dict, None, None]:
    """Yield at most *max_entries* entries in total.

    Args:
        entries: Iterable of parsed log entry dicts.
        max_entries: Hard cap on the total number of entries yielded.

    Yields:
        Up to *max_entries* entries.

    Raises:
        ValueError: If *max_entries* is less than 0.
    """
    if max_entries < 0:
        raise ValueError(f"max_entries must be >= 0, got {max_entries}")

    emitted = 0
    for entry in entries:
        if emitted >= max_entries:
            break
        yield entry
        emitted += 1


def counts_by_field(
    entries: Iterable[dict],
    field: str,
    missing_label: str = "__missing__",
) -> dict[str, int]:
    """Return a mapping of field-value -> count without filtering.

    Useful for inspecting distribution before choosing a cap.
    """
    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        key = str(entry.get(field, missing_label))
        counts[key] += 1
    return dict(counts)
