"""Per-profile notes storage for stashenv."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashenv.store import _stash_dir


def _notes_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "notes.json"


def _load_notes(project_dir: Path) -> dict[str, str]:
    path = _notes_path(project_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_notes(project_dir: Path, notes: dict[str, str]) -> None:
    path = _notes_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2))


def set_note(project_dir: Path, profile: str, note: str) -> None:
    """Set or replace the note for a profile."""
    from stashenv.store import list_profiles
    if profile not in list_profiles(project_dir):
        raise KeyError(f"Profile '{profile}' does not exist.")
    notes = _load_notes(project_dir)
    notes[profile] = note
    _save_notes(project_dir, notes)


def get_note(project_dir: Path, profile: str) -> Optional[str]:
    """Return the note for a profile, or None if not set."""
    return _load_notes(project_dir).get(profile)


def clear_note(project_dir: Path, profile: str) -> None:
    """Remove the note for a profile if it exists."""
    notes = _load_notes(project_dir)
    notes.pop(profile, None)
    _save_notes(project_dir, notes)


def list_notes(project_dir: Path) -> dict[str, str]:
    """Return all profile notes."""
    return dict(_load_notes(project_dir))
