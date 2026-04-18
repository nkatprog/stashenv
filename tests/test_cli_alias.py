import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.cli_alias import alias_cmd
from stashenv.store import save_profile


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    save_profile(str(tmp_path), "production", "SECRET=abc\nDEBUG=false\n", "pass")
    save_profile(str(tmp_path), "staging", "SECRET=xyz\nDEBUG=true\n", "pass")
    return tmp_path


def test_set_alias(runner, project_dir):
    result = runner.invoke(alias_cmd, ["set", "prod", "production", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "production" in result.output


def test_set_alias_nonexistent_profile(runner, project_dir):
    result = runner.invoke(alias_cmd, ["set", "ghost", "nonexistent", "--project", str(project_dir)])
    assert result.exit_code != 0


def test_list_aliases(runner, project_dir):
    runner.invoke(alias_cmd, ["set", "prod", "production", "--project", str(project_dir)])
    runner.invoke(alias_cmd, ["set", "stg", "staging", "--project", str(project_dir)])
    result = runner.invoke(alias_cmd, ["list", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "stg" in result.output


def test_list_aliases_empty(runner, project_dir):
    result = runner.invoke(alias_cmd, ["list", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_remove_alias(runner, project_dir):
    runner.invoke(alias_cmd, ["set", "prod", "production", "--project", str(project_dir)])
    result = runner.invoke(alias_cmd, ["remove", "prod", "--project", str(project_dir)])
    assert result.exit_code == 0
    list_result = runner.invoke(alias_cmd, ["list", "--project", str(project_dir)])
    assert "prod" not in list_result.output


def test_resolve_alias(runner, project_dir):
    runner.invoke(alias_cmd, ["set", "prod", "production", "--project", str(project_dir)])
    result = runner.invoke(alias_cmd, ["resolve", "prod", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "production" in result.output


def test_resolve_unknown_alias(runner, project_dir):
    result = runner.invoke(alias_cmd, ["resolve", "unknown", "--project", str(project_dir)])
    assert result.exit_code != 0
