"""checkpoint.py — Track and resume log processing positions.

Provides utilities for saving and loading byte-offset checkpoints so that
long-running or repeated logslice runs can resume from where they left off
rather than reprocessing an entire file from the start.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

# Default directory for checkpoint files when no explicit path is given.
_DEFAULT_CHECKPOINT_DIR = Path(".logslice_checkpoints")

# Schema version stored in every checkpoint file so future readers can
# detect incompatible formats and warn accordingly.
_SCHEMA_VERSION = 1


def _checkpoint_path(source: str, directory: Path) -> Path:
    """Return the checkpoint file path for *source* inside *directory*.

    The source string (typically a file path) is normalised to a safe
    filename by replacing path separators and other special characters.
    """
    safe_name = source.replace(os.sep, "__").replace("/", "__").lstrip(".")
    safe_name = safe_name or "_root"
    return directory / f"{safe_name}.json"


def save_checkpoint(
    source: str,
    offset: int,
    *,
    directory: Path = _DEFAULT_CHECKPOINT_DIR,
    extra: Optional[Dict] = None,
) -> Path:
    """Persist a byte-offset checkpoint for *source*.

    Parameters
    ----------
    source:
        Identifier for the log source — usually an absolute or relative file
        path but can be any string that uniquely names the stream.
    offset:
        The byte position in *source* up to which entries have been
        successfully processed.
    directory:
        Directory in which checkpoint files are stored.  Created automatically
        if it does not already exist.
    extra:
        Optional mapping of additional metadata to embed in the checkpoint
        (e.g. last timestamp seen, entry count processed).

    Returns
    -------
    Path
        The path to the written checkpoint file.
    """
    if offset < 0:
        raise ValueError(f"offset must be non-negative, got {offset}")

    directory.mkdir(parents=True, exist_ok=True)
    path = _checkpoint_path(source, directory)

    payload: Dict = {
        "_version": _SCHEMA_VERSION,
        "source": source,
        "offset": offset,
    }
    if extra:
        payload["extra"] = extra

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_checkpoint(
    source: str,
    *,
    directory: Path = _DEFAULT_CHECKPOINT_DIR,
) -> Optional[Dict]:
    """Load the checkpoint for *source*, returning ``None`` if none exists.

    Parameters
    ----------
    source:
        The same identifier used when :func:`save_checkpoint` was called.
    directory:
        Directory to search for checkpoint files.

    Returns
    -------
    dict or None
        The full checkpoint payload (including ``offset`` and any ``extra``
        keys) or ``None`` when no checkpoint file is found.
    """
    path = _checkpoint_path(source, directory)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable checkpoint — treat as missing.
        return None

    if data.get("_version", 0) != _SCHEMA_VERSION:
        # Incompatible format; caller should reprocess from the start.
        return None

    return data


def get_offset(
    source: str,
    *,
    directory: Path = _DEFAULT_CHECKPOINT_DIR,
    default: int = 0,
) -> int:
    """Return the saved byte offset for *source*, or *default* if absent."""
    checkpoint = load_checkpoint(source, directory=directory)
    if checkpoint is None:
        return default
    return int(checkpoint.get("offset", default))


def delete_checkpoint(
    source: str,
    *,
    directory: Path = _DEFAULT_CHECKPOINT_DIR,
) -> bool:
    """Remove the checkpoint file for *source*.

    Returns ``True`` if a file was deleted, ``False`` if none existed.
    """
    path = _checkpoint_path(source, directory)
    if path.exists():
        path.unlink()
        return True
    return False
