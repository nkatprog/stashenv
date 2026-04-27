"""Access control for profiles: restrict which users/roles can read or write a profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

ACCESS_FILENAME = ".access.json"


class AccessDeniedError(Exception):
    """Raised when an operation is not permitted for the given actor."""


def _access_path(project_dir: Path) -> Path:
    return project_dir / ".stashenv" / ACCESS_FILENAME


def _load_acl(project_dir: Path) -> dict:
    path = _access_path(project_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_acl(project_dir: Path, acl: dict) -> None:
    path = _access_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(acl, indent=2))


def set_access(project_dir: Path, profile: str, actor: str, permissions: list[str]) -> None:
    """Grant actor specific permissions ('read', 'write') on profile."""
    valid = {"read", "write"}
    unknown = set(permissions) - valid
    if unknown:
        raise ValueError(f"Unknown permissions: {unknown}")
    acl = _load_acl(project_dir)
    acl.setdefault(profile, {})[actor] = sorted(set(permissions))
    _save_acl(project_dir, acl)


def revoke_access(project_dir: Path, profile: str, actor: str) -> None:
    """Remove all permissions for actor on profile."""
    acl = _load_acl(project_dir)
    acl.get(profile, {}).pop(actor, None)
    _save_acl(project_dir, acl)


def get_permissions(project_dir: Path, profile: str, actor: str) -> list[str]:
    """Return list of permissions actor has on profile."""
    acl = _load_acl(project_dir)
    return acl.get(profile, {}).get(actor, [])


def check_permission(project_dir: Path, profile: str, actor: str, permission: str) -> None:
    """Raise AccessDeniedError if actor lacks permission on profile."""
    perms = get_permissions(project_dir, profile, actor)
    if permission not in perms:
        raise AccessDeniedError(
            f"Actor '{actor}' does not have '{permission}' permission on profile '{profile}'."
        )


def list_access(project_dir: Path, profile: Optional[str] = None) -> dict:
    """Return ACL dict, optionally filtered to a single profile."""
    acl = _load_acl(project_dir)
    if profile is not None:
        return {profile: acl.get(profile, {})}
    return acl
