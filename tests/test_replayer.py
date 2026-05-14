"""Tests for logslice.replayer."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import pytest

from logslice.replayer import replay_entries, replay_with_wall_clock

LogEntry = dict[str, Any]


def _entry(ts: str, message: str = "msg") -> LogEntry:
    return {"timestamp": ts, "message": message}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAME_TS = "2024-01-01T12:00:00+00:00"
TS_PLUS_1 = "2024-01-01T12:00:01+00:00"
TS_PLUS_2 = "2024-01-01T12:00:02+00:00"


# ---------------------------------------------------------------------------
# replay_entries – basic behaviour
# ---------------------------------------------------------------------------

class TestReplayEntries:
    def test_yields_all_entries(self):
        entries = [_entry(SAME_TS, "a"), _entry(TS_PLUS_1, "b")]
        result = list(replay_entries(entries, speed=1000.0))
        assert len(result) == 2

    def test_entries_unchanged(self):
        src = [_entry(SAME_TS, "hello")]
        (out,) = list(replay_entries(src, speed=1000.0))
        assert out == src[0]

    def test_empty_input_yields_nothing(self):
        assert list(replay_entries([], speed=1.0)) == []

    def test_invalid_speed_raises(self):
        with pytest.raises(ValueError, match="speed"):
            list(replay_entries([_entry(SAME_TS)], speed=0))

    def test_negative_speed_raises(self):
        with pytest.raises(ValueError, match="speed"):
            list(replay_entries([_entry(SAME_TS)], speed=-1.0))

    def test_negative_max_gap_raises(self):
        with pytest.raises(ValueError, match="max_gap"):
            list(replay_entries([_entry(SAME_TS)], speed=1.0, max_gap=-0.1))

    def test_no_timestamp_field_skips_sleep(self):
        """Entries without timestamps are passed through without delay."""
        entries = [{"message": "no ts"}, {"message": "also no ts"}]
        result = list(replay_entries(entries, speed=1.0))
        assert result == entries

    def test_max_gap_caps_delay(self):
        """With a very high speed and tiny max_gap the call should be fast."""
        entries = [_entry(SAME_TS), _entry(TS_PLUS_1), _entry(TS_PLUS_2)]
        start = time.monotonic()
        list(replay_entries(entries, speed=1.0, max_gap=0.0))
        elapsed = time.monotonic() - start
        assert elapsed < 0.5

    def test_high_speed_completes_quickly(self):
        entries = [_entry(SAME_TS), _entry(TS_PLUS_1), _entry(TS_PLUS_2)]
        start = time.monotonic()
        list(replay_entries(entries, speed=10_000.0))
        elapsed = time.monotonic() - start
        assert elapsed < 0.5


# ---------------------------------------------------------------------------
# replay_with_wall_clock
# ---------------------------------------------------------------------------

class TestReplayWithWallClock:
    def test_yields_pairs(self):
        entries = [_entry(SAME_TS, "a"), _entry(TS_PLUS_1, "b")]
        pairs = list(replay_with_wall_clock(entries, speed=10_000.0))
        assert len(pairs) == 2
        for wall_time, entry in pairs:
            assert isinstance(wall_time, datetime)
            assert wall_time.tzinfo is not None

    def test_wall_times_are_non_decreasing(self):
        entries = [_entry(SAME_TS), _entry(TS_PLUS_1), _entry(TS_PLUS_2)]
        pairs = list(replay_with_wall_clock(entries, speed=10_000.0))
        times = [wt for wt, _ in pairs]
        assert times == sorted(times)

    def test_entry_passthrough_unchanged(self):
        src = _entry(SAME_TS, "check")
        ((_wt, out),) = list(replay_with_wall_clock([src], speed=1.0))
        assert out == src
