"""Tests for logslice.splitter."""

from __future__ import annotations

import pytest

from logslice.splitter import split_by_field, split_by_predicate, split_by_rules


def _entry(level: str = "info", service: str = "api", **kwargs) -> dict:
    return {"level": level, "service": service, "message": "ok", **kwargs}


# ---------------------------------------------------------------------------
# split_by_field
# ---------------------------------------------------------------------------

class TestSplitByField:
    def test_groups_entries_by_field_value(self):
        entries = [_entry(level="info"), _entry(level="error"), _entry(level="info")]
        result = split_by_field(entries, "level")
        assert len(result["info"]) == 2
        assert len(result["error"]) == 1

    def test_missing_field_uses_default_label(self):
        entries = [_entry(), {"message": "no level"}]
        result = split_by_field(entries, "level")
        assert "__missing__" in result
        assert len(result["__missing__"]) == 1

    def test_custom_missing_label(self):
        entries = [{"message": "bare"}]
        result = split_by_field(entries, "level", missing_label="unknown")
        assert "unknown" in result

    def test_empty_entries_returns_empty_dict(self):
        assert split_by_field([], "level") == {}

    def test_single_bucket_when_all_same_value(self):
        entries = [_entry(level="debug")] * 5
        result = split_by_field(entries, "level")
        assert list(result.keys()) == ["debug"]
        assert len(result["debug"]) == 5


# ---------------------------------------------------------------------------
# split_by_predicate
# ---------------------------------------------------------------------------

class TestSplitByPredicate:
    def test_two_buckets_created(self):
        entries = [_entry(level="error"), _entry(level="info")]
        result = split_by_predicate(entries, lambda e: e.get("level") == "error")
        assert len(result["match"]) == 1
        assert len(result["no_match"]) == 1

    def test_custom_labels(self):
        entries = [_entry(level="warn")]
        result = split_by_predicate(
            entries,
            lambda e: e.get("level") == "warn",
            true_label="warnings",
            false_label="other",
        )
        assert "warnings" in result
        assert len(result["warnings"]) == 1

    def test_all_match(self):
        entries = [_entry(level="error")] * 3
        result = split_by_predicate(entries, lambda e: True)
        assert len(result["match"]) == 3
        assert result["no_match"] == []


# ---------------------------------------------------------------------------
# split_by_rules
# ---------------------------------------------------------------------------

class TestSplitByRules:
    def test_first_matching_rule_wins(self):
        entries = [_entry(level="error"), _entry(level="warn"), _entry(level="info")]
        rules = [
            ("errors", lambda e: e.get("level") == "error"),
            ("warnings", lambda e: e.get("level") == "warn"),
        ]
        result = split_by_rules(entries, rules)
        assert len(result["errors"]) == 1
        assert len(result["warnings"]) == 1
        assert len(result["__default__"]) == 1

    def test_unmatched_dropped_when_no_default(self):
        entries = [_entry(level="debug")]
        rules = [("errors", lambda e: e.get("level") == "error")]
        result = split_by_rules(entries, rules, default_label=None)
        assert "__default__" not in result
        assert "debug" not in result

    def test_empty_rules_all_go_to_default(self):
        entries = [_entry(), _entry()]
        result = split_by_rules(entries, [])
        assert len(result["__default__"]) == 2

    def test_empty_entries_returns_empty(self):
        rules = [("errors", lambda e: True)]
        assert split_by_rules([], rules) == {}
