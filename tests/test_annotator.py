"""Tests for logslice.annotator."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from logslice.annotator import (
    annotate_entries,
    annotate_entry,
    field_length,
    has_field,
)


def _entry(**kwargs: Any) -> Dict[str, Any]:
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# annotate_entry
# ---------------------------------------------------------------------------

class TestAnnotateEntry:
    def test_annotation_added_under_namespace(self):
        entry = _entry()
        result = annotate_entry(entry, [("tag", lambda e: "test")])
        assert result["_annotations"]["tag"] == "test"

    def test_original_entry_not_mutated(self):
        entry = _entry()
        annotate_entry(entry, [("tag", lambda e: "x")])
        assert "_annotations" not in entry

    def test_custom_namespace(self):
        entry = _entry()
        result = annotate_entry(entry, [("k", lambda e: 1)], namespace="_meta")
        assert "_meta" in result
        assert result["_meta"]["k"] == 1

    def test_none_return_skips_annotation(self):
        entry = _entry()
        result = annotate_entry(entry, [("skip", lambda e: None)])
        assert "_annotations" not in result

    def test_exception_in_fn_skips_annotation(self):
        def boom(e: Dict[str, Any]) -> Any:
            raise ValueError("oops")

        entry = _entry()
        result = annotate_entry(entry, [("bad", boom)])
        assert "_annotations" not in result

    def test_existing_annotation_not_overwritten_by_default(self):
        entry = _entry(_annotations={"tag": "original"})
        result = annotate_entry(entry, [("tag", lambda e: "new")])
        assert result["_annotations"]["tag"] == "original"

    def test_existing_annotation_overwritten_when_flag_set(self):
        entry = _entry(_annotations={"tag": "original"})
        result = annotate_entry(entry, [("tag", lambda e: "new")], overwrite=True)
        assert result["_annotations"]["tag"] == "new"

    def test_multiple_annotations_all_stored(self):
        entry = _entry()
        result = annotate_entry(
            entry,
            [("a", lambda e: 1), ("b", lambda e: 2)],
        )
        assert result["_annotations"] == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# annotate_entries
# ---------------------------------------------------------------------------

class TestAnnotateEntries:
    def test_yields_all_entries(self):
        entries = [_entry(), _entry(message="world")]
        results = list(annotate_entries(entries, [("x", lambda e: 1)]))
        assert len(results) == 2

    def test_empty_input_yields_nothing(self):
        results = list(annotate_entries([], [("x", lambda e: 1)]))
        assert results == []


# ---------------------------------------------------------------------------
# Built-in helpers
# ---------------------------------------------------------------------------

def test_has_field_returns_true_when_present():
    fn = has_field("level")
    assert fn(_entry()) is True


def test_has_field_returns_none_when_absent():
    fn = has_field("nonexistent")
    assert fn(_entry()) is None


def test_field_length_returns_length_of_string_field():
    fn = field_length("message")
    assert fn(_entry(message="hello")) == 5


def test_field_length_returns_none_for_missing_field():
    fn = field_length("nonexistent")
    assert fn(_entry()) is None
