"""Group multiple profiles under a named group for batch operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from stashenv.store import _stash_dir, list_profiles


class GroupError(Exception):
    pass


def _groups_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "groups.json"


def _load_groups(project_dir: Path) -> dict:
    p = _groups_path(project_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(project_dir: Path, groups: dict) -> None:
    p = _groups_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(groups, indent=2))


def create_group(project_dir: Path, group: str, profiles: List[str]) -> None:
    """Create or overwrite a named group of profiles."""
    existing = list_profiles(project_dir)
    missing = [p for p in profiles if p not in existing]
    if missing:
        raise GroupError(f"Profiles not found: {', '.join(missing)}")
    groups = _load_groups(project_dir)
    groups[group] = list(profiles)
    _save_groups(project_dir, groups)


def delete_group(project_dir: Path, group: str) -> None:
    """Remove a named group (does not delete profiles)."""
    groups = _load_groups(project_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    del groups[group]
    _save_groups(project_dir, groups)


def get_group(project_dir: Path, group: str) -> List[str]:
    """Return the list of profiles in a group."""
    groups = _load_groups(project_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    return groups[group]


def list_groups(project_dir: Path) -> dict:
    """Return all groups as {name: [profiles]}."""
    return _load_groups(project_dir)


def add_to_group(project_dir: Path, group: str, profile: str) -> None:
    """Add a profile to an existing group."""
    existing = list_profiles(project_dir)
    if profile not in existing:
        raise GroupError(f"Profile '{profile}' does not exist.")
    groups = _load_groups(project_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    if profile not in groups[group]:
        groups[group].append(profile)
        _save_groups(project_dir, groups)


def remove_from_group(project_dir: Path, group: str, profile: str) -> None:
    """Remove a profile from a group."""
    groups = _load_groups(project_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    if profile not in groups[group]:
        raise GroupError(f"Profile '{profile}' is not in group '{group}'.")
    groups[group].remove(profile)
    _save_groups(project_dir, groups)
