"""Output writer for logslice — handles writing formatted log entries to files or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Iterator, Optional, TextIO, Union

from logslice.formatter import format_entries


def open_output(path: Optional[Union[str, Path]]) -> TextIO:
    """Open a file path for writing, or return stdout if path is None."""
    if path is None:
        return sys.stdout
    return open(path, "w", encoding="utf-8")


def write_entries(
    entries: Iterable[dict],
    output: TextIO,
    fmt: str = "json",
    flush_each: bool = False,
) -> int:
    """Write formatted log entries to *output*.

    Args:
        entries:    Iterable of parsed log entry dicts.
        output:     Writable text stream (file or stdout).
        fmt:        One of ``'json'``, ``'pretty'``, or ``'compact'``.
        flush_each: If True, flush after every line (useful for streaming).

    Returns:
        The number of entries written.
    """
    count = 0
    for line in format_entries(entries, fmt=fmt):
        output.write(line + "\n")
        if flush_each:
            output.flush()
        count += 1
    return count


def write_to_path(
    entries: Iterable[dict],
    path: Optional[Union[str, Path]],
    fmt: str = "json",
) -> int:
    """Convenience wrapper: open *path* (or stdout) and write entries.

    Args:
        entries: Iterable of parsed log entry dicts.
        path:    Destination file path, or ``None`` to write to stdout.
        fmt:     One of ``'json'``, ``'pretty'``, or ``'compact'``.

    Returns:
        The number of entries written.

    Raises:
        OSError: If *path* cannot be opened for writing.
    """
    stream = open_output(path)
    try:
        return write_entries(entries, stream, fmt=fmt)
    finally:
        if stream is not sys.stdout:
            stream.close()
