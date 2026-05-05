"""Statistics collection for parsed log entries."""

from collections import Counter
from typing import Iterable, Dict, Any


def compute_stats(entries: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics over a collection of log entries.

    Args:
        entries: Iterable of parsed log entry dicts.

    Returns:
        A dict containing:
          - total: total number of entries processed
          - level_counts: Counter of values found in the 'level' field
          - earliest: ISO timestamp string of the earliest entry, or None
          - latest: ISO timestamp string of the latest entry, or None
          - fields_seen: sorted list of all unique top-level field names
    """
    total = 0
    level_counts: Counter = Counter()
    timestamps = []
    fields_seen: set = set()

    for entry in entries:
        total += 1
        fields_seen.update(entry.keys())

        level = entry.get("level")
        if level is not None:
            level_counts[str(level)] += 1

        ts = entry.get("timestamp") or entry.get("time") or entry.get("ts")
        if ts is not None:
            timestamps.append(str(ts))

    timestamps_sorted = sorted(timestamps)

    return {
        "total": total,
        "level_counts": dict(level_counts),
        "earliest": timestamps_sorted[0] if timestamps_sorted else None,
        "latest": timestamps_sorted[-1] if timestamps_sorted else None,
        "fields_seen": sorted(fields_seen),
    }


def format_stats(stats: Dict[str, Any]) -> str:
    """Format a stats dict as a human-readable summary string.

    Args:
        stats: Dict returned by compute_stats.

    Returns:
        A multi-line string suitable for printing to a terminal.
    """
    lines = [
        f"Total entries : {stats['total']}",
        f"Earliest      : {stats['earliest'] or 'N/A'}",
        f"Latest        : {stats['latest'] or 'N/A'}",
    ]

    if stats["level_counts"]:
        lines.append("Levels        :")
        for level, count in sorted(stats["level_counts"].items()):
            lines.append(f"  {level:<12} {count}")
    else:
        lines.append("Levels        : N/A")

    lines.append(f"Fields seen   : {', '.join(stats['fields_seen']) or 'none'}")
    return "\n".join(lines)
