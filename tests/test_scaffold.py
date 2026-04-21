"""Tests for stashenv.scaffold."""

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.scaffold import scaffold_env_file, scaffold_example_file, ScaffoldError


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path / "myproject")


def _save(project_dir, name, data, password="secret"):
    save_profile(project_dir, name, data, password)


def test_scaffold_creates_env_file(project_dir, tmp_path):
    _save(project_dir, "dev", {"DB_HOST": "localhost", "PORT": "5432"})
    dest = tmp_path / ".env"
    result = scaffold_env_file(project_dir, "dev", "secret", output_path=str(dest))
    assert result == dest.resolve()
    assert dest.exists()
    content = dest.read_text()
    assert "DB_HOST=localhost" in content
    assert "PORT=5432" in content


def test_scaffold_raises_if_file_exists_without_overwrite(project_dir, tmp_path):
    _save(project_dir, "dev", {"KEY": "value"})
    dest = tmp_path / ".env"
    dest.write_text("existing")
    with pytest.raises(ScaffoldError, match="already exists"):
        scaffold_env_file(project_dir, "dev", "secret", output_path=str(dest))


def test_scaffold_overwrites_when_flag_set(project_dir, tmp_path):
    _save(project_dir, "dev", {"KEY": "new_value"})
    dest = tmp_path / ".env"
    dest.write_text("old content")
    scaffold_env_file(project_dir, "dev", "secret", output_path=str(dest), overwrite=True)
    content = dest.read_text()
    assert "KEY=new_value" in content
    assert "old content" not in content


def test_scaffold_nonexistent_profile_raises(project_dir, tmp_path):
    dest = tmp_path / ".env"
    with pytest.raises(ScaffoldError, match="not found"):
        scaffold_env_file(project_dir, "ghost", "secret", output_path=str(dest))


def test_scaffold_example_redacts_values(project_dir, tmp_path):
    _save(project_dir, "prod", {"API_KEY": "supersecret", "DB_URL": "postgres://..."})
    dest = tmp_path / ".env.example"
    scaffold_example_file(project_dir, "prod", "secret", output_path=str(dest))
    content = dest.read_text()
    assert "API_KEY=" in content
    assert "supersecret" not in content
    assert "DB_URL=" in content
    assert "postgres" not in content


def test_scaffold_example_contains_all_keys(project_dir, tmp_path):
    data = {"ALPHA": "1", "BETA": "2", "GAMMA": "3"}
    _save(project_dir, "staging", data)
    dest = tmp_path / ".env.example"
    scaffold_example_file(project_dir, "staging", "secret", output_path=str(dest))
    content = dest.read_text()
    for key in data:
        assert key in content
