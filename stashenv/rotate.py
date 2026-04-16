"""Password rotation for stashenv profiles."""

from pathlib import Path
from stashenv.store import load_profile, save_profile, list_profiles, _stash_dir
from stashenv.audit import log_event


def rotate_profile(
    project: str,
    profile: str,
    old_password: str,
    new_password: str,
) -> None:
    """Re-encrypt a single profile with a new password."""
    data = load_profile(project, profile, old_password)
    save_profile(project, profile, data, new_password)
    log_event(project, "rotate", profile)


def rotate_all_profiles(
    project: str,
    old_password: str,
    new_password: str,
) -> list[str]:
    """Re-encrypt all profiles in a project with a new password.

    Returns list of rotated profile names.
    """
    profiles = list_profiles(project)
    if not profiles:
        return []

    rotated = []
    for profile in profiles:
        try:
            rotate_profile(project, profile, old_password, new_password)
            rotated.append(profile)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to rotate profile '{profile}': {exc}"
            ) from exc

    return rotated
