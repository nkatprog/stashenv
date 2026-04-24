"""Tests for stashenv.merge."""

import pytest

from stashenv.merge import MergeConflictError, _merge_dicts, merge_profiles
from stashenv.store import load_profile, save_profile


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, name, data, password="secret"):
    save_profile(project_dir, name, data, password)


# ---------------------------------------------------------------------------
# Unit tests for _merge_dicts
# ---------------------------------------------------------------------------

def test_merge_dicts_no_conflict():
    result = _merge_dicts({"A": "1"}, {"B": "2"}, strategy="override")
    assert result == {"A": "1", "B": "2"}


def test_merge_dicts_override_strategy():
    result = _merge_dicts({"A": "base"}, {"A": "new"}, strategy="override")
    assert result["A"] == "new"


def test_merge_dicts_base_strategy():
    result = _merge_dicts({"A": "base"}, {"A": "new"}, strategy="base")
    assert result["A"] == "base"


def test_merge_dicts_error_strategy_raises():
    with pytest.raises(MergeConflictError, match="A"):
        _merge_dicts({"A": "1"}, {"A": "2"}, strategy="error")


def test_merge_dicts_error_strategy_no_conflict_ok():
    result = _merge_dicts({"A": "1"}, {"B": "2"}, strategy="error")
    assert result == {"A": "1", "B": "2"}


def test_merge_dicts_override_adds_unique_keys():
    result = _merge_dicts({"A": "1", "C": "3"}, {"B": "2", "C": "99"}, strategy="override")
    assert result["A"] == "1"
    assert result["B"] == "2"
    assert result["C"] == "99"


# ---------------------------------------------------------------------------
# Integration tests for merge_profiles
# ---------------------------------------------------------------------------

def test_merge_profiles_creates_dest(project_dir):
    _save(project_dir, "base", {"HOST": "localhost", "PORT": "5432"})
    _save(project_dir, "override", {"PORT": "6543", "DEBUG": "true"})

    result = merge_profiles(project_dir, "base", "override", "merged", "secret")

    assert result["HOST"] == "localhost"
    assert result["PORT"] == "6543"
    assert result["DEBUG"] == "true"


def test_merge_profiles_saved_and_loadable(project_dir):
    _save(project_dir, "base", {"A": "1"})
    _save(project_dir, "override", {"B": "2"})

    merge_profiles(project_dir, "base", "override", "merged", "secret")
    loaded = load_profile(project_dir, "merged", "secret")

    assert loaded == {"A": "1", "B": "2"}


def test_merge_profiles_base_strategy(project_dir):
    _save(project_dir, "base", {"KEY": "from-base"})
    _save(project_dir, "override", {"KEY": "from-override"})

    result = merge_profiles(
        project_dir, "base", "override", "merged", "secret", strategy="base"
    )
    assert result["KEY"] == "from-base"


def test_merge_profiles_error_strategy_raises(project_dir):
    _save(project_dir, "base", {"KEY": "1"})
    _save(project_dir, "override", {"KEY": "2"})

    with pytest.raises(MergeConflictError):
        merge_profiles(
            project_dir, "base", "override", "merged", "secret", strategy="error"
        )


def test_merge_profiles_dest_different_project(tmp_path):
    src = str(tmp_path / "src")
    dst = str(tmp_path / "dst")

    _save(src, "base", {"X": "1"}, "pw")
    _save(src, "extra", {"Y": "2"}, "pw")

    merge_profiles(src, "base", "extra", "combined", "pw", dest_project_dir=dst)
    loaded = load_profile(dst, "combined", "pw")

    assert loaded == {"X": "1", "Y": "2"}


def test_merge_profiles_dest_different_password(project_dir):
    _save(project_dir, "base", {"A": "1"})
    _save(project_dir, "extra", {"B": "2"})

    merge_profiles(
        project_dir, "base", "extra", "secured", "secret", dest_password="newpass"
    )
    loaded = load_profile(project_dir, "secured", "newpass")
    assert loaded["A"] == "1"
    assert loaded["B"] == "2"
