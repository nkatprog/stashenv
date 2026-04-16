"""Unit tests for stashenv.store."""

import pytest
from pathlib import Path
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile


ENV_CONTENT = "API_KEY=abc123\nDEBUG=true\n"
PASSWORD = "passw0rd"


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_save_and_load(project_dir):
    save_profile(project_dir, "dev", ENV_CONTENT, PASSWORD)
    result = load_profile(project_dir, "dev", PASSWORD)
    assert result == ENV_CONTENT


def test_list_profiles(project_dir):
    assert list_profiles(project_dir) == []
    save_profile(project_dir, "dev", ENV_CONTENT, PASSWORD)
    save_profile(project_dir, "prod", ENV_CONTENT, PASSWORD)
    assert list_profiles(project_dir) == ["dev", "prod"]


def test_load_nonexistent_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        load_profile(project_dir, "ghost", PASSWORD)


def test_wrong_password_on_load(project_dir):
    save_profile(project_dir, "staging", ENV_CONTENT, PASSWORD)
    with pytest.raises(ValueError):
        load_profile(project_dir, "staging", "badpass")


def test_delete_profile(project_dir):
    save_profile(project_dir, "dev", ENV_CONTENT, PASSWORD)
    delete_profile(project_dir, "dev")
    assert list_profiles(project_dir) == []


def test_delete_nonexistent_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        delete_profile(project_dir, "nope")
