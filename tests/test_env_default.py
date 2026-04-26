"""Tests for stashenv.env_default."""
from __future__ import annotations

import pytest
from pathlib import Path

from stashenv.env_default import (
    apply_defaults,
    get_default,
    list_defaults,
    remove_default,
    set_default,
)
from stashenv.store import save_profile, load_profile


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, data: dict, password: str = "pw") -> None:
    save_profile(project_dir, profile, password, data)


def test_set_and_get_default(project_dir: Path) -> None:
    set_default(project_dir, "LOG_LEVEL", "INFO")
    assert get_default(project_dir, "LOG_LEVEL") == "INFO"


def test_get_default_none_when_not_set(project_dir: Path) -> None:
    assert get_default(project_dir, "MISSING_KEY") is None


def test_set_default_overwrites_existing(project_dir: Path) -> None:
    set_default(project_dir, "LOG_LEVEL", "DEBUG")
    set_default(project_dir, "LOG_LEVEL", "WARNING")
    assert get_default(project_dir, "LOG_LEVEL") == "WARNING"


def test_remove_default(project_dir: Path) -> None:
    set_default(project_dir, "LOG_LEVEL", "INFO")
    remove_default(project_dir, "LOG_LEVEL")
    assert get_default(project_dir, "LOG_LEVEL") is None


def test_remove_nonexistent_default_is_noop(project_dir: Path) -> None:
    remove_default(project_dir, "GHOST_KEY")  # should not raise


def test_list_defaults_empty(project_dir: Path) -> None:
    assert list_defaults(project_dir) == {}


def test_list_defaults_multiple(project_dir: Path) -> None:
    set_default(project_dir, "A", "1")
    set_default(project_dir, "B", "2")
    result = list_defaults(project_dir)
    assert result == {"A": "1", "B": "2"}


def test_apply_defaults_fills_missing_keys(project_dir: Path) -> None:
    _save(project_dir, "dev", {"EXISTING": "yes"}, password="pw")
    set_default(project_dir, "LOG_LEVEL", "INFO")
    set_default(project_dir, "EXISTING", "overwritten?")

    filled = apply_defaults(project_dir, "dev", "pw")

    assert filled == ["LOG_LEVEL"]
    data = load_profile(project_dir, "dev", "pw")
    assert data["LOG_LEVEL"] == "INFO"
    assert data["EXISTING"] == "yes"  # existing value must not be overwritten


def test_apply_defaults_no_defaults_returns_empty(project_dir: Path) -> None:
    _save(project_dir, "dev", {"KEY": "val"}, password="pw")
    filled = apply_defaults(project_dir, "dev", "pw")
    assert filled == []


def test_apply_defaults_all_present_returns_empty(project_dir: Path) -> None:
    _save(project_dir, "dev", {"LOG_LEVEL": "DEBUG"}, password="pw")
    set_default(project_dir, "LOG_LEVEL", "INFO")
    filled = apply_defaults(project_dir, "dev", "pw")
    assert filled == []
