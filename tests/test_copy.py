import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile, list_profiles
from stashenv.copy import copy_profile, rename_profile


PASSWORD = "testpass"
DATA = b"KEY=value\nFOO=bar\n"


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_copy_within_project(project_dir):
    save_profile(project_dir, "dev", DATA, PASSWORD)
    copy_profile(project_dir, "dev", project_dir, "dev-copy", PASSWORD)
    assert load_profile(project_dir, "dev-copy", PASSWORD) == DATA
    assert "dev" in list_profiles(project_dir)
    assert "dev-copy" in list_profiles(project_dir)


def test_copy_across_projects(project_dir, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    save_profile(project_dir, "prod", DATA, PASSWORD)
    copy_profile(project_dir, "prod", other, "prod", PASSWORD)
    assert load_profile(other, "prod", PASSWORD) == DATA


def test_copy_with_new_password(project_dir):
    save_profile(project_dir, "dev", DATA, PASSWORD)
    copy_profile(project_dir, "dev", project_dir, "dev2", PASSWORD, dst_password="newpass")
    assert load_profile(project_dir, "dev2", "newpass") == DATA
    with pytest.raises(Exception):
        load_profile(project_dir, "dev2", PASSWORD)


def test_rename_profile(project_dir):
    save_profile(project_dir, "staging", DATA, PASSWORD)
    rename_profile(project_dir, "staging", "stage", PASSWORD)
    assert "stage" in list_profiles(project_dir)
    assert "staging" not in list_profiles(project_dir)
    assert load_profile(project_dir, "stage", PASSWORD) == DATA


def test_rename_to_existing_raises(project_dir):
    save_profile(project_dir, "a", DATA, PASSWORD)
    save_profile(project_dir, "b", DATA, PASSWORD)
    with pytest.raises(FileExistsError):
        rename_profile(project_dir, "a", "b", PASSWORD)


def test_copy_nonexistent_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        copy_profile(project_dir, "ghost", project_dir, "copy", PASSWORD)
