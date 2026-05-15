"""Tests for logslice.classifier."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from logslice.classifier import (
    build_rule,
    classify_entries,
    classify_entry,
    rules_from_config,
)

Entry = Dict[str, Any]


def _entry(**kwargs: Any) -> Entry:
    base: Entry = {"timestamp": "2024-01-01T00:00:00Z", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# build_rule
# ---------------------------------------------------------------------------


class TestBuildRule:
    def test_name_stored(self):
        rule = build_rule("errors", "level", "ERROR")
        assert rule["name"] == "errors"

    def test_predicate_matches(self):
        rule = build_rule("errors", "level", "ERROR")
        assert rule["predicate"](_entry(level="ERROR"))

    def test_predicate_no_match(self):
        rule = build_rule("errors", "level", "ERROR")
        assert not rule["predicate"](_entry(level="INFO"))

    def test_missing_field_returns_false(self):
        rule = build_rule("errors", "level", "ERROR")
        assert not rule["predicate"](_entry())

    def test_default_priority_is_zero(self):
        rule = build_rule("x", "f", "p")
        assert rule["priority"] == 0


# ---------------------------------------------------------------------------
# classify_entry
# ---------------------------------------------------------------------------


class TestClassifyEntry:
    def test_matching_rule_sets_class(self):
        rules = [build_rule("errors", "level", "ERROR")]
        result = classify_entry(_entry(level="ERROR"), rules)
        assert result["_class"] == "errors"

    def test_no_match_uses_default(self):
        rules = [build_rule("errors", "level", "ERROR")]
        result = classify_entry(_entry(level="INFO"), rules)
        assert result["_class"] == "unclassified"

    def test_custom_default_label(self):
        result = classify_entry(_entry(), [], default="other")
        assert result["_class"] == "other"

    def test_original_entry_not_mutated(self):
        entry = _entry(level="ERROR")
        rules = [build_rule("errors", "level", "ERROR")]
        classify_entry(entry, rules)
        assert "_class" not in entry

    def test_priority_order_respected(self):
        rules = [
            build_rule("low", "level", "ERROR", priority=10),
            build_rule("high", "level", "ERROR", priority=1),
        ]
        result = classify_entry(_entry(level="ERROR"), rules)
        assert result["_class"] == "high"

    def test_multi_returns_all_matches(self):
        rules = [
            build_rule("errors", "level", "ERROR"),
            build_rule("critical", "message", "disk"),
        ]
        entry = _entry(level="ERROR", message="disk full")
        result = classify_entry(entry, rules, multi=True)
        assert set(result["_class"]) == {"errors", "critical"}

    def test_multi_no_match_uses_default_list(self):
        result = classify_entry(_entry(), [], multi=True)
        assert result["_class"] == ["unclassified"]


# ---------------------------------------------------------------------------
# classify_entries
# ---------------------------------------------------------------------------


class TestClassifyEntries:
    def test_yields_all_entries(self):
        entries = [_entry(level="INFO"), _entry(level="ERROR")]
        rules = [build_rule("errors", "level", "ERROR")]
        results = list(classify_entries(entries, rules))
        assert len(results) == 2

    def test_empty_input_yields_nothing(self):
        assert list(classify_entries([], [])) == []

    def test_correct_classification_applied(self):
        entries = [_entry(level="WARN")]
        rules = [build_rule("warnings", "level", "WARN")]
        result = next(classify_entries(entries, rules))
        assert result["_class"] == "warnings"


# ---------------------------------------------------------------------------
# rules_from_config
# ---------------------------------------------------------------------------


class TestRulesFromConfig:
    def test_builds_correct_number_of_rules(self):
        cfg = [
            {"name": "a", "field": "level", "pattern": "ERROR"},
            {"name": "b", "field": "level", "pattern": "WARN"},
        ]
        rules = rules_from_config(cfg)
        assert len(rules) == 2

    def test_predicate_works_after_build(self):
        cfg = [{"name": "errors", "field": "level", "pattern": "ERROR"}]
        rules = rules_from_config(cfg)
        assert rules[0]["predicate"](_entry(level="ERROR"))

    def test_optional_priority_defaults_to_zero(self):
        cfg = [{"name": "x", "field": "f", "pattern": "p"}]
        rules = rules_from_config(cfg)
        assert rules[0]["priority"] == 0

    def test_explicit_priority_preserved(self):
        cfg = [{"name": "x", "field": "f", "pattern": "p", "priority": 5}]
        rules = rules_from_config(cfg)
        assert rules[0]["priority"] == 5
