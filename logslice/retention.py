"""Retention policy helpers — prune old archive files by age or count."""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence


def _mtime(path: Path) -> datetime:
    """Return the modification time of *path* as a UTC-aware datetime."""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def list_archives(directory: str | Path, pattern: str = "*.ndjson.gz") -> list[Path]:
    """Return all archive files in *directory* matching *pattern*, sorted by mtime."""
    directory = Path(directory)
    files = list(directory.glob(pattern))
    files.sort(key=lambda p: p.stat().st_mtime)
    return files


def prune_by_age(
    directory: str | Path,
    max_age_days: float,
    pattern: str = "*.ndjson.gz",
    dry_run: bool = False,
) -> list[Path]:
    """Delete archive files older than *max_age_days* days.

    Returns the list of files that were (or would be) removed.
    """
    if max_age_days < 0:
        raise ValueError("max_age_days must be >= 0")
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=max_age_days)
    removed: list[Path] = []
    for path in list_archives(directory, pattern):
        if _mtime(path) < cutoff:
            if not dry_run:
                path.unlink()
            removed.append(path)
    return removed


def prune_by_count(
    directory: str | Path,
    keep: int,
    pattern: str = "*.ndjson.gz",
    dry_run: bool = False,
) -> list[Path]:
    """Keep only the *keep* most-recent archive files; delete the rest.

    Returns the list of files that were (or would be) removed.
    """
    if keep < 0:
        raise ValueError("keep must be >= 0")
    files = list_archives(directory, pattern)  # sorted oldest-first
    to_remove = files[: max(0, len(files) - keep)]
    for path in to_remove:
        if not dry_run:
            path.unlink()
    return to_remove


def apply_retention(
    directory: str | Path,
    max_age_days: float | None = None,
    keep: int | None = None,
    pattern: str = "*.ndjson.gz",
    dry_run: bool = False,
) -> list[Path]:
    """Apply age-based and/or count-based retention in one call.

    Returns the deduplicated list of removed (or would-be-removed) paths.
    """
    removed: set[Path] = set()
    if max_age_days is not None:
        removed.update(prune_by_age(directory, max_age_days, pattern, dry_run))
    if keep is not None:
        removed.update(prune_by_count(directory, keep, pattern, dry_run))
    return sorted(removed, key=lambda p: p.name)
