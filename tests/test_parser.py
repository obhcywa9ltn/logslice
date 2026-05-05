"""Tests for logslice.parser module."""

import pytest
from datetime import datetime
from logslice.parser import parse_log_line, parse_timestamp, iter_log_entries


class TestParseLogLine:
    def test_valid_json(self):
        result = parse_log_line('{"level": "info", "message": "ok"}')
        assert result == {"level": "info", "message": "ok"}

    def test_invalid_json_returns_none(self):
        assert parse_log_line("not json") is None

    def test_empty_line_returns_none(self):
        assert parse_log_line("") is None
        assert parse_log_line("   ") is None

    def test_whitespace_stripped(self):
        result = parse_log_line('  {"key": "value"}  ')
        assert result == {"key": "value"}


class TestParseTimestamp:
    def test_iso_format(self):
        dt = parse_timestamp("2024-01-15T10:30:00")
        assert dt == datetime(2024, 1, 15, 10, 30, 0)

    def test_iso_format_with_microseconds(self):
        dt = parse_timestamp("2024-01-15T10:30:00.123456")
        assert dt == datetime(2024, 1, 15, 10, 30, 0, 123456)

    def test_space_separated_format(self):
        dt = parse_timestamp("2024-01-15 10:30:00")
        assert dt == datetime(2024, 1, 15, 10, 30, 0)

    def test_invalid_returns_none(self):
        assert parse_timestamp("not-a-date") is None
        assert parse_timestamp("") is None


class TestIterLogEntries:
    SAMPLE_LINES = [
        '{"timestamp": "2024-01-15T08:00:00", "level": "info", "msg": "start"}',
        '{"timestamp": "2024-01-15T09:00:00", "level": "warn", "msg": "slow"}',
        '{"timestamp": "2024-01-15T10:00:00", "level": "error", "msg": "fail"}',
        "invalid line",
        '{"timestamp": "2024-01-15T11:00:00", "level": "info", "msg": "end"}',
    ]

    def test_no_filter_returns_all_valid(self):
        entries = list(iter_log_entries(self.SAMPLE_LINES))
        assert len(entries) == 4

    def test_start_filter(self):
        start = datetime(2024, 1, 15, 9, 0, 0)
        entries = list(iter_log_entries(self.SAMPLE_LINES, start=start))
        assert len(entries) == 3
        assert entries[0]["msg"] == "slow"

    def test_end_filter(self):
        end = datetime(2024, 1, 15, 9, 0, 0)
        entries = list(iter_log_entries(self.SAMPLE_LINES, end=end))
        assert len(entries) == 2
        assert entries[-1]["msg"] == "slow"

    def test_start_and_end_filter(self):
        start = datetime(2024, 1, 15, 9, 0, 0)
        end = datetime(2024, 1, 15, 10, 0, 0)
        entries = list(iter_log_entries(self.SAMPLE_LINES, start=start, end=end))
        assert len(entries) == 2

    def test_custom_timestamp_field(self):
        lines = ['{"ts": "2024-01-15T09:00:00", "msg": "hello"}']
        entries = list(iter_log_entries(lines, timestamp_field="ts"))
        assert len(entries) == 1

    def test_missing_timestamp_field_skipped_when_filtering(self):
        lines = ['{"msg": "no timestamp"}']
        start = datetime(2024, 1, 1)
        entries = list(iter_log_entries(lines, start=start))
        assert len(entries) == 0
