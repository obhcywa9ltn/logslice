"""Tests for logslice.stats module."""

import pytest
from logslice.stats import compute_stats, format_stats


SAMPLE_ENTRIES = [
    {"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "message": "started"},
    {"timestamp": "2024-01-01T10:05:00Z", "level": "WARN", "message": "slow query"},
    {"timestamp": "2024-01-01T10:10:00Z", "level": "ERROR", "message": "failed"},
    {"timestamp": "2024-01-01T10:15:00Z", "level": "INFO", "message": "retry"},
]


class TestComputeStats:
    def test_total_count(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        assert stats["total"] == 4

    def test_level_counts(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        assert stats["level_counts"] == {"INFO": 2, "WARN": 1, "ERROR": 1}

    def test_earliest_and_latest(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        assert stats["earliest"] == "2024-01-01T10:00:00Z"
        assert stats["latest"] == "2024-01-01T10:15:00Z"

    def test_fields_seen(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        assert stats["fields_seen"] == ["level", "message", "timestamp"]

    def test_empty_entries(self):
        stats = compute_stats([])
        assert stats["total"] == 0
        assert stats["level_counts"] == {}
        assert stats["earliest"] is None
        assert stats["latest"] is None
        assert stats["fields_seen"] == []

    def test_entries_without_level(self):
        entries = [{"timestamp": "2024-01-01T09:00:00Z", "msg": "hello"}]
        stats = compute_stats(entries)
        assert stats["level_counts"] == {}

    def test_fallback_timestamp_keys(self):
        entries = [
            {"time": "2024-03-01T08:00:00Z", "level": "INFO"},
            {"ts": "2024-03-01T09:00:00Z", "level": "DEBUG"},
        ]
        stats = compute_stats(entries)
        assert stats["earliest"] == "2024-03-01T08:00:00Z"
        assert stats["latest"] == "2024-03-01T09:00:00Z"

    def test_accepts_generator(self):
        def _gen():
            yield {"timestamp": "2024-06-01T00:00:00Z", "level": "INFO"}
            yield {"timestamp": "2024-06-02T00:00:00Z", "level": "INFO"}

        stats = compute_stats(_gen())
        assert stats["total"] == 2


class TestFormatStats:
    def test_contains_total(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        output = format_stats(stats)
        assert "Total entries" in output
        assert "4" in output

    def test_contains_level_names(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        output = format_stats(stats)
        assert "INFO" in output
        assert "ERROR" in output

    def test_contains_timestamps(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        output = format_stats(stats)
        assert "2024-01-01T10:00:00Z" in output
        assert "2024-01-01T10:15:00Z" in output

    def test_empty_stats_shows_na(self):
        stats = compute_stats([])
        output = format_stats(stats)
        assert "N/A" in output

    def test_returns_string(self):
        stats = compute_stats(SAMPLE_ENTRIES)
        assert isinstance(format_stats(stats), str)
