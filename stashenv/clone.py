"""Clone a profile to a new project directory."""
from pathlib import Path
from stashenv.store import load_profile, save_profile, list_profiles


def clone_profile(
    src_project: Path,
    src_name: str,
    dst_project: Path,
    dst_name: str,
    password: str,
    dst_password: str | None = None,
) -> None:
    """Clone a profile from src_project to dst_project.

    If dst_password is None, the same password is used for the destination.
    Raises FileNotFoundError if the source profile does not exist.
    Raises FileExistsError if the destination profile already exists.
    """
    dst_password = dst_password or password

    existing = list_profiles(dst_project)
    if dst_name in existing:
        raise FileExistsError(
            f"Profile '{dst_name}' already exists in {dst_project}"
        )

    env_text = load_profile(src_project, src_name, password)
    save_profile(dst_project, dst_name, env_text, dst_password)


def clone_all_profiles(
    src_project: Path,
    dst_project: Path,
    password: str,
    dst_password: str | None = None,
    skip_existing: bool = False,
) -> list[str]:
    """Clone all profiles from src_project to dst_project.

    Returns list of cloned profile names.
    If skip_existing is True, silently skips profiles that already exist
    in the destination; otherwise raises FileExistsError.
    """
    cloned: list[str] = []
    for name in list_profiles(src_project):
        try:
            clone_profile(src_project, name, dst_project, name, password, dst_password)
            cloned.append(name)
        except FileExistsError:
            if not skip_existing:
                raise
    return cloned
