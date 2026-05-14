"""High-level pipeline that chains filtering, transformation, and formatting."""

from datetime import datetime
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional

from logslice.filter import filter_entries
from logslice.transformer import transform_entries, TransformMap
from logslice.redactor import redact_entries
from logslice.deduplicator import deduplicate_entries
from logslice.sampler import sample_entries
from logslice.formatter import format_entries


def build_pipeline(
    entries: Iterable[Dict[str, Any]],
    *,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    patterns: Optional[List[tuple]] = None,
    transforms: Optional[TransformMap] = None,
    redact: bool = False,
    sensitive_fields: Optional[List[str]] = None,
    deduplicate: bool = False,
    sample_rate: Optional[float] = None,
    fmt: str = "json",
    indent: Optional[int] = None,
) -> Iterator[str]:
    """Chain log processing steps into a single lazy iterator of formatted strings.

    Steps (each optional):
      1. Time-range + field-pattern filtering
      2. Field transformation
      3. Sensitive-field redaction
      4. Deduplication
      5. Random sampling
      6. Formatting

    Args:
        entries:          Iterable of parsed log entry dicts.
        start:            Inclusive lower bound for timestamp filtering.
        end:              Inclusive upper bound for timestamp filtering.
        patterns:         List of (field, regex) tuples for field filtering.
        transforms:       Mapping of field -> callable for value transformation.
        redact:           Whether to redact sensitive fields.
        sensitive_fields: Fields to redact (uses defaults when None).
        deduplicate:      Whether to remove duplicate entries.
        sample_rate:      Float in (0, 1] for random sampling, or None to skip.
        fmt:              Output format: "json", "pretty", or "compact".
        indent:           JSON indent level (only used when fmt=="json").

    Raises:
        ValueError: If sample_rate is provided but not in the range (0, 1].
        ValueError: If fmt is not one of "json", "pretty", or "compact".

    Yields:
        Formatted log lines as strings.
    """
    if sample_rate is not None and not (0 < sample_rate <= 1):
        raise ValueError(
            f"sample_rate must be in the range (0, 1], got {sample_rate!r}"
        )

    valid_formats = {"json", "pretty", "compact"}
    if fmt not in valid_formats:
        raise ValueError(
            f"fmt must be one of {sorted(valid_formats)}, got {fmt!r}"
        )

    stream: Iterable[Dict[str, Any]] = entries

    # 1. Filter
    stream = filter_entries(
        stream,
        start=start,
        end=end,
        patterns=patterns or [],
    )

    # 2. Transform
    if transforms:
        stream = transform_entries(stream, transforms)

    # 3. Redact
    if redact:
        stream = redact_entries(stream, fields=sensitive_fields)

    # 4. Deduplicate
    if deduplicate:
        stream = deduplicate_entries(stream)

    # 5. Sample
    if sample_rate is not None:
        stream = sample_entries(stream, rate=sample_rate)

    # 6. Format
    yield from format_entries(stream, fmt=fmt, indent=indent)
