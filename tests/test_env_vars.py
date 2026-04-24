"""Tests for stashenv.env_vars — individual variable management within profiles."""

from __future__ import annotations

import pytest

from stashenv.store import save_profile
from stashenv.env_vars import (
    KeyNotFoundError,
    get_var,
    list_vars,
    rename_var,
    set_var,
    unset_var,
)


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, password, data):
    save_profile(project_dir, profile, password, data)


# ---------------------------------------------------------------------------
# set_var
# ---------------------------------------------------------------------------

def test_set_var_creates_new_key(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1"})
    set_var(project_dir, "dev", "pw", "B", "2")
    assert get_var(project_dir, "dev", "pw", "B") == "2"


def test_set_var_overwrites_existing_key(project_dir):
    _save(project_dir, "dev", "pw", {"A": "old"})
    set_var(project_dir, "dev", "pw", "A", "new")
    assert get_var(project_dir, "dev", "pw", "A") == "new"


# ---------------------------------------------------------------------------
# get_var
# ---------------------------------------------------------------------------

def test_get_var_returns_correct_value(project_dir):
    _save(project_dir, "dev", "pw", {"URL": "http://localhost"})
    assert get_var(project_dir, "dev", "pw", "URL") == "http://localhost"


def test_get_var_missing_key_raises(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1"})
    with pytest.raises(KeyNotFoundError):
        get_var(project_dir, "dev", "pw", "MISSING")


# ---------------------------------------------------------------------------
# unset_var
# ---------------------------------------------------------------------------

def test_unset_var_removes_key(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1", "B": "2"})
    unset_var(project_dir, "dev", "pw", "A")
    remaining = list_vars(project_dir, "dev", "pw")
    assert "A" not in remaining
    assert remaining["B"] == "2"


def test_unset_var_missing_key_raises(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1"})
    with pytest.raises(KeyNotFoundError):
        unset_var(project_dir, "dev", "pw", "NOPE")


# ---------------------------------------------------------------------------
# list_vars
# ---------------------------------------------------------------------------

def test_list_vars_returns_all_pairs(project_dir):
    data = {"X": "10", "Y": "20", "Z": "30"}
    _save(project_dir, "prod", "secret", data)
    assert list_vars(project_dir, "prod", "secret") == data


# ---------------------------------------------------------------------------
# rename_var
# ---------------------------------------------------------------------------

def test_rename_var_changes_key_name(project_dir):
    _save(project_dir, "dev", "pw", {"OLD": "value"})
    rename_var(project_dir, "dev", "pw", "OLD", "NEW")
    env = list_vars(project_dir, "dev", "pw")
    assert "OLD" not in env
    assert env["NEW"] == "value"


def test_rename_var_missing_old_key_raises(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1"})
    with pytest.raises(KeyNotFoundError):
        rename_var(project_dir, "dev", "pw", "GHOST", "NEW")


def test_rename_var_conflict_raises_without_overwrite(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1", "B": "2"})
    with pytest.raises(KeyError):
        rename_var(project_dir, "dev", "pw", "A", "B")


def test_rename_var_conflict_allowed_with_overwrite(project_dir):
    _save(project_dir, "dev", "pw", {"A": "1", "B": "old"})
    rename_var(project_dir, "dev", "pw", "A", "B", overwrite=True)
    env = list_vars(project_dir, "dev", "pw")
    assert env["B"] == "1"
    assert "A" not in env
