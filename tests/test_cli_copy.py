import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.store import save_profile
from stashenv.cli_copy import copy_cmd, rename_cmd


DATA = b"KEY=val\n"
PASSWORD = "secret"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_copy_cmd_success(runner, project_dir):
    save_profile(project_dir, "dev", DATA, PASSWORD)
    result = runner.invoke(
        copy_cmd,
        ["dev", "dev-copy", "--project", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Copied" in result.output


def test_copy_cmd_nonexistent(runner, project_dir):
    result = runner.invoke(
        copy_cmd,
        ["ghost", "copy", "--project", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_copy_cmd_conflict(runner, project_dir):
    """Copying to an already-existing profile name should fail."""
    save_profile(project_dir, "dev", DATA, PASSWORD)
    save_profile(project_dir, "dev-copy", DATA, PASSWORD)
    result = runner.invoke(
        copy_cmd,
        ["dev", "dev-copy", "--project", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rename_cmd_success(runner, project_dir):
    save_profile(project_dir, "staging", DATA, PASSWORD)
    result = runner.invoke(
        rename_cmd,
        ["staging", "stage", "--project", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Renamed" in result.output


def test_rename_cmd_conflict(runner, project_dir):
    save_profile(project_dir, "a", DATA, PASSWORD)
    save_profile(project_dir, "b", DATA, PASSWORD)
    result = runner.invoke(
        rename_cmd,
        ["a", "b", "--project", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 1
    assert "Error" in result.output
