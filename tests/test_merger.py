"""Tests for logslice.merger."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.merger import merge_entries, merge_all


def _ts(hour: int, minute: int = 0) -> str:
    return datetime(2024, 1, 1, hour, minute, 0, tzinfo=timezone.utc).isoformat()


def _entry(msg: str, hour: int, minute: int = 0, **extra) -> dict:
    return {"timestamp": _ts(hour, minute), "message": msg, **extra}


# ---------------------------------------------------------------------------
# merge_entries
# ---------------------------------------------------------------------------

class TestMergeEntries:
    def test_two_streams_merged_in_order(self):
        a = [_entry("a1", 1), _entry("a2", 3)]
        b = [_entry("b1", 2), _entry("b2", 4)]
        result = list(merge_entries(a, b))
        messages = [e["message"] for e in result]
        assert messages == ["a1", "b1", "a2", "b2"]

    def test_single_stream_passthrough(self):
        a = [_entry("x", 1), _entry("y", 2)]
        assert list(merge_entries(a)) == a

    def test_empty_streams_yield_nothing(self):
        assert list(merge_entries([], [])) == []

    def test_one_empty_one_non_empty(self):
        a = [_entry("only", 5)]
        result = list(merge_entries([], a))
        assert len(result) == 1
        assert result[0]["message"] == "only"

    def test_three_streams(self):
        a = [_entry("a", 1), _entry("d", 4)]
        b = [_entry("b", 2)]
        c = [_entry("c", 3), _entry("e", 5)]
        messages = [e["message"] for e in merge_entries(a, b, c)]
        assert messages == ["a", "b", "c", "d", "e"]

    def test_entries_without_timestamp_sorted_last(self):
        a = [_entry("early", 1)]
        b = [{"message": "no-ts"}]
        result = list(merge_entries(a, b))
        assert result[-1]["message"] == "no-ts"

    def test_custom_key(self):
        a = [{"level": "a"}, {"level": "c"}]
        b = [{"level": "b"}, {"level": "d"}]
        result = list(merge_entries(a, b, key="level"))
        assert [e["level"] for e in result] == ["a", "b", "c", "d"]

    def test_custom_key_missing_value_sorted_last(self):
        a = [{"level": "a"}]
        b = [{"other": "x"}]
        result = list(merge_entries(a, b, key="level"))
        assert result[0]["level"] == "a"
        assert "level" not in result[1]

    def test_preserves_all_fields(self):
        a = [_entry("msg", 1, service="svc-a")]
        b = [_entry("msg2", 2, service="svc-b")]
        result = list(merge_entries(a, b))
        assert result[0]["service"] == "svc-a"
        assert result[1]["service"] == "svc-b"


# ---------------------------------------------------------------------------
# merge_all
# ---------------------------------------------------------------------------

def test_merge_all_equivalent_to_merge_entries():
    a = [_entry("a", 1), _entry("c", 3)]
    b = [_entry("b", 2), _entry("d", 4)]
    via_merge_entries = list(merge_entries(a, b))
    via_merge_all = list(merge_all([a, b]))
    assert via_merge_entries == via_merge_all


def test_merge_all_empty_iterable_yields_nothing():
    assert list(merge_all([])) == []
