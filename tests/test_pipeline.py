"""Tests for logslice.pipeline.build_pipeline."""

from datetime import datetime, timezone
import json

import pytest

from logslice.pipeline import build_pipeline


def _ts(hour: int) -> str:
    return f"2024-06-01T{hour:02d}:00:00+00:00"


def _entry(message: str, level: str = "INFO", hour: int = 12, **extra):
    e = {"timestamp": _ts(hour), "level": level, "message": message}
    e.update(extra)
    return e


def _dt(hour: int) -> datetime:
    return datetime(2024, 6, 1, hour, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Basic pass-through
# ---------------------------------------------------------------------------

def test_empty_entries_yields_nothing():
    results = list(build_pipeline([]))
    assert results == []


def test_passthrough_yields_all_entries():
    entries = [_entry("a"), _entry("b")]
    results = list(build_pipeline(entries))
    assert len(results) == 2


def test_output_is_valid_json_by_default():
    entries = [_entry("hello")]
    line = list(build_pipeline(entries))[0]
    parsed = json.loads(line)
    assert parsed["message"] == "hello"


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_time_range_filters_entries():
    entries = [_entry("early", hour=8), _entry("mid", hour=12), _entry("late", hour=20)]
    results = list(build_pipeline(entries, start=_dt(10), end=_dt(15)))
    assert len(results) == 1
    assert json.loads(results[0])["message"] == "mid"


def test_field_pattern_filters_entries():
    entries = [_entry("ok", level="INFO"), _entry("bad", level="ERROR")]
    results = list(build_pipeline(entries, patterns=[("level", "INFO")]))
    assert len(results) == 1
    assert json.loads(results[0])["level"] == "INFO"


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------

def test_transforms_applied_to_field():
    entries = [_entry("hello", level="info")]
    results = list(build_pipeline(entries, transforms={"level": str.upper}))
    assert json.loads(results[0])["level"] == "INFO"


# ---------------------------------------------------------------------------
# Redaction
# ---------------------------------------------------------------------------

def test_redaction_removes_sensitive_fields():
    entries = [_entry("login", password="secret")]
    results = list(build_pipeline(entries, redact=True))
    parsed = json.loads(results[0])
    assert parsed.get("password") == "[REDACTED]"


def test_no_redaction_by_default():
    entries = [_entry("login", password="secret")]
    results = list(build_pipeline(entries, redact=False))
    parsed = json.loads(results[0])
    assert parsed["password"] == "secret"


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def test_deduplication_removes_duplicates():
    entry = _entry("dup msg")
    entries = [entry, dict(entry), dict(entry)]
    results = list(build_pipeline(entries, deduplicate=True))
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def test_compact_format_no_newlines_inside_entry():
    entries = [_entry("compact test")]
    results = list(build_pipeline(entries, fmt="compact"))
    assert "\n" not in results[0]


def test_pretty_format_contains_field_labels():
    entries = [_entry("pretty test")]
    results = list(build_pipeline(entries, fmt="pretty"))
    assert "message" in results[0].lower() or "pretty test" in results[0]
