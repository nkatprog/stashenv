"""Profile locking to prevent concurrent modifications."""

import json
import os
import time
from pathlib import Path

from stashenv.store import _stash_dir

LOCK_TIMEOUT = 30  # seconds


def _lock_path(project_dir: Path, profile: str) -> Path:
    return _stash_dir(project_dir) / f"{profile}.lock"


def acquire_lock(project_dir: Path, profile: str, owner: str = None) -> bool:
    """Acquire a lock for a profile. Returns True if successful."""
    lock_file = _lock_path(project_dir, profile)
    lock_file.parent.mkdir(parents=True, exist_ok=True)

    if lock_file.exists():
        data = json.loads(lock_file.read_text())
        age = time.time() - data["timestamp"]
        if age < LOCK_TIMEOUT:
            return False
        # Stale lock — remove it
        lock_file.unlink()

    payload = {"owner": owner or str(os.getpid()), "timestamp": time.time()}
    lock_file.write_text(json.dumps(payload))
    return True


def release_lock(project_dir: Path, profile: str) -> None:
    """Release a lock for a profile."""
    lock_file = _lock_path(project_dir, profile)
    if lock_file.exists():
        lock_file.unlink()


def get_lock_info(project_dir: Path, profile: str) -> dict | None:
    """Return lock info dict or None if not locked."""
    lock_file = _lock_path(project_dir, profile)
    if not lock_file.exists():
        return None
    data = json.loads(lock_file.read_text())
    age = time.time() - data["timestamp"]
    if age >= LOCK_TIMEOUT:
        lock_file.unlink()
        return None
    data["age_seconds"] = round(age, 1)
    return data


def list_locks(project_dir: Path) -> list[dict]:
    """List all active locks in a project."""
    stash = _stash_dir(project_dir)
    if not stash.exists():
        return []
    results = []
    for lock_file in stash.glob("*.lock"):
        profile = lock_file.stem
        info = get_lock_info(project_dir, profile)
        if info:
            info["profile"] = profile
            results.append(info)
    return results
