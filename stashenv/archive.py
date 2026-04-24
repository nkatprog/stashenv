"""Archive and unarchive profiles — move them out of active use without deleting."""

from __future__ import annotations

import shutil
from pathlib import Path

from stashenv.store import _stash_dir, _profile_path, load_profile, save_profile


def _archive_dir(project_dir: Path) -> Path:
    d = _stash_dir(project_dir) / "archived"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _archived_profile_path(project_dir: Path, profile: str) -> Path:
    return _archive_dir(project_dir) / f"{profile}.env.enc"


def archive_profile(project_dir: Path, profile: str, password: str) -> None:
    """Move *profile* to the archive. Raises FileNotFoundError if not found."""
    src = _profile_path(project_dir, profile)
    if not src.exists():
        raise FileNotFoundError(f"Profile '{profile}' not found.")

    dest = _archived_profile_path(project_dir, profile)
    if dest.exists():
        raise FileExistsError(f"Archived profile '{profile}' already exists.")

    # Verify password before moving.
    load_profile(project_dir, profile, password)

    shutil.move(str(src), str(dest))


def unarchive_profile(project_dir: Path, profile: str, password: str) -> None:
    """Restore *profile* from the archive back to active profiles."""
    src = _archived_profile_path(project_dir, profile)
    if not src.exists():
        raise FileNotFoundError(f"Archived profile '{profile}' not found.")

    dest = _profile_path(project_dir, profile)
    if dest.exists():
        raise FileExistsError(
            f"Active profile '{profile}' already exists. Delete it first."
        )

    # Verify password before restoring.
    load_profile.__module__  # noqa — just ensure import is live
    # Manually verify by loading from archive path.
    from stashenv.crypto import decrypt
    from stashenv.store import _stash_dir as _sd  # noqa

    data = src.read_bytes()
    decrypt(data, password)  # raises on wrong password

    shutil.move(str(src), str(dest))


def list_archived_profiles(project_dir: Path) -> list[str]:
    """Return names of all archived profiles."""
    d = _archive_dir(project_dir)
    return sorted(p.stem.removesuffix(".env") for p in d.glob("*.env.enc"))
