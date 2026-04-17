"""Tests for stashenv.lock."""

import time
import pytest
from pathlib import Path

from stashenv.lock import acquire_lock, release_lock, get_lock_info, list_locks, LOCK_TIMEOUT


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_acquire_lock_succeeds(project_dir):
    assert acquire_lock(project_dir, "dev", owner="alice") is True


def test_acquire_lock_twice_fails(project_dir):
    acquire_lock(project_dir, "dev", owner="alice")
    assert acquire_lock(project_dir, "dev", owner="bob") is False


def test_release_allows_reacquire(project_dir):
    acquire_lock(project_dir, "dev", owner="alice")
    release_lock(project_dir, "dev")
    assert acquire_lock(project_dir, "dev", owner="bob") is True


def test_release_nonexistent_lock_is_noop(project_dir):
    release_lock(project_dir, "ghost")  # should not raise


def test_get_lock_info_returns_none_when_unlocked(project_dir):
    assert get_lock_info(project_dir, "dev") is None


def test_get_lock_info_returns_owner(project_dir):
    acquire_lock(project_dir, "dev", owner="ci-runner")
    info = get_lock_info(project_dir, "dev")
    assert info is not None
    assert info["owner"] == "ci-runner"
    assert "age_seconds" in info


def test_stale_lock_is_cleared(project_dir, monkeypatch):
    acquire_lock(project_dir, "dev", owner="old")
    # Backdate the lock timestamp
    import json
    from stashenv.lock import _lock_path
    lp = _lock_path(project_dir, "dev")
    data = json.loads(lp.read_text())
    data["timestamp"] = time.time() - LOCK_TIMEOUT - 5
    lp.write_text(json.dumps(data))

    assert get_lock_info(project_dir, "dev") is None
    assert acquire_lock(project_dir, "dev", owner="new") is True


def test_list_locks_empty(project_dir):
    assert list_locks(project_dir) == []


def test_list_locks_shows_active(project_dir):
    acquire_lock(project_dir, "dev", owner="alice")
    acquire_lock(project_dir, "prod", owner="bob")
    locks = list_locks(project_dir)
    profiles = {l["profile"] for l in locks}
    assert profiles == {"dev", "prod"}


def test_lock_different_profiles_independent(project_dir):
    assert acquire_lock(project_dir, "dev") is True
    assert acquire_lock(project_dir, "prod") is True
