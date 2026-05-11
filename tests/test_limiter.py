"""Tests for logslice.limiter."""

from __future__ import annotations

import pytest

from logslice.limiter import counts_by_field, limit_by_field, limit_total


def _entry(level: str = "info", msg: str = "hello") -> dict:
    return {"level": level, "message": msg}


# ---------------------------------------------------------------------------
# limit_by_field
# ---------------------------------------------------------------------------

class TestLimitByField:
    def test_allows_up_to_max_per_value(self):
        entries = [_entry("info")] * 5
        result = list(limit_by_field(entries, "level", max_per_value=3))
        assert len(result) == 3

    def test_different_values_each_get_own_cap(self):
        entries = [_entry("info")] * 3 + [_entry("error")] * 3
        result = list(limit_by_field(entries, "level", max_per_value=2))
        assert len(result) == 4
        assert sum(1 for e in result if e["level"] == "info") == 2
        assert sum(1 for e in result if e["level"] == "error") == 2

    def test_missing_field_uses_label(self):
        entries = [{"message": "no level"}] * 4
        result = list(limit_by_field(entries, "level", max_per_value=2))
        assert len(result) == 2

    def test_custom_missing_label_does_not_affect_real_values(self):
        entries = [_entry("info")] * 2 + [{"message": "bare"}] * 2
        result = list(
            limit_by_field(entries, "level", max_per_value=1, missing_label="NONE")
        )
        assert len(result) == 2

    def test_max_per_value_one_yields_one_per_key(self):
        entries = [_entry("warn")] * 10
        result = list(limit_by_field(entries, "level", max_per_value=1))
        assert len(result) == 1

    def test_invalid_max_raises(self):
        with pytest.raises(ValueError, match="max_per_value"):
            list(limit_by_field([], "level", max_per_value=0))

    def test_empty_entries_yields_nothing(self):
        assert list(limit_by_field([], "level", max_per_value=5)) == []

    def test_entries_not_mutated(self):
        original = _entry("debug")
        entries = [original]
        result = list(limit_by_field(entries, "level", max_per_value=1))
        assert result[0] is original


# ---------------------------------------------------------------------------
# limit_total
# ---------------------------------------------------------------------------

class TestLimitTotal:
    def test_yields_up_to_max(self):
        entries = [_entry()] * 10
        result = list(limit_total(entries, max_entries=4))
        assert len(result) == 4

    def test_fewer_entries_than_max_yields_all(self):
        entries = [_entry()] * 3
        result = list(limit_total(entries, max_entries=10))
        assert len(result) == 3

    def test_zero_max_yields_nothing(self):
        entries = [_entry()] * 5
        assert list(limit_total(entries, max_entries=0)) == []

    def test_negative_max_raises(self):
        with pytest.raises(ValueError, match="max_entries"):
            list(limit_total([], max_entries=-1))

    def test_empty_input_yields_nothing(self):
        assert list(limit_total([], max_entries=5)) == []


# ---------------------------------------------------------------------------
# counts_by_field
# ---------------------------------------------------------------------------

class TestCountsByField:
    def test_counts_correctly(self):
        entries = [_entry("info")] * 3 + [_entry("error")] * 2
        result = counts_by_field(entries, "level")
        assert result == {"info": 3, "error": 2}

    def test_missing_field_counted_under_label(self):
        entries = [{"message": "bare"}] * 2
        result = counts_by_field(entries, "level", missing_label="N/A")
        assert result == {"N/A": 2}

    def test_empty_returns_empty_dict(self):
        assert counts_by_field([], "level") == {}
