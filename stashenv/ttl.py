"""TTL (time-to-live) support for profiles — auto-expire after a duration."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir, list_profiles

_TTL_FILENAME = ".ttl.json"


def _ttl_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / _TTL_FILENAME


def _load_ttl(project_dir: Path) -> dict:
    path = _ttl_path(project_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_ttl(project_dir: Path, data: dict) -> None:
    _ttl_path(project_dir).write_text(json.dumps(data, indent=2))


def set_ttl(project_dir: Path, profile: str, seconds: int) -> None:
    """Set a TTL for *profile*; it will be considered expired after *seconds*."""
    profiles = list_profiles(project_dir)
    if profile not in profiles:
        raise FileNotFoundError(f"Profile '{profile}' does not exist.")
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    data = _load_ttl(project_dir)
    data[profile] = {"created_at": time.time(), "ttl": seconds}
    _save_ttl(project_dir, data)


def clear_ttl(project_dir: Path, profile: str) -> None:
    """Remove the TTL entry for *profile*."""
    data = _load_ttl(project_dir)
    data.pop(profile, None)
    _save_ttl(project_dir, data)


def get_ttl(project_dir: Path, profile: str) -> Optional[dict]:
    """Return TTL info dict or None if not set."""
    return _load_ttl(project_dir).get(profile)


def is_expired(project_dir: Path, profile: str) -> bool:
    """Return True if the profile's TTL has elapsed."""
    info = get_ttl(project_dir, profile)
    if info is None:
        return False
    return (time.time() - info["created_at"]) >= info["ttl"]


def list_expired(project_dir: Path) -> list[str]:
    """Return names of all profiles whose TTL has elapsed."""
    return [p for p in list_profiles(project_dir) if is_expired(project_dir, p)]
