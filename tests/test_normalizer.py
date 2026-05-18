"""Tests for logslice.normalizer."""

from __future__ import annotations

import pytest

from logslice.normalizer import (
    coerce_field,
    lowercase_field,
    normalize_entries,
    normalize_entry,
)


def _entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00Z", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# coerce_field
# ---------------------------------------------------------------------------

class TestCoerceField:
    def test_coerce_to_int(self):
        e = _entry(code="42")
        result = coerce_field(e, "code", "int")
        assert result["code"] == 42
        assert isinstance(result["code"], int)

    def test_coerce_to_float(self):
        e = _entry(duration="1.5")
        result = coerce_field(e, "duration", "float")
        assert result["duration"] == pytest.approx(1.5)

    def test_coerce_to_str(self):
        e = _entry(code=404)
        result = coerce_field(e, "code", "str")
        assert result["code"] == "404"

    def test_coerce_bool_true(self):
        for raw in ("true", "1", "yes"):
            e = _entry(flag=raw)
            assert coerce_field(e, "flag", "bool")["flag"] is True

    def test_coerce_bool_false(self):
        e = _entry(flag="false")
        assert coerce_field(e, "flag", "bool")["flag"] is False

    def test_missing_field_ok_by_default(self):
        e = _entry()
        result = coerce_field(e, "nonexistent", "int")
        assert result == e

    def test_missing_field_raises_when_not_ok(self):
        with pytest.raises(KeyError):
            coerce_field(_entry(), "nonexistent", "int", missing_ok=False)

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown type"):
            coerce_field(_entry(x=1), "x", "datetime")

    def test_original_entry_not_mutated(self):
        e = _entry(code="7")
        coerce_field(e, "code", "int")
        assert e["code"] == "7"


# ---------------------------------------------------------------------------
# lowercase_field
# ---------------------------------------------------------------------------

class TestLowercaseField:
    def test_string_lowercased(self):
        e = _entry(level="ERROR")
        assert lowercase_field(e, "level")["level"] == "error"

    def test_non_string_unchanged(self):
        e = _entry(code=404)
        assert lowercase_field(e, "code")["code"] == 404

    def test_missing_field_ok_by_default(self):
        e = _entry()
        result = lowercase_field(e, "missing")
        assert result == e

    def test_missing_field_raises_when_not_ok(self):
        with pytest.raises(KeyError):
            lowercase_field(_entry(), "missing", missing_ok=False)


# ---------------------------------------------------------------------------
# normalize_entry
# ---------------------------------------------------------------------------

class TestNormalizeEntry:
    def test_coercions_applied(self):
        e = _entry(status="200")
        result = normalize_entry(e, coercions={"status": "int"})
        assert result["status"] == 200

    def test_lowercase_applied(self):
        e = _entry(level="WARNING")
        result = normalize_entry(e, lowercase=["level"])
        assert result["level"] == "warning"

    def test_strip_nulls_removes_none(self):
        e = _entry(trace_id=None)
        result = normalize_entry(e, strip_nulls=True)
        assert "trace_id" not in result

    def test_strip_nulls_false_keeps_none(self):
        e = _entry(trace_id=None)
        result = normalize_entry(e, strip_nulls=False)
        assert "trace_id" in result

    def test_combined_rules(self):
        e = _entry(level="INFO", code="0", empty=None)
        result = normalize_entry(
            e,
            coercions={"code": "int"},
            lowercase=["level"],
            strip_nulls=True,
        )
        assert result["level"] == "info"
        assert result["code"] == 0
        assert "empty" not in result


# ---------------------------------------------------------------------------
# normalize_entries
# ---------------------------------------------------------------------------

def test_normalize_entries_yields_all():
    entries = [_entry(level="DEBUG"), _entry(level="INFO")]
    results = list(normalize_entries(entries, lowercase=["level"]))
    assert len(results) == 2
    assert all(r["level"] == r["level"].lower() for r in results)


def test_normalize_entries_empty():
    assert list(normalize_entries([], coercions={"x": "int"})) == []
