"""Tests for logslice.summarizer."""

from __future__ import annotations

from typing import Dict, Any

import pytest

from logslice.summarizer import format_summary, summarize_entries


def _entry(
    message: str = "hello",
    level: str = "INFO",
    timestamp: str = "2024-01-01T00:00:00Z",
    **extra: Any,
) -> Dict[str, Any]:
    return {"message": message, "level": level, "timestamp": timestamp, **extra}


# ---------------------------------------------------------------------------
# summarize_entries
# ---------------------------------------------------------------------------


class TestSummarizeEntries:
    def test_empty_input_returns_zero_total(self):
        result = summarize_entries([])
        assert result["total"] == 0

    def test_total_count(self):
        entries = [_entry() for _ in range(7)]
        result = summarize_entries(entries)
        assert result["total"] == 7

    def test_level_counts(self):
        entries = [
            _entry(level="INFO"),
            _entry(level="INFO"),
            _entry(level="ERROR"),
        ]
        result = summarize_entries(entries)
        assert result["by_level"]["INFO"] == 2
        assert result["by_level"]["ERROR"] == 1

    def test_missing_level_not_counted(self):
        entries = [{"message": "no level", "timestamp": "2024-01-01T00:00:00Z"}]
        result = summarize_entries(entries)
        assert result["by_level"] == {}

    def test_top_messages_most_common_first(self):
        entries = [
            _entry(message="a"),
            _entry(message="b"),
            _entry(message="b"),
            _entry(message="b"),
            _entry(message="a"),
        ]
        result = summarize_entries(entries, top_n=2)
        assert result["top_messages"][0] == ("b", 3)
        assert result["top_messages"][1] == ("a", 2)

    def test_top_n_limits_messages(self):
        entries = [_entry(message=str(i)) for i in range(10)]
        result = summarize_entries(entries, top_n=3)
        assert len(result["top_messages"]) == 3

    def test_earliest_and_latest(self):
        entries = [
            _entry(timestamp="2024-01-03T00:00:00Z"),
            _entry(timestamp="2024-01-01T00:00:00Z"),
            _entry(timestamp="2024-01-02T00:00:00Z"),
        ]
        result = summarize_entries(entries)
        assert result["earliest"] == "2024-01-01T00:00:00Z"
        assert result["latest"] == "2024-01-03T00:00:00Z"

    def test_empty_earliest_latest_are_none(self):
        result = summarize_entries([])
        assert result["earliest"] is None
        assert result["latest"] is None

    def test_custom_field_names(self):
        entries = [{"msg": "hi", "severity": "WARN", "ts": "2024-01-01T00:00:00Z"}]
        result = summarize_entries(
            entries,
            level_field="severity",
            message_field="msg",
            timestamp_field="ts",
        )
        assert result["total"] == 1
        assert result["by_level"]["WARN"] == 1


# ---------------------------------------------------------------------------
# format_summary
# ---------------------------------------------------------------------------


class TestFormatSummary:
    def _base_summary(self):
        return summarize_entries(
            [
                _entry(message="started", level="INFO", timestamp="2024-01-01T00:00:00Z"),
                _entry(message="failed", level="ERROR", timestamp="2024-01-02T00:00:00Z"),
                _entry(message="started", level="INFO", timestamp="2024-01-03T00:00:00Z"),
            ]
        )

    def test_returns_string(self):
        result = format_summary(self._base_summary())
        assert isinstance(result, str)

    def test_contains_total(self):
        result = format_summary(self._base_summary())
        assert "3" in result

    def test_contains_level(self):
        result = format_summary(self._base_summary())
        assert "ERROR" in result
        assert "INFO" in result

    def test_contains_top_message(self):
        result = format_summary(self._base_summary())
        assert "started" in result

    def test_long_message_truncated(self):
        long_msg = "x" * 80
        summary = summarize_entries([_entry(message=long_msg)])
        result = format_summary(summary)
        assert "..." in result

    def test_empty_summary_no_crash(self):
        summary = summarize_entries([])
        result = format_summary(summary)
        assert "0" in result
