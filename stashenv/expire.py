"""Profile expiry: set and check TTL-based expiration on profiles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _expire_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "expiry.json"


def _load_expiry(project_dir: Path) -> dict:
    p = _expire_path(project_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(project_dir: Path, data: dict) -> None:
    p = _expire_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_expiry(project_dir: Path, profile: str, expires_at: datetime) -> None:
    """Set an expiry datetime (UTC) for a profile."""
    data = _load_expiry(project_dir)
    data[profile] = expires_at.astimezone(timezone.utc).isoformat()
    _save_expiry(project_dir, data)


def clear_expiry(project_dir: Path, profile: str) -> None:
    """Remove expiry for a profile."""
    data = _load_expiry(project_dir)
    data.pop(profile, None)
    _save_expiry(project_dir, data)


def get_expiry(project_dir: Path, profile: str) -> Optional[datetime]:
    """Return the expiry datetime for a profile, or None."""
    data = _load_expiry(project_dir)
    raw = data.get(profile)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(project_dir: Path, profile: str) -> bool:
    """Return True if the profile has passed its expiry time."""
    expiry = get_expiry(project_dir, profile)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expiry(project_dir: Path) -> dict[str, datetime]:
    """Return all profile expiry entries."""
    data = _load_expiry(project_dir)
    return {k: datetime.fromisoformat(v) for k, v in data.items()}
