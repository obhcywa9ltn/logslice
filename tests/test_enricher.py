"""Tests for logslice.enricher."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from logslice.enricher import enrich_entries, enrich_entry


def _entry(**kwargs: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {"timestamp": "2024-01-01T00:00:00Z", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# enrich_entry — static_fields
# ---------------------------------------------------------------------------

class TestStaticFields:
    def test_static_field_added(self):
        result = enrich_entry(_entry(), static_fields={"env": "prod"})
        assert result["env"] == "prod"

    def test_static_field_not_overwritten_by_default(self):
        result = enrich_entry(_entry(env="staging"), static_fields={"env": "prod"})
        assert result["env"] == "staging"

    def test_static_field_overwritten_when_flag_set(self):
        result = enrich_entry(_entry(env="staging"), static_fields={"env": "prod"}, overwrite=True)
        assert result["env"] == "prod"

    def test_original_entry_not_mutated(self):
        original = _entry()
        enrich_entry(original, static_fields={"env": "prod"})
        assert "env" not in original


# ---------------------------------------------------------------------------
# enrich_entry — add_severity
# ---------------------------------------------------------------------------

class TestAddSeverity:
    @pytest.mark.parametrize("level,expected", [
        ("debug", 7),
        ("info", 6),
        ("warning", 4),
        ("warn", 4),
        ("error", 3),
        ("critical", 2),
        ("DEBUG", 7),
    ])
    def test_known_levels(self, level: str, expected: int):
        result = enrich_entry(_entry(level=level), add_severity=True)
        assert result["severity"] == expected

    def test_unknown_level_not_added(self):
        result = enrich_entry(_entry(level="verbose"), add_severity=True)
        assert "severity" not in result

    def test_missing_level_not_added(self):
        result = enrich_entry(_entry(), add_severity=True)
        assert "severity" not in result

    def test_existing_severity_not_overwritten(self):
        result = enrich_entry(_entry(level="info", severity=99), add_severity=True)
        assert result["severity"] == 99

    def test_existing_severity_overwritten_when_flag_set(self):
        result = enrich_entry(_entry(level="info", severity=99), add_severity=True, overwrite=True)
        assert result["severity"] == 6


# ---------------------------------------------------------------------------
# enrich_entry — extract_fields
# ---------------------------------------------------------------------------

class TestExtractFields:
    def test_extracts_capture_group(self):
        entry = _entry(message="user=alice logged in")
        result = enrich_entry(entry, extract_fields={"user": r"user=(\w+)"})
        assert result["user"] == "alice"

    def test_no_match_field_not_added(self):
        entry = _entry(message="no user here")
        result = enrich_entry(entry, extract_fields={"user": r"user=(\w+)"})
        assert "user" not in result

    def test_existing_field_not_overwritten_by_default(self):
        entry = _entry(message="user=alice", user="bob")
        result = enrich_entry(entry, extract_fields={"user": r"user=(\w+)"})
        assert result["user"] == "bob"

    def test_multiple_patterns(self):
        entry = _entry(message="user=alice req_id=42")
        result = enrich_entry(
            entry,
            extract_fields={"user": r"user=(\w+)", "req_id": r"req_id=(\d+)"},
        )
        assert result["user"] == "alice"
        assert result["req_id"] == "42"


# ---------------------------------------------------------------------------
# enrich_entries
# ---------------------------------------------------------------------------

class TestEnrichEntries:
    def test_yields_all_entries(self):
        entries = [_entry(level="info"), _entry(level="error")]
        result = list(enrich_entries(entries, add_severity=True))
        assert len(result) == 2

    def test_enrichment_applied_to_each(self):
        entries = [_entry(level="info"), _entry(level="error")]
        result = list(enrich_entries(entries, add_severity=True))
        assert result[0]["severity"] == 6
        assert result[1]["severity"] == 3

    def test_empty_input_yields_nothing(self):
        result = list(enrich_entries([], static_fields={"env": "prod"}))
        assert result == []
