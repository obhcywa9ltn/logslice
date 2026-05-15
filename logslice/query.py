"""Simple field-equality query engine built on top of logslice.indexer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.indexer import build_index, lookup

Entry = Dict[str, Any]


@dataclass
class Query:
    """Declarative query over a collection of log entries.

    Attributes:
        filters:  Exact-match constraints ``{field: value}``.
        excludes: Exact-match exclusions ``{field: value}``.
        limit:    Maximum number of results (``None`` means unlimited).
    """

    filters: Dict[str, Any] = field(default_factory=dict)
    excludes: Dict[str, Any] = field(default_factory=dict)
    limit: Optional[int] = None

    def __post_init__(self) -> None:
        if self.limit is not None and self.limit < 0:
            raise ValueError(f"limit must be a non-negative integer, got {self.limit}")


def _matches(entry: Entry, query: Query) -> bool:
    """Return True when *entry* satisfies all filter and exclude clauses."""
    for key, value in query.filters.items():
        if str(entry.get(key, "")) != str(value):
            return False
    for key, value in query.excludes.items():
        if str(entry.get(key, "")) == str(value):
            return False
    return True


def run_query(entries: Iterable[Entry], query: Query) -> Iterator[Entry]:
    """Yield entries that satisfy *query*, respecting any ``limit``."""
    count = 0
    for entry in entries:
        if query.limit is not None and count >= query.limit:
            return
        if _matches(entry, query):
            yield entry
            count += 1


def run_indexed_query(
    entries: Iterable[Entry],
    query: Query,
    index_field: str,
) -> Iterator[Entry]:
    """Run *query* using a single-field index for the first filter clause.

    If *index_field* is not present in ``query.filters`` the function falls
    back to a full linear scan via :func:`run_query`.
    """
    if index_field not in query.filters:
        yield from run_query(entries, query)
        return

    all_entries: List[Entry] = list(entries)
    idx = build_index(all_entries, index_field)
    candidates = lookup(idx, query.filters[index_field])
    yield from run_query(candidates, query)
