"""Tests for logslice.query."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from logslice.query import Query, _matches, run_indexed_query, run_query


def _entry(**kwargs: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {"level": "info", "service": "api", "message": "ok"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# _matches
# ---------------------------------------------------------------------------

class TestMatches:
    def test_empty_query_matches_all(self):
        assert _matches(_entry(), Query()) is True

    def test_filter_match(self):
        q = Query(filters={"level": "info"})
        assert _matches(_entry(level="info"), q) is True

    def test_filter_no_match(self):
        q = Query(filters={"level": "error"})
        assert _matches(_entry(level="info"), q) is False

    def test_exclude_match_filters_out(self):
        q = Query(excludes={"level": "info"})
        assert _matches(_entry(level="info"), q) is False

    def test_exclude_non_match_keeps_entry(self):
        q = Query(excludes={"level": "error"})
        assert _matches(_entry(level="info"), q) is True

    def test_multiple_filters_all_must_match(self):
        q = Query(filters={"level": "info", "service": "api"})
        assert _matches(_entry(level="info", service="api"), q) is True
        assert _matches(_entry(level="info", service="worker"), q) is False

    def test_missing_field_treated_as_empty_string(self):
        q = Query(filters={"level": ""})
        assert _matches({"message": "no level"}, q) is True


# ---------------------------------------------------------------------------
# run_query
# ---------------------------------------------------------------------------

class TestRunQuery:
    def test_returns_matching_entries(self):
        entries = [_entry(level="info"), _entry(level="error")]
        result = list(run_query(entries, Query(filters={"level": "info"})))
        assert len(result) == 1
        assert result[0]["level"] == "info"

    def test_limit_respected(self):
        entries = [_entry(level="info")] * 10
        result = list(run_query(entries, Query(filters={"level": "info"}, limit=3)))
        assert len(result) == 3

    def test_empty_entries_yields_nothing(self):
        assert list(run_query([], Query())) == []

    def test_no_match_yields_nothing(self):
        entries = [_entry(level="info")]
        result = list(run_query(entries, Query(filters={"level": "debug"})))
        assert result == []


# ---------------------------------------------------------------------------
# run_indexed_query
# ---------------------------------------------------------------------------

class TestRunIndexedQuery:
    def test_indexed_field_narrows_results(self):
        entries = [
            _entry(level="info", service="api"),
            _entry(level="error", service="worker"),
            _entry(level="info", service="worker"),
        ]
        q = Query(filters={"level": "info", "service": "api"})
        result = list(run_indexed_query(entries, q, index_field="level"))
        assert len(result) == 1
        assert result[0]["service"] == "api"

    def test_falls_back_to_linear_scan_when_field_not_in_filters(self):
        entries = [_entry(level="info"), _entry(level="error")]
        q = Query(filters={"level": "info"})
        result = list(run_indexed_query(entries, q, index_field="service"))
        assert len(result) == 1

    def test_limit_still_respected_with_index(self):
        entries = [_entry(level="info")] * 5
        q = Query(filters={"level": "info"}, limit=2)
        result = list(run_indexed_query(entries, q, index_field="level"))
        assert len(result) == 2
