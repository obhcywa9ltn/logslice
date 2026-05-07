"""Tests for logslice.schema."""

from __future__ import annotations

import pytest

from logslice.schema import FieldSpec, Schema, validate_entries


def _entry(**kwargs) -> dict:
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "ok"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# FieldSpec
# ---------------------------------------------------------------------------

class TestFieldSpec:
    def test_required_field_present_no_error(self):
        spec = FieldSpec(name="level", required=True)
        assert spec.validate(_entry()) == []

    def test_required_field_missing_returns_error(self):
        spec = FieldSpec(name="service", required=True)
        errors = spec.validate(_entry())
        assert len(errors) == 1
        assert "service" in errors[0]

    def test_optional_missing_field_no_error(self):
        spec = FieldSpec(name="service", required=False)
        assert spec.validate(_entry()) == []

    def test_correct_type_no_error(self):
        spec = FieldSpec(name="level", expected_type="str")
        assert spec.validate(_entry()) == []

    def test_wrong_type_returns_error(self):
        spec = FieldSpec(name="level", expected_type="int")
        errors = spec.validate(_entry())
        assert len(errors) == 1
        assert "int" in errors[0] or "str" in errors[0]

    def test_unknown_expected_type_returns_error(self):
        spec = FieldSpec(name="level", expected_type="uuid")
        errors = spec.validate(_entry())
        assert any("Unknown" in e for e in errors)

    def test_field_missing_and_no_required_no_type_error(self):
        spec = FieldSpec(name="missing", expected_type="str")
        # field absent, not required — no type check performed
        assert spec.validate(_entry()) == []


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class TestSchema:
    def _make_schema(self):
        return Schema(specs=[
            FieldSpec(name="timestamp", required=True, expected_type="str"),
            FieldSpec(name="level", required=True, expected_type="str"),
            FieldSpec(name="message", required=True, expected_type="str"),
        ])

    def test_valid_entry_no_errors(self):
        schema = self._make_schema()
        assert schema.validate_entry(_entry()) == []

    def test_is_valid_true_for_good_entry(self):
        schema = self._make_schema()
        assert schema.is_valid(_entry()) is True

    def test_missing_required_field_invalid(self):
        schema = self._make_schema()
        entry = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO"}
        assert schema.is_valid(entry) is False

    def test_multiple_errors_collected(self):
        schema = self._make_schema()
        errors = schema.validate_entry({})
        assert len(errors) == 3


# ---------------------------------------------------------------------------
# validate_entries
# ---------------------------------------------------------------------------

class TestValidateEntries:
    def _schema(self):
        return Schema(specs=[FieldSpec(name="level", required=True)])

    def test_yields_all_entries_with_errors(self):
        entries = [_entry(), {"timestamp": "x"}]
        results = list(validate_entries(entries, self._schema()))
        assert len(results) == 2

    def test_valid_entry_has_empty_errors(self):
        results = list(validate_entries([_entry()], self._schema()))
        entry, errors = results[0]
        assert errors == []

    def test_invalid_entry_has_errors(self):
        results = list(validate_entries([{"timestamp": "x"}], self._schema()))
        _, errors = results[0]
        assert len(errors) > 0

    def test_drop_invalid_skips_bad_entries(self):
        entries = [_entry(), {"timestamp": "x"}]
        results = list(validate_entries(entries, self._schema(), drop_invalid=True))
        assert len(results) == 1
        assert results[0][1] == []

    def test_empty_entries_yields_nothing(self):
        assert list(validate_entries([], self._schema())) == []
