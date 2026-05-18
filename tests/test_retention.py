"""Tests for logslice.retention."""

from __future__ import annotations

import gzip
import time
from pathlib import Path

import pytest

from logslice.retention import (
    apply_retention,
    list_archives,
    prune_by_age,
    prune_by_count,
)


def _make_archive(directory: Path, name: str) -> Path:
    p = directory / name
    with gzip.open(p, "wt") as fh:
        fh.write('{"ok": true}\n')
    return p


# ---------------------------------------------------------------------------
# list_archives
# ---------------------------------------------------------------------------

class TestListArchives:
    def test_returns_matching_files(self, tmp_path):
        _make_archive(tmp_path, "a.ndjson.gz")
        _make_archive(tmp_path, "b.ndjson.gz")
        files = list_archives(tmp_path)
        assert len(files) == 2

    def test_ignores_non_matching_files(self, tmp_path):
        (tmp_path / "notes.txt").write_text("hi")
        _make_archive(tmp_path, "log.ndjson.gz")
        files = list_archives(tmp_path)
        assert len(files) == 1

    def test_sorted_by_mtime_oldest_first(self, tmp_path):
        a = _make_archive(tmp_path, "first.ndjson.gz")
        time.sleep(0.05)
        b = _make_archive(tmp_path, "second.ndjson.gz")
        files = list_archives(tmp_path)
        assert files[0].name == "first.ndjson.gz"
        assert files[1].name == "second.ndjson.gz"

    def test_empty_directory_returns_empty(self, tmp_path):
        assert list_archives(tmp_path) == []


# ---------------------------------------------------------------------------
# prune_by_age
# ---------------------------------------------------------------------------

class TestPruneByAge:
    def test_negative_max_age_raises(self, tmp_path):
        with pytest.raises(ValueError):
            prune_by_age(tmp_path, max_age_days=-1)

    def test_dry_run_does_not_delete(self, tmp_path):
        p = _make_archive(tmp_path, "old.ndjson.gz")
        # Set mtime far in the past
        old_time = 0.0
        import os
        os.utime(p, (old_time, old_time))
        removed = prune_by_age(tmp_path, max_age_days=0, dry_run=True)
        assert p in removed
        assert p.exists()

    def test_deletes_old_files(self, tmp_path):
        p = _make_archive(tmp_path, "old.ndjson.gz")
        import os
        os.utime(p, (0.0, 0.0))
        removed = prune_by_age(tmp_path, max_age_days=1)
        assert p in removed
        assert not p.exists()

    def test_keeps_recent_files(self, tmp_path):
        p = _make_archive(tmp_path, "new.ndjson.gz")
        removed = prune_by_age(tmp_path, max_age_days=365)
        assert p not in removed
        assert p.exists()

    def test_returns_empty_when_nothing_to_prune(self, tmp_path):
        _make_archive(tmp_path, "recent.ndjson.gz")
        removed = prune_by_age(tmp_path, max_age_days=9999)
        assert removed == []


# ---------------------------------------------------------------------------
# prune_by_count
# ---------------------------------------------------------------------------

class TestPruneByCount:
    def test_negative_keep_raises(self, tmp_path):
        with pytest.raises(ValueError):
            prune_by_count(tmp_path, keep=-1)

    def test_keeps_n_most_recent(self, tmp_path):
        a = _make_archive(tmp_path, "a.ndjson.gz")
        time.sleep(0.05)
        b = _make_archive(tmp_path, "b.ndjson.gz")
        time.sleep(0.05)
        c = _make_archive(tmp_path, "c.ndjson.gz")
        prune_by_count(tmp_path, keep=2)
        assert not a.exists()
        assert b.exists()
        assert c.exists()

    def test_dry_run_does_not_delete(self, tmp_path):
        a = _make_archive(tmp_path, "a.ndjson.gz")
        time.sleep(0.05)
        _make_archive(tmp_path, "b.ndjson.gz")
        removed = prune_by_count(tmp_path, keep=1, dry_run=True)
        assert a in removed
        assert a.exists()

    def test_keep_zero_removes_all(self, tmp_path):
        _make_archive(tmp_path, "x.ndjson.gz")
        prune_by_count(tmp_path, keep=0)
        assert list_archives(tmp_path) == []

    def test_keep_more_than_existing_removes_nothing(self, tmp_path):
        _make_archive(tmp_path, "only.ndjson.gz")
        removed = prune_by_count(tmp_path, keep=100)
        assert removed == []


# ---------------------------------------------------------------------------
# apply_retention
# ---------------------------------------------------------------------------

class TestApplyRetention:
    def test_applies_both_policies(self, tmp_path):
        import os
        old = _make_archive(tmp_path, "old.ndjson.gz")
        os.utime(old, (0.0, 0.0))
        time.sleep(0.05)
        mid = _make_archive(tmp_path, "mid.ndjson.gz")
        time.sleep(0.05)
        new = _make_archive(tmp_path, "new.ndjson.gz")
        # age prunes 'old'; count (keep=1) prunes 'mid'
        removed = apply_retention(tmp_path, max_age_days=1, keep=1)
        names = {p.name for p in removed}
        assert "old.ndjson.gz" in names
        assert "mid.ndjson.gz" in names
        assert new.exists()

    def test_no_policies_removes_nothing(self, tmp_path):
        _make_archive(tmp_path, "a.ndjson.gz")
        removed = apply_retention(tmp_path)
        assert removed == []
