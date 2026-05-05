"""Tests for logslice.formatter module."""

import json
import pytest

from logslice.formatter import (
    format_entry_json,
    format_entry_pretty,
    format_entry_compact,
    format_entries,
    SUPPORTED_FORMATS,
)


SAMPLE_ENTRY = {
    "timestamp": "2024-01-15T10:00:00Z",
    "level": "INFO",
    "message": "Server started",
    "pid": 1234,
}


class TestFormatEntryJson:
    def test_returns_valid_json(self):
        result = format_entry_json(SAMPLE_ENTRY)
        parsed = json.loads(result)
        assert parsed == SAMPLE_ENTRY

    def test_single_line(self):
        result = format_entry_json(SAMPLE_ENTRY)
        assert "\n" not in result

    def test_handles_non_serializable_with_default(self):
        from datetime import datetime
        entry = {"ts": datetime(2024, 1, 1, 12, 0, 0), "msg": "ok"}
        result = format_entry_json(entry)
        assert "2024-01-01" in result


class TestFormatEntryPretty:
    def test_returns_indented_json(self):
        result = format_entry_pretty(SAMPLE_ENTRY)
        assert "\n" in result
        parsed = json.loads(result)
        assert parsed == SAMPLE_ENTRY

    def test_custom_indent(self):
        result = format_entry_pretty(SAMPLE_ENTRY, indent=4)
        assert "    " in result


class TestFormatEntryCompact:
    def test_all_fields_included(self):
        result = format_entry_compact({"level": "INFO", "pid": 42})
        assert "level=INFO" in result
        assert "pid=42" in result

    def test_values_with_spaces_are_quoted(self):
        result = format_entry_compact({"message": "Server started"})
        assert 'message="Server started"' in result

    def test_fields_filter_selects_subset(self):
        result = format_entry_compact(SAMPLE_ENTRY, fields=["level", "pid"])
        assert "level=INFO" in result
        assert "pid=1234" in result
        assert "timestamp" not in result

    def test_missing_fields_are_skipped(self):
        result = format_entry_compact(SAMPLE_ENTRY, fields=["level", "nonexistent"])
        assert "level=INFO" in result
        assert "nonexistent" not in result


class TestFormatEntries:
    def test_json_format(self):
        results = format_entries([SAMPLE_ENTRY], fmt="json")
        assert len(results) == 1
        assert json.loads(results[0]) == SAMPLE_ENTRY

    def test_pretty_format(self):
        results = format_entries([SAMPLE_ENTRY], fmt="pretty")
        assert "\n" in results[0]

    def test_compact_format(self):
        results = format_entries([SAMPLE_ENTRY], fmt="compact")
        assert "level=INFO" in results[0]

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            format_entries([SAMPLE_ENTRY], fmt="xml")

    def test_empty_entries_returns_empty_list(self):
        assert format_entries([], fmt="json") == []

    def test_supported_formats_constant(self):
        assert "json" in SUPPORTED_FORMATS
        assert "pretty" in SUPPORTED_FORMATS
        assert "compact" in SUPPORTED_FORMATS
