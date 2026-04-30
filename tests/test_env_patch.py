"""Tests for stashenv.env_patch."""

from __future__ import annotations

import pytest

from stashenv.env_patch import PatchError, format_patch_result, patch_profile
from stashenv.store import load_profile, save_profile


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, env, password="secret"):
    save_profile(project_dir, profile, env, password)


def test_patch_adds_new_key(project_dir):
    _save(project_dir, "dev", {"EXISTING": "yes"})
    result = patch_profile(project_dir, "dev", "secret", set_keys={"NEW_KEY": "hello"})
    assert "NEW_KEY" in result.added
    assert result.updated == []
    env = load_profile(project_dir, "dev", "secret")
    assert env["NEW_KEY"] == "hello"
    assert env["EXISTING"] == "yes"


def test_patch_updates_existing_key(project_dir):
    _save(project_dir, "dev", {"DB_URL": "old"})
    result = patch_profile(project_dir, "dev", "secret", set_keys={"DB_URL": "new"})
    assert "DB_URL" in result.updated
    assert result.added == []
    env = load_profile(project_dir, "dev", "secret")
    assert env["DB_URL"] == "new"


def test_patch_removes_key(project_dir):
    _save(project_dir, "dev", {"A": "1", "B": "2"})
    result = patch_profile(project_dir, "dev", "secret", remove_keys=["A"])
    assert "A" in result.removed
    env = load_profile(project_dir, "dev", "secret")
    assert "A" not in env
    assert env["B"] == "2"


def test_patch_remove_nonexistent_key_raises(project_dir):
    _save(project_dir, "dev", {"X": "1"})
    with pytest.raises(PatchError, match="MISSING"):
        patch_profile(project_dir, "dev", "secret", remove_keys=["MISSING"])


def test_patch_combined_set_and_remove(project_dir):
    _save(project_dir, "dev", {"OLD": "gone", "KEEP": "yes"})
    result = patch_profile(
        project_dir,
        "dev",
        "secret",
        set_keys={"NEW": "value"},
        remove_keys=["OLD"],
    )
    assert result.total_changes == 2
    env = load_profile(project_dir, "dev", "secret")
    assert "OLD" not in env
    assert env["NEW"] == "value"
    assert env["KEEP"] == "yes"


def test_patch_no_changes_returns_empty_result(project_dir):
    _save(project_dir, "dev", {"A": "1"})
    result = patch_profile(project_dir, "dev", "secret")
    assert result.total_changes == 0


def test_format_patch_result_no_changes(project_dir):
    _save(project_dir, "dev", {})
    result = patch_profile(project_dir, "dev", "secret")
    assert format_patch_result(result) == "No changes applied."


def test_format_patch_result_shows_symbols(project_dir):
    _save(project_dir, "dev", {"OLD": "x"})
    result = patch_profile(
        project_dir,
        "dev",
        "secret",
        set_keys={"NEW": "y", "OLD": "z"},
    )
    output = format_patch_result(result)
    assert "+" in output or "~" in output
