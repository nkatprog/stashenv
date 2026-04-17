"""Snapshot support: capture and restore full profile sets for a project."""

from __future__ import annotations

import json
import time
from pathlib import Path

from stashenv.store import _stash_dir, list_profiles, load_profile, save_profile


def _snapshot_dir(project_dir: Path) -> Path:
    d = _stash_dir(project_dir) / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_snapshot(project_dir: Path, password: str, label: str | None = None) -> str:
    """Capture all profiles and save as a named snapshot. Returns snapshot id."""
    profiles = list_profiles(project_dir)
    data: dict[str, str] = {}
    for name in profiles:
        data[name] = load_profile(project_dir, name, password)

    snapshot_id = label or str(int(time.time()))
    snapshot_file = _snapshot_dir(project_dir) / f"{snapshot_id}.json"
    if snapshot_file.exists():
        raise FileExistsError(f"Snapshot '{snapshot_id}' already exists.")

    snapshot_file.write_text(json.dumps({"profiles": data, "created": time.time()}))
    return snapshot_id


def list_snapshots(project_dir: Path) -> list[str]:
    """Return sorted list of snapshot ids."""
    d = _snapshot_dir(project_dir)
    return sorted(p.stem for p in d.glob("*.json"))


def restore_snapshot(project_dir: Path, snapshot_id: str, password: str) -> list[str]:
    """Restore all profiles from snapshot. Returns list of restored profile names."""
    snapshot_file = _snapshot_dir(project_dir) / f"{snapshot_id}.json"
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found.")

    data = json.loads(snapshot_file.read_text())
    restored = []
    for name, env_text in data["profiles"].items():
        save_profile(project_dir, name, env_text, password)
        restored.append(name)
    return restored


def delete_snapshot(project_dir: Path, snapshot_id: str) -> None:
    """Delete a snapshot by id."""
    snapshot_file = _snapshot_dir(project_dir) / f"{snapshot_id}.json"
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found.")
    snapshot_file.unlink()
