import pytest
from click.testing import CliRunner
from stashenv.cli_search import search_cmd
from stashenv.store import save_profile

PASSWORD = "clipass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, content):
    save_profile(project_dir, profile, content, PASSWORD)


def test_search_finds_key(runner, project_dir):
    _save(project_dir, "dev", "API_KEY=abc\nHOST=localhost\n")
    result = runner.invoke(
        search_cmd,
        ["API_KEY", "--project", project_dir, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "abc" not in result.output  # hidden by default


def test_search_reveal_values(runner, project_dir):
    _save(project_dir, "dev", "TOKEN=supersecret\n")
    result = runner.invoke(
        search_cmd,
        ["TOKEN", "--project", project_dir, "--password", PASSWORD, "--reveal"],
    )
    assert result.exit_code == 0
    assert "supersecret" in result.output


def test_search_no_match(runner, project_dir):
    _save(project_dir, "dev", "FOO=bar\n")
    result = runner.invoke(
        search_cmd,
        ["MISSING", "--project", project_dir, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "No matches found" in result.output


def test_search_values_flag(runner, project_dir):
    _save(project_dir, "dev", "SECRET=needle\n")
    result = runner.invoke(
        search_cmd,
        ["needle", "--project", project_dir, "--password", PASSWORD, "--values", "--reveal"],
    )
    assert result.exit_code == 0
    assert "SECRET" in result.output
