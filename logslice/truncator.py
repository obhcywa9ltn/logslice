"""truncator.py — Truncate long field values in log entries."""

from __future__ import annotations

from typing import Any, Dict, Generator, Iterable, Optional

_DEFAULT_MAX_LENGTH = 256
_DEFAULT_PLACEHOLDER = "..."


def truncate_value(value: Any, max_length: int, placeholder: str) -> Any:
    """Truncate a string value to *max_length* characters.

    Non-string values are returned unchanged.  If the value is already within
    the limit it is returned as-is.
    """
    if not isinstance(value, str):
        return value
    if len(value) <= max_length:
        return value
    cut = max(0, max_length - len(placeholder))
    return value[:cut] + placeholder


def truncate_entry(
    entry: Dict[str, Any],
    fields: Optional[Iterable[str]] = None,
    max_length: int = _DEFAULT_MAX_LENGTH,
    placeholder: str = _DEFAULT_PLACEHOLDER,
) -> Dict[str, Any]:
    """Return a copy of *entry* with long field values truncated.

    Parameters
    ----------
    entry:
        The log entry dict to process.
    fields:
        An optional iterable of field names to consider.  When *None* every
        string field in the entry is a candidate.
    max_length:
        Maximum allowed length for a string value (default 256).
    placeholder:
        Suffix appended to truncated values (default ``"..."``).
    """
    if max_length < 0:
        raise ValueError("max_length must be >= 0")

    target_fields = set(fields) if fields is not None else None
    result: Dict[str, Any] = {}
    for key, value in entry.items():
        if target_fields is None or key in target_fields:
            result[key] = truncate_value(value, max_length, placeholder)
        else:
            result[key] = value
    return result


def truncate_entries(
    entries: Iterable[Dict[str, Any]],
    fields: Optional[Iterable[str]] = None,
    max_length: int = _DEFAULT_MAX_LENGTH,
    placeholder: str = _DEFAULT_PLACEHOLDER,
) -> Generator[Dict[str, Any], None, None]:
    """Yield truncated copies of each entry in *entries*."""
    fields_frozen = list(fields) if fields is not None else None
    for entry in entries:
        yield truncate_entry(entry, fields_frozen, max_length, placeholder)
