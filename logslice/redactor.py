"""Field redaction for sensitive log data."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional

# Default field names considered sensitive
DEFAULT_SENSITIVE_FIELDS = {
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "credit_card",
}

REDACT_PLACEHOLDER = "***REDACTED***"


def redact_entry(
    entry: Dict[str, Any],
    fields: Optional[Iterable[str]] = None,
    patterns: Optional[Iterable[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> Dict[str, Any]:
    """Return a copy of *entry* with sensitive fields replaced by *placeholder*.

    Args:
        entry: A parsed log entry dict.
        fields: Explicit field names to redact (case-insensitive).
        patterns: Regex patterns; any key matching a pattern is redacted.
        placeholder: Replacement value for redacted fields.

    Returns:
        A new dict with sensitive values replaced.
    """
    sensitive: set[str] = set(DEFAULT_SENSITIVE_FIELDS)
    if fields:
        sensitive.update(f.lower() for f in fields)

    compiled_patterns: List[re.Pattern[str]] = []
    if patterns:
        for pat in patterns:
            compiled_patterns.append(re.compile(pat, re.IGNORECASE))

    result: Dict[str, Any] = {}
    for key, value in entry.items():
        key_lower = key.lower()
        should_redact = key_lower in sensitive or any(
            p.search(key) for p in compiled_patterns
        )
        result[key] = placeholder if should_redact else value
    return result


def redact_entries(
    entries: Iterable[Dict[str, Any]],
    fields: Optional[Iterable[str]] = None,
    patterns: Optional[Iterable[str]] = None,
    placeholder: str = REDACT_PLACEHOLDER,
) -> Iterator[Dict[str, Any]]:
    """Yield redacted copies of each entry in *entries*."""
    field_list = list(fields) if fields else None
    pattern_list = list(patterns) if patterns else None
    for entry in entries:
        yield redact_entry(entry, fields=field_list, patterns=pattern_list, placeholder=placeholder)
