"""Tests for stashenv.cli_lock."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.cli_lock import lock_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_acquire_and_status(runner, project_dir):
    result = runner.invoke(lock_cmd, ["acquire", "dev", "--project", str(project_dir), "--owner", "tester"])
    assert result.exit_code == 0
    assert "acquired" in result.output

    result = runner.invoke(lock_cmd, ["status", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "tester" in result.output


def test_acquire_conflict(runner, project_dir):
    runner.invoke(lock_cmd, ["acquire", "dev", "--project", str(project_dir), "--owner", "first"])
    result = runner.invoke(lock_cmd, ["acquire", "dev", "--project", str(project_dir), "--owner", "second"])
    assert result.exit_code != 0
    assert "first" in result.output


def test_release_cmd(runner, project_dir):
    runner.invoke(lock_cmd, ["acquire", "dev", "--project", str(project_dir)])
    result = runner.invoke(lock_cmd, ["release", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "released" in result.output

    status = runner.invoke(lock_cmd, ["status", "dev", "--project", str(project_dir)])
    assert "not locked" in status.output


def test_list_no_locks(runner, project_dir):
    result = runner.invoke(lock_cmd, ["list", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "No active locks" in result.output


def test_list_shows_locks(runner, project_dir):
    runner.invoke(lock_cmd, ["acquire", "dev", "--project", str(project_dir), "--owner", "alice"])
    runner.invoke(lock_cmd, ["acquire", "prod", "--project", str(project_dir), "--owner", "bob"])
    result = runner.invoke(lock_cmd, ["list", "--project", str(project_dir)])
    assert "dev" in result.output
    assert "prod" in result.output
