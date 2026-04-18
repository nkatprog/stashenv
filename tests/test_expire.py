"""Tests for stashenv.expire module."""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stashenv.expire import (
    set_expiry,
    clear_expiry,
    get_expiry,
    is_expired,
    list_expiry,
)
from stashenv.store import save_profile


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _save(project_dir, name, password="pw"):
    save_profile(project_dir, name, {"KEY": "val"}, password)


def test_set_and_get_expiry(project_dir):
    _save(project_dir, "dev")
    future = datetime.now(timezone.utc) + timedelta(days=7)
    set_expiry(project_dir, "dev", future)
    result = get_expiry(project_dir, "dev")
    assert result is not None
    assert abs((result - future).total_seconds()) < 1


def test_get_expiry_none_when_not_set(project_dir):
    _save(project_dir, "dev")
    assert get_expiry(project_dir, "dev") is None


def test_is_not_expired_for_future(project_dir):
    _save(project_dir, "dev")
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    set_expiry(project_dir, "dev", future)
    assert not is_expired(project_dir, "dev")


def test_is_expired_for_past(project_dir):
    _save(project_dir, "dev")
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    set_expiry(project_dir, "dev", past)
    assert is_expired(project_dir, "dev")


def test_no_expiry_means_not_expired(project_dir):
    _save(project_dir, "dev")
    assert not is_expired(project_dir, "dev")


def test_clear_expiry(project_dir):
    _save(project_dir, "dev")
    future = datetime.now(timezone.utc) + timedelta(days=1)
    set_expiry(project_dir, "dev", future)
    clear_expiry(project_dir, "dev")
    assert get_expiry(project_dir, "dev") is None


def test_list_expiry(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    t1 = datetime.now(timezone.utc) + timedelta(days=1)
    t2 = datetime.now(timezone.utc) + timedelta(days=2)
    set_expiry(project_dir, "dev", t1)
    set_expiry(project_dir, "prod", t2)
    result = list_expiry(project_dir)
    assert set(result.keys()) == {"dev", "prod"}


def test_list_expiry_empty(project_dir):
    assert list_expiry(project_dir) == {}
