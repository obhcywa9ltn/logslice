"""Tests for logslice.tagger."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from logslice.tagger import (
    build_rule,
    filter_by_tag,
    tag_entries,
    tag_entry,
)


def _entry(**kwargs: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {"message": "hello", "level": "info"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# tag_entry
# ---------------------------------------------------------------------------

class TestTagEntry:
    def test_matching_rule_adds_tag(self):
        rules = [("low", lambda e: e.get("level") == "info")]
        result = tag_entry(_entry(), rules)
        assert "low" in result["tags"]

    def test_non_matching_rule_no_tag(self):
        rules = [("error", lambda e: e.get("level") == "error")]
        result = tag_entry(_entry(level="info"), rules)
        assert result["tags"] == []

    def test_original_entry_not_mutated(self):
        entry = _entry()
        rules = [("x", lambda e: True)]
        tag_entry(entry, rules)
        assert "tags" not in entry

    def test_multi_true_applies_all_matching(self):
        rules = [
            ("a", lambda e: True),
            ("b", lambda e: True),
        ]
        result = tag_entry(_entry(), rules, multi=True)
        assert "a" in result["tags"]
        assert "b" in result["tags"]

    def test_multi_false_applies_only_first_match(self):
        rules = [
            ("a", lambda e: True),
            ("b", lambda e: True),
        ]
        result = tag_entry(_entry(), rules, multi=False)
        assert result["tags"] == ["a"]

    def test_custom_tag_field(self):
        rules = [("important", lambda e: True)]
        result = tag_entry(_entry(), rules, tag_field="labels")
        assert "important" in result["labels"]
        assert "tags" not in result

    def test_duplicate_tag_not_added_twice(self):
        rules = [
            ("dup", lambda e: True),
            ("dup", lambda e: True),
        ]
        result = tag_entry(_entry(), rules)
        assert result["tags"].count("dup") == 1

    def test_predicate_exception_treated_as_no_match(self):
        def bad(_e):
            raise RuntimeError("boom")

        result = tag_entry(_entry(), [("boom", bad)])
        assert result["tags"] == []

    def test_existing_tags_preserved(self):
        entry = _entry(tags=["pre-existing"])
        rules = [("new", lambda e: True)]
        result = tag_entry(entry, rules)
        assert "pre-existing" in result["tags"]
        assert "new" in result["tags"]


# ---------------------------------------------------------------------------
# build_rule
# ---------------------------------------------------------------------------

def test_build_rule_matches_correct_value():
    tag, pred = build_rule("warn", "level", "warning")
    assert tag == "warn"
    assert pred({"level": "warning"}) is True
    assert pred({"level": "info"}) is False


# ---------------------------------------------------------------------------
# tag_entries
# ---------------------------------------------------------------------------

def test_tag_entries_yields_all():
    entries = [_entry(level="info"), _entry(level="error")]
    rules = [("err", lambda e: e.get("level") == "error")]
    results = list(tag_entries(entries, rules))
    assert len(results) == 2
    assert "err" not in results[0]["tags"]
    assert "err" in results[1]["tags"]


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

def test_filter_by_tag_returns_only_matching():
    entries = [
        _entry(tags=["a", "b"]),
        _entry(tags=["b"]),
        _entry(tags=["a"]),
    ]
    result = list(filter_by_tag(entries, "a"))
    assert len(result) == 2


def test_filter_by_tag_empty_when_none_match():
    entries = [_entry(tags=["x"]), _entry(tags=[])]
    result = list(filter_by_tag(entries, "missing"))
    assert result == []


def test_filter_by_tag_custom_field():
    entries = [_entry(labels=["vip"]), _entry(labels=[])]
    result = list(filter_by_tag(entries, "vip", tag_field="labels"))
    assert len(result) == 1
