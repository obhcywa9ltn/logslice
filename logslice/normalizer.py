"""Field normalisation — coerce, rename, and standardise log entry values."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Iterator, Mapping, Optional

# Built-in coercion helpers
_COERCIONS: Dict[str, Callable[[Any], Any]] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": lambda v: v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes"),
}


def coerce_field(
    entry: Dict[str, Any],
    field: str,
    type_name: str,
    *,
    missing_ok: bool = True,
) -> Dict[str, Any]:
    """Return a copy of *entry* with *field* coerced to *type_name*.

    Supported type names: ``str``, ``int``, ``float``, ``bool``.
    If *field* is absent and *missing_ok* is ``True`` the entry is returned
    unchanged; otherwise ``KeyError`` is raised.
    """
    if field not in entry:
        if missing_ok:
            return dict(entry)
        raise KeyError(field)
    coerce = _COERCIONS.get(type_name)
    if coerce is None:
        raise ValueError(f"Unknown type name {type_name!r}. Choose from: {list(_COERCIONS)}")
    result = dict(entry)
    result[field] = coerce(entry[field])
    return result


def lowercase_field(
    entry: Dict[str, Any],
    field: str,
    *,
    missing_ok: bool = True,
) -> Dict[str, Any]:
    """Return a copy of *entry* with *field* lower-cased (string fields only)."""
    if field not in entry:
        if missing_ok:
            return dict(entry)
        raise KeyError(field)
    result = dict(entry)
    value = entry[field]
    result[field] = value.lower() if isinstance(value, str) else value
    return result


def normalize_entry(
    entry: Dict[str, Any],
    *,
    coercions: Optional[Mapping[str, str]] = None,
    lowercase: Iterable[str] = (),
    strip_nulls: bool = False,
) -> Dict[str, Any]:
    """Apply a set of normalisation rules to a single entry.

    Parameters
    ----------
    coercions:
        Mapping of ``field -> type_name`` pairs passed to :func:`coerce_field`.
    lowercase:
        Iterable of field names whose string values should be lower-cased.
    strip_nulls:
        When ``True``, keys whose value is ``None`` are removed.
    """
    result = dict(entry)
    for field, type_name in (coercions or {}).items():
        result = coerce_field(result, field, type_name)
    for field in lowercase:
        result = lowercase_field(result, field)
    if strip_nulls:
        result = {k: v for k, v in result.items() if v is not None}
    return result


def normalize_entries(
    entries: Iterable[Dict[str, Any]],
    *,
    coercions: Optional[Mapping[str, str]] = None,
    lowercase: Iterable[str] = (),
    strip_nulls: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Yield normalised copies of every entry in *entries*."""
    lc = list(lowercase)
    for entry in entries:
        yield normalize_entry(
            entry,
            coercions=coercions,
            lowercase=lc,
            strip_nulls=strip_nulls,
        )
