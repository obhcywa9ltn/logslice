"""Tests for logslice.writer."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from logslice.writer import write_entries, write_to_path


SAMPLE_ENTRIES = [
    {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "start"},
    {"timestamp": "2024-01-01T00:01:00Z", "level": "ERROR", "message": "fail"},
]


class TestWriteEntries:
    def test_returns_count(self):
        buf = io.StringIO()
        count = write_entries(SAMPLE_ENTRIES, buf, fmt="json")
        assert count == 2

    def test_json_output_is_valid(self):
        buf = io.StringIO()
        write_entries(SAMPLE_ENTRIES, buf, fmt="json")
        lines = buf.getvalue().strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "timestamp" in parsed

    def test_compact_output_contains_message(self):
        buf = io.StringIO()
        write_entries(SAMPLE_ENTRIES, buf, fmt="compact")
        output = buf.getvalue()
        assert "start" in output
        assert "fail" in output

    def test_empty_entries_writes_nothing(self):
        buf = io.StringIO()
        count = write_entries([], buf, fmt="json")
        assert count == 0
        assert buf.getvalue() == ""

    def test_flush_each_does_not_raise(self):
        buf = io.StringIO()
        count = write_entries(SAMPLE_ENTRIES, buf, fmt="json", flush_each=True)
        assert count == 2


class TestWriteToPath:
    def test_writes_to_file(self, tmp_path: Path):
        out_file = tmp_path / "output.log"
        count = write_to_path(SAMPLE_ENTRIES, out_file, fmt="json")
        assert count == 2
        lines = out_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

    def test_file_contains_valid_json(self, tmp_path: Path):
        out_file = tmp_path / "output.log"
        write_to_path(SAMPLE_ENTRIES, out_file, fmt="json")
        for line in out_file.read_text().strip().splitlines():
            json.loads(line)  # must not raise

    def test_none_path_writes_to_stdout(self, capsys):
        count = write_to_path(SAMPLE_ENTRIES, None, fmt="compact")
        assert count == 2
        captured = capsys.readouterr()
        assert "start" in captured.out

    def test_empty_entries_creates_empty_file(self, tmp_path: Path):
        out_file = tmp_path / "empty.log"
        count = write_to_path([], out_file, fmt="json")
        assert count == 0
        assert out_file.read_text() == ""
