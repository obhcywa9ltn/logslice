"""Tests for logslice.transformer."""

import pytest
from logslice.transformer import (
    transform_entry,
    rename_fields,
    drop_fields,
    add_fields,
    transform_entries,
)


def _entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# transform_entry
# ---------------------------------------------------------------------------

class TestTransformEntry:
    def test_applies_transform_to_existing_field(self):
        entry = _entry(level="info")
        result = transform_entry(entry, {"level": str.upper})
        assert result["level"] == "INFO"

    def test_other_fields_unchanged(self):
        entry = _entry(count=3)
        result = transform_entry(entry, {"count": lambda x: x * 2})
        assert result["message"] == "hello"
        assert result["count"] == 6

    def test_missing_field_skipped_by_default(self):
        entry = _entry()
        result = transform_entry(entry, {"nonexistent": str.upper})
        assert "nonexistent" not in result

    def test_missing_field_raises_when_skip_missing_false(self):
        entry = _entry()
        with pytest.raises(KeyError, match="nonexistent"):
            transform_entry(entry, {"nonexistent": str.upper}, skip_missing=False)

    def test_returns_new_dict(self):
        entry = _entry()
        result = transform_entry(entry, {})
        assert result is not entry

    def test_multiple_transforms_applied(self):
        entry = _entry(level="info", message="hello")
        result = transform_entry(entry, {"level": str.upper, "message": str.title})
        assert result["level"] == "INFO"
        assert result["message"] == "Hello"


# ---------------------------------------------------------------------------
# rename_fields
# ---------------------------------------------------------------------------

class TestRenameFields:
    def test_renames_existing_field(self):
        entry = _entry()
        result = rename_fields(entry, {"message": "msg"})
        assert "msg" in result
        assert "message" not in result

    def test_unrenamed_fields_preserved(self):
        entry = _entry()
        result = rename_fields(entry, {"level": "severity"})
        assert result["timestamp"] == entry["timestamp"]

    def test_rename_nonexistent_field_is_noop(self):
        entry = _entry()
        result = rename_fields(entry, {"ghost": "spirit"})
        assert result == entry


# ---------------------------------------------------------------------------
# drop_fields
# ---------------------------------------------------------------------------

class TestDropFields:
    def test_drops_specified_field(self):
        entry = _entry()
        result = drop_fields(entry, ["level"])
        assert "level" not in result

    def test_other_fields_retained(self):
        entry = _entry()
        result = drop_fields(entry, ["level"])
        assert "message" in result
        assert "timestamp" in result

    def test_drop_nonexistent_field_is_safe(self):
        entry = _entry()
        result = drop_fields(entry, ["ghost"])
        assert result == entry

    def test_drop_multiple_fields(self):
        entry = _entry()
        result = drop_fields(entry, ["level", "message"])
        assert "level" not in result
        assert "message" not in result


# ---------------------------------------------------------------------------
# add_fields
# ---------------------------------------------------------------------------

class TestAddFields:
    def test_adds_new_field(self):
        entry = _entry()
        result = add_fields(entry, {"env": "prod"})
        assert result["env"] == "prod"

    def test_does_not_overwrite_by_default(self):
        entry = _entry(level="INFO")
        result = add_fields(entry, {"level": "DEBUG"})
        assert result["level"] == "INFO"

    def test_overwrites_when_flag_set(self):
        entry = _entry(level="INFO")
        result = add_fields(entry, {"level": "DEBUG"}, overwrite=True)
        assert result["level"] == "DEBUG"


# ---------------------------------------------------------------------------
# transform_entries
# ---------------------------------------------------------------------------

def test_transform_entries_yields_transformed():
    entries = [_entry(level="debug"), _entry(level="info")]
    results = list(transform_entries(entries, {"level": str.upper}))
    assert results[0]["level"] == "DEBUG"
    assert results[1]["level"] == "INFO"


def test_transform_entries_empty_input():
    results = list(transform_entries([], {"level": str.upper}))
    assert results == []
