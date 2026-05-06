"""Field transformation utilities for log entries."""

from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional


TransformMap = Dict[str, Callable[[Any], Any]]


def transform_entry(
    entry: Dict[str, Any],
    transforms: TransformMap,
    skip_missing: bool = True,
) -> Dict[str, Any]:
    """Apply field-level transformations to a single log entry.

    Args:
        entry: The original log entry dict.
        transforms: Mapping of field name to a callable that transforms its value.
        skip_missing: If True, silently skip fields not present in the entry.
                      If False, raise KeyError for missing fields.

    Returns:
        A new dict with transformed fields merged in.
    """
    result = dict(entry)
    for field, fn in transforms.items():
        if field not in result:
            if not skip_missing:
                raise KeyError(f"Field '{field}' not found in log entry")
            continue
        result[field] = fn(result[field])
    return result


def rename_fields(
    entry: Dict[str, Any],
    renames: Dict[str, str],
) -> Dict[str, Any]:
    """Rename fields in a log entry.

    Args:
        entry: The original log entry dict.
        renames: Mapping of old field name to new field name.

    Returns:
        A new dict with renamed fields.
    """
    result = {}
    for key, value in entry.items():
        new_key = renames.get(key, key)
        result[new_key] = value
    return result


def drop_fields(
    entry: Dict[str, Any],
    fields: List[str],
) -> Dict[str, Any]:
    """Return a copy of the entry with specified fields removed."""
    return {k: v for k, v in entry.items() if k not in fields}


def add_fields(
    entry: Dict[str, Any],
    additions: Dict[str, Any],
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Return a copy of the entry with additional fields merged in."""
    result = dict(entry)
    for key, value in additions.items():
        if overwrite or key not in result:
            result[key] = value
    return result


def transform_entries(
    entries: Iterable[Dict[str, Any]],
    transforms: TransformMap,
    skip_missing: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Apply transform_entry to each entry in an iterable."""
    for entry in entries:
        yield transform_entry(entry, transforms, skip_missing=skip_missing)
