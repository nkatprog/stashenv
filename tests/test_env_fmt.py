"""Tests for stashenv.env_fmt."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.env_fmt import FormatError, format_env_text, format_profile, format_all_profiles
from stashenv.store import save_profile, load_profile
from stashenv.cli_env_fmt import fmt_cmd


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, name: str, text: str, pw: str = "pw") -> None:
    save_profile(project_dir, name, pw, text)


# ── format_env_text ──────────────────────────────────────────────────────────

def test_format_sorts_keys():
    text = "ZEBRA=1\nAPPLE=2\nMIDDLE=3"
    result = format_env_text(text, sort_keys=True)
    lines = result.splitlines()
    assert lines == ["APPLE=2", "MIDDLE=3", "ZEBRA=1"]


def test_format_no_sort_preserves_order():
    text = "ZEBRA=1\nAPPLE=2"
    result = format_env_text(text, sort_keys=False)
    assert result.splitlines() == ["ZEBRA=1", "APPLE=2"]


def test_format_strips_extra_spaces():
    text = "  KEY  =  value  "
    result = format_env_text(text, sort_keys=False)
    assert result == "KEY=value"


def test_format_strip_comments():
    text = "# comment\nKEY=val"
    result = format_env_text(text, sort_keys=False, strip_comments=True)
    assert "#" not in result
    assert "KEY=val" in result


def test_format_strip_blanks():
    text = "KEY=val\n\nOTHER=x"
    result = format_env_text(text, sort_keys=False, strip_blanks=True)
    assert "\n\n" not in result


def test_format_invalid_line_raises():
    with pytest.raises(FormatError):
        format_env_text("NOEQUALSSIGN", sort_keys=False)


# ── format_profile ────────────────────────────────────────────────────────────

def test_format_profile_saves_sorted(project_dir: Path):
    _save(project_dir, "dev", "Z=1\nA=2")
    formatted = format_profile(project_dir, "dev", "pw")
    assert formatted.splitlines()[0].startswith("A=")
    # Verify it was persisted
    stored = load_profile(project_dir, "dev", "pw")
    assert stored == formatted


def test_format_all_profiles(project_dir: Path):
    _save(project_dir, "dev", "Z=1\nA=2")
    _save(project_dir, "prod", "Y=9\nB=3")
    results = format_all_profiles(project_dir, "pw")
    assert set(results.keys()) == {"dev", "prod"}
    for text in results.values():
        lines = [l for l in text.splitlines() if l.strip()]
        assert lines == sorted(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_run_cmd_formats_profile(runner: CliRunner, project_dir: Path):
    _save(project_dir, "dev", "Z=1\nA=2")
    result = runner.invoke(
        fmt_cmd,
        ["run", "dev", "--project-dir", str(project_dir), "--password", "pw"],
    )
    assert result.exit_code == 0
    assert "dev" in result.output


def test_run_cmd_dry_run_does_not_save(runner: CliRunner, project_dir: Path):
    original = "Z=1\nA=2"
    _save(project_dir, "dev", original)
    runner.invoke(
        fmt_cmd,
        ["run", "dev", "--project-dir", str(project_dir), "--password", "pw", "--dry-run"],
    )
    stored = load_profile(project_dir, "dev", "pw")
    assert stored == original


def test_run_cmd_nonexistent_profile(runner: CliRunner, project_dir: Path):
    result = runner.invoke(
        fmt_cmd,
        ["run", "ghost", "--project-dir", str(project_dir), "--password", "pw"],
    )
    assert result.exit_code != 0


def test_all_cmd_formats_all(runner: CliRunner, project_dir: Path):
    _save(project_dir, "dev", "Z=1\nA=2")
    _save(project_dir, "prod", "Y=9\nB=3")
    result = runner.invoke(
        fmt_cmd,
        ["all", "--project-dir", str(project_dir), "--password", "pw"],
    )
    assert result.exit_code == 0
    assert "2 profile(s)" in result.output
