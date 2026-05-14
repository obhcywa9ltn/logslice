"""Replay log entries with timing delays that mirror original inter-event gaps."""

from __future__ import annotations

import time
from collections.abc import Generator, Iterable
from datetime import datetime, timezone
from typing import Any

from logslice.parser import parse_timestamp

LogEntry = dict[str, Any]


def _get_ts(entry: LogEntry) -> datetime | None:
    """Return a timezone-aware datetime from the entry's timestamp field, or None."""
    raw = entry.get("timestamp")
    if raw is None:
        return None
    return parse_timestamp(raw)


def replay_entries(
    entries: Iterable[LogEntry],
    *,
    speed: float = 1.0,
    max_gap: float | None = None,
) -> Generator[LogEntry, None, None]:
    """Yield entries with real-time delays that mirror original inter-event gaps.

    Args:
        entries:  Source log entries (must contain a ``timestamp`` field).
        speed:    Playback multiplier.  2.0 plays back twice as fast; 0.5 half speed.
                  Must be > 0.
        max_gap:  Cap on any single inter-event delay in seconds.  *None* means no cap.

    Yields:
        Each entry unchanged, after the appropriate sleep.
    """
    if speed <= 0:
        raise ValueError(f"speed must be positive, got {speed!r}")
    if max_gap is not None and max_gap < 0:
        raise ValueError(f"max_gap must be non-negative, got {max_gap!r}")

    prev_ts: datetime | None = None

    for entry in entries:
        ts = _get_ts(entry)

        if ts is not None and prev_ts is not None:
            gap = (ts - prev_ts).total_seconds()
            if gap > 0:
                delay = gap / speed
                if max_gap is not None:
                    delay = min(delay, max_gap)
                time.sleep(delay)

        if ts is not None:
            prev_ts = ts

        yield entry


def replay_with_wall_clock(
    entries: Iterable[LogEntry],
    *,
    speed: float = 1.0,
    max_gap: float | None = None,
) -> Generator[tuple[datetime, LogEntry], None, None]:
    """Like :func:`replay_entries` but also yields the wall-clock time of emission.

    Yields:
        ``(wall_time, entry)`` pairs where *wall_time* is the UTC datetime
        at which the entry was yielded after any sleep.
    """
    for entry in replay_entries(entries, speed=speed, max_gap=max_gap):
        yield datetime.now(tz=timezone.utc), entry
