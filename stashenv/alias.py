"""Profile aliasing — create short names that point to existing profiles."""

from __future__ import annotations

import json
from pathlib import Path


def _alias_path(project_dir: Path) -> Path:
    return project_dir / ".stashenv" / "aliases.json"


def _load_aliases(project_dir: Path) -> dict[str, str]:
    p = _alias_path(project_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(project_dir: Path, aliases: dict[str, str]) -> None:
    p = _alias_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(aliases, indent=2))


def set_alias(project_dir: Path, alias: str, profile: str) -> None:
    """Create or overwrite an alias pointing to *profile*."""
    from stashenv.store import list_profiles

    if profile not in list_profiles(project_dir):
        raise KeyError(f"Profile '{profile}' does not exist.")
    aliases = _load_aliases(project_dir)
    aliases[alias] = profile
    _save_aliases(project_dir, aliases)


def remove_alias(project_dir: Path, alias: str) -> None:
    """Remove an alias. No-op if it does not exist."""
    aliases = _load_aliases(project_dir)
    aliases.pop(alias, None)
    _save_aliases(project_dir, aliases)


def resolve_alias(project_dir: Path, alias: str) -> str:
    """Return the profile name for *alias*, or *alias* itself if not found."""
    aliases = _load_aliases(project_dir)
    return aliases.get(alias, alias)


def list_aliases(project_dir: Path) -> dict[str, str]:
    """Return all alias -> profile mappings."""
    return _load_aliases(project_dir)
