"""Build and query an in-memory index over log entries by field value."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, Iterator, List


# Type alias for a single log entry
Entry = Dict[str, Any]


def build_index(entries: Iterable[Entry], field: str) -> Dict[str, List[Entry]]:
    """Return a mapping of field value -> list of entries that carry that value.

    Entries that lack *field* are stored under the empty-string key ``""``.
    """
    index: Dict[str, List[Entry]] = defaultdict(list)
    for entry in entries:
        key = str(entry.get(field, ""))
        index[key].append(entry)
    return dict(index)


def lookup(index: Dict[str, List[Entry]], value: Any) -> List[Entry]:
    """Return all entries whose indexed field equals *value*.

    Returns an empty list when *value* is not present in the index.
    """
    return index.get(str(value), [])


def lookup_many(index: Dict[str, List[Entry]], values: Iterable[Any]) -> Iterator[Entry]:
    """Yield entries matching any of *values*, preserving per-value order.

    Duplicates are not suppressed — an entry that appears under multiple values
    will be yielded once per matching value.
    """
    for value in values:
        yield from lookup(index, value)


def index_keys(index: Dict[str, List[Entry]]) -> List[str]:
    """Return the sorted list of distinct keys present in *index*."""
    return sorted(index.keys())


def reindex(index: Dict[str, List[Entry]], field: str) -> Dict[str, List[Entry]]:
    """Flatten *index* back to a stream and re-index by a different *field*."""
    all_entries: List[Entry] = []
    for entries in index.values():
        all_entries.extend(entries)
    return build_index(all_entries, field)
