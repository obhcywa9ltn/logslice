"""Tests for logslice.filter module."""

from datetime import datetime, timezone
from typing import Iterator

import pytest

from logslice.filter import filter_by_time_range, filter_entries, match_field_patterns


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc)


SAMPLE_ENTRIES = [
    {"timestamp": dt(10), "level": "INFO", "message": "server started"},
    {"timestamp": dt(11), "level": "ERROR", "message": "disk full"},
    {"timestamp": dt(12), "level": "INFO", "message": "request received"},
    {"timestamp": dt(13), "level": "WARN", "message": "high memory"},
    {"timestamp": dt(14), "level": "ERROR", "message": "connection refused"},
]


class TestMatchFieldPatterns:
    def test_single_matching_pattern(self):
        entry = {"level": "ERROR", "message": "disk full"}
        assert match_field_patterns(entry, [("level", "ERROR")])

    def test_single_non_matching_pattern(self):
        entry = {"level": "INFO", "message": "ok"}
        assert not match_field_patterns(entry, [("level", "ERROR")])

    def test_multiple_patterns_all_match(self):
        entry = {"level": "ERROR", "message": "disk full"}
        assert match_field_patterns(entry, [("level", "ERROR"), ("message", "disk")])

    def test_multiple_patterns_partial_match(self):
        entry = {"level": "ERROR", "message": "ok"}
        assert not match_field_patterns(entry, [("level", "ERROR"), ("message", "disk")])

    def test_missing_field_returns_false(self):
        entry = {"message": "hello"}
        assert not match_field_patterns(entry, [("level", "INFO")])

    def test_empty_patterns_returns_true(self):
        entry = {"level": "INFO"}
        assert match_field_patterns(entry, [])

    def test_regex_partial_match(self):
        entry = {"message": "connection refused by server"}
        assert match_field_patterns(entry, [("message", "refused")])


class TestFilterByTimeRange:
    def _run(self, start=None, end=None):
        return list(filter_by_time_range(iter(SAMPLE_ENTRIES), start=start, end=end))

    def test_no_bounds_returns_all(self):
        assert len(self._run()) == len(SAMPLE_ENTRIES)

    def test_start_bound(self):
        results = self._run(start=dt(12))
        assert all(e["timestamp"] >= dt(12) for e in results)
        assert len(results) == 3

    def test_end_bound(self):
        results = self._run(end=dt(11))
        assert all(e["timestamp"] <= dt(11) for e in results)
        assert len(results) == 2

    def test_both_bounds(self):
        results = self._run(start=dt(11), end=dt(13))
        assert len(results) == 3

    def test_entry_missing_timestamp_skipped(self):
        entries = [{"level": "INFO"}, {"timestamp": dt(10), "level": "INFO"}]
        results = list(filter_by_time_range(iter(entries), start=dt(9)))
        assert len(results) == 1


class TestFilterEntries:
    def test_combined_time_and_pattern(self):
        results = list(
            filter_entries(
                iter(SAMPLE_ENTRIES),
                patterns=[("level", "ERROR")],
                start=dt(11),
                end=dt(13),
            )
        )
        assert len(results) == 1
        assert results[0]["message"] == "disk full"

    def test_pattern_only(self):
        results = list(filter_entries(iter(SAMPLE_ENTRIES), patterns=[("level", "INFO")]))
        assert len(results) == 2

    def test_no_filters_returns_all(self):
        results = list(filter_entries(iter(SAMPLE_ENTRIES)))
        assert len(results) == len(SAMPLE_ENTRIES)
