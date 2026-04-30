"""Apply a patch (partial key-value updates) to an existing profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stashenv.store import load_profile, save_profile


class PatchError(Exception):
    pass


@dataclass
class PatchResult:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.updated) + len(self.removed)


def patch_profile(
    project_dir: str,
    profile: str,
    password: str,
    *,
    set_keys: Optional[Dict[str, str]] = None,
    remove_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Apply incremental changes to a profile without replacing it entirely.

    Args:
        project_dir: Root directory of the project.
        profile: Name of the profile to patch.
        password: Decryption/encryption password.
        set_keys: Mapping of keys to add or update.
        remove_keys: List of keys to remove.

    Returns:
        PatchResult describing what changed.

    Raises:
        PatchError: If a key to remove does not exist.
    """
    set_keys = set_keys or {}
    remove_keys = remove_keys or []

    env = load_profile(project_dir, profile, password)
    result = PatchResult()

    for key in remove_keys:
        if key not in env:
            raise PatchError(f"Key '{key}' not found in profile '{profile}'")
        del env[key]
        result.removed.append(key)

    for key, value in set_keys.items():
        if key in env:
            result.updated.append(key)
        else:
            result.added.append(key)
        env[key] = value

    save_profile(project_dir, profile, env, password)
    return result


def format_patch_result(result: PatchResult) -> str:
    lines: List[str] = []
    for key in result.added:
        lines.append(f"  + {key}")
    for key in result.updated:
        lines.append(f"  ~ {key}")
    for key in result.removed:
        lines.append(f"  - {key}")
    if not lines:
        return "No changes applied."
    return "\n".join(lines)
