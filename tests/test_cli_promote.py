"""CLI tests for the promote command."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_promote import promote_cmd
from stashenv.store import load_profile, save_profile


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, name: str, content: str, password: str = "pw") -> None:
    save_profile(project_dir, name, content, password)


def test_promote_success(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev", "FOO=bar\n")
    result = runner.invoke(
        promote_cmd,
        ["run", "dev", "--password", "pw", "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0, result.output
    assert "dev" in result.output and "staging" in result.output
    assert load_profile(project_dir, "staging", "pw") == "FOO=bar\n"


def test_promote_explicit_target(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev", "BAR=1\n")
    result = runner.invoke(
        promote_cmd,
        ["run", "dev", "--password", "pw", "--target", "prod", "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0, result.output
    assert "prod" in result.output


def test_promote_conflict_without_overwrite(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev", "K=1\n")
    _save(project_dir, "staging", "K=OLD\n")
    result = runner.invoke(
        promote_cmd,
        ["run", "dev", "--password", "pw", "--project-dir", str(project_dir)],
    )
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_promote_overwrite_flag(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev", "K=NEW\n")
    _save(project_dir, "staging", "K=OLD\n")
    result = runner.invoke(
        promote_cmd,
        ["run", "dev", "--password", "pw", "--overwrite", "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0, result.output
    assert load_profile(project_dir, "staging", "pw") == "K=NEW\n"


def test_promote_nonexistent_profile(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        promote_cmd,
        ["run", "ghost", "--password", "pw", "--project-dir", str(project_dir)],
    )
    assert result.exit_code != 0
