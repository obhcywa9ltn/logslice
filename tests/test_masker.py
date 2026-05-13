"""Tests for logslice.masker."""

from __future__ import annotations

import pytest

from logslice.masker import _mask_string, mask_entry, mask_entries


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "hello"}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# _mask_string
# ---------------------------------------------------------------------------

class TestMaskString:
    def test_long_string_masked_from_start(self):
        assert _mask_string("abcdefgh", visible=4) == "abcd****"

    def test_short_string_fully_masked(self):
        assert _mask_string("abc", visible=4) == "***"

    def test_exact_length_fully_masked(self):
        assert _mask_string("abcd", visible=4) == "****"

    def test_show_end_keeps_last_chars(self):
        assert _mask_string("abcdefgh", visible=4, show_end=True) == "****efgh"

    def test_custom_mask_char(self):
        result = _mask_string("abcdefgh", visible=2, mask_char="#")
        assert result == "ab######"

    def test_single_char_masked(self):
        assert _mask_string("x", visible=4) == "*"


# ---------------------------------------------------------------------------
# mask_entry
# ---------------------------------------------------------------------------

class TestMaskEntry:
    def test_default_sensitive_fields_masked(self):
        entry = _entry(password="supersecret")
        result = mask_entry(entry)
        assert result["password"] != "supersecret"
        assert "supe" in result["password"]

    def test_non_sensitive_fields_preserved(self):
        entry = _entry(user="alice", password="s3cr3t")
        result = mask_entry(entry)
        assert result["user"] == "alice"

    def test_explicit_fields_masked(self):
        entry = _entry(email="user@example.com")
        result = mask_entry(entry, fields=["email"])
        assert result["email"].startswith("user")
        assert "@" not in result["email"][4:]

    def test_missing_field_ignored(self):
        entry = _entry()
        result = mask_entry(entry, fields=["nonexistent"])
        assert result == entry

    def test_non_string_value_not_masked(self):
        entry = _entry(token=12345)
        result = mask_entry(entry)
        assert result["token"] == 12345

    def test_original_entry_not_mutated(self):
        entry = _entry(password="hunter2")
        original_pw = entry["password"]
        mask_entry(entry)
        assert entry["password"] == original_pw

    def test_pattern_skips_non_matching_values(self):
        entry = _entry(token="public-info")
        result = mask_entry(entry, fields=["token"], pattern=r"^sk-")
        assert result["token"] == "public-info"

    def test_pattern_masks_matching_values(self):
        entry = _entry(token="sk-abcdefgh")
        result = mask_entry(entry, fields=["token"], pattern=r"^sk-")
        assert result["token"] != "sk-abcdefgh"


# ---------------------------------------------------------------------------
# mask_entries
# ---------------------------------------------------------------------------

class TestMaskEntries:
    def test_yields_same_count(self):
        entries = [_entry(password=f"pw{i}") for i in range(5)]
        result = list(mask_entries(entries))
        assert len(result) == 5

    def test_all_entries_masked(self):
        entries = [_entry(password="secret") for _ in range(3)]
        for result in mask_entries(entries):
            assert result["password"] != "secret"

    def test_empty_iterable_yields_nothing(self):
        assert list(mask_entries([])) == []
