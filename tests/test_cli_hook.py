"""Tests for stashenv.cli_hook CLI commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_hook import hook_cmd
from stashenv.hook import list_hooks


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        hook_cmd,
        ["set", "dev", "post_load", "echo hi", "--project", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "post_load" in result.output
    assert "dev" in result.output


def test_set_cmd_persists(runner: CliRunner, project_dir: Path) -> None:
    runner.invoke(
        hook_cmd,
        ["set", "staging", "pre_save", "make check", "--project", str(project_dir)],
    )
    hooks = list_hooks(project_dir, "staging")
    assert hooks.get("pre_save") == "make check"


def test_remove_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    runner.invoke(
        hook_cmd,
        ["set", "dev", "post_save", "true", "--project", str(project_dir)],
    )
    result = runner.invoke(
        hook_cmd,
        ["remove", "dev", "post_save", "--project", str(project_dir)],
    )
    assert result.exit_code == 0
    assert list_hooks(project_dir, "dev") == {}


def test_list_cmd_no_hooks(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        hook_cmd,
        ["list", "dev", "--project", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "No hooks" in result.output


def test_list_cmd_shows_hooks(runner: CliRunner, project_dir: Path) -> None:
    runner.invoke(
        hook_cmd,
        ["set", "prod", "pre_load", "vault login", "--project", str(project_dir)],
    )
    result = runner.invoke(
        hook_cmd,
        ["list", "prod", "--project", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "pre_load" in result.output
    assert "vault login" in result.output


def test_set_invalid_event(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        hook_cmd,
        ["set", "dev", "on_delete", "rm -rf /", "--project", str(project_dir)],
    )
    assert result.exit_code != 0
