"""Profile pinning — mark profiles as active/pinned for a project."""
from __future__ import annotations
import json
from pathlib import Path
from stashenv.store import _stash_dir


def _pin_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "pinned.json"


def _load_pins(project_dir: Path) -> dict:
    p = _pin_path(project_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(project_dir: Path, data: dict) -> None:
    p = _pin_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def pin_profile(project_dir: Path, profile: str) -> None:
    """Pin a profile as the active one for this project."""
    from stashenv.store import list_profiles
    if profile not in list_profiles(project_dir):
        raise FileNotFoundError(f"Profile '{profile}' does not exist.")
    data = _load_pins(project_dir)
    data["pinned"] = profile
    _save_pins(project_dir, data)


def unpin_profile(project_dir: Path) -> None:
    """Remove the pinned profile for this project."""
    data = _load_pins(project_dir)
    data.pop("pinned", None)
    _save_pins(project_dir, data)


def get_pinned(project_dir: Path) -> str | None:
    """Return the currently pinned profile name, or None."""
    return _load_pins(project_dir).get("pinned")
