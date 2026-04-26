"""Tests for stashenv.env_count."""

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.env_count import (
    count_profile,
    count_all_profiles,
    format_count,
    ProfileCount,
)

PASSWORD = "test-secret"


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, content: str) -> None:
    save_profile(project_dir, profile, content, PASSWORD)


def test_count_profile_basic(project_dir: Path) -> None:
    _save(project_dir, "dev", "FOO=bar\nBAZ=qux\n")
    result = count_profile(project_dir, "dev", PASSWORD)
    assert result.profile == "dev"
    assert result.total == 2
    assert result.non_empty == 2
    assert result.empty == 0


def test_count_profile_with_empty_values(project_dir: Path) -> None:
    _save(project_dir, "staging", "FOO=bar\nEMPTY=\nANOTHER=value\n")
    result = count_profile(project_dir, "staging", PASSWORD)
    assert result.total == 3
    assert result.empty == 1
    assert result.non_empty == 2


def test_count_profile_ignores_comments_and_blanks(project_dir: Path) -> None:
    content = "# this is a comment\n\nFOO=bar\n   \nBAZ=1\n"
    _save(project_dir, "prod", content)
    result = count_profile(project_dir, "prod", PASSWORD)
    assert result.total == 2


def test_count_all_profiles(project_dir: Path) -> None:
    _save(project_dir, "dev", "A=1\nB=2\n")
    _save(project_dir, "prod", "X=\nY=yes\nZ=no\n")
    summary = count_all_profiles(project_dir, PASSWORD)
    assert summary.total_profiles == 2
    assert summary.grand_total_keys == 5


def test_count_all_profiles_with_filter(project_dir: Path) -> None:
    _save(project_dir, "dev", "A=1\n")
    _save(project_dir, "dev-debug", "B=2\nC=3\n")
    _save(project_dir, "prod", "X=1\n")
    summary = count_all_profiles(project_dir, PASSWORD, profile_filter="dev")
    names = [p.profile for p in summary.profiles]
    assert "dev" in names
    assert "dev-debug" in names
    assert "prod" not in names


def test_count_all_profiles_empty_project(project_dir: Path) -> None:
    summary = count_all_profiles(project_dir, PASSWORD)
    assert summary.total_profiles == 0
    assert summary.grand_total_keys == 0


def test_format_count_renders_table(project_dir: Path) -> None:
    _save(project_dir, "dev", "A=1\nB=\n")
    summary = count_all_profiles(project_dir, PASSWORD)
    output = format_count(summary)
    assert "dev" in output
    assert "Total" in output or "TOTAL" in output
    assert "2" in output


def test_format_count_no_profiles(project_dir: Path) -> None:
    summary = count_all_profiles(project_dir, PASSWORD)
    output = format_count(summary)
    assert "No profiles found" in output
