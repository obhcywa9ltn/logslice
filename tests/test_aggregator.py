"""Tests for logslice.aggregator module."""

import pytest

from logslice.aggregator import (
    count_by_field,
    format_aggregation,
    group_by_field,
    top_values,
)


def _entry(level="info", service="web", **kwargs):
    entry = {"level": level, "service": service, "message": "test"}
    entry.update(kwargs)
    return entry


# ---------------------------------------------------------------------------
# group_by_field
# ---------------------------------------------------------------------------

class TestGroupByField:
    def test_groups_by_existing_field(self):
        entries = [_entry(level="info"), _entry(level="error"), _entry(level="info")]
        groups = group_by_field(entries, "level")
        assert len(groups["info"]) == 2
        assert len(groups["error"]) == 1

    def test_missing_field_uses_label(self):
        entries = [_entry(), {"message": "no level"}]
        groups = group_by_field(entries, "level", missing_label="UNKNOWN")
        assert "UNKNOWN" in groups
        assert len(groups["UNKNOWN"]) == 1

    def test_empty_entries_returns_empty(self):
        assert group_by_field([], "level") == {}

    def test_single_group(self):
        entries = [_entry(level="debug")] * 3
        groups = group_by_field(entries, "level")
        assert list(groups.keys()) == ["debug"]
        assert len(groups["debug"]) == 3


# ---------------------------------------------------------------------------
# count_by_field
# ---------------------------------------------------------------------------

class TestCountByField:
    def test_counts_correctly(self):
        entries = [_entry(level="info")] * 4 + [_entry(level="warn")] * 2
        counts = count_by_field(entries, "level")
        assert counts["info"] == 4
        assert counts["warn"] == 2

    def test_missing_field_counted_under_label(self):
        entries = [_entry(), {"message": "bare"}]
        counts = count_by_field(entries, "level")
        assert counts["<missing>"] == 1

    def test_empty_entries_returns_empty(self):
        assert count_by_field([], "service") == {}


# ---------------------------------------------------------------------------
# top_values
# ---------------------------------------------------------------------------

class TestTopValues:
    def test_returns_sorted_descending(self):
        counts = {"a": 3, "b": 10, "c": 1}
        result = top_values(counts, n=3)
        assert result[0] == ("b", 10)
        assert result[-1] == ("c", 1)

    def test_limits_to_n(self):
        counts = {str(i): i for i in range(20)}
        result = top_values(counts, n=5)
        assert len(result) == 5

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            top_values({"a": 1}, n=0)


# ---------------------------------------------------------------------------
# format_aggregation
# ---------------------------------------------------------------------------

class TestFormatAggregation:
    def test_contains_field_name(self):
        counts = {"info": 5, "error": 2}
        output = format_aggregation(counts, "level")
        assert "level" in output

    def test_contains_counts(self):
        counts = {"info": 5, "error": 2}
        output = format_aggregation(counts, "level")
        assert "info: 5" in output
        assert "error: 2" in output

    def test_top_limits_output(self):
        counts = {str(i): i + 1 for i in range(10)}
        output = format_aggregation(counts, "code", top=3)
        lines = [l for l in output.splitlines() if l.startswith("  ")]
        assert len(lines) == 3

    def test_empty_counts(self):
        output = format_aggregation({}, "level")
        assert "level" in output
