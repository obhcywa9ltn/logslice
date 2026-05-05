"""Tests for logslice.redactor."""

from __future__ import annotations

import pytest

from logslice.redactor import (
    REDACT_PLACEHOLDER,
    redact_entries,
    redact_entry,
)


def _entry(**kwargs):
    base = {"timestamp": "2024-01-01T00:00:00Z", "level": "INFO", "message": "hello"}
    base.update(kwargs)
    return base


class TestRedactEntry:
    def test_default_sensitive_fields_are_redacted(self):
        entry = _entry(password="s3cr3t", token="abc123")
        result = redact_entry(entry)
        assert result["password"] == REDACT_PLACEHOLDER
        assert result["token"] == REDACT_PLACEHOLDER

    def test_non_sensitive_fields_are_preserved(self):
        entry = _entry(user="alice", request_id="xyz")
        result = redact_entry(entry)
        assert result["user"] == "alice"
        assert result["request_id"] == "xyz"

    def test_explicit_fields_are_redacted(self):
        entry = _entry(ssn="123-45-6789", name="Bob")
        result = redact_entry(entry, fields=["ssn"])
        assert result["ssn"] == REDACT_PLACEHOLDER
        assert result["name"] == "Bob"

    def test_field_matching_is_case_insensitive(self):
        entry = _entry(Password="hunter2")
        result = redact_entry(entry)
        assert result["Password"] == REDACT_PLACEHOLDER

    def test_pattern_matching_redacts_field(self):
        entry = _entry(user_secret_key="topsecret", message="ok")
        result = redact_entry(entry, patterns=[r"secret"])
        assert result["user_secret_key"] == REDACT_PLACEHOLDER
        assert result["message"] == "ok"

    def test_custom_placeholder(self):
        entry = _entry(password="oops")
        result = redact_entry(entry, placeholder="[hidden]")
        assert result["password"] == "[hidden]"

    def test_returns_new_dict_not_mutated(self):
        entry = _entry(password="original")
        result = redact_entry(entry)
        assert entry["password"] == "original"
        assert result is not entry

    def test_empty_entry_returns_empty(self):
        result = redact_entry({})
        assert result == {}

    def test_multiple_patterns_any_match_redacts(self):
        entry = _entry(auth_header="Bearer xyz", api_token="tok")
        result = redact_entry(entry, patterns=[r"^auth", r"token$"])
        assert result["auth_header"] == REDACT_PLACEHOLDER
        assert result["api_token"] == REDACT_PLACEHOLDER


class TestRedactEntries:
    def test_yields_all_entries(self):
        entries = [_entry(password="x"), _entry(token="y"), _entry(user="z")]
        results = list(redact_entries(entries))
        assert len(results) == 3

    def test_all_entries_have_passwords_redacted(self):
        entries = [_entry(password=f"pw{i}") for i in range(5)]
        for result in redact_entries(entries):
            assert result["password"] == REDACT_PLACEHOLDER

    def test_empty_iterable_yields_nothing(self):
        assert list(redact_entries([])) == []

    def test_custom_fields_propagated_to_all(self):
        entries = [_entry(ssn="111"), _entry(ssn="222")]
        results = list(redact_entries(entries, fields=["ssn"]))
        assert all(r["ssn"] == REDACT_PLACEHOLDER for r in results)
