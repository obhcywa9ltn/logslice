"""Tests for logslice.router."""

from __future__ import annotations

from typing import Iterable

import pytest

from logslice.router import Router, build_router


def _entry(level: str = "info", **kwargs) -> dict:
    return {"level": level, "message": "msg", **kwargs}


def _collecting_sink(store: list):
    """Return a sink that appends entries to *store* and returns the count."""
    def sink(entries: Iterable[dict]) -> int:
        items = list(entries)
        store.extend(items)
        return len(items)
    return sink


class TestRouter:
    def test_entry_routed_to_correct_sink(self):
        errors: list = []
        others: list = []
        rules = [
            ("errors", lambda e: e.get("level") == "error", _collecting_sink(errors)),
            ("others", lambda e: True, _collecting_sink(others)),
        ]
        router = Router(rules)
        router.route([_entry("error"), _entry("info")])
        assert len(errors) == 1
        assert len(others) == 1

    def test_stop_on_first_match_prevents_double_routing(self):
        bucket_a: list = []
        bucket_b: list = []
        rules = [
            ("a", lambda e: True, _collecting_sink(bucket_a)),
            ("b", lambda e: True, _collecting_sink(bucket_b)),
        ]
        router = Router(rules, stop_on_first_match=True)
        router.route([_entry()])
        assert len(bucket_a) == 1
        assert len(bucket_b) == 0

    def test_multi_match_when_stop_on_first_match_false(self):
        bucket_a: list = []
        bucket_b: list = []
        rules = [
            ("a", lambda e: True, _collecting_sink(bucket_a)),
            ("b", lambda e: True, _collecting_sink(bucket_b)),
        ]
        router = Router(rules, stop_on_first_match=False)
        router.route([_entry()])
        assert len(bucket_a) == 1
        assert len(bucket_b) == 1

    def test_unmatched_entry_goes_to_default_sink(self):
        default_buf: list = []
        rules = [
            ("errors", lambda e: e.get("level") == "error", _collecting_sink([])),
        ]
        router = Router(rules, default_sink=_collecting_sink(default_buf))
        router.route([_entry("info")])
        assert len(default_buf) == 1

    def test_unmatched_entry_dropped_without_default_sink(self):
        buf: list = []
        rules = [("errors", lambda e: e.get("level") == "error", _collecting_sink(buf))]
        router = Router(rules)
        counts = router.route([_entry("info")])
        assert counts["errors"] == 0
        assert "__default__" not in counts

    def test_counts_returned_per_sink(self):
        rules = [
            ("all", lambda e: True, _collecting_sink([])),
        ]
        router = Router(rules)
        counts = router.route([_entry(), _entry(), _entry()])
        assert counts["all"] == 3

    def test_empty_entries_returns_zero_counts(self):
        rules = [("all", lambda e: True, _collecting_sink([]))]
        router = Router(rules)
        counts = router.route([])
        assert counts["all"] == 0


class TestBuildRouter:
    def test_returns_router_instance(self):
        router = build_router([])
        assert isinstance(router, Router)

    def test_routes_correctly_via_factory(self):
        buf: list = []
        rules = [("all", lambda e: True, _collecting_sink(buf))]
        router = build_router(rules)
        router.route([_entry()])
        assert len(buf) == 1
