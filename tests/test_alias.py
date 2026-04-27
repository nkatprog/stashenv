"""Tests for stashenv.alias."""

import pytest
from pathlib import Path

from stashenv.alias import set_alias, remove_alias, resolve_alias, list_aliases
from stashenv.store import save_profile


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, name: str, password: str = "pw") -> None:
    save_profile(project_dir, name, {"KEY": "value"}, password)


def test_set_and_list_alias(project_dir):
    _save(project_dir, "production")
    set_alias(project_dir, "prod", "production")
    aliases = list_aliases(project_dir)
    assert aliases["prod"] == "production"


def test_set_alias_nonexistent_profile_raises(project_dir):
    with pytest.raises(KeyError, match="does not exist"):
        set_alias(project_dir, "prod", "ghost")


def test_resolve_known_alias(project_dir):
    _save(project_dir, "staging")
    set_alias(project_dir, "stg", "staging")
    assert resolve_alias(project_dir, "stg") == "staging"


def test_resolve_unknown_returns_input(project_dir):
    assert resolve_alias(project_dir, "anything") == "anything"


def test_remove_alias(project_dir):
    _save(project_dir, "dev")
    set_alias(project_dir, "d", "dev")
    remove_alias(project_dir, "d")
    assert "d" not in list_aliases(project_dir)


def test_remove_nonexistent_alias_is_noop(project_dir):
    remove_alias(project_dir, "missing")  # should not raise


def test_overwrite_alias(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "staging")
    set_alias(project_dir, "env", "dev")
    set_alias(project_dir, "env", "staging")
    assert list_aliases(project_dir)["env"] == "staging"


def test_list_aliases_empty(project_dir):
    assert list_aliases(project_dir) == {}


def test_multiple_aliases_can_point_to_same_profile(project_dir):
    """Multiple alias names may resolve to the same underlying profile."""
    _save(project_dir, "production")
    set_alias(project_dir, "prod", "production")
    set_alias(project_dir, "prd", "production")
    aliases = list_aliases(project_dir)
    assert aliases["prod"] == "production"
    assert aliases["prd"] == "production"
    assert resolve_alias(project_dir, "prod") == resolve_alias(project_dir, "prd")
