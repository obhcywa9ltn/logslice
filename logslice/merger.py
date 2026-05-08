"""Merge multiple sorted log entry streams into a single ordered stream."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator

from logslice.parser import parse_timestamp


def _entry_sort_key(entry: dict) -> tuple:
    """Return a sort key for a log entry based on its timestamp."""
    raw = entry.get("timestamp") or entry.get("ts") or entry.get("time") or ""
    ts = parse_timestamp(raw)
    # Entries without a parseable timestamp sort to the end.
    if ts is None:
        return (1, 0)
    return (0, ts.timestamp())


def merge_entries(
    *streams: Iterable[dict],
    key: str | None = None,
) -> Iterator[dict]:
    """Merge multiple log-entry iterables into one time-ordered stream.

    Uses a heap-based k-way merge so the individual streams are each assumed
    to be already sorted (e.g. produced by ``sort_by_timestamp``).

    Args:
        *streams: Any number of iterables that yield log-entry dicts.
        key: Optional field name to sort by.  Defaults to the standard
             timestamp fields (``timestamp``, ``ts``, ``time``).

    Yields:
        Log-entry dicts in ascending order of the chosen key.
    """
    if key is not None:
        def sort_key(entry: dict) -> tuple:
            val = entry.get(key, "")
            return (0, str(val)) if val != "" else (1, "")
    else:
        sort_key = _entry_sort_key  # type: ignore[assignment]

    # heap items: (sort_key, stream_index, entry)
    # stream_index breaks ties deterministically so dicts are never compared.
    heap: list[tuple] = []
    iters = [iter(s) for s in streams]

    for idx, it in enumerate(iters):
        entry = next(it, None)
        if entry is not None:
            heapq.heappush(heap, (sort_key(entry), idx, entry))

    while heap:
        sk, idx, entry = heapq.heappop(heap)
        yield entry
        nxt = next(iters[idx], None)
        if nxt is not None:
            heapq.heappush(heap, (sort_key(nxt), idx, nxt))


def merge_all(streams: Iterable[Iterable[dict]], key: str | None = None) -> Iterator[dict]:
    """Convenience wrapper that accepts an iterable of streams."""
    return merge_entries(*streams, key=key)
