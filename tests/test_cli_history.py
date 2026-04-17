"""Tests for stashenv.cli_history."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.cli_history import history_cmd
from stashenv.history import record_change


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_show_empty_history(runner, project_dir):
    result = runner.invoke(history_cmd, ["show", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_show_history_with_records(runner, project_dir):
    record_change(project_dir, "prod", "save")
    result = runner.invoke(history_cmd, ["show", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "save" in result.output


def test_show_filtered_by_profile(runner, project_dir):
    record_change(project_dir, "prod", "save")
    record_change(project_dir, "dev", "rotate")
    result = runner.invoke(history_cmd, ["show", "--project", str(project_dir), "--profile", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" not in result.output


def test_clear_all_history(runner, project_dir):
    record_change(project_dir, "prod", "save")
    result = runner.invoke(history_cmd, ["clear", "--project", str(project_dir)], input="y\n")
    assert result.exit_code == 0
    assert "Cleared 1 record(s)" in result.output


def test_clear_profile_history(runner, project_dir):
    record_change(project_dir, "prod", "save")
    record_change(project_dir, "dev", "save")
    result = runner.invoke(
        history_cmd,
        ["clear", "--project", str(project_dir), "--profile", "prod"],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "Cleared 1 record(s)" in result.output
