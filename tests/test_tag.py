"""Tests for stashenv.tag and stashenv.cli_tag."""
import pytest
from click.testing import CliRunner
from stashenv.store import save_profile
from stashenv.tag import add_tag, remove_tag, list_tags, profiles_by_tag
from stashenv.cli_tag import tag_cmd


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, name, password="pass"):
    save_profile(project_dir, name, "KEY=val\n", password)


def test_add_and_list_tag(project_dir):
    _save(project_dir, "dev")
    add_tag(project_dir, "dev", "production")
    assert "production" in list_tags(project_dir, "dev")


def test_add_duplicate_tag_is_idempotent(project_dir):
    _save(project_dir, "dev")
    add_tag(project_dir, "dev", "ci")
    add_tag(project_dir, "dev", "ci")
    assert list_tags(project_dir, "dev").count("ci") == 1


def test_remove_tag(project_dir):
    _save(project_dir, "dev")
    add_tag(project_dir, "dev", "ci")
    remove_tag(project_dir, "dev", "ci")
    assert "ci" not in list_tags(project_dir, "dev")


def test_remove_nonexistent_tag_raises(project_dir):
    _save(project_dir, "dev")
    with pytest.raises(ValueError):
        remove_tag(project_dir, "dev", "ghost")


def test_add_tag_nonexistent_profile_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        add_tag(project_dir, "missing", "ci")


def test_profiles_by_tag(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "staging")
    add_tag(project_dir, "dev", "cloud")
    add_tag(project_dir, "staging", "cloud")
    result = profiles_by_tag(project_dir, "cloud")
    assert set(result) == {"dev", "staging"}


def test_profiles_by_tag_no_match(project_dir):
    _save(project_dir, "dev")
    assert profiles_by_tag(project_dir, "nope") == []


def test_cli_add_and_find(project_dir):
    runner = CliRunner()
    _save(project_dir, "prod")
    result = runner.invoke(tag_cmd, ["add", "prod", "live", "--project", project_dir])
    assert result.exit_code == 0
    result = runner.invoke(tag_cmd, ["find", "live", "--project", project_dir])
    assert "prod" in result.output


def test_cli_list_no_tags(project_dir):
    runner = CliRunner()
    _save(project_dir, "dev")
    result = runner.invoke(tag_cmd, ["list", "dev", "--project", project_dir])
    assert "No tags" in result.output
