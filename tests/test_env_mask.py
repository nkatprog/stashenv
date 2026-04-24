"""Tests for stashenv.env_mask."""
import pytest
from pathlib import Path
from click.testing import CliRunner

from stashenv.store import save_profile
from stashenv.env_mask import mask_profile, format_masked, _should_mask, _mask_value
from stashenv.cli_env_mask import mask_cmd

PASSWORD = "hunter2"


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, env: dict) -> None:
    content = "\n".join(f"{k}={v}" for k, v in env.items())
    save_profile(profile, content, PASSWORD, str(project_dir))


# --- unit tests for helpers ---

def test_should_mask_known_keys():
    assert _should_mask("PASSWORD") is True
    assert _should_mask("DB_PASSWORD") is True
    assert _should_mask("API_KEY") is True
    assert _should_mask("SECRET_TOKEN") is True


def test_should_mask_safe_keys():
    assert _should_mask("HOST") is False
    assert _should_mask("PORT") is False
    assert _should_mask("DEBUG") is False


def test_should_mask_extra_patterns():
    assert _should_mask("MY_INTERNAL_KEY", extra_patterns=["INTERNAL"]) is True
    assert _should_mask("HOSTNAME", extra_patterns=["INTERNAL"]) is False


def test_mask_value_full():
    result = _mask_value("supersecret", reveal_chars=0)
    assert "s" not in result
    assert set(result) == {"*"}


def test_mask_value_partial():
    result = _mask_value("supersecret", reveal_chars=3)
    assert result.startswith("sup")
    assert result.endswith("*")
    assert len(result) == len("supersecret")


def test_mask_value_empty_string():
    assert _mask_value("", reveal_chars=4) == ""


# --- integration tests ---

def test_mask_profile_hides_sensitive(project_dir):
    _save(project_dir, "dev", {"HOST": "localhost", "DB_PASSWORD": "s3cr3t"})
    result = mask_profile("dev", PASSWORD, str(project_dir))
    assert result.masked["HOST"] == "localhost"
    assert result.masked["DB_PASSWORD"] != "s3cr3t"
    assert "*" in result.masked["DB_PASSWORD"]


def test_mask_profile_show_all(project_dir):
    _save(project_dir, "dev", {"HOST": "localhost", "SECRET": "topsecret"})
    result = mask_profile("dev", PASSWORD, str(project_dir), show_all=True)
    assert result.masked["SECRET"] == "topsecret"
    assert "SECRET" in result.revealed_keys


def test_format_masked_contains_profile_name(project_dir):
    _save(project_dir, "prod", {"HOST": "example.com"})
    result = mask_profile("prod", PASSWORD, str(project_dir))
    output = format_masked(result)
    assert "prod" in output
    assert "HOST=example.com" in output


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_show_masks_secret(runner, project_dir):
    _save(project_dir, "staging", {"APP_HOST": "staging.example.com", "API_KEY": "abc123"})
    result = runner.invoke(
        mask_cmd,
        ["show", "staging", "--password", PASSWORD, "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "APP_HOST=staging.example.com" in result.output
    assert "abc123" not in result.output
    assert "masked" in result.output


def test_cli_show_nonexistent_profile(runner, project_dir):
    result = runner.invoke(
        mask_cmd,
        ["show", "ghost", "--password", PASSWORD, "--project-dir", str(project_dir)],
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output
