"""Export and import .env profiles to/from plaintext or encrypted files."""

from __future__ import annotations

import os
from pathlib import Path

from stashenv.store import load_profile, save_profile


def export_profile(project_dir: str, profile_name: str, password: str, output_path: str) -> None:
    """Decrypt a stored profile and write it as a plaintext .env file."""
    env_content = load_profile(project_dir, profile_name, password)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(env_content, encoding="utf-8")


def import_profile(project_dir: str, profile_name: str, password: str, input_path: str) -> None:
    """Read a plaintext .env file and store it as an encrypted profile."""
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    env_content = src.read_text(encoding="utf-8")
    save_profile(project_dir, profile_name, password, env_content)


def env_to_dict(env_content: str) -> dict[str, str]:
    """Parse .env content into a key/value dictionary (ignores comments and blanks)."""
    result: dict[str, str] = {}
    for line in env_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def dict_to_env(data: dict[str, str]) -> str:
    """Serialize a key/value dictionary back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"
