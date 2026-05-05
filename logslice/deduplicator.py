"""Deduplication utilities for log entries."""

import hashlib
import json
from typing import Iterator, Iterable, Optional, List


def _entry_fingerprint(entry: dict, fields: Optional[List[str]] = None) -> str:
    """Compute a stable hash fingerprint for a log entry.

    If *fields* is given, only those keys are included in the hash.
    Otherwise the full entry (excluding the timestamp key) is used.
    """
    if fields:
        subset = {k: entry[k] for k in fields if k in entry}
    else:
        subset = {k: v for k, v in entry.items() if k != "timestamp"}

    serialized = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def deduplicate_entries(
    entries: Iterable[dict],
    fields: Optional[List[str]] = None,
    keep_first: bool = True,
) -> Iterator[dict]:
    """Yield log entries with duplicates removed.

    Args:
        entries: Iterable of parsed log entry dicts.
        fields: Optional list of field names to use for comparison.
                If None, all fields except ``timestamp`` are compared.
        keep_first: When True (default) the first occurrence is kept;
                    when False the last occurrence is kept.

    Yields:
        Unique log entry dicts.
    """
    if keep_first:
        seen: set = set()
        for entry in entries:
            fp = _entry_fingerprint(entry, fields)
            if fp not in seen:
                seen.add(fp)
                yield entry
    else:
        # Collect all entries, then yield last occurrence in original order.
        ordered: list = []
        last_index: dict = {}
        for idx, entry in enumerate(entries):
            fp = _entry_fingerprint(entry, fields)
            last_index[fp] = idx
            ordered.append((fp, entry))
        seen_last: set = set()
        for fp, entry in ordered:
            if last_index[fp] not in seen_last:
                if last_index[fp] == ordered.index((fp, entry)):
                    seen_last.add(last_index[fp])
                    yield entry


def count_duplicates(
    entries: Iterable[dict],
    fields: Optional[List[str]] = None,
) -> int:
    """Return the number of duplicate entries (total minus unique count)."""
    seen: set = set()
    total = 0
    for entry in entries:
        fp = _entry_fingerprint(entry, fields)
        seen.add(fp)
        total += 1
    return total - len(seen)
