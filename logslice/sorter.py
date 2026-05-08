"""logslice.sorter — Sort log entries by a field or timestamp."""

from __future__ import annotations

from typing import Iterable, Iterator, Optional


def _get_sort_key(entry: dict, field: str, default):
    """Return the value of *field* from *entry*, falling back to *default*."""
    return entry.get(field, default)


def sort_entries(
    entries: Iterable[dict],
    field: str = "timestamp",
    reverse: bool = False,
    missing_last: bool = True,
) -> Iterator[dict]:
    """Sort *entries* by *field*.

    Parameters
    ----------
    entries:
        An iterable of parsed log-entry dicts.
    field:
        The dict key to sort by.  Defaults to ``"timestamp"``.
    reverse:
        When ``True`` sort in descending order.
    missing_last:
        When ``True`` entries that lack *field* are placed at the end
        (or beginning when *reverse* is ``True``).
    """
    # Materialise so we can sort in-memory.
    items = list(entries)

    # Build a sentinel that sorts after (or before) every real value.
    # For strings the sentinel is either "\xff" * 40 or "" depending on direction.
    # We use a two-tuple key: (has_field, value) so missing entries always land
    # at the desired end regardless of the field type.
    def key(entry: dict):
        value = entry.get(field)
        has_field = value is not None
        if missing_last:
            # (False, ...) < (True, ...) so missing entries sort first when
            # ascending; we flip the boolean to push them last.
            return (has_field, value if has_field else "")
        else:
            return (not has_field, value if has_field else "")

    items.sort(key=key, reverse=reverse)
    return iter(items)


def sort_by_timestamp(
    entries: Iterable[dict],
    reverse: bool = False,
) -> Iterator[dict]:
    """Convenience wrapper — sort entries by the ``timestamp`` field."""
    return sort_entries(entries, field="timestamp", reverse=reverse)
