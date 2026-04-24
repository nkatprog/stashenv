"""Tests for stashenv.env_set bulk set/unset functionality."""
from __future__ import annotations

from pathlib import Path

import pytest

from stashenv.store import save_profile, load_profile
from stashenv.env_set import set_vars, unset_vars, set_from_file, EnvSetError


PASSWORD = "test-secret"


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, data: dict) -> None:
    save_profile(project_dir, profile, PASSWORD, data)


# ---------------------------------------------------------------------------
# set_vars
# ---------------------------------------------------------------------------

def test_set_vars_adds_new_keys(project_dir):
    _save(project_dir, "dev", {"EXISTING": "yes"})
    result = set_vars(project_dir, "dev", PASSWORD, {"NEW_KEY": "hello", "ANOTHER": "world"})
    assert result["NEW_KEY"] == "hello"
    assert result["ANOTHER"] == "world"
    assert result["EXISTING"] == "yes"


def test_set_vars_overwrites_existing_key(project_dir):
    _save(project_dir, "dev", {"FOO": "old"})
    result = set_vars(project_dir, "dev", PASSWORD, {"FOO": "new"})
    assert result["FOO"] == "new"


def test_set_vars_persists_to_disk(project_dir):
    _save(project_dir, "dev", {})
    set_vars(project_dir, "dev", PASSWORD, {"PERSIST": "1"})
    reloaded = load_profile(project_dir, "dev", PASSWORD)
    assert reloaded["PERSIST"] == "1"


# ---------------------------------------------------------------------------
# unset_vars
# ---------------------------------------------------------------------------

def test_unset_vars_removes_keys(project_dir):
    _save(project_dir, "dev", {"A": "1", "B": "2", "C": "3"})
    result = unset_vars(project_dir, "dev", PASSWORD, ["A", "C"])
    assert "A" not in result
    assert "C" not in result
    assert result["B"] == "2"


def test_unset_vars_ignores_missing_keys(project_dir):
    _save(project_dir, "dev", {"X": "10"})
    result = unset_vars(project_dir, "dev", PASSWORD, ["X", "MISSING"])
    assert "X" not in result
    assert "MISSING" not in result


# ---------------------------------------------------------------------------
# set_from_file
# ---------------------------------------------------------------------------

def test_set_from_file_imports_all_pairs(project_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    _save(project_dir, "dev", {})
    result = set_from_file(project_dir, "dev", PASSWORD, env_file)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_set_from_file_skips_comments_and_blanks(project_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\n\nKEY=value\n")
    _save(project_dir, "dev", {})
    result = set_from_file(project_dir, "dev", PASSWORD, env_file)
    assert list(result.keys()) == ["KEY"]


def test_set_from_file_no_overwrite_keeps_existing(project_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=from_file\n")
    _save(project_dir, "dev", {"KEY": "original"})
    result = set_from_file(project_dir, "dev", PASSWORD, env_file, overwrite=False)
    assert result["KEY"] == "original"


def test_set_from_file_missing_file_raises(project_dir, tmp_path):
    with pytest.raises(EnvSetError, match="File not found"):
        set_from_file(project_dir, "dev", PASSWORD, tmp_path / "ghost.env")


def test_set_from_file_invalid_line_raises(project_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("BADLINE\n")
    _save(project_dir, "dev", {})
    with pytest.raises(EnvSetError, match="Invalid line"):
        set_from_file(project_dir, "dev", PASSWORD, env_file)
