"""Tests for stashenv.share and stashenv.cli_share."""

from __future__ import annotations

import json
import base64
from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.store import save_profile, load_profile
from stashenv.share import create_share_bundle, write_share_bundle, import_share_bundle
from stashenv.cli_share import share_cmd


ENV_TEXT = "DB_HOST=localhost\nDB_PORT=5432\n"
PASSWORD = "secret"
SHARE_PASSWORD = "sharepass"


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    d = tmp_path / "project"
    d.mkdir()
    save_profile(d, "prod", ENV_TEXT, PASSWORD)
    return d


def test_create_share_bundle_returns_json(project_dir: Path) -> None:
    bundle_bytes = create_share_bundle(project_dir, "prod", PASSWORD, SHARE_PASSWORD)
    bundle = json.loads(bundle_bytes)
    assert bundle["profile"] == "prod"
    assert "data" in bundle
    assert bundle["recipient"] is None


def test_create_share_bundle_with_recipient(project_dir: Path) -> None:
    bundle_bytes = create_share_bundle(project_dir, "prod", PASSWORD, SHARE_PASSWORD, "alice")
    bundle = json.loads(bundle_bytes)
    assert bundle["recipient"] == "alice"


def test_import_share_bundle_roundtrip(project_dir: Path, tmp_path: Path) -> None:
    bundle_path = tmp_path / "prod.bundle"
    write_share_bundle(project_dir, "prod", PASSWORD, SHARE_PASSWORD, bundle_path)
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    name = import_share_bundle(bundle_path, SHARE_PASSWORD, dest_dir, "newpass")
    assert name == "prod"
    result = load_profile(dest_dir, "prod", "newpass")
    assert result == ENV_TEXT


def test_import_with_profile_override(project_dir: Path, tmp_path: Path) -> None:
    bundle_path = tmp_path / "prod.bundle"
    write_share_bundle(project_dir, "prod", PASSWORD, SHARE_PASSWORD, bundle_path)
    dest_dir = tmp_path / "dest2"
    dest_dir.mkdir()
    name = import_share_bundle(bundle_path, SHARE_PASSWORD, dest_dir, "newpass", "staging")
    assert name == "staging"
    result = load_profile(dest_dir, "staging", "newpass")
    assert result == ENV_TEXT


def test_import_wrong_share_password_raises(project_dir: Path, tmp_path: Path) -> None:
    bundle_path = tmp_path / "prod.bundle"
    write_share_bundle(project_dir, "prod", PASSWORD, SHARE_PASSWORD, bundle_path)
    dest_dir = tmp_path / "dest3"
    dest_dir.mkdir()
    with pytest.raises(Exception):
        import_share_bundle(bundle_path, "wrongpass", dest_dir, "newpass")


def test_import_missing_bundle_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        import_share_bundle(tmp_path / "missing.bundle", SHARE_PASSWORD, tmp_path, "pass")


def test_cli_export_and_import(project_dir: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    bundle_path = tmp_path / "out.bundle"
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    result = runner.invoke(
        share_cmd,
        ["export", "prod", str(bundle_path),
         "--project", str(project_dir),
         "--password", PASSWORD,
         "--share-password", SHARE_PASSWORD],
    )
    assert result.exit_code == 0, result.output
    assert bundle_path.exists()

    result = runner.invoke(
        share_cmd,
        ["import", str(bundle_path),
         "--project", str(dest_dir),
         "--share-password", SHARE_PASSWORD,
         "--password", "destpass"],
    )
    assert result.exit_code == 0, result.output
    assert "prod" in result.output
    loaded = load_profile(dest_dir, "prod", "destpass")
    assert loaded == ENV_TEXT
