"""watchdog.py — Tail and watch a log file for new entries in real time."""

from __future__ import annotations

import os
import time
from collections.abc import Generator, Iterator
from typing import Optional

from logslice.parser import parse_log_line


def _read_new_lines(fp, last_pos: int) -> tuple[list[str], int]:
    """Seek to *last_pos*, read any new lines, return them and the new position."""
    fp.seek(0, 2)  # seek to end to get current file size
    current_size = fp.tell()

    if current_size < last_pos:
        # File was truncated / rotated — restart from beginning.
        last_pos = 0

    fp.seek(last_pos)
    lines = fp.readlines()
    new_pos = fp.tell()
    return lines, new_pos


def tail_file(
    path: str,
    poll_interval: float = 0.25,
    max_iterations: Optional[int] = None,
) -> Generator[dict, None, None]:
    """Yield parsed log entries as they are appended to *path*.

    Parameters
    ----------
    path:
        Path to the log file to watch.
    poll_interval:
        Seconds to sleep between polls when no new data is available.
    max_iterations:
        If set, stop after this many poll cycles (useful for testing).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found: {path}")

    iterations = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fp:
        # Start at the end of the existing content.
        fp.seek(0, 2)
        last_pos = fp.tell()

        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break

            lines, last_pos = _read_new_lines(fp, last_pos)
            for raw in lines:
                entry = parse_log_line(raw)
                if entry is not None:
                    yield entry

            iterations += 1
            if not lines:
                time.sleep(poll_interval)


def watch_entries(
    paths: list[str],
    poll_interval: float = 0.25,
    max_iterations: Optional[int] = None,
) -> Iterator[dict]:
    """Round-robin watch multiple log files and yield new entries.

    Entries are yielded in the order they are discovered across files.
    """
    if not paths:
        return

    generators = [
        tail_file(p, poll_interval=poll_interval, max_iterations=max_iterations)
        for p in paths
    ]
    for gen in generators:
        yield from gen
