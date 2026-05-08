"""Tests for logslice.truncator."""

from __future__ import annotations

import pytest

from logslice.truncator import (
    truncate_entry,
    truncate_entries,
    truncate_value,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

class TestTruncateValue:
    def test_short_string_unchanged(self):
        assert truncate_value("hi", 10, "...") == "hi"

    def test_exact_length_unchanged(self):
        assert truncate_value("hello", 5, "...") == "hello"

    def test_long_string_truncated(self):
        result = truncate_value("abcdefghij", 6, "...")
        assert result == "abc..."
        assert len(result) == 6

    def test_non_string_returned_unchanged(self):
        assert truncate_value(42, 5, "...") == 42
        assert truncate_value(None, 5, "...") is None
        assert truncate_value([1, 2], 5, "...") == [1, 2]

    def test_custom_placeholder(self):
        result = truncate_value("abcdefgh", 5, "~")
        assert result == "abcd~"

    def test_max_length_zero_yields_placeholder_only(self):
        result = truncate_value("hello", 3, "...")
        assert result == "..."


# ---------------------------------------------------------------------------
# truncate_entry
# ---------------------------------------------------------------------------

class TestTruncateEntry:
    def test_long_message_truncated(self):
        e = _entry(message="x" * 300)
        result = truncate_entry(e, max_length=10)
        assert len(result["message"]) == 10

    def test_short_fields_unchanged(self):
        e = _entry(message="short")
        result = truncate_entry(e, max_length=50)
        assert result["message"] == "short"

    def test_specific_fields_only(self):
        e = _entry(message="x" * 100, level="y" * 100)
        result = truncate_entry(e, fields=["message"], max_length=20)
        assert len(result["message"]) == 20
        assert result["level"] == "y" * 100  # untouched

    def test_non_string_field_untouched(self):
        e = {"count": 9999, "message": "ok"}
        result = truncate_entry(e, max_length=5)
        assert result["count"] == 9999

    def test_returns_new_dict(self):
        e = _entry()
        result = truncate_entry(e)
        assert result is not e

    def test_negative_max_length_raises(self):
        with pytest.raises(ValueError):
            truncate_entry(_entry(), max_length=-1)

    def test_empty_entry_returns_empty(self):
        assert truncate_entry({}) == {}


# ---------------------------------------------------------------------------
# truncate_entries
# ---------------------------------------------------------------------------

class TestTruncateEntries:
    def test_yields_all_entries(self):
        entries = [_entry(message="a" * 300) for _ in range(5)]
        results = list(truncate_entries(entries, max_length=20))
        assert len(results) == 5

    def test_all_messages_truncated(self):
        entries = [_entry(message="z" * 200)]
        result = list(truncate_entries(entries, max_length=50))[0]
        assert len(result["message"]) == 50

    def test_empty_iterable_yields_nothing(self):
        assert list(truncate_entries([], max_length=10)) == []

    def test_generator_is_lazy(self):
        def _gen():
            for i in range(3):
                yield _entry(message="m" * 300)

        gen = truncate_entries(_gen(), max_length=10)
        first = next(gen)
        assert len(first["message"]) == 10
