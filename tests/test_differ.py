"""Tests for logslice.differ."""
import pytest

from logslice.differ import DiffResult, diff_entries, format_diff


def _e(id_, **kwargs):
    return {"id": id_, **kwargs}


# ---------------------------------------------------------------------------
# diff_entries
# ---------------------------------------------------------------------------

class TestDiffEntries:
    def test_identical_streams_yield_nothing(self):
        left = [_e("a", msg="hello"), _e("b", msg="world")]
        right = [_e("a", msg="hello"), _e("b", msg="world")]
        assert list(diff_entries(left, right)) == []

    def test_added_entry(self):
        left = [_e("a", msg="hi")]
        right = [_e("a", msg="hi"), _e("b", msg="new")]
        results = list(diff_entries(left, right))
        assert len(results) == 1
        assert results[0].status == "added"
        assert results[0].key == "b"
        assert results[0].left is None

    def test_removed_entry(self):
        left = [_e("a", msg="hi"), _e("b", msg="bye")]
        right = [_e("a", msg="hi")]
        results = list(diff_entries(left, right))
        assert len(results) == 1
        assert results[0].status == "removed"
        assert results[0].key == "b"
        assert results[0].right is None

    def test_changed_entry(self):
        left = [_e("a", level="info", msg="hello")]
        right = [_e("a", level="error", msg="hello")]
        results = list(diff_entries(left, right))
        assert len(results) == 1
        r = results[0]
        assert r.status == "changed"
        assert r.key == "a"
        assert "level" in r.changed_fields

    def test_ignore_fields_not_reported(self):
        left = [_e("a", ts="2024-01-01", msg="hi")]
        right = [_e("a", ts="2024-01-02", msg="hi")]
        results = list(diff_entries(left, right, ignore_fields=["ts"]))
        assert results == []

    def test_custom_key_field(self):
        left = [{"trace": "x1", "msg": "old"}]
        right = [{"trace": "x1", "msg": "new"}, {"trace": "x2", "msg": "added"}]
        results = list(diff_entries(left, right, key_field="trace"))
        statuses = {r.status for r in results}
        assert "changed" in statuses
        assert "added" in statuses

    def test_empty_left(self):
        right = [_e("a", msg="hi")]
        results = list(diff_entries([], right))
        assert results[0].status == "added"

    def test_empty_right(self):
        left = [_e("a", msg="hi")]
        results = list(diff_entries(left, []))
        assert results[0].status == "removed"

    def test_both_empty(self):
        assert list(diff_entries([], [])) == []

    def test_multiple_changed_fields(self):
        left = [_e("1", a=1, b=2, c=3)]
        right = [_e("1", a=9, b=2, c=99)]
        r = list(diff_entries(left, right))[0]
        assert set(r.changed_fields) == {"a", "c"}

    def test_entry_missing_key_field_skipped(self):
        left = [{"msg": "no id here"}]
        right = [{"msg": "also no id"}]
        assert list(diff_entries(left, right)) == []


# ---------------------------------------------------------------------------
# format_diff
# ---------------------------------------------------------------------------

class TestFormatDiff:
    def test_added_prefix(self):
        r = DiffResult("added", "k1", None, {"id": "k1"}, [])
        assert format_diff(r).startswith("[+]")

    def test_removed_prefix(self):
        r = DiffResult("removed", "k1", {"id": "k1"}, None, [])
        assert format_diff(r).startswith("[-]")

    def test_changed_prefix_and_fields(self):
        r = DiffResult("changed", "k1", {}, {}, ["level", "msg"])
        text = format_diff(r)
        assert text.startswith("[~]")
        assert "level" in text
        assert "msg" in text
