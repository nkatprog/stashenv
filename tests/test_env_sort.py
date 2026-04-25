"""Tests for stashenv.env_sort."""

from __future__ import annotations

import pytest

from stashenv.env_sort import SortError, preview_sort, sort_profile
from stashenv.store import load_profile, save_profile


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, data, password="secret"):
    save_profile(project_dir, profile, password, data)


def test_sort_profile_alphabetically(project_dir):
    _save(project_dir, "dev", {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"})
    result = sort_profile(project_dir, "dev", "secret")
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_profile_persists_to_disk(project_dir):
    _save(project_dir, "dev", {"Z": "1", "A": "2", "M": "3"})
    sort_profile(project_dir, "dev", "secret")
    loaded = load_profile(project_dir, "dev", "secret")
    assert list(loaded.keys()) == ["A", "M", "Z"]


def test_sort_profile_reverse(project_dir):
    _save(project_dir, "dev", {"APPLE": "1", "ZEBRA": "2", "MANGO": "3"})
    result = sort_profile(project_dir, "dev", "secret", reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_profile_group_prefixes(project_dir):
    data = {
        "DB_HOST": "localhost",
        "APP_NAME": "myapp",
        "DB_PORT": "5432",
        "APP_ENV": "dev",
    }
    _save(project_dir, "dev", data)
    result = sort_profile(project_dir, "dev", "secret", group_prefixes=True)
    keys = list(result.keys())
    # APP group before DB group (alphabetical prefix order)
    assert keys.index("APP_ENV") < keys.index("DB_HOST")
    assert keys.index("APP_NAME") < keys.index("DB_HOST")
    # Within groups, sorted alphabetically
    assert keys.index("APP_ENV") < keys.index("APP_NAME")
    assert keys.index("DB_HOST") < keys.index("DB_PORT")


def test_preview_sort_does_not_modify_disk(project_dir):
    original = {"Z": "1", "A": "2"}
    _save(project_dir, "dev", original)
    keys = preview_sort(project_dir, "dev", "secret")
    assert keys == ["A", "Z"]
    # Original order on disk should be unchanged
    loaded = load_profile(project_dir, "dev", "secret")
    assert list(loaded.keys()) == ["Z", "A"]


def test_preview_sort_reverse(project_dir):
    _save(project_dir, "dev", {"A": "1", "B": "2", "C": "3"})
    keys = preview_sort(project_dir, "dev", "secret", reverse=True)
    assert keys == ["C", "B", "A"]


def test_sort_single_key_profile(project_dir):
    _save(project_dir, "dev", {"ONLY_KEY": "value"})
    result = sort_profile(project_dir, "dev", "secret")
    assert list(result.keys()) == ["ONLY_KEY"]


def test_sort_empty_profile(project_dir):
    _save(project_dir, "dev", {})
    result = sort_profile(project_dir, "dev", "secret")
    assert result == {}
