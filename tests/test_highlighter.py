"""Tests for logslice.highlighter."""

from __future__ import annotations

import pytest

from logslice.highlighter import (
    _RESET,
    _LEVEL_COLOURS,
    highlight_level,
    highlight_pattern,
    highlight_entry,
    highlight_entries,
)


def _entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# highlight_level
# ---------------------------------------------------------------------------

class TestHighlightLevel:
    def test_known_level_contains_ansi_code(self):
        result = highlight_level(_entry(level="error"))
        assert _LEVEL_COLOURS["error"] in result
        assert _RESET in result

    def test_known_level_preserves_original_text(self):
        result = highlight_level(_entry(level="info"))
        assert "info" in result

    def test_unknown_level_returns_plain_text(self):
        result = highlight_level(_entry(level="verbose"))
        assert result == "verbose"
        assert "\033[" not in result

    def test_missing_level_returns_empty_string(self):
        result = highlight_level({})
        assert result == ""

    @pytest.mark.parametrize("level", ["debug", "info", "warning", "error", "critical"])
    def test_all_standard_levels_are_coloured(self, level):
        result = highlight_level(_entry(level=level))
        assert _RESET in result


# ---------------------------------------------------------------------------
# highlight_pattern
# ---------------------------------------------------------------------------

class TestHighlightPattern:
    def test_match_is_wrapped(self):
        result = highlight_pattern("hello world", "world")
        assert "world" in result
        assert _RESET in result

    def test_no_match_returns_original(self):
        result = highlight_pattern("hello world", "xyz")
        assert result == "hello world"

    def test_multiple_matches_all_wrapped(self):
        result = highlight_pattern("aaa bbb aaa", "aaa")
        assert result.count(_RESET) == 2

    def test_custom_colour_applied(self):
        from logslice.highlighter import _COLOURS
        result = highlight_pattern("test", "test", colour="blue")
        assert _COLOURS["blue"] in result


# ---------------------------------------------------------------------------
# highlight_entry
# ---------------------------------------------------------------------------

class TestHighlightEntry:
    def test_level_field_is_coloured(self):
        result = highlight_entry(_entry(level="error"))
        assert _RESET in result["level"]

    def test_non_level_string_highlighted_when_pattern_matches(self):
        result = highlight_entry(_entry(message="error occurred"), patterns=["error"])
        assert _RESET in result["message"]

    def test_no_patterns_leaves_strings_unchanged(self):
        entry = _entry(message="hello")
        result = highlight_entry(entry)
        assert result["message"] == "hello"

    def test_original_entry_not_mutated(self):
        entry = _entry(level="info", message="test")
        highlight_entry(entry, patterns=["test"])
        assert entry["message"] == "test"

    def test_non_string_values_passed_through(self):
        entry = _entry(count=42)
        result = highlight_entry(entry, patterns=["42"])
        assert result["count"] == 42


# ---------------------------------------------------------------------------
# highlight_entries
# ---------------------------------------------------------------------------

class TestHighlightEntries:
    def test_yields_same_number_of_entries(self):
        entries = [_entry(level="info"), _entry(level="error")]
        result = list(highlight_entries(entries))
        assert len(result) == 2

    def test_empty_input_yields_nothing(self):
        assert list(highlight_entries([])) == []

    def test_pattern_applied_across_all_entries(self):
        entries = [_entry(message="foo bar"), _entry(message="foo baz")]
        result = list(highlight_entries(entries, patterns=["foo"]))
        for r in result:
            assert _RESET in r["message"]
