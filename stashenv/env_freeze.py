"""Freeze and unfreeze profiles to prevent accidental modification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashenv.store import _stash_dir


class FreezeError(Exception):
    pass


def _freeze_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "frozen.json"


def _load_frozen(project_dir: Path) -> List[str]:
    p = _freeze_path(project_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_frozen(project_dir: Path, frozen: List[str]) -> None:
    p = _freeze_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sorted(set(frozen)), indent=2))


def freeze_profile(project_dir: Path, profile: str) -> None:
    """Mark a profile as frozen so it cannot be overwritten."""
    from stashenv.store import list_profiles

    if profile not in list_profiles(project_dir):
        raise FreezeError(f"Profile '{profile}' does not exist.")
    frozen = _load_frozen(project_dir)
    if profile not in frozen:
        frozen.append(profile)
    _save_frozen(project_dir, frozen)


def unfreeze_profile(project_dir: Path, profile: str) -> None:
    """Remove the frozen mark from a profile."""
    frozen = _load_frozen(project_dir)
    frozen = [p for p in frozen if p != profile]
    _save_frozen(project_dir, frozen)


def is_frozen(project_dir: Path, profile: str) -> bool:
    """Return True if the profile is currently frozen."""
    return profile in _load_frozen(project_dir)


def list_frozen(project_dir: Path) -> List[str]:
    """Return all frozen profile names for the project."""
    return _load_frozen(project_dir)


def assert_not_frozen(project_dir: Path, profile: str) -> None:
    """Raise FreezeError if the profile is frozen."""
    if is_frozen(project_dir, profile):
        raise FreezeError(
            f"Profile '{profile}' is frozen and cannot be modified. "
            "Run 'stashenv freeze unset' to unfreeze it first."
        )
