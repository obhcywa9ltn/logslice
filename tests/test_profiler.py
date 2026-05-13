"""Tests for logslice.profiler."""

from __future__ import annotations

import pytest

from logslice.profiler import ProfileResult, format_profile, profile_entries


def _entry(msg: str = "hello") -> dict:
    return {"timestamp": "2024-01-01T00:00:00Z", "message": msg, "level": "INFO"}


# ---------------------------------------------------------------------------
# profile_entries
# ---------------------------------------------------------------------------


class TestProfileEntries:
    def test_total_count_matches(self):
        entries = [_entry(str(i)) for i in range(5)]
        gen, result = profile_entries(iter(entries))
        list(gen)  # consume
        assert result.total_entries == 5

    def test_empty_entries_zero_count(self):
        gen, result = profile_entries(iter([]))
        list(gen)
        assert result.total_entries == 0

    def test_elapsed_is_non_negative(self):
        gen, result = profile_entries(iter([_entry()]))
        list(gen)
        assert result.elapsed_seconds >= 0.0

    def test_entries_per_second_positive_for_non_empty(self):
        gen, result = profile_entries(iter([_entry(), _entry()]))
        list(gen)
        assert result.entries_per_second > 0

    def test_entries_per_second_zero_for_empty(self):
        gen, result = profile_entries(iter([]))
        list(gen)
        assert result.entries_per_second == 0.0

    def test_gap_stats_none_for_single_entry(self):
        gen, result = profile_entries(iter([_entry()]))
        list(gen)
        assert result.min_gap_seconds is None
        assert result.max_gap_seconds is None
        assert result.avg_gap_seconds is None

    def test_gap_stats_populated_for_multiple_entries(self):
        gen, result = profile_entries(iter([_entry(), _entry(), _entry()]))
        list(gen)
        assert result.min_gap_seconds is not None
        assert result.max_gap_seconds is not None
        assert result.avg_gap_seconds is not None

    def test_min_le_avg_le_max(self):
        gen, result = profile_entries(iter([_entry(str(i)) for i in range(10)]))
        list(gen)
        assert result.min_gap_seconds <= result.avg_gap_seconds <= result.max_gap_seconds  # type: ignore[operator]

    def test_result_not_populated_before_consumption(self):
        entries = [_entry() for _ in range(3)]
        _gen, result = profile_entries(iter(entries))
        # do NOT consume — totals should still be at defaults
        assert result.total_entries == 0

    def test_yields_all_entries_unchanged(self):
        entries = [_entry(str(i)) for i in range(4)]
        gen, _ = profile_entries(iter(entries))
        out = list(gen)
        assert out == entries


# ---------------------------------------------------------------------------
# format_profile
# ---------------------------------------------------------------------------


class TestFormatProfile:
    def test_contains_entries_label(self):
        r = ProfileResult(total_entries=42, elapsed_seconds=1.0, entries_per_second=42.0)
        assert "entries" in format_profile(r)

    def test_contains_throughput_label(self):
        r = ProfileResult(total_entries=10, elapsed_seconds=0.5, entries_per_second=20.0)
        assert "throughput" in format_profile(r)

    def test_gap_lines_absent_when_none(self):
        r = ProfileResult(total_entries=1, elapsed_seconds=0.001, entries_per_second=1000.0)
        text = format_profile(r)
        assert "gap" not in text

    def test_gap_lines_present_when_populated(self):
        r = ProfileResult(
            total_entries=3,
            elapsed_seconds=0.003,
            entries_per_second=1000.0,
            min_gap_seconds=0.001,
            max_gap_seconds=0.002,
            avg_gap_seconds=0.0015,
        )
        text = format_profile(r)
        assert "gap min" in text
        assert "gap max" in text
        assert "gap avg" in text
