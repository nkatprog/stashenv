"""Tests for stashenv.export module."""

import pytest
from pathlib import Path

from stashenv.export import export_profile, import_profile, env_to_dict, dict_to_env
from stashenv.store import save_profile, load_profile


PASSWORD = "testpass"
PROFILE = "staging"
ENV_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n"


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path / "myproject")


def test_export_writes_plaintext(project_dir, tmp_path):
    save_profile(project_dir, PROFILE, PASSWORD, ENV_CONTENT)
    out_file = str(tmp_path / "exported.env")
    export_profile(project_dir, PROFILE, PASSWORD, out_file)
    assert Path(out_file).read_text() == ENV_CONTENT


def test_import_stores_profile(project_dir, tmp_path):
    src = tmp_path / "source.env"
    src.write_text(ENV_CONTENT)
    import_profile(project_dir, PROFILE, PASSWORD, str(src))
    loaded = load_profile(project_dir, PROFILE, PASSWORD)
    assert loaded == ENV_CONTENT


def test_import_missing_file_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        import_profile(project_dir, PROFILE, PASSWORD, "/nonexistent/file.env")


def test_export_wrong_password_raises(project_dir, tmp_path):
    save_profile(project_dir, PROFILE, PASSWORD, ENV_CONTENT)
    out_file = str(tmp_path / "out.env")
    with pytest.raises(Exception):
        export_profile(project_dir, PROFILE, "wrongpass", out_file)


def test_env_to_dict_parses_correctly():
    result = env_to_dict(ENV_CONTENT)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


def test_env_to_dict_ignores_comments_and_blanks():
    content = "# comment\n\nKEY=value\n"
    assert env_to_dict(content) == {"KEY": "value"}


def test_dict_to_env_roundtrip():
    data = {"A": "1", "B": "2"}
    assert env_to_dict(dict_to_env(data)) == data
