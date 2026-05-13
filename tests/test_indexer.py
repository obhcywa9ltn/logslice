"""Tests for logslice.indexer."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from logslice.indexer import (
    build_index,
    index_keys,
    lookup,
    lookup_many,
    reindex,
)


def _entry(level: str = "info", service: str = "api", msg: str = "ok") -> Dict[str, Any]:
    return {"level": level, "service": service, "message": msg}


# ---------------------------------------------------------------------------
# build_index
# ---------------------------------------------------------------------------

class TestBuildIndex:
    def test_groups_by_field(self):
        entries = [_entry("info"), _entry("error"), _entry("info")]
        idx = build_index(entries, "level")
        assert len(idx["info"]) == 2
        assert len(idx["error"]) == 1

    def test_missing_field_uses_empty_string(self):
        entries = [{"message": "no level"}]
        idx = build_index(entries, "level")
        assert "" in idx
        assert idx[""][0]["message"] == "no level"

    def test_empty_entries_returns_empty_dict(self):
        assert build_index([], "level") == {}

    def test_preserves_entry_identity(self):
        e = _entry()
        idx = build_index([e], "level")
        assert idx["info"][0] is e


# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------

class TestLookup:
    def test_returns_matching_entries(self):
        entries = [_entry("info"), _entry("error")]
        idx = build_index(entries, "level")
        result = lookup(idx, "info")
        assert len(result) == 1
        assert result[0]["level"] == "info"

    def test_missing_value_returns_empty_list(self):
        idx = build_index([_entry("info")], "level")
        assert lookup(idx, "debug") == []

    def test_numeric_value_coerced_to_string(self):
        entries = [{"code": 200, "msg": "ok"}]
        idx = build_index(entries, "code")
        assert lookup(idx, 200) == entries


# ---------------------------------------------------------------------------
# lookup_many
# ---------------------------------------------------------------------------

class TestLookupMany:
    def test_yields_entries_for_all_values(self):
        entries = [_entry("info"), _entry("error"), _entry("warn")]
        idx = build_index(entries, "level")
        result = list(lookup_many(idx, ["info", "warn"]))
        levels = [e["level"] for e in result]
        assert "info" in levels
        assert "warn" in levels
        assert "error" not in levels

    def test_empty_values_yields_nothing(self):
        idx = build_index([_entry()], "level")
        assert list(lookup_many(idx, [])) == []


# ---------------------------------------------------------------------------
# index_keys
# ---------------------------------------------------------------------------

def test_index_keys_sorted():
    entries = [_entry("info"), _entry("error"), _entry("warn")]
    idx = build_index(entries, "level")
    assert index_keys(idx) == ["error", "info", "warn"]


# ---------------------------------------------------------------------------
# reindex
# ---------------------------------------------------------------------------

def test_reindex_by_different_field():
    entries = [
        _entry("info", service="api"),
        _entry("error", service="worker"),
        _entry("info", service="api"),
    ]
    idx = build_index(entries, "level")
    new_idx = reindex(idx, "service")
    assert len(new_idx["api"]) == 2
    assert len(new_idx["worker"]) == 1
