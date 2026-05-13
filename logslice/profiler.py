"""logslice.profiler — measures processing throughput and latency across log entries."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from logslice.parser import LogEntry


@dataclass
class ProfileResult:
    total_entries: int = 0
    elapsed_seconds: float = 0.0
    entries_per_second: float = 0.0
    min_gap_seconds: float | None = None
    max_gap_seconds: float | None = None
    avg_gap_seconds: float | None = None


def profile_entries(
    entries: Iterable[LogEntry],
) -> tuple[Iterator[LogEntry], ProfileResult]:
    """Wrap *entries* to collect throughput metrics as they are consumed.

    Returns a (lazy iterator, result-holder) pair.  The ProfileResult is
    populated **in-place** once the iterator is fully consumed.
    """
    result = ProfileResult()

    def _gen() -> Iterator[LogEntry]:
        gaps: list[float] = []
        prev_wall: float | None = None
        start = time.perf_counter()

        for entry in entries:
            now = time.perf_counter()
            if prev_wall is not None:
                gaps.append(now - prev_wall)
            prev_wall = now
            result.total_entries += 1
            yield entry

        result.elapsed_seconds = time.perf_counter() - start
        result.entries_per_second = (
            result.total_entries / result.elapsed_seconds
            if result.elapsed_seconds > 0
            else 0.0
        )
        if gaps:
            result.min_gap_seconds = min(gaps)
            result.max_gap_seconds = max(gaps)
            result.avg_gap_seconds = sum(gaps) / len(gaps)

    return _gen(), result


def format_profile(result: ProfileResult) -> str:
    """Return a human-readable summary of *result*."""
    lines = [
        f"entries      : {result.total_entries}",
        f"elapsed      : {result.elapsed_seconds:.4f}s",
        f"throughput   : {result.entries_per_second:.1f} entries/s",
    ]
    if result.min_gap_seconds is not None:
        lines += [
            f"gap min      : {result.min_gap_seconds * 1_000:.3f}ms",
            f"gap max      : {result.max_gap_seconds * 1_000:.3f}ms",  # type: ignore[operator]
            f"gap avg      : {result.avg_gap_seconds * 1_000:.3f}ms",  # type: ignore[operator]
        ]
    return "\n".join(lines)
