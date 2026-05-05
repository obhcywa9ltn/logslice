"""Output formatters for log entries."""

import json
from typing import Any, Dict, List, Optional


SUPPORTED_FORMATS = ("json", "pretty", "compact")


def format_entry_json(entry: Dict[str, Any]) -> str:
    """Format a log entry as a JSON string (one entry per line)."""
    return json.dumps(entry, default=str)


def format_entry_pretty(entry: Dict[str, Any], indent: int = 2) -> str:
    """Format a log entry as indented, human-readable JSON."""
    return json.dumps(entry, indent=indent, default=str)


def format_entry_compact(entry: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    """Format a log entry as a compact key=value string.

    Args:
        entry: The log entry dictionary.
        fields: Optional list of field names to include. If None, all fields
                are included.

    Returns:
        A compact string representation of the entry.
    """
    if fields:
        items = {k: entry[k] for k in fields if k in entry}
    else:
        items = entry

    parts = []
    for key, value in items.items():
        if isinstance(value, str) and " " in value:
            parts.append(f'{key}="{value}"')
        else:
            parts.append(f"{key}={value}")
    return " ".join(parts)


def format_entries(
    entries: List[Dict[str, Any]],
    fmt: str = "json",
    fields: Optional[List[str]] = None,
) -> List[str]:
    """Format a list of log entries using the specified format.

    Args:
        entries: List of log entry dictionaries.
        fmt: Output format — one of 'json', 'pretty', or 'compact'.
        fields: Optional list of fields for compact format.

    Returns:
        A list of formatted strings.

    Raises:
        ValueError: If an unsupported format is specified.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    results = []
    for entry in entries:
        if fmt == "json":
            results.append(format_entry_json(entry))
        elif fmt == "pretty":
            results.append(format_entry_pretty(entry))
        elif fmt == "compact":
            results.append(format_entry_compact(entry, fields=fields))
    return results
