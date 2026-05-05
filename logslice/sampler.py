"""Sampling utilities for reducing large log streams."""

from typing import Iterable, Iterator, Optional
import random


def sample_entries(
    entries: Iterable[dict],
    rate: float,
    seed: Optional[int] = None,
) -> Iterator[dict]:
    """Yield a random sample of log entries at the given rate.

    Args:
        entries: Iterable of parsed log entry dicts.
        rate: Fraction of entries to keep, between 0.0 and 1.0 inclusive.
        seed: Optional random seed for reproducibility.

    Yields:
        Log entry dicts that passed the sampling filter.

    Raises:
        ValueError: If rate is not between 0.0 and 1.0.
    """
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"Sample rate must be between 0.0 and 1.0, got {rate!r}")

    rng = random.Random(seed)

    for entry in entries:
        if rng.random() < rate:
            yield entry


def sample_every_nth(
    entries: Iterable[dict],
    n: int,
) -> Iterator[dict]:
    """Yield every n-th log entry (deterministic reservoir-style sampling).

    Args:
        entries: Iterable of parsed log entry dicts.
        n: Keep one entry for every n entries seen. Must be >= 1.

    Yields:
        Every n-th log entry.

    Raises:
        ValueError: If n is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n!r}")

    for i, entry in enumerate(entries):
        if i % n == 0:
            yield entry


def head_entries(entries: Iterable[dict], limit: int) -> Iterator[dict]:
    """Yield at most `limit` entries from the beginning of the stream.

    Args:
        entries: Iterable of parsed log entry dicts.
        limit: Maximum number of entries to yield.

    Yields:
        Up to `limit` log entries.

    Raises:
        ValueError: If limit is negative.
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit!r}")

    for i, entry in enumerate(entries):
        if i >= limit:
            break
        yield entry
