"""Diff two streams of log entries by a key field, reporting added/removed/changed entries."""
from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, NamedTuple, Optional


class DiffResult(NamedTuple):
    status: str          # 'added' | 'removed' | 'changed'
    key: str
    left: Optional[Dict]  # None when status == 'added'
    right: Optional[Dict] # None when status == 'removed'
    changed_fields: List[str]


def _index(entries: Iterable[Dict], key_field: str) -> Dict[str, Dict]:
    """Build a dict keyed by *key_field* value (last entry wins on collision)."""
    return {str(e[key_field]): e for e in entries if key_field in e}


def diff_entries(
    left: Iterable[Dict],
    right: Iterable[Dict],
    key_field: str = "id",
    ignore_fields: Optional[List[str]] = None,
) -> Iterator[DiffResult]:
    """Yield :class:`DiffResult` items describing differences between *left* and *right*.

    Args:
        left: baseline stream of log entry dicts.
        right: new stream of log entry dicts.
        key_field: field used to match entries across streams.
        ignore_fields: fields excluded from change detection (e.g. ``timestamp``).
    """
    ignore = set(ignore_fields or [])
    left_idx = _index(left, key_field)
    right_idx = _index(right, key_field)

    all_keys = set(left_idx) | set(right_idx)

    for key in sorted(all_keys):
        in_left = key in left_idx
        in_right = key in right_idx

        if in_left and not in_right:
            yield DiffResult("removed", key, left_idx[key], None, [])
        elif in_right and not in_left:
            yield DiffResult("added", key, None, right_idx[key], [])
        else:
            le, re = left_idx[key], right_idx[key]
            all_f = (set(le) | set(re)) - ignore - {key_field}
            changed = sorted(f for f in all_f if le.get(f) != re.get(f))
            if changed:
                yield DiffResult("changed", key, le, re, changed)


def format_diff(result: DiffResult) -> str:
    """Return a human-readable single-line summary of a :class:`DiffResult`."""
    if result.status == "added":
        return f"[+] {result.key}"
    if result.status == "removed":
        return f"[-] {result.key}"
    fields = ", ".join(result.changed_fields)
    return f"[~] {result.key}  changed: {fields}"
