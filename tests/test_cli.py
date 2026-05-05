"""Tests for logslice.cli module."""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.cli import build_parser, main, parse_datetime, parse_pattern


LOG_LINES = [
    '{"timestamp": "2024-01-15T10:00:00+00:00", "level": "INFO", "message": "start"}',
    '{"timestamp": "2024-01-15T11:00:00+00:00", "level": "ERROR", "message": "fail"}',
    '{"timestamp": "2024-01-15T12:00:00+00:00", "level": "INFO", "message": "end"}',
]


class TestParseDatetime:
    def test_valid_datetime(self):
        dt = parse_datetime("2024-01-15T10:00:00")
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.hour == 10

    def test_invalid_datetime_raises(self):
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            parse_datetime("not-a-date")


class TestParsePattern:
    def test_valid_pattern(self):
        assert parse_pattern("level=ERROR") == ("level", "ERROR")

    def test_pattern_with_regex(self):
        assert parse_pattern("message=disk.*full") == ("message", "disk.*full")

    def test_missing_equals_raises(self):
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            parse_pattern("levelERROR")


class TestBuildParser:
    def test_defaults(self):
        args = build_parser().parse_args([])
        assert args.file == "-"
        assert args.start is None
        assert args.end is None
        assert args.patterns is None

    def test_file_argument(self):
        args = build_parser().parse_args(["mylog.json"])
        assert args.file == "mylog.json"

    def test_multiple_match_patterns(self):
        args = build_parser().parse_args(["--match", "level=ERROR", "--match", "host=web1"])
        assert len(args.patterns) == 2


class TestMain:
    def _run(self, argv, stdin_content=""):
        captured = []
        with patch("sys.stdin", StringIO(stdin_content)):
            with patch("builtins.print", side_effect=lambda *a, **kw: captured.append(a[0])):
                exit_code = main(argv)
        return exit_code, captured

    def test_reads_from_stdin(self):
        content = "\n".join(LOG_LINES)
        code, output = self._run([], stdin_content=content)
        assert code == 0
        assert len(output) == 3

    def test_filter_by_level(self):
        content = "\n".join(LOG_LINES)
        code, output = self._run(["--match", "level=ERROR"], stdin_content=content)
        assert code == 0
        assert len(output) == 1
        assert json.loads(output[0])["level"] == "ERROR"

    def test_missing_file_returns_error(self):
        code, _ = self._run(["nonexistent_file_xyz.log"])
        assert code == 1
