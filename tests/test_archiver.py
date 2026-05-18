"""Tests for logslice.archiver."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from logslice.archiver import (
    _window_label,
    archive_by_size,
    archive_by_window,
    read_archive,
)


def _entry(ts: str, msg: str = "hello") -> dict:
    return {"timestamp": ts, "message": msg, "level": "INFO"}


# ---------------------------------------------------------------------------
# _window_label
# ---------------------------------------------------------------------------

class TestWindowLabel:
    def test_day_window(self):
        e = _entry("2024-03-15T10:23:00Z")
        assert _window_label(e, "day") == "20240315"

    def test_hour_window(self):
        e = _entry("2024-03-15T10:23:00Z")
        assert _window_label(e, "hour") == "20240315_10"

    def test_month_window(self):
        e = _entry("2024-03-15T10:23:00Z")
        assert _window_label(e, "month") == "202403"

    def test_missing_timestamp_returns_unknown(self):
        assert _window_label({}, "day") == "unknown"

    def test_invalid_timestamp_returns_unknown(self):
        assert _window_label({"timestamp": "not-a-date"}, "day") == "unknown"


# ---------------------------------------------------------------------------
# archive_by_window
# ---------------------------------------------------------------------------

class TestArchiveByWindow:
    def test_creates_output_dir(self, tmp_path):
        out = tmp_path / "archives"
        archive_by_window([_entry("2024-01-01T00:00:00Z")], out)
        assert out.is_dir()

    def test_returns_counts(self, tmp_path):
        entries = [
            _entry("2024-01-01T00:00:00Z"),
            _entry("2024-01-01T12:00:00Z"),
            _entry("2024-01-02T08:00:00Z"),
        ]
        counts = archive_by_window(entries, tmp_path, window="day")
        assert sum(counts.values()) == 3

    def test_two_days_two_files(self, tmp_path):
        entries = [
            _entry("2024-01-01T00:00:00Z"),
            _entry("2024-01-02T00:00:00Z"),
        ]
        counts = archive_by_window(entries, tmp_path, window="day")
        assert len(counts) == 2

    def test_same_day_one_file(self, tmp_path):
        entries = [_entry("2024-01-01T00:00:00Z"), _entry("2024-01-01T23:59:59Z")]
        counts = archive_by_window(entries, tmp_path, window="day")
        assert len(counts) == 1

    def test_files_are_gzipped_ndjson(self, tmp_path):
        archive_by_window([_entry("2024-06-10T05:00:00Z", "test")], tmp_path)
        gz_files = list(tmp_path.glob("*.gz"))
        assert gz_files
        with gzip.open(gz_files[0], "rt") as fh:
            data = json.loads(fh.readline())
        assert data["message"] == "test"

    def test_custom_prefix(self, tmp_path):
        archive_by_window([_entry("2024-01-01T00:00:00Z")], tmp_path, prefix="myapp")
        gz_files = list(tmp_path.glob("myapp_*.gz"))
        assert len(gz_files) == 1

    def test_empty_entries_no_files(self, tmp_path):
        counts = archive_by_window([], tmp_path)
        assert counts == {}
        assert list(tmp_path.glob("*.gz")) == []


# ---------------------------------------------------------------------------
# archive_by_size
# ---------------------------------------------------------------------------

class TestArchiveBySizeEntries:
    def test_single_chunk(self, tmp_path):
        entries = [_entry("2024-01-01T00:00:00Z") for _ in range(5)]
        counts = archive_by_size(entries, tmp_path, max_entries=10)
        assert len(counts) == 1
        assert list(counts.values())[0] == 5

    def test_exact_multiple_chunks(self, tmp_path):
        entries = [_entry("2024-01-01T00:00:00Z") for _ in range(6)]
        counts = archive_by_size(entries, tmp_path, max_entries=3)
        assert len(counts) == 2

    def test_remainder_in_final_chunk(self, tmp_path):
        entries = [_entry("2024-01-01T00:00:00Z") for _ in range(7)]
        counts = archive_by_size(entries, tmp_path, max_entries=3)
        values = sorted(counts.values())
        assert values == [1, 3, 3]

    def test_invalid_max_entries_raises(self, tmp_path):
        with pytest.raises(ValueError):
            archive_by_size([], tmp_path, max_entries=0)

    def test_files_numbered_sequentially(self, tmp_path):
        entries = [_entry("2024-01-01T00:00:00Z") for _ in range(4)]
        archive_by_size(entries, tmp_path, max_entries=2)
        names = sorted(p.name for p in tmp_path.glob("*.gz"))
        assert names[0].startswith("logslice_0000")
        assert names[1].startswith("logslice_0001")

    def test_empty_entries_no_files(self, tmp_path):
        counts = archive_by_size([], tmp_path)
        assert counts == {}


# ---------------------------------------------------------------------------
# read_archive
# ---------------------------------------------------------------------------

class TestReadArchive:
    def test_round_trip(self, tmp_path):
        original = [_entry("2024-05-01T00:00:00Z", f"msg{i}") for i in range(3)]
        counts = archive_by_size(original, tmp_path, max_entries=10)
        path = next(iter(counts))
        recovered = list(read_archive(path))
        assert len(recovered) == 3
        assert recovered[0]["message"] == "msg0"

    def test_skips_blank_lines(self, tmp_path):
        path = tmp_path / "test.ndjson.gz"
        with gzip.open(path, "wt") as fh:
            fh.write('{"a": 1}\n\n{"b": 2}\n')
        result = list(read_archive(path))
        assert len(result) == 2

    def test_skips_invalid_json(self, tmp_path):
        path = tmp_path / "bad.ndjson.gz"
        with gzip.open(path, "wt") as fh:
            fh.write('{"ok": true}\nnot-json\n')
        result = list(read_archive(path))
        assert len(result) == 1
        assert result[0]["ok"] is True
