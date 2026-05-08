"""Rate-limiting utilities for logslice.

Allows capping the number of log entries emitted per time-bucket so that
downstream consumers are not overwhelmed by bursty log sources.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Generator, Iterable, Optional


def _bucket_key(ts: datetime, bucket_seconds: int) -> int:
    """Return an integer bucket key for *ts* rounded down to *bucket_seconds*."""
    epoch = int(ts.replace(tzinfo=timezone.utc).timestamp()) if ts.tzinfo else int(ts.timestamp())
    return epoch - (epoch % bucket_seconds)


def rate_limit_entries(
    entries: Iterable[dict],
    max_per_bucket: int,
    bucket_seconds: int = 1,
    timestamp_field: str = "timestamp",
) -> Generator[dict, None, None]:
    """Yield entries, dropping those that exceed *max_per_bucket* in any bucket.

    Args:
        entries: Iterable of parsed log-entry dicts.
        max_per_bucket: Maximum number of entries allowed per time bucket.
        bucket_seconds: Width of each time bucket in seconds (default: 1).
        timestamp_field: Name of the field that holds the entry timestamp.

    Yields:
        Entries that fall within the rate limit for their bucket.
    """
    if max_per_bucket <= 0:
        raise ValueError("max_per_bucket must be a positive integer")
    if bucket_seconds <= 0:
        raise ValueError("bucket_seconds must be a positive integer")

    counts: Dict[int, int] = defaultdict(int)

    for entry in entries:
        ts: Optional[datetime] = entry.get(timestamp_field)
        if not isinstance(ts, datetime):
            # Entries without a parseable timestamp always pass through.
            yield entry
            continue

        key = _bucket_key(ts, bucket_seconds)
        if counts[key] < max_per_bucket:
            counts[key] += 1
            yield entry


def count_by_bucket(
    entries: Iterable[dict],
    bucket_seconds: int = 1,
    timestamp_field: str = "timestamp",
) -> Dict[int, int]:
    """Return a mapping of bucket-key → entry-count without filtering."""
    if bucket_seconds <= 0:
        raise ValueError("bucket_seconds must be a positive integer")

    counts: Dict[int, int] = defaultdict(int)
    for entry in entries:
        ts: Optional[datetime] = entry.get(timestamp_field)
        if isinstance(ts, datetime):
            counts[_bucket_key(ts, bucket_seconds)] += 1
    return dict(counts)
