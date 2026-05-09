"""Tests for logslice.watchdog."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from logslice.watchdog import tail_file, watch_entries, _read_new_lines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_line(fp, entry: dict) -> None:
    fp.write(json.dumps(entry) + "\n")
    fp.flush()


def _tmp_log(content: str = "") -> str:
    """Create a temporary file with *content* and return its path."""
    fd, path = tempfile.mkstemp(suffix=".log")
    os.write(fd, content.encode())
    os.close(fd)
    return path


# ---------------------------------------------------------------------------
# _read_new_lines
# ---------------------------------------------------------------------------

class TestReadNewLines:
    def test_reads_appended_line(self, tmp_path: Path) -> None:
        p = tmp_path / "app.log"
        p.write_text('{"msg": "first"}\n')
        with open(p, "r") as fp:
            lines, pos = _read_new_lines(fp, 0)
        assert len(lines) == 1
        assert "first" in lines[0]

    def test_no_new_lines_returns_empty(self, tmp_path: Path) -> None:
        p = tmp_path / "app.log"
        p.write_text('{"msg": "hi"}\n')
        with open(p, "r") as fp:
            fp.seek(0, 2)
            end = fp.tell()
            lines, new_pos = _read_new_lines(fp, end)
        assert lines == []
        assert new_pos == end

    def test_resets_on_truncation(self, tmp_path: Path) -> None:
        p = tmp_path / "app.log"
        p.write_text('{"msg": "old"}\n')
        with open(p, "r") as fp:
            # Pretend we were at a position beyond current file size.
            lines, new_pos = _read_new_lines(fp, last_pos=9999)
        # Should have reset to 0 and read from the beginning.
        assert len(lines) == 1
        assert new_pos > 0


# ---------------------------------------------------------------------------
# tail_file
# ---------------------------------------------------------------------------

class TestTailFile:
    def test_raises_for_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            list(tail_file("/no/such/file.log", max_iterations=1))

    def test_yields_entries_written_before_watch(self, tmp_path: Path) -> None:
        p = tmp_path / "app.log"
        p.write_text('{"level": "info", "message": "boot"}\n')
        # max_iterations=0 → read existing tail position only (no new data).
        entries = list(tail_file(str(p), max_iterations=0))
        # Nothing yielded because we start at end-of-file.
        assert entries == []

    def test_invalid_json_lines_are_skipped(self, tmp_path: Path) -> None:
        p = tmp_path / "app.log"
        p.write_text("not json\n")
        with open(p, "r") as fp:
            fp.seek(0, 2)
            start = fp.tell()
        # Append another bad line; max_iterations=1 forces one poll.
        with open(p, "a") as fp:
            fp.write("also not json\n")
        entries = list(tail_file(str(p), poll_interval=0, max_iterations=1))
        assert entries == []

    def test_valid_appended_entry_is_yielded(self, tmp_path: Path) -> None:
        p = tmp_path / "app.log"
        p.write_text("")  # empty file
        entry = {"level": "warn", "message": "watch out"}
        with open(p, "a") as fp:
            fp.write(json.dumps(entry) + "\n")
        entries = list(tail_file(str(p), poll_interval=0, max_iterations=1))
        assert len(entries) == 1
        assert entries[0]["message"] == "watch out"


# ---------------------------------------------------------------------------
# watch_entries
# ---------------------------------------------------------------------------

class TestWatchEntries:
    def test_empty_paths_yields_nothing(self) -> None:
        assert list(watch_entries([])) == []

    def test_multiple_files_combined(self, tmp_path: Path) -> None:
        p1 = tmp_path / "a.log"
        p2 = tmp_path / "b.log"
        p1.write_text('{"message": "alpha"}\n')
        p2.write_text('{"message": "beta"}\n')
        entries = list(
            watch_entries([str(p1), str(p2)], poll_interval=0, max_iterations=1)
        )
        messages = {e["message"] for e in entries}
        assert messages == {"alpha", "beta"}
