"""Tests for stashenv.env_access."""

from __future__ import annotations

from pathlib import Path

import pytest

from stashenv.env_access import (
    AccessDeniedError,
    check_permission,
    get_permissions,
    list_access,
    revoke_access,
    set_access,
)


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_and_get_permissions(project_dir: Path) -> None:
    set_access(project_dir, "production", "alice", ["read"])
    perms = get_permissions(project_dir, "production", "alice")
    assert perms == ["read"]


def test_set_multiple_permissions(project_dir: Path) -> None:
    set_access(project_dir, "staging", "bob", ["read", "write"])
    perms = get_permissions(project_dir, "staging", "bob")
    assert set(perms) == {"read", "write"}


def test_get_permissions_no_entry_returns_empty(project_dir: Path) -> None:
    perms = get_permissions(project_dir, "production", "unknown")
    assert perms == []


def test_set_invalid_permission_raises(project_dir: Path) -> None:
    with pytest.raises(ValueError, match="Unknown permissions"):
        set_access(project_dir, "production", "alice", ["execute"])


def test_revoke_removes_actor(project_dir: Path) -> None:
    set_access(project_dir, "production", "alice", ["read", "write"])
    revoke_access(project_dir, "production", "alice")
    perms = get_permissions(project_dir, "production", "alice")
    assert perms == []


def test_revoke_nonexistent_actor_is_noop(project_dir: Path) -> None:
    revoke_access(project_dir, "production", "ghost")  # should not raise


def test_check_permission_passes(project_dir: Path) -> None:
    set_access(project_dir, "dev", "carol", ["read"])
    check_permission(project_dir, "dev", "carol", "read")  # should not raise


def test_check_permission_raises_when_missing(project_dir: Path) -> None:
    set_access(project_dir, "dev", "carol", ["read"])
    with pytest.raises(AccessDeniedError, match="write"):
        check_permission(project_dir, "dev", "carol", "write")


def test_list_access_all_profiles(project_dir: Path) -> None:
    set_access(project_dir, "dev", "alice", ["read"])
    set_access(project_dir, "prod", "bob", ["write"])
    acl = list_access(project_dir)
    assert "dev" in acl
    assert "prod" in acl


def test_list_access_filtered_to_profile(project_dir: Path) -> None:
    set_access(project_dir, "dev", "alice", ["read"])
    set_access(project_dir, "prod", "bob", ["write"])
    acl = list_access(project_dir, profile="dev")
    assert "dev" in acl
    assert "prod" not in acl


def test_set_access_overwrites_previous(project_dir: Path) -> None:
    set_access(project_dir, "dev", "alice", ["read", "write"])
    set_access(project_dir, "dev", "alice", ["read"])
    perms = get_permissions(project_dir, "dev", "alice")
    assert perms == ["read"]
