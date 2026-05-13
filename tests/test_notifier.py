"""Tests for logslice.notifier."""

from __future__ import annotations

import io
import json
from typing import List

from logslice.notifier import (
    collecting_notifier,
    console_notifier,
    json_notifier,
    multi_notifier,
)


def _entry(**kwargs) -> dict:
    return {"timestamp": "2024-01-01T00:00:00Z", "message": "test", **kwargs}


# ---------------------------------------------------------------------------
# console_notifier
# ---------------------------------------------------------------------------

class TestConsoleNotifier:
    def test_output_contains_rule_name(self, capsys):
        handler = console_notifier()
        handler("my-rule", _entry())
        captured = capsys.readouterr()
        assert "my-rule" in captured.out

    def test_output_contains_message(self, capsys):
        handler = console_notifier()
        handler("r", _entry(message="something bad"))
        captured = capsys.readouterr()
        assert "something bad" in captured.out

    def test_custom_prefix(self, capsys):
        handler = console_notifier(prefix="!!")
        handler("r", _entry())
        captured = capsys.readouterr()
        assert captured.out.startswith("!!")


# ---------------------------------------------------------------------------
# collecting_notifier
# ---------------------------------------------------------------------------

class TestCollectingNotifier:
    def test_appends_record(self):
        store: List[dict] = []
        handler = collecting_notifier(store)
        handler("rule-a", _entry(level="ERROR"))
        assert len(store) == 1
        assert store[0]["rule"] == "rule-a"

    def test_entry_preserved(self):
        store: List[dict] = []
        handler = collecting_notifier(store)
        e = _entry(level="WARN")
        handler("r", e)
        assert store[0]["entry"] is e

    def test_multiple_alerts_accumulate(self):
        store: List[dict] = []
        handler = collecting_notifier(store)
        handler("r1", _entry())
        handler("r2", _entry())
        assert len(store) == 2


# ---------------------------------------------------------------------------
# json_notifier
# ---------------------------------------------------------------------------

class TestJsonNotifier:
    def test_writes_valid_json_line(self):
        buf = io.StringIO()
        handler = json_notifier(buf)
        handler("my-rule", _entry(level="ERROR"))
        line = buf.getvalue().strip()
        record = json.loads(line)
        assert record["rule"] == "my-rule"
        assert record["entry"]["level"] == "ERROR"

    def test_each_alert_on_own_line(self):
        buf = io.StringIO()
        handler = json_notifier(buf)
        handler("r", _entry())
        handler("r", _entry())
        lines = [l for l in buf.getvalue().splitlines() if l.strip()]
        assert len(lines) == 2

    def test_empty_entry_still_writes(self):
        buf = io.StringIO()
        handler = json_notifier(buf)
        handler("r", {})
        record = json.loads(buf.getvalue().strip())
        assert record["entry"] == {}


# ---------------------------------------------------------------------------
# multi_notifier
# ---------------------------------------------------------------------------

class TestMultiNotifier:
    def test_all_handlers_called(self):
        calls: List[str] = []
        h1 = lambda name, _: calls.append(f"h1:{name}")
        h2 = lambda name, _: calls.append(f"h2:{name}")
        handler = multi_notifier(h1, h2)
        handler("rule", _entry())
        assert calls == ["h1:rule", "h2:rule"]

    def test_zero_handlers_is_noop(self):
        handler = multi_notifier()
        handler("rule", _entry())  # must not raise

    def test_single_handler_delegates(self):
        store: List[dict] = []
        inner = collecting_notifier(store)
        handler = multi_notifier(inner)
        handler("r", _entry())
        assert len(store) == 1
