"""Tests for logslice.ratelimiter."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from logslice.ratelimiter import (
    _bucket_key,
    count_by_bucket,
    rate_limit_entries,
)


def _ts(offset_seconds: int = 0) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0)
    return base + timedelta(seconds=offset_seconds)


def _entry(offset: int = 0, **extra) -> dict:
    return {"timestamp": _ts(offset), "message": f"msg-{offset}", **extra}


# ---------------------------------------------------------------------------
# _bucket_key
# ---------------------------------------------------------------------------

class TestBucketKey:
    def test_same_second_same_key(self):
        t1 = datetime(2024, 1, 1, 0, 0, 1)
        t2 = datetime(2024, 1, 1, 0, 0, 1)
        assert _bucket_key(t1, 1) == _bucket_key(t2, 1)

    def test_different_seconds_different_keys(self):
        t1 = datetime(2024, 1, 1, 0, 0, 1)
        t2 = datetime(2024, 1, 1, 0, 0, 2)
        assert _bucket_key(t1, 1) != _bucket_key(t2, 1)

    def test_same_10s_bucket(self):
        t1 = datetime(2024, 1, 1, 0, 0, 0)
        t2 = datetime(2024, 1, 1, 0, 0, 9)
        assert _bucket_key(t1, 10) == _bucket_key(t2, 10)

    def test_different_10s_buckets(self):
        t1 = datetime(2024, 1, 1, 0, 0, 9)
        t2 = datetime(2024, 1, 1, 0, 0, 10)
        assert _bucket_key(t1, 10) != _bucket_key(t2, 10)


# ---------------------------------------------------------------------------
# rate_limit_entries
# ---------------------------------------------------------------------------

class TestRateLimitEntries:
    def test_allows_up_to_limit(self):
        entries = [_entry(0), _entry(0), _entry(0)]
        result = list(rate_limit_entries(entries, max_per_bucket=2, bucket_seconds=1))
        assert len(result) == 2

    def test_all_pass_when_under_limit(self):
        entries = [_entry(0), _entry(1), _entry(2)]
        result = list(rate_limit_entries(entries, max_per_bucket=5, bucket_seconds=1))
        assert len(result) == 3

    def test_separate_buckets_counted_independently(self):
        # 2 entries at t=0, 2 entries at t=1; limit=1 per second → 2 pass
        entries = [_entry(0), _entry(0), _entry(1), _entry(1)]
        result = list(rate_limit_entries(entries, max_per_bucket=1, bucket_seconds=1))
        assert len(result) == 2

    def test_no_timestamp_passes_through(self):
        entries = [{"message": "no-ts"}, {"message": "no-ts-2"}]
        result = list(rate_limit_entries(entries, max_per_bucket=1))
        assert len(result) == 2

    def test_invalid_max_per_bucket_raises(self):
        with pytest.raises(ValueError):
            list(rate_limit_entries([], max_per_bucket=0))

    def test_invalid_bucket_seconds_raises(self):
        with pytest.raises(ValueError):
            list(rate_limit_entries([], max_per_bucket=1, bucket_seconds=0))

    def test_custom_timestamp_field(self):
        entries = [
            {"ts": _ts(0), "message": "a"},
            {"ts": _ts(0), "message": "b"},
        ]
        result = list(
            rate_limit_entries(entries, max_per_bucket=1, timestamp_field="ts")
        )
        assert len(result) == 1

    def test_empty_entries_yields_nothing(self):
        assert list(rate_limit_entries([], max_per_bucket=10)) == []


# ---------------------------------------------------------------------------
# count_by_bucket
# ---------------------------------------------------------------------------

class TestCountByBucket:
    def test_counts_correctly(self):
        entries = [_entry(0), _entry(0), _entry(1)]
        counts = count_by_bucket(entries, bucket_seconds=1)
        values = list(counts.values())
        assert sorted(values) == [1, 2]

    def test_empty_returns_empty_dict(self):
        assert count_by_bucket([], bucket_seconds=1) == {}

    def test_invalid_bucket_seconds_raises(self):
        with pytest.raises(ValueError):
            count_by_bucket([], bucket_seconds=-1)
