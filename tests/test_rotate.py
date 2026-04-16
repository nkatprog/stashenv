"""Tests for stashenv.rotate."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile, list_profiles
from stashenv.rotate import rotate_profile, rotate_all_profiles


@pytest.fixture
def project_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    return tmp_path


def _save(project, name, data, password, project_dir):
    save_profile(project, name, data, password)


def test_rotate_profile_allows_new_password(project_dir):
    _save("myapp", "dev", "KEY=value\n", "oldpass", project_dir)
    rotate_profile("myapp", "dev", "oldpass", "newpass")
    result = load_profile("myapp", "dev", "newpass")
    assert result == "KEY=value\n"


def test_rotate_profile_old_password_fails_after(project_dir):
    _save("myapp", "dev", "KEY=value\n", "oldpass", project_dir)
    rotate_profile("myapp", "dev", "oldpass", "newpass")
    with pytest.raises(Exception):
        load_profile("myapp", "dev", "oldpass")


def test_rotate_profile_wrong_old_password_raises(project_dir):
    _save("myapp", "dev", "KEY=value\n", "correct", project_dir)
    with pytest.raises(Exception):
        rotate_profile("myapp", "dev", "wrong", "newpass")


def test_rotate_all_profiles(project_dir):
    for name in ("dev", "staging", "prod"):
        _save("myapp", name, f"ENV={name}\n", "oldpass", project_dir)

    rotated = rotate_all_profiles("myapp", "oldpass", "newpass")
    assert sorted(rotated) == ["dev", "prod", "staging"]

    for name in ("dev", "staging", "prod"):
        result = load_profile("myapp", name, "newpass")
        assert result == f"ENV={name}\n"


def test_rotate_all_empty_project_returns_empty(project_dir):
    rotated = rotate_all_profiles("emptyapp", "oldpass", "newpass")
    assert rotated == []


def test_rotate_all_wrong_password_raises(project_dir):
    _save("myapp", "dev", "KEY=val\n", "correct", project_dir)
    with pytest.raises(RuntimeError, match="Failed to rotate"):
        rotate_all_profiles("myapp", "wrong", "newpass")
