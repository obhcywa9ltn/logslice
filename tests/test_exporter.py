"""Tests for logslice.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from logslice.exporter import (
    export_as_csv,
    export_as_ndjson,
    export_as_tsv,
    export_entries,
)


def _entry(**kwargs) -> dict:
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "hi"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# export_as_ndjson
# ---------------------------------------------------------------------------

class TestExportAsNdjson:
    def test_each_line_is_valid_json(self):
        lines = list(export_as_ndjson([_entry(), _entry(level="ERROR")]))
        assert len(lines) == 2
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_empty_yields_nothing(self):
        assert list(export_as_ndjson([])) == []

    def test_non_serialisable_uses_str_default(self):
        from datetime import datetime
        entry = {"ts": datetime(2024, 1, 1), "msg": "x"}
        line = next(export_as_ndjson([entry]))
        obj = json.loads(line)
        assert "ts" in obj


# ---------------------------------------------------------------------------
# export_as_csv
# ---------------------------------------------------------------------------

class TestExportAsCsv:
    def test_first_row_is_header(self):
        rows = list(export_as_csv([_entry()], fields=["timestamp", "level", "message"]))
        reader = csv.reader(io.StringIO("".join(rows)))
        header = next(reader)
        assert header == ["timestamp", "level", "message"]

    def test_data_row_count(self):
        entries = [_entry(), _entry(level="WARN")]
        rows = list(export_as_csv(entries, fields=["timestamp", "level", "message"]))
        all_rows = list(csv.reader(io.StringIO("".join(rows))))
        assert len(all_rows) == 3  # header + 2 data rows

    def test_missing_field_is_empty_string(self):
        entry = {"timestamp": "2024-01-01T00:00:00Z", "level": "DEBUG"}
        rows = "".join(export_as_csv([entry], fields=["timestamp", "level", "message"]))
        reader = list(csv.reader(io.StringIO(rows)))
        assert reader[1][2] == ""

    def test_empty_entries_yields_nothing(self):
        assert list(export_as_csv([])) == []

    def test_auto_detect_fields(self):
        rows = "".join(export_as_csv([_entry()]))
        header_line = rows.splitlines()[0]
        for field in ["timestamp", "level", "message"]:
            assert field in header_line


# ---------------------------------------------------------------------------
# export_as_tsv
# ---------------------------------------------------------------------------

class TestExportAsTsv:
    def test_delimiter_is_tab(self):
        rows = "".join(export_as_tsv([_entry()], fields=["timestamp", "level"]))
        assert "\t" in rows

    def test_empty_yields_nothing(self):
        assert list(export_as_tsv([])) == []


# ---------------------------------------------------------------------------
# export_entries dispatcher
# ---------------------------------------------------------------------------

class TestExportEntries:
    def test_ndjson_format(self):
        lines = list(export_entries([_entry()], fmt="ndjson"))
        assert json.loads(lines[0])["level"] == "INFO"

    def test_csv_format(self):
        output = "".join(export_entries([_entry()], fmt="csv", fields=["level"]))
        assert "level" in output

    def test_tsv_format(self):
        output = "".join(export_entries([_entry()], fmt="tsv", fields=["level"]))
        assert "\t" in output or "level" in output

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            list(export_entries([_entry()], fmt="xml"))  # type: ignore[arg-type]
