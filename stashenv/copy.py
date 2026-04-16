"""Copy/rename profiles within or across projects."""

from pathlib import Path
from stashenv.store import load_profile, save_profile, list_profiles, _profile_path


def copy_profile(
    src_project: Path,
    src_name: str,
    dst_project: Path,
    dst_name: str,
    password: str,
    dst_password: str | None = None,
) -> None:
    """Copy a profile from src to dst, optionally re-encrypting with a new password."""
    data = load_profile(src_project, src_name, password)
    target_password = dst_password if dst_password is not None else password
    save_profile(dst_project, dst_name, data, target_password)


def rename_profile(
    project: Path,
    old_name: str,
    new_name: str,
    password: str,
) -> None:
    """Rename a profile by copying then deleting the original."""
    if new_name in list_profiles(project):
        raise FileExistsError(f"Profile '{new_name}' already exists.")
    copy_profile(project, old_name, project, new_name, password)
    _profile_path(project, old_name).unlink()
