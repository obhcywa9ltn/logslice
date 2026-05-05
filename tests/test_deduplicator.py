"""Tests for logslice.deduplicator."""

import pytest
from logslice.deduplicator import (
    _entry_fingerprint,
    deduplicate_entries,
    count_duplicates,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(msg: str, level: str = "INFO", ts: str = "2024-01-01T00:00:00Z") -> dict:
    return {"timestamp": ts, "level": level, "message": msg}


# ---------------------------------------------------------------------------
# _entry_fingerprint
# ---------------------------------------------------------------------------

class TestEntryFingerprint:
    def test_same_entry_same_fingerprint(self):
        e = _entry("hello")
        assert _entry_fingerprint(e) == _entry_fingerprint(e)

    def test_different_messages_different_fingerprints(self):
        assert _entry_fingerprint(_entry("a")) != _entry_fingerprint(_entry("b"))

    def test_timestamp_excluded_by_default(self):
        e1 = _entry("same", ts="2024-01-01T00:00:00Z")
        e2 = _entry("same", ts="2024-06-01T12:00:00Z")
        assert _entry_fingerprint(e1) == _entry_fingerprint(e2)

    def test_fields_subset_used_when_provided(self):
        e1 = {"timestamp": "t1", "level": "INFO", "message": "x", "host": "a"}
        e2 = {"timestamp": "t2", "level": "INFO", "message": "x", "host": "b"}
        # With only 'level' and 'message', both look the same
        assert _entry_fingerprint(e1, fields=["level", "message"]) == \
               _entry_fingerprint(e2, fields=["level", "message"])
        # With 'host' included they differ
        assert _entry_fingerprint(e1, fields=["message", "host"]) != \
               _entry_fingerprint(e2, fields=["message", "host"])

    def test_missing_fields_ignored_gracefully(self):
        e = _entry("hi")
        # 'host' is not present; should not raise
        fp = _entry_fingerprint(e, fields=["level", "host"])
        assert isinstance(fp, str) and len(fp) == 64


# ---------------------------------------------------------------------------
# deduplicate_entries
# ---------------------------------------------------------------------------

class TestDeduplicateEntries:
    def test_no_duplicates_returns_all(self):
        entries = [_entry("a"), _entry("b"), _entry("c")]
        result = list(deduplicate_entries(entries))
        assert len(result) == 3

    def test_duplicates_removed_keep_first(self):
        entries = [_entry("a"), _entry("b"), _entry("a")]
        result = list(deduplicate_entries(entries, keep_first=True))
        assert len(result) == 2
        assert result[0]["message"] == "a"
        assert result[1]["message"] == "b"

    def test_empty_input_yields_nothing(self):
        assert list(deduplicate_entries([])) == []

    def test_all_duplicates_yields_one(self):
        entries = [_entry("same")] * 5
        result = list(deduplicate_entries(entries))
        assert len(result) == 1

    def test_field_subset_deduplication(self):
        e1 = {"timestamp": "t1", "level": "INFO", "message": "x", "host": "a"}
        e2 = {"timestamp": "t2", "level": "INFO", "message": "x", "host": "b"}
        # Deduplicate on message only — both collapse to one
        result = list(deduplicate_entries([e1, e2], fields=["message"]))
        assert len(result) == 1

    def test_is_lazy_generator(self):
        import types
        entries = [_entry("a")]
        result = deduplicate_entries(entries)
        assert isinstance(result, types.GeneratorType)


# ---------------------------------------------------------------------------
# count_duplicates
# ---------------------------------------------------------------------------

class TestCountDuplicates:
    def test_no_duplicates_returns_zero(self):
        entries = [_entry("a"), _entry("b")]
        assert count_duplicates(entries) == 0

    def test_counts_correctly(self):
        entries = [_entry("a"), _entry("a"), _entry("b"), _entry("a")]
        assert count_duplicates(entries) == 2

    def test_empty_input_returns_zero(self):
        assert count_duplicates([]) == 0

    def test_with_field_subset(self):
        e1 = {"timestamp": "t1", "level": "INFO", "message": "x", "host": "a"}
        e2 = {"timestamp": "t2", "level": "INFO", "message": "x", "host": "b"}
        # On message alone both are duplicates → 1 duplicate
        assert count_duplicates([e1, e2], fields=["message"]) == 1
