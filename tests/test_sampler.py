"""Tests for logslice.sampler module."""

import pytest
from logslice.sampler import sample_entries, sample_every_nth, head_entries


ENTRIES = [{"id": i, "message": f"log line {i}"} for i in range(100)]


# ---------------------------------------------------------------------------
# sample_entries
# ---------------------------------------------------------------------------

class TestSampleEntries:
    def test_rate_zero_yields_nothing(self):
        result = list(sample_entries(ENTRIES, rate=0.0))
        assert result == []

    def test_rate_one_yields_all(self):
        result = list(sample_entries(ENTRIES, rate=1.0))
        assert result == ENTRIES

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError, match="Sample rate"):
            list(sample_entries(ENTRIES, rate=1.5))

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            list(sample_entries(ENTRIES, rate=-0.1))

    def test_seed_produces_reproducible_output(self):
        result_a = list(sample_entries(ENTRIES, rate=0.5, seed=42))
        result_b = list(sample_entries(ENTRIES, rate=0.5, seed=42))
        assert result_a == result_b

    def test_different_seeds_differ(self):
        result_a = list(sample_entries(ENTRIES, rate=0.5, seed=1))
        result_b = list(sample_entries(ENTRIES, rate=0.5, seed=2))
        # Extremely unlikely to be identical over 100 entries
        assert result_a != result_b

    def test_partial_rate_reduces_count(self):
        result = list(sample_entries(ENTRIES, rate=0.5, seed=0))
        assert 0 < len(result) < len(ENTRIES)

    def test_empty_input_yields_nothing(self):
        result = list(sample_entries([], rate=0.5))
        assert result == []


# ---------------------------------------------------------------------------
# sample_every_nth
# ---------------------------------------------------------------------------

class TestSampleEveryNth:
    def test_n_equals_one_yields_all(self):
        result = list(sample_every_nth(ENTRIES, n=1))
        assert result == ENTRIES

    def test_n_equals_two_halves_count(self):
        result = list(sample_every_nth(ENTRIES, n=2))
        assert len(result) == 50
        assert result[0] == ENTRIES[0]
        assert result[1] == ENTRIES[2]

    def test_n_larger_than_stream(self):
        result = list(sample_every_nth(ENTRIES[:5], n=10))
        assert result == [ENTRIES[0]]

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError, match="n must be"):
            list(sample_every_nth(ENTRIES, n=0))

    def test_empty_input(self):
        assert list(sample_every_nth([], n=3)) == []


# ---------------------------------------------------------------------------
# head_entries
# ---------------------------------------------------------------------------

class TestHeadEntries:
    def test_limit_zero_yields_nothing(self):
        assert list(head_entries(ENTRIES, limit=0)) == []

    def test_limit_larger_than_stream_yields_all(self):
        result = list(head_entries(ENTRIES[:10], limit=50))
        assert result == ENTRIES[:10]

    def test_limit_exact(self):
        result = list(head_entries(ENTRIES, limit=5))
        assert result == ENTRIES[:5]

    def test_negative_limit_raises(self):
        with pytest.raises(ValueError, match="limit must be"):
            list(head_entries(ENTRIES, limit=-1))

    def test_empty_input(self):
        assert list(head_entries([], limit=10)) == []
