"""Profile storage: save and load encrypted .env profiles on disk."""

import os
from pathlib import Path

from stashenv.crypto import encrypt, decrypt

STASH_DIR_NAME = ".stashenv"


def _stash_dir(project_dir: Path) -> Path:
    return project_dir / STASH_DIR_NAME


def _profile_path(project_dir: Path, profile_name: str) -> Path:
    return _stash_dir(project_dir) / f"{profile_name}.enc"


def save_profile(project_dir: Path, profile_name: str, env_content: str, password: str) -> Path:
    """Encrypt and save an env profile. Returns the path written."""
    stash = _stash_dir(project_dir)
    stash.mkdir(parents=True, exist_ok=True)
    payload = encrypt(env_content, password)
    path = _profile_path(project_dir, profile_name)
    path.write_bytes(payload)
    return path


def load_profile(project_dir: Path, profile_name: str, password: str) -> str:
    """Load and decrypt an env profile. Returns plaintext env content."""
    path = _profile_path(project_dir, profile_name)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile_name}' not found in {project_dir}.")
    payload = path.read_bytes()
    return decrypt(payload, password)


def list_profiles(project_dir: Path) -> list[str]:
    """Return names of all stored profiles for the project."""
    stash = _stash_dir(project_dir)
    if not stash.exists():
        return []
    return [p.stem for p in sorted(stash.glob("*.enc"))]


def delete_profile(project_dir: Path, profile_name: str) -> None:
    """Delete a stored profile."""
    path = _profile_path(project_dir, profile_name)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{profile_name}' not found.")
    path.unlink()
