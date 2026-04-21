"""Scaffold a new .env file from a stored profile or template."""

from pathlib import Path
from typing import Optional

from stashenv.store import load_profile, list_profiles
from stashenv.export import dict_to_env


class ScaffoldError(Exception):
    pass


def scaffold_env_file(
    project_dir: str,
    profile_name: str,
    password: str,
    output_path: str = ".env",
    overwrite: bool = False,
    redact_values: bool = False,
) -> Path:
    """Write a .env file from a stored profile to the given output path.

    Args:
        project_dir: Directory whose stash to read from.
        profile_name: Name of the profile to scaffold.
        password: Password to decrypt the profile.
        output_path: Destination path for the .env file.
        overwrite: If False, raises ScaffoldError when file already exists.
        redact_values: If True, write keys with empty values (useful for .env.example).

    Returns:
        The resolved Path that was written.
    """
    dest = Path(output_path).resolve()

    if dest.exists() and not overwrite:
        raise ScaffoldError(
            f"File already exists: {dest}. Use overwrite=True to replace it."
        )

    available = list_profiles(project_dir)
    if profile_name not in available:
        raise ScaffoldError(
            f"Profile '{profile_name}' not found in project '{project_dir}'."
        )

    env_dict = load_profile(project_dir, profile_name, password)

    if redact_values:
        env_dict = {k: "" for k in env_dict}

    content = dict_to_env(env_dict)
    dest.write_text(content, encoding="utf-8")
    return dest


def scaffold_example_file(
    project_dir: str,
    profile_name: str,
    password: str,
    output_path: str = ".env.example",
    overwrite: bool = False,
) -> Path:
    """Convenience wrapper that scaffolds a redacted .env.example file."""
    return scaffold_env_file(
        project_dir=project_dir,
        profile_name=profile_name,
        password=password,
        output_path=output_path,
        overwrite=overwrite,
        redact_values=True,
    )
