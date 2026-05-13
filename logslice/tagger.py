"""Tag log entries with user-defined labels based on field predicates."""

from __future__ import annotations

from typing import Any, Callable, Dict, Generator, Iterable, List, Tuple

# A rule is a (tag, predicate) pair where predicate receives the entry dict
TagRule = Tuple[str, Callable[[Dict[str, Any]], bool]]


def tag_entry(
    entry: Dict[str, Any],
    rules: List[TagRule],
    tag_field: str = "tags",
    multi: bool = True,
) -> Dict[str, Any]:
    """Return a copy of *entry* with a *tag_field* list populated.

    Args:
        entry:     The log entry dict.
        rules:     Ordered list of (tag, predicate) pairs.
        tag_field: Key under which tags are stored (default ``"tags"``).
        multi:     When *False* only the first matching tag is applied.

    Returns:
        A new dict; the original is never mutated.
    """
    result = dict(entry)
    existing: List[str] = list(result.get(tag_field) or [])
    for tag, predicate in rules:
        try:
            matched = predicate(entry)
        except Exception:
            matched = False
        if matched:
            if tag not in existing:
                existing.append(tag)
            if not multi:
                break
    result[tag_field] = existing
    return result


def tag_entries(
    entries: Iterable[Dict[str, Any]],
    rules: List[TagRule],
    tag_field: str = "tags",
    multi: bool = True,
) -> Generator[Dict[str, Any], None, None]:
    """Apply :func:`tag_entry` to each entry in *entries*."""
    for entry in entries:
        yield tag_entry(entry, rules, tag_field=tag_field, multi=multi)


def build_rule(tag: str, field: str, value: Any) -> TagRule:
    """Convenience factory: tag when ``entry[field] == value``."""
    return (tag, lambda e, f=field, v=value: e.get(f) == v)


def filter_by_tag(
    entries: Iterable[Dict[str, Any]],
    tag: str,
    tag_field: str = "tags",
) -> Generator[Dict[str, Any], None, None]:
    """Yield only entries whose *tag_field* list contains *tag*."""
    for entry in entries:
        tags = entry.get(tag_field) or []
        if tag in tags:
            yield entry
