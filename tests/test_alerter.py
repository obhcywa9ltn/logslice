"""Tests for logslice.alerter."""

from __future__ import annotations

from typing import List

import pytest

from logslice.alerter import (
    alert_entries,
    build_rule,
    check_entry,
    count_alerts,
)


def _entry(level: str = "INFO", message: str = "ok", **kwargs) -> dict:
    return {"level": level, "message": message, **kwargs}


# ---------------------------------------------------------------------------
# check_entry
# ---------------------------------------------------------------------------

class TestCheckEntry:
    def test_matching_rule_fires(self):
        rule = build_rule("high-error", "level", "ERROR")
        fired: List[str] = []
        check_entry(_entry(level="ERROR"), [rule], handler=lambda n, _: fired.append(n))
        assert fired == ["high-error"]

    def test_non_matching_rule_does_not_fire(self):
        rule = build_rule("high-error", "level", "ERROR")
        fired: List[str] = []
        check_entry(_entry(level="INFO"), [rule], handler=lambda n, _: fired.append(n))
        assert fired == []

    def test_returns_fired_rule_names(self):
        rules = [
            build_rule("r1", "level", "ERROR"),
            build_rule("r2", "message", "fail", op="contains"),
        ]
        fired = check_entry(_entry(level="ERROR", message="hard fail"), rules,
                            handler=lambda *_: None)
        assert set(fired) == {"r1", "r2"}

    def test_predicate_exception_is_silenced(self):
        bad_rule = {"name": "boom", "predicate": lambda _: 1 / 0}
        fired = check_entry(_entry(), [bad_rule], handler=lambda *_: None)
        assert fired == []


# ---------------------------------------------------------------------------
# build_rule
# ---------------------------------------------------------------------------

class TestBuildRule:
    def test_eq_op(self):
        rule = build_rule("r", "level", "WARN")
        assert rule["predicate"]({"level": "WARN"}) is True
        assert rule["predicate"]({"level": "INFO"}) is False

    def test_neq_op(self):
        rule = build_rule("r", "level", "INFO", op="neq")
        assert rule["predicate"]({"level": "ERROR"}) is True
        assert rule["predicate"]({"level": "INFO"}) is False

    def test_contains_op(self):
        rule = build_rule("r", "message", "timeout", op="contains")
        assert rule["predicate"]({"message": "connection timeout reached"}) is True
        assert rule["predicate"]({"message": "all good"}) is False

    def test_gt_op(self):
        rule = build_rule("r", "duration_ms", 500, op="gt")
        assert rule["predicate"]({"duration_ms": 600}) is True
        assert rule["predicate"]({"duration_ms": 400}) is False

    def test_lt_op(self):
        rule = build_rule("r", "score", 10, op="lt")
        assert rule["predicate"]({"score": 5}) is True
        assert rule["predicate"]({"score": 15}) is False

    def test_missing_field_returns_false(self):
        rule = build_rule("r", "nonexistent", "value")
        assert rule["predicate"]({}) is False

    def test_unknown_op_raises(self):
        with pytest.raises(ValueError, match="Unknown op"):
            build_rule("r", "level", "ERROR", op="regex")


# ---------------------------------------------------------------------------
# alert_entries
# ---------------------------------------------------------------------------

class TestAlertEntries:
    def test_passthrough_yields_all_entries(self):
        rules = [build_rule("r", "level", "ERROR")]
        entries = [_entry(level="INFO"), _entry(level="ERROR")]
        result = list(alert_entries(entries, rules, handler=lambda *_: None))
        assert len(result) == 2

    def test_passthrough_false_yields_only_matches(self):
        rules = [build_rule("r", "level", "ERROR")]
        entries = [_entry(level="INFO"), _entry(level="ERROR"), _entry(level="DEBUG")]
        result = list(alert_entries(entries, rules, handler=lambda *_: None,
                                    passthrough=False))
        assert len(result) == 1
        assert result[0]["level"] == "ERROR"

    def test_handler_called_for_each_match(self):
        rules = [build_rule("r", "level", "ERROR")]
        entries = [_entry(level="ERROR"), _entry(level="ERROR"), _entry(level="INFO")]
        calls: List[str] = []
        list(alert_entries(entries, rules, handler=lambda n, _: calls.append(n)))
        assert calls == ["r", "r"]

    def test_empty_entries_yields_nothing(self):
        rules = [build_rule("r", "level", "ERROR")]
        result = list(alert_entries([], rules))
        assert result == []


# ---------------------------------------------------------------------------
# count_alerts
# ---------------------------------------------------------------------------

class TestCountAlerts:
    def test_counts_per_rule(self):
        rules = [
            build_rule("errors", "level", "ERROR"),
            build_rule("warns", "level", "WARN"),
        ]
        entries = [
            _entry(level="ERROR"),
            _entry(level="ERROR"),
            _entry(level="WARN"),
            _entry(level="INFO"),
        ]
        counts = count_alerts(entries, rules)
        assert counts["errors"] == 2
        assert counts["warns"] == 1
        assert "INFO" not in counts

    def test_no_matches_returns_empty(self):
        rules = [build_rule("r", "level", "CRITICAL")]
        counts = count_alerts([_entry(level="INFO")], rules)
        assert counts == {}
