"""Tests for stashenv.env_stats."""
import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.env_stats import (
    profile_stats,
    project_stats,
    format_profile_stats,
    ProfileStats,
)

PASSWORD = "test-secret"


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, content: str) -> None:
    save_profile(str(project_dir), profile, content, PASSWORD)


def test_profile_stats_basic(project_dir: Path) -> None:
    _save(project_dir, "dev", "API_KEY=abc\nDB_URL=postgres://localhost\nDEBUG=true\n")
    stats = profile_stats(str(project_dir), "dev", PASSWORD)
    assert stats.profile == "dev"
    assert stats.total_keys == 3
    assert stats.empty_values == 0


def test_profile_stats_empty_values(project_dir: Path) -> None:
    _save(project_dir, "staging", "API_KEY=\nDB_URL=postgres://host\n")
    stats = profile_stats(str(project_dir), "staging", PASSWORD)
    assert stats.total_keys == 2
    assert stats.empty_values == 1


def test_profile_stats_duplicate_values(project_dir: Path) -> None:
    _save(project_dir, "prod", "A=same\nB=same\nC=different\n")
    stats = profile_stats(str(project_dir), "prod", PASSWORD)
    assert stats.duplicate_values == 2
    assert stats.unique_values == 1


def test_profile_stats_unique_values(project_dir: Path) -> None:
    _save(project_dir, "local", "X=one\nY=two\nZ=three\n")
    stats = profile_stats(str(project_dir), "local", PASSWORD)
    assert stats.unique_values == 3
    assert stats.duplicate_values == 0


def test_profile_stats_longest_key(project_dir: Path) -> None:
    _save(project_dir, "dev", "SHORT=1\nVERY_LONG_KEY_NAME=2\n")
    stats = profile_stats(str(project_dir), "dev", PASSWORD)
    assert stats.longest_key == "VERY_LONG_KEY_NAME"


def test_project_stats_aggregates(project_dir: Path) -> None:
    _save(project_dir, "dev", "A=1\nB=2\n")
    _save(project_dir, "prod", "X=10\nY=20\nZ=30\n")
    stats = project_stats(str(project_dir), PASSWORD)
    assert stats.total_profiles == 2
    assert stats.total_keys == 5
    assert len(stats.profiles) == 2


def test_project_stats_empty_project(project_dir: Path) -> None:
    stats = project_stats(str(project_dir), PASSWORD)
    assert stats.total_profiles == 0
    assert stats.total_keys == 0
    assert stats.profiles == []


def test_format_profile_stats_output(project_dir: Path) -> None:
    _save(project_dir, "dev", "KEY=value\n")
    stats = profile_stats(str(project_dir), "dev", PASSWORD)
    output = format_profile_stats(stats)
    assert "dev" in output
    assert "Keys" in output
    assert "Empty values" in output
    assert "Duplicate" in output


def test_avg_value_length(project_dir: Path) -> None:
    _save(project_dir, "dev", "A=ab\nB=abcd\n")
    stats = profile_stats(str(project_dir), "dev", PASSWORD)
    assert stats.avg_value_length == 3.0
