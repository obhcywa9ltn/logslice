"""Archive log entries to compressed files by time window or size."""

from __future__ import annotations

import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator


def _window_label(entry: dict, window: str) -> str:
    """Return a string label for the time window the entry belongs to."""
    ts = entry.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return "unknown"
    if window == "hour":
        return dt.strftime("%Y%m%d_%H")
    if window == "day":
        return dt.strftime("%Y%m%d")
    if window == "month":
        return dt.strftime("%Y%m")
    return dt.strftime("%Y%m%d")


def archive_by_window(
    entries: Iterable[dict],
    output_dir: str | Path,
    window: str = "day",
    prefix: str = "logslice",
) -> dict[str, int]:
    """Write entries into per-window gzipped NDJSON files.

    Returns a mapping of archive path -> entry count.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    handles: dict[str, gzip.GzipFile] = {}
    counts: dict[str, int] = {}
    try:
        for entry in entries:
            label = _window_label(entry, window)
            path = str(output_dir / f"{prefix}_{label}.ndjson.gz")
            if path not in handles:
                handles[path] = gzip.open(path, "at", encoding="utf-8")
                counts[path] = 0
            handles[path].write(json.dumps(entry, default=str) + "\n")
            counts[path] += 1
    finally:
        for fh in handles.values():
            fh.close()
    return counts


def archive_by_size(
    entries: Iterable[dict],
    output_dir: str | Path,
    max_entries: int = 10_000,
    prefix: str = "logslice",
) -> dict[str, int]:
    """Write entries into sequentially numbered gzipped NDJSON files.

    Each file holds at most *max_entries* entries.
    Returns a mapping of archive path -> entry count.
    """
    if max_entries < 1:
        raise ValueError("max_entries must be >= 1")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    chunk = 0
    current_path = ""
    fh: gzip.GzipFile | None = None
    current_count = 0
    try:
        for entry in entries:
            if fh is None or current_count >= max_entries:
                if fh is not None:
                    fh.close()
                current_path = str(output_dir / f"{prefix}_{chunk:04d}.ndjson.gz")
                fh = gzip.open(current_path, "at", encoding="utf-8")
                counts[current_path] = 0
                current_count = 0
                chunk += 1
            fh.write(json.dumps(entry, default=str) + "\n")
            counts[current_path] += 1
            current_count += 1
    finally:
        if fh is not None:
            fh.close()
    return counts


def read_archive(path: str | Path) -> Iterator[dict]:
    """Yield parsed log entries from a gzipped NDJSON archive file."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    pass
