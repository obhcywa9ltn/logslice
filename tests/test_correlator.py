"""Tests for logslice.correlator."""

import pytest

from logslice.correlator import (
    correlation_summary,
    find_by_correlation_id,
    group_by_correlation_id,
    iter_correlated,
)


def _entry(request_id: str, message: str = "msg", **extra) -> dict:
    e = {"request_id": request_id, "message": message}
    e.update(extra)
    return e


# ---------------------------------------------------------------------------
# group_by_correlation_id
# ---------------------------------------------------------------------------

class TestGroupByCorrelationId:
    def test_groups_by_field(self):
        entries = [_entry("a"), _entry("b"), _entry("a")]
        groups = group_by_correlation_id(entries)
        assert len(groups["a"]) == 2
        assert len(groups["b"]) == 1

    def test_missing_field_uses_default_label(self):
        entries = [{"message": "no id"}]
        groups = group_by_correlation_id(entries)
        assert "__no_id__" in groups

    def test_custom_missing_label(self):
        entries = [{"message": "no id"}]
        groups = group_by_correlation_id(entries, missing_label="unknown")
        assert "unknown" in groups

    def test_empty_entries_returns_empty(self):
        assert group_by_correlation_id([]) == {}

    def test_custom_field(self):
        entries = [{"trace_id": "x", "msg": "a"}, {"trace_id": "x", "msg": "b"}]
        groups = group_by_correlation_id(entries, field="trace_id")
        assert len(groups["x"]) == 2


# ---------------------------------------------------------------------------
# iter_correlated
# ---------------------------------------------------------------------------

class TestIterCorrelated:
    def test_yields_groups_meeting_min(self):
        entries = [_entry("a"), _entry("a"), _entry("b")]
        result = list(iter_correlated(entries, min_entries=2))
        assert len(result) == 1
        assert len(result[0]) == 2

    def test_min_entries_one_yields_all_groups(self):
        entries = [_entry("a"), _entry("b")]
        result = list(iter_correlated(entries, min_entries=1))
        assert len(result) == 2

    def test_invalid_min_entries_raises(self):
        with pytest.raises(ValueError):
            list(iter_correlated([], min_entries=0))

    def test_empty_entries_yields_nothing(self):
        assert list(iter_correlated([], min_entries=1)) == []


# ---------------------------------------------------------------------------
# find_by_correlation_id
# ---------------------------------------------------------------------------

class TestFindByCorrelationId:
    def test_returns_matching_entries(self):
        entries = [_entry("abc"), _entry("abc"), _entry("xyz")]
        result = find_by_correlation_id(entries, "abc")
        assert len(result) == 2

    def test_no_match_returns_empty(self):
        entries = [_entry("abc")]
        result = find_by_correlation_id(entries, "zzz")
        assert result == []

    def test_custom_field(self):
        entries = [{"trace_id": "t1"}, {"trace_id": "t2"}]
        result = find_by_correlation_id(entries, "t1", field="trace_id")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# correlation_summary
# ---------------------------------------------------------------------------

class TestCorrelationSummary:
    def test_returns_count_per_group(self):
        groups = {"a": [_entry("a"), _entry("a")], "b": [_entry("b")]}
        summary = correlation_summary(groups)
        counts = {s["correlation_id"]: s["count"] for s in summary}
        assert counts["a"] == 2
        assert counts["b"] == 1

    def test_label_sample_included_when_requested(self):
        groups = {"a": [{"request_id": "a", "level": "error"}]}
        summary = correlation_summary(groups, label_field="level")
        assert summary[0]["label_sample"] == "error"

    def test_label_sample_none_when_field_absent(self):
        groups = {"a": [{"request_id": "a"}]}
        summary = correlation_summary(groups, label_field="level")
        assert summary[0]["label_sample"] is None

    def test_empty_groups_returns_empty(self):
        assert correlation_summary({}) == []
