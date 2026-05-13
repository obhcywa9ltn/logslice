"""Field value masking — partially obscure sensitive values while preserving structure."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, Optional

_DEFAULT_MASK_CHAR = "*"
_DEFAULT_VISIBLE_CHARS = 4


def _mask_string(
    value: str,
    visible: int = _DEFAULT_VISIBLE_CHARS,
    mask_char: str = _DEFAULT_MASK_CHAR,
    show_end: bool = False,
) -> str:
    """Return *value* with all but *visible* characters replaced by *mask_char*.

    When *show_end* is True the last *visible* characters are kept instead of
    the first ones.
    """
    if len(value) <= visible:
        return mask_char * len(value)
    masked_len = len(value) - visible
    if show_end:
        return mask_char * masked_len + value[-visible:]
    return value[:visible] + mask_char * masked_len


def mask_entry(
    entry: Dict[str, Any],
    fields: Optional[Iterable[str]] = None,
    *,
    visible: int = _DEFAULT_VISIBLE_CHARS,
    mask_char: str = _DEFAULT_MASK_CHAR,
    show_end: bool = False,
    pattern: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a copy of *entry* with specified field values partially masked.

    Parameters
    ----------
    entry:      The log entry dict.
    fields:     Explicit field names to mask.  Defaults to a sensible set.
    visible:    Number of characters to leave unmasked.
    mask_char:  Character used for masking.
    show_end:   If True, keep the *last* visible characters instead of first.
    pattern:    Optional regex; only string values matching this pattern are
                masked (applied on top of the field selection).
    """
    default_fields = {"token", "password", "secret", "api_key", "auth", "credential"}
    target_fields = set(fields) if fields is not None else default_fields

    compiled = re.compile(pattern) if pattern else None
    result = dict(entry)

    for field in target_fields:
        if field not in result:
            continue
        value = result[field]
        if not isinstance(value, str):
            continue
        if compiled and not compiled.search(value):
            continue
        result[field] = _mask_string(value, visible=visible, mask_char=mask_char, show_end=show_end)

    return result


def mask_entries(
    entries: Iterable[Dict[str, Any]],
    fields: Optional[Iterable[str]] = None,
    **kwargs: Any,
) -> Iterator[Dict[str, Any]]:
    """Yield masked copies of each entry in *entries*."""
    field_list = list(fields) if fields is not None else None
    for entry in entries:
        yield mask_entry(entry, fields=field_list, **kwargs)
