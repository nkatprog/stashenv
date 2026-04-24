"""Tests for stashenv.archive."""

from __future__ import annotations

import pytest
from pathlib import Path

from stashenv.archive import (
    archive_profile,
    unarchive_profile,
    list_archived_profiles,
)
from stashenv.store import save_profile, load_profile


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, data: dict, password: str = "secret") -> None:
    save_profile(project_dir, profile, data, password)


def test_archive_moves_profile_out_of_active(project_dir: Path) -> None:
    _save(project_dir, "dev", {"KEY": "val"})
    archive_profile(project_dir, "dev", "secret")

    from stashenv.store import list_profiles
    assert "dev" not in list_profiles(project_dir)


def test_archived_profile_appears_in_list(project_dir: Path) -> None:
    _save(project_dir, "staging", {"A": "1"})
    archive_profile(project_dir, "staging", "secret")
    assert "staging" in list_archived_profiles(project_dir)


def test_list_archived_empty_when_none(project_dir: Path) -> None:
    assert list_archived_profiles(project_dir) == []


def test_archive_nonexistent_raises(project_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        archive_profile(project_dir, "ghost", "secret")


def test_archive_wrong_password_raises(project_dir: Path) -> None:
    _save(project_dir, "prod", {"X": "y"})
    with pytest.raises(Exception):
        archive_profile(project_dir, "prod", "wrongpass")


def test_unarchive_restores_profile(project_dir: Path) -> None:
    _save(project_dir, "dev", {"KEY": "hello"})
    archive_profile(project_dir, "dev", "secret")
    unarchive_profile(project_dir, "dev", "secret")

    result = load_profile(project_dir, "dev", "secret")
    assert result == {"KEY": "hello"}


def test_unarchive_removes_from_archive_list(project_dir: Path) -> None:
    _save(project_dir, "dev", {"K": "v"})
    archive_profile(project_dir, "dev", "secret")
    unarchive_profile(project_dir, "dev", "secret")
    assert "dev" not in list_archived_profiles(project_dir)


def test_unarchive_nonexistent_raises(project_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        unarchive_profile(project_dir, "ghost", "secret")


def test_archive_duplicate_raises(project_dir: Path) -> None:
    _save(project_dir, "dev", {"K": "v"})
    archive_profile(project_dir, "dev", "secret")
    _save(project_dir, "dev", {"K": "v2"})
    with pytest.raises(FileExistsError):
        archive_profile(project_dir, "dev", "secret")
