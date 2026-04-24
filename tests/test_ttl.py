"""Tests for stashenv.ttl."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from stashenv.store import save_profile
from stashenv.ttl import (
    set_ttl,
    clear_ttl,
    get_ttl,
    is_expired,
    list_expired,
)

PASSWORD = "secret"
ENV_CONTENT = "KEY=value\n"


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str) -> None:
    save_profile(project_dir, profile, ENV_CONTENT.encode(), PASSWORD)


def test_set_and_get_ttl(project_dir: Path) -> None:
    _save(project_dir, "dev")
    set_ttl(project_dir, "dev", 3600)
    info = get_ttl(project_dir, "dev")
    assert info is not None
    assert info["ttl"] == 3600
    assert "created_at" in info


def test_get_ttl_none_when_not_set(project_dir: Path) -> None:
    _save(project_dir, "dev")
    assert get_ttl(project_dir, "dev") is None


def test_set_ttl_nonexistent_profile_raises(project_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        set_ttl(project_dir, "ghost", 60)


def test_set_ttl_zero_raises(project_dir: Path) -> None:
    _save(project_dir, "dev")
    with pytest.raises(ValueError):
        set_ttl(project_dir, "dev", 0)


def test_is_not_expired_for_future_ttl(project_dir: Path) -> None:
    _save(project_dir, "dev")
    set_ttl(project_dir, "dev", 9999)
    assert not is_expired(project_dir, "dev")


def test_is_expired_for_past_ttl(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _save(project_dir, "dev")
    set_ttl(project_dir, "dev", 1)
    # Wind clock forward so TTL has elapsed
    monkeypatch.setattr("stashenv.ttl.time.time", lambda: time.time() + 10)
    assert is_expired(project_dir, "dev")


def test_clear_ttl_removes_entry(project_dir: Path) -> None:
    _save(project_dir, "dev")
    set_ttl(project_dir, "dev", 100)
    clear_ttl(project_dir, "dev")
    assert get_ttl(project_dir, "dev") is None


def test_list_expired_returns_correct_profiles(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    set_ttl(project_dir, "dev", 1)
    set_ttl(project_dir, "prod", 9999)
    monkeypatch.setattr("stashenv.ttl.time.time", lambda: time.time() + 10)
    expired = list_expired(project_dir)
    assert "dev" in expired
    assert "prod" not in expired
