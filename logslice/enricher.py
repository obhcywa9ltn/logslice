"""Entry enrichment: add or derive fields from existing log entry data."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, Iterable, Iterator, Optional


_ENRICHERS: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def _level_severity(entry: Dict[str, Any]) -> Optional[int]:
    """Map a 'level' string to a numeric severity (syslog-style)."""
    mapping = {
        "debug": 7,
        "info": 6,
        "notice": 5,
        "warning": 4,
        "warn": 4,
        "error": 3,
        "critical": 2,
        "alert": 1,
        "emergency": 0,
    }
    level = str(entry.get("level", "")).lower()
    return mapping.get(level)


def enrich_entry(
    entry: Dict[str, Any],
    *,
    add_severity: bool = False,
    extract_fields: Optional[Dict[str, str]] = None,
    static_fields: Optional[Dict[str, Any]] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Return a new entry dict enriched according to the requested options.

    Args:
        entry: The original log entry.
        add_severity: If True, add a ``severity`` integer derived from ``level``.
        extract_fields: Mapping of {new_field: regex} applied to ``message``.
            The first capture group is used as the value.
        static_fields: Key/value pairs unconditionally added to every entry.
        overwrite: When False (default) existing keys are not overwritten.

    Returns:
        A shallow copy of *entry* with enrichments applied.
    """
    result = dict(entry)

    if static_fields:
        for key, value in static_fields.items():
            if overwrite or key not in result:
                result[key] = value

    if add_severity:
        if overwrite or "severity" not in result:
            sev = _level_severity(entry)
            if sev is not None:
                result["severity"] = sev

    if extract_fields:
        message = str(entry.get("message", ""))
        for field, pattern in extract_fields.items():
            if not overwrite and field in result:
                continue
            match = re.search(pattern, message)
            if match and match.lastindex and match.lastindex >= 1:
                result[field] = match.group(1)

    return result


def enrich_entries(
    entries: Iterable[Dict[str, Any]],
    **kwargs: Any,
) -> Iterator[Dict[str, Any]]:
    """Apply :func:`enrich_entry` to every entry in *entries*."""
    for entry in entries:
        yield enrich_entry(entry, **kwargs)
