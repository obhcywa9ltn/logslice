"""annotator.py – attach computed annotations to log entries.

Annotations are derived key/value pairs added under a configurable
namespace key (default ``"_annotations"``) so they never collide with
the original fields.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple

Annotation = Tuple[str, Callable[[Dict[str, Any]], Any]]


def annotate_entry(
    entry: Dict[str, Any],
    annotations: List[Annotation],
    *,
    namespace: str = "_annotations",
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Return a shallow copy of *entry* with computed annotations attached.

    Each element of *annotations* is a ``(name, callable)`` pair.  The
    callable receives the entry dict and must return a JSON-serialisable
    value (or ``None`` to skip that annotation).

    Parameters
    ----------
    entry:       Source log entry dict.
    annotations: Ordered list of ``(label, fn)`` pairs.
    namespace:   Top-level key under which annotations are stored.
    overwrite:   When *True*, replace an existing annotation with the
                 same label; otherwise leave the existing value intact.
    """
    result = dict(entry)
    bucket: Dict[str, Any] = dict(result.get(namespace) or {})

    for label, fn in annotations:
        if not overwrite and label in bucket:
            continue
        try:
            value = fn(entry)
        except Exception:  # noqa: BLE001
            value = None
        if value is not None:
            bucket[label] = value

    if bucket:
        result[namespace] = bucket
    return result


def annotate_entries(
    entries: Iterable[Dict[str, Any]],
    annotations: List[Annotation],
    *,
    namespace: str = "_annotations",
    overwrite: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Yield annotated copies of every entry in *entries*."""
    for entry in entries:
        yield annotate_entry(
            entry,
            annotations,
            namespace=namespace,
            overwrite=overwrite,
        )


# ---------------------------------------------------------------------------
# Built-in annotation helpers
# ---------------------------------------------------------------------------

def has_field(field: str) -> Callable[[Dict[str, Any]], Optional[bool]]:
    """Return an annotation fn that records whether *field* is present."""
    def _fn(entry: Dict[str, Any]) -> Optional[bool]:
        return field in entry or None  # None skips when False would be noisy
    return _fn


def field_length(field: str) -> Callable[[Dict[str, Any]], Optional[int]]:
    """Return an annotation fn that records the string length of *field*."""
    def _fn(entry: Dict[str, Any]) -> Optional[int]:
        value = entry.get(field)
        return len(str(value)) if value is not None else None
    return _fn
