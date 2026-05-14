"""Summarize log entries into a human-readable digest."""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Any


def summarize_entries(
    entries: Iterable[Dict[str, Any]],
    *,
    level_field: str = "level",
    message_field: str = "message",
    timestamp_field: str = "timestamp",
    top_n: int = 5,
) -> Dict[str, Any]:
    """Consume *entries* and return a summary dict.

    The summary includes:
    - total entry count
    - per-level counts
    - top N most-common messages
    - earliest and latest timestamps (as raw strings / values)
    """
    total = 0
    level_counts: Counter = Counter()
    message_counts: Counter = Counter()
    earliest = None
    latest = None

    for entry in entries:
        total += 1

        level = entry.get(level_field)
        if level is not None:
            level_counts[str(level)] += 1

        message = entry.get(message_field)
        if message is not None:
            message_counts[str(message)] += 1

        ts = entry.get(timestamp_field)
        if ts is not None:
            ts_str = str(ts)
            if earliest is None or ts_str < earliest:
                earliest = ts_str
            if latest is None or ts_str > latest:
                latest = ts_str

    return {
        "total": total,
        "by_level": dict(level_counts),
        "top_messages": message_counts.most_common(top_n),
        "earliest": earliest,
        "latest": latest,
    }


def format_summary(summary: Dict[str, Any]) -> str:
    """Return a multi-line human-readable string for *summary*."""
    lines: List[str] = []
    lines.append(f"Total entries : {summary['total']}")
    lines.append(f"Earliest      : {summary['earliest'] or 'n/a'}")
    lines.append(f"Latest        : {summary['latest'] or 'n/a'}")

    if summary["by_level"]:
        lines.append("Levels:")
        for level, count in sorted(summary["by_level"].items()):
            lines.append(f"  {level:<12} {count}")

    if summary["top_messages"]:
        lines.append("Top messages:")
        for msg, count in summary["top_messages"]:
            truncated = msg if len(msg) <= 60 else msg[:57] + "..."
            lines.append(f"  ({count:>4}x) {truncated}")

    return "\n".join(lines)
