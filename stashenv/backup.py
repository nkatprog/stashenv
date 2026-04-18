"""Backup and restore all profiles for a project to/from a single encrypted archive."""
from __future__ import annotations

import json
import os
from pathlib import Path

from stashenv.crypto import encrypt, decrypt
from stashenv.store import _stash_dir, list_profiles, load_profile, save_profile


def create_backup(project_dir: str, password: str, backup_path: str) -> int:
    """Encrypt all profiles into a single backup file. Returns number of profiles backed up."""
    profiles = list_profiles(project_dir)
    if not profiles:
        raise ValueError("No profiles found to back up.")

    data: dict[str, str] = {}
    for name in profiles:
        content = load_profile(project_dir, name, password)
        data[name] = content

    payload = json.dumps(data).encode()
    token = encrypt(payload, password)

    Path(backup_path).write_bytes(token)
    return len(profiles)


def restore_backup(project_dir: str, password: str, backup_path: str, overwrite: bool = False) -> list[str]:
    """Decrypt a backup file and restore all profiles. Returns list of restored profile names."""
    raw = Path(backup_path).read_bytes()
    payload = decrypt(raw, password)
    data: dict[str, str] = json.loads(payload.decode())

    existing = set(list_profiles(project_dir))
    restored = []

    for name, content in data.items():
        if name in existing and not overwrite:
            raise FileExistsError(
                f"Profile '{name}' already exists. Use overwrite=True to replace."
            )
        save_profile(project_dir, name, content, password)
        restored.append(name)

    return restored


def list_backup_profiles(backup_path: str, password: str) -> list[str]:
    """List profile names stored inside a backup file without restoring them."""
    raw = Path(backup_path).read_bytes()
    payload = decrypt(raw, password)
    data: dict[str, str] = json.loads(payload.decode())
    return sorted(data.keys())
