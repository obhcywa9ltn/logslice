"""Tests for logslice.sorter."""

from __future__ import annotations

import pytest

from logslice.sorter import sort_entries, sort_by_timestamp


def _entry(ts: str, msg: str = "msg") -> dict:
    return {"timestamp": ts, "message": msg}


class TestSortEntries:
    def test_sorts_ascending_by_timestamp(self):
        entries = [
            _entry("2024-01-03"),
            _entry("2024-01-01"),
            _entry("2024-01-02"),
        ]
        result = list(sort_entries(entries, field="timestamp"))
        assert [e["timestamp"] for e in result] == [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
        ]

    def test_sorts_descending_when_reverse_true(self):
        entries = [
            _entry("2024-01-01"),
            _entry("2024-01-03"),
            _entry("2024-01-02"),
        ]
        result = list(sort_entries(entries, field="timestamp", reverse=True))
        assert result[0]["timestamp"] == "2024-01-03"
        assert result[-1]["timestamp"] == "2024-01-01"

    def test_sorts_by_arbitrary_field(self):
        entries = [
            {"level": "warn"},
            {"level": "debug"},
            {"level": "info"},
        ]
        result = list(sort_entries(entries, field="level"))
        assert [e["level"] for e in result] == ["debug", "info", "warn"]

    def test_missing_field_placed_last_by_default(self):
        entries = [
            {"timestamp": "2024-01-02"},
            {"message": "no timestamp"},
            {"timestamp": "2024-01-01"},
        ]
        result = list(sort_entries(entries, field="timestamp", missing_last=True))
        assert result[-1] == {"message": "no timestamp"}

    def test_missing_field_placed_first_when_flag_false(self):
        entries = [
            {"timestamp": "2024-01-02"},
            {"message": "no timestamp"},
            {"timestamp": "2024-01-01"},
        ]
        result = list(sort_entries(entries, field="timestamp", missing_last=False))
        assert result[0] == {"message": "no timestamp"}

    def test_empty_entries_returns_empty(self):
        assert list(sort_entries([])) == []

    def test_single_entry_returned_unchanged(self):
        entry = _entry("2024-01-01")
        result = list(sort_entries([entry]))
        assert result == [entry]

    def test_original_iterable_not_mutated(self):
        original = [
            _entry("2024-01-02"),
            _entry("2024-01-01"),
        ]
        _ = list(sort_entries(original))
        # Original list order should be unchanged.
        assert original[0]["timestamp"] == "2024-01-02"


class TestSortByTimestamp:
    def test_convenience_wrapper_ascending(self):
        entries = [_entry("2024-03-01"), _entry("2024-01-01"), _entry("2024-02-01")]
        result = list(sort_by_timestamp(entries))
        assert result[0]["timestamp"] == "2024-01-01"

    def test_convenience_wrapper_descending(self):
        entries = [_entry("2024-01-01"), _entry("2024-03-01"), _entry("2024-02-01")]
        result = list(sort_by_timestamp(entries, reverse=True))
        assert result[0]["timestamp"] == "2024-03-01"
