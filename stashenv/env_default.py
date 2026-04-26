"""Set and manage default values for keys in a profile.

A default is applied when a key is missing from the profile on load,
or can be explicitly applied to fill in missing keys.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir, load_profile, save_profile


class DefaultError(Exception):
    pass


def _defaults_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "defaults.json"


def _load_defaults(project_dir: Path) -> dict[str, str]:
    path = _defaults_path(project_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_defaults(project_dir: Path, defaults: dict[str, str]) -> None:
    path = _defaults_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(defaults, indent=2))


def set_default(project_dir: Path, key: str, value: str) -> None:
    """Register a default value for a key."""
    defaults = _load_defaults(project_dir)
    defaults[key] = value
    _save_defaults(project_dir, defaults)


def remove_default(project_dir: Path, key: str) -> None:
    """Remove a registered default for a key."""
    defaults = _load_defaults(project_dir)
    defaults.pop(key, None)
    _save_defaults(project_dir, defaults)


def get_default(project_dir: Path, key: str) -> Optional[str]:
    """Return the registered default for key, or None."""
    return _load_defaults(project_dir).get(key)


def list_defaults(project_dir: Path) -> dict[str, str]:
    """Return all registered defaults."""
    return _load_defaults(project_dir)


def apply_defaults(project_dir: Path, profile: str, password: str) -> list[str]:
    """Fill missing keys in profile with registered defaults.

    Returns a list of keys that were filled in.
    """
    defaults = _load_defaults(project_dir)
    if not defaults:
        return []
    data = load_profile(project_dir, profile, password)
    filled: list[str] = []
    for key, value in defaults.items():
        if key not in data:
            data[key] = value
            filled.append(key)
    if filled:
        save_profile(project_dir, profile, password, data)
    return filled
