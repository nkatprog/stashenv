"""Tests for stashenv.inherit."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.store import save_profile, load_profile
from stashenv.inherit import inherit_profile, apply_base_to_all
from stashenv.cli_inherit import inherit_cmd

PASSWORD = "testpass"


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, name: str, env: dict, password: str = PASSWORD) -> None:
    save_profile(project_dir, name, env, password)


# ---------------------------------------------------------------------------
# Unit tests for inherit_profile
# ---------------------------------------------------------------------------

def test_inherit_child_values_take_precedence(project_dir: Path) -> None:
    _save(project_dir, "base", {"KEY": "base_val", "BASE_ONLY": "yes"})
    _save(project_dir, "child", {"KEY": "child_val", "CHILD_ONLY": "yes"})

    merged = inherit_profile(project_dir, "base", "child", PASSWORD)

    assert merged["KEY"] == "child_val"        # child wins
    assert merged["BASE_ONLY"] == "yes"        # inherited from base
    assert merged["CHILD_ONLY"] == "yes"       # kept from child


def test_inherit_override_base_wins(project_dir: Path) -> None:
    _save(project_dir, "base", {"KEY": "base_val"})
    _save(project_dir, "child", {"KEY": "child_val"})

    merged = inherit_profile(project_dir, "base", "child", PASSWORD, override=True)

    assert merged["KEY"] == "base_val"  # base overrides child


def test_inherit_saves_merged_to_child(project_dir: Path) -> None:
    _save(project_dir, "base", {"NEW_KEY": "from_base"})
    _save(project_dir, "child", {"CHILD_KEY": "mine"})

    inherit_profile(project_dir, "base", "child", PASSWORD)

    reloaded = load_profile(project_dir, "child", PASSWORD)
    assert reloaded["NEW_KEY"] == "from_base"
    assert reloaded["CHILD_KEY"] == "mine"


def test_inherit_same_profile_raises(project_dir: Path) -> None:
    _save(project_dir, "base", {"KEY": "val"})
    with pytest.raises(ValueError, match="different"):
        inherit_profile(project_dir, "base", "base", PASSWORD)


def test_inherit_missing_profile_raises(project_dir: Path) -> None:
    _save(project_dir, "base", {"KEY": "val"})
    with pytest.raises(FileNotFoundError):
        inherit_profile(project_dir, "base", "ghost", PASSWORD)


# ---------------------------------------------------------------------------
# Unit tests for apply_base_to_all
# ---------------------------------------------------------------------------

def test_apply_base_to_all_updates_others(project_dir: Path) -> None:
    _save(project_dir, "base", {"SHARED": "shared_val"})
    _save(project_dir, "dev", {"DEV_KEY": "dev"})
    _save(project_dir, "prod", {"PROD_KEY": "prod"})

    results = apply_base_to_all(project_dir, "base", PASSWORD)

    assert set(results.keys()) == {"dev", "prod"}
    assert results["dev"]["SHARED"] == "shared_val"
    assert results["prod"]["SHARED"] == "shared_val"


def test_apply_base_to_all_skips_base(project_dir: Path) -> None:
    _save(project_dir, "base", {"KEY": "val"})
    _save(project_dir, "other", {"OTHER": "x"})

    results = apply_base_to_all(project_dir, "base", PASSWORD)
    assert "base" not in results


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_apply_merges_profiles(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "base", {"BASE_KEY": "bval"})
    _save(project_dir, "child", {"CHILD_KEY": "cval"})

    result = runner.invoke(
        inherit_cmd,
        ["apply", "base", "child", "--password", PASSWORD, "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0, result.output
    assert "Merged" in result.output

    reloaded = load_profile(project_dir, "child", PASSWORD)
    assert reloaded["BASE_KEY"] == "bval"


def test_cli_apply_nonexistent_profile(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "base", {"KEY": "val"})

    result = runner.invoke(
        inherit_cmd,
        ["apply", "base", "ghost", "--password", PASSWORD, "--project-dir", str(project_dir)],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
