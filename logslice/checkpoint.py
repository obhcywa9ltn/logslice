"""checkpoint.py — Persist and restore file-read offsets for resumable log tailing."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".logslice", "checkpoints")


def _checkpoint_path(log_path: str, checkpoint_dir: str = _DEFAULT_DIR) -> str:
    """Return the checkpoint file path for *log_path*."""
    safe_name = Path(log_path).name.replace(os.sep, "_") + ".json"
    return os.path.join(checkpoint_dir, safe_name)


def save_checkpoint(
    log_path: str,
    offset: int,
    checkpoint_dir: str = _DEFAULT_DIR,
    extra: Optional[dict] = None,
) -> str:
    """Persist *offset* for *log_path*; return the checkpoint file path."""
    cp_path = _checkpoint_path(log_path, checkpoint_dir)
    os.makedirs(os.path.dirname(cp_path), exist_ok=True)
    payload: dict = {"log_path": log_path, "offset": offset}
    if extra:
        payload.update(extra)
    with open(cp_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    return cp_path


def load_checkpoint(
    log_path: str,
    checkpoint_dir: str = _DEFAULT_DIR,
) -> Optional[dict]:
    """Load and return the checkpoint dict for *log_path*, or *None* if absent."""
    cp_path = _checkpoint_path(log_path, checkpoint_dir)
    if not os.path.exists(cp_path):
        return None
    with open(cp_path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return None


def get_offset(
    log_path: str,
    checkpoint_dir: str = _DEFAULT_DIR,
    default: int = 0,
) -> int:
    """Return the saved byte offset for *log_path*, or *default* if none exists."""
    checkpoint = load_checkpoint(log_path, checkpoint_dir)
    if checkpoint is None:
        return default
    return int(checkpoint.get("offset", default))


def delete_checkpoint(
    log_path: str,
    checkpoint_dir: str = _DEFAULT_DIR,
) -> bool:
    """Delete the checkpoint for *log_path*. Return True if it existed."""
    cp_path = _checkpoint_path(log_path, checkpoint_dir)
    if os.path.exists(cp_path):
        os.remove(cp_path)
        return True
    return False


def list_checkpoints(checkpoint_dir: str = _DEFAULT_DIR) -> list[str]:
    """Return a sorted list of log paths that have saved checkpoints."""
    if not os.path.isdir(checkpoint_dir):
        return []
    results = []
    for fname in sorted(os.listdir(checkpoint_dir)):
        if fname.endswith(".json"):
            full = os.path.join(checkpoint_dir, fname)
            data = load_checkpoint.__wrapped__ if hasattr(load_checkpoint, "__wrapped__") else None
            try:
                with open(full, "r", encoding="utf-8") as fh:
                    payload = json.load(fh)
                results.append(payload.get("log_path", fname))
            except (json.JSONDecodeError, OSError):
                pass
    return results
