import pytest
from click.testing import CliRunner
from stashenv.cli_compare import compare_cmd
from stashenv.store import save_profile


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def test_compare_equal_profiles(runner, project_dir):
    save_profile(project_dir, "dev", "KEY=val\n", "pw")
    save_profile(project_dir, "staging", "KEY=val\n", "pw")
    result = runner.invoke(
        compare_cmd, ["run", "dev", "staging",
                      "--project-a", project_dir, "--project-b", project_dir,
                      "--password-a", "pw", "--password-b", "pw"]
    )
    assert result.exit_code == 0
    assert "equal" in result.output


def test_compare_nonexistent_profile(runner, project_dir):
    save_profile(project_dir, "dev", "KEY=val\n", "pw")
    result = runner.invoke(
        compare_cmd, ["run", "dev", "ghost",
                      "--project-a", project_dir, "--project-b", project_dir,
                      "--password-a", "pw", "--password-b", "pw"]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_compare_wrong_password(runner, project_dir):
    save_profile(project_dir, "dev", "KEY=val\n", "pw")
    save_profile(project_dir, "staging", "KEY=val\n", "pw")
    result = runner.invoke(
        compare_cmd, ["run", "dev", "staging",
                      "--project-a", project_dir, "--project-b", project_dir,
                      "--password-a", "pw", "--password-b", "wrong"]
    )
    assert result.exit_code != 0


def test_compare_summary_line(runner, project_dir):
    save_profile(project_dir, "a", "X=1\nY=2\n", "pw")
    save_profile(project_dir, "b", "X=1\nZ=3\n", "pw")
    result = runner.invoke(
        compare_cmd, ["run", "a", "b",
                      "--project-a", project_dir, "--project-b", project_dir,
                      "--password-a", "pw", "--password-b", "pw"]
    )
    assert result.exit_code == 0
    assert "Summary" in result.output
