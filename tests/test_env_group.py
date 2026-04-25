"""Tests for stashenv/env_group.py and stashenv/cli_env_group.py."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.env_group import (
    GroupError,
    add_to_group,
    create_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)
from stashenv.store import save_profile
from stashenv.cli_env_group import group_cmd

PASSWORD = "testpass"


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _save(project_dir, name, data=None):
    save_profile(project_dir, name, data or {"KEY": "value"}, PASSWORD)


# --- Unit tests ---

def test_create_group_and_get(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "staging")
    create_group(project_dir, "lower", ["dev", "staging"])
    assert get_group(project_dir, "lower") == ["dev", "staging"]


def test_create_group_missing_profile_raises(project_dir):
    _save(project_dir, "dev")
    with pytest.raises(GroupError, match="ghost"):
        create_group(project_dir, "g", ["dev", "ghost"])


def test_list_groups_empty(project_dir):
    assert list_groups(project_dir) == {}


def test_list_groups_returns_all(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    create_group(project_dir, "all", ["dev", "prod"])
    groups = list_groups(project_dir)
    assert "all" in groups
    assert set(groups["all"]) == {"dev", "prod"}


def test_delete_group(project_dir):
    _save(project_dir, "dev")
    create_group(project_dir, "g", ["dev"])
    delete_group(project_dir, "g")
    assert "g" not in list_groups(project_dir)


def test_delete_nonexistent_group_raises(project_dir):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group(project_dir, "nope")


def test_add_to_group(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "staging")
    create_group(project_dir, "g", ["dev"])
    add_to_group(project_dir, "g", "staging")
    assert "staging" in get_group(project_dir, "g")


def test_add_to_group_nonexistent_profile_raises(project_dir):
    _save(project_dir, "dev")
    create_group(project_dir, "g", ["dev"])
    with pytest.raises(GroupError, match="does not exist"):
        add_to_group(project_dir, "g", "ghost")


def test_remove_from_group(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "staging")
    create_group(project_dir, "g", ["dev", "staging"])
    remove_from_group(project_dir, "g", "staging")
    assert "staging" not in get_group(project_dir, "g")


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_create_and_list(runner, project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    result = runner.invoke(
        group_cmd, ["create", "all", "dev", "prod", "--project", str(project_dir)]
    )
    assert result.exit_code == 0
    assert "all" in result.output

    result2 = runner.invoke(group_cmd, ["list", "--project", str(project_dir)])
    assert "all" in result2.output
    assert "dev" in result2.output


def test_cli_create_missing_profile(runner, project_dir):
    result = runner.invoke(
        group_cmd, ["create", "g", "ghost", "--project", str(project_dir)]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_show_group(runner, project_dir):
    _save(project_dir, "dev")
    create_group(project_dir, "g", ["dev"])
    result = runner.invoke(group_cmd, ["show", "g", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "dev" in result.output
