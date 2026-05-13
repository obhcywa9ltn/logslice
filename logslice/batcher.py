"""Batch log entries into fixed-size or time-windowed groups."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Iterator, List


def batch_by_size(
    entries: Iterable[dict],
    size: int,
) -> Iterator[List[dict]]:
    """Yield lists of *size* entries.  The final batch may be smaller."""
    if size < 1:
        raise ValueError(f"size must be >= 1, got {size!r}")

    batch: List[dict] = []
    for entry in entries:
        batch.append(entry)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def batch_by_time(
    entries: Iterable[dict],
    window_seconds: float,
    timestamp_field: str = "timestamp",
) -> Iterator[List[dict]]:
    """Yield lists of entries that fall within the same time window.

    Entries without a parseable *timestamp_field* are placed in the
    current open window rather than dropped.
    """
    if window_seconds <= 0:
        raise ValueError(f"window_seconds must be > 0, got {window_seconds!r}")

    delta = timedelta(seconds=window_seconds)
    window_start: datetime | None = None
    batch: List[dict] = []

    for entry in entries:
        raw = entry.get(timestamp_field)
        ts: datetime | None = None
        if isinstance(raw, datetime):
            ts = raw
        elif isinstance(raw, str):
            try:
                ts = datetime.fromisoformat(raw)
            except (ValueError, TypeError):
                ts = None

        if window_start is None:
            window_start = ts

        if ts is not None and window_start is not None and ts >= window_start + delta:
            if batch:
                yield batch
            batch = [entry]
            window_start = ts
        else:
            batch.append(entry)

    if batch:
        yield batch


def flatten_batches(batches: Iterable[List[dict]]) -> Iterator[dict]:
    """Inverse of batching — yield individual entries from nested batches."""
    for batch in batches:
        yield from batch
