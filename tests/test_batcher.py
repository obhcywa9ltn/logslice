"""Tests for logslice.batcher."""

from datetime import datetime, timedelta

import pytest

from logslice.batcher import batch_by_size, batch_by_time, flatten_batches


def _entry(ts: datetime, message: str = "msg") -> dict:
    return {"timestamp": ts.isoformat(), "message": message}


_BASE = datetime(2024, 1, 1, 12, 0, 0)


# ---------------------------------------------------------------------------
# batch_by_size
# ---------------------------------------------------------------------------

class TestBatchBySize:
    def test_exact_multiple(self):
        entries = [_entry(_BASE)] * 6
        batches = list(batch_by_size(entries, 2))
        assert len(batches) == 3
        assert all(len(b) == 2 for b in batches)

    def test_remainder_in_final_batch(self):
        entries = [_entry(_BASE)] * 5
        batches = list(batch_by_size(entries, 3))
        assert len(batches) == 2
        assert len(batches[-1]) == 2

    def test_size_larger_than_entries(self):
        entries = [_entry(_BASE)] * 3
        batches = list(batch_by_size(entries, 10))
        assert len(batches) == 1
        assert len(batches[0]) == 3

    def test_empty_input_yields_nothing(self):
        assert list(batch_by_size([], 5)) == []

    def test_size_one_yields_single_element_batches(self):
        entries = [_entry(_BASE)] * 4
        batches = list(batch_by_size(entries, 1))
        assert len(batches) == 4
        assert all(len(b) == 1 for b in batches)

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError):
            list(batch_by_size([], 0))

    def test_negative_size_raises(self):
        with pytest.raises(ValueError):
            list(batch_by_size([], -3))


# ---------------------------------------------------------------------------
# batch_by_time
# ---------------------------------------------------------------------------

class TestBatchByTime:
    def test_single_window(self):
        entries = [_entry(_BASE + timedelta(seconds=i)) for i in range(5)]
        batches = list(batch_by_time(entries, window_seconds=10))
        assert len(batches) == 1
        assert len(batches[0]) == 5

    def test_two_windows(self):
        early = [_entry(_BASE + timedelta(seconds=i)) for i in range(3)]
        late = [_entry(_BASE + timedelta(seconds=20 + i)) for i in range(3)]
        batches = list(batch_by_time(early + late, window_seconds=10))
        assert len(batches) == 2

    def test_entry_without_timestamp_stays_in_current_window(self):
        entries = [
            _entry(_BASE),
            {"message": "no-ts"},
            _entry(_BASE + timedelta(seconds=1)),
        ]
        batches = list(batch_by_time(entries, window_seconds=5))
        assert len(batches) == 1
        assert len(batches[0]) == 3

    def test_empty_input_yields_nothing(self):
        assert list(batch_by_time([], window_seconds=5)) == []

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            list(batch_by_time([], window_seconds=0))


# ---------------------------------------------------------------------------
# flatten_batches
# ---------------------------------------------------------------------------

def test_flatten_batches_restores_entries():
    entries = [_entry(_BASE + timedelta(seconds=i)) for i in range(6)]
    batches = list(batch_by_size(entries, 2))
    restored = list(flatten_batches(batches))
    assert restored == entries


def test_flatten_empty_batches_yields_nothing():
    assert list(flatten_batches([])) == []
