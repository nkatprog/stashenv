"""Unit tests for stashenv.promote."""

from pathlib import Path

import pytest

from stashenv.promote import DEFAULT_PIPELINE, _next_tier, promote_profile
from stashenv.store import load_profile, save_profile


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, name: str, content: str, password: str = "pw") -> None:
    save_profile(project_dir, name, content, password)


# ---------------------------------------------------------------------------
# _next_tier
# ---------------------------------------------------------------------------

def test_next_tier_returns_correct_successor() -> None:
    assert _next_tier("dev", DEFAULT_PIPELINE) == "staging"
    assert _next_tier("staging", DEFAULT_PIPELINE) == "prod"


def test_next_tier_last_raises() -> None:
    with pytest.raises(ValueError, match="last tier"):
        _next_tier("prod", DEFAULT_PIPELINE)


def test_next_tier_unknown_raises() -> None:
    with pytest.raises(ValueError, match="not part of the pipeline"):
        _next_tier("unknown", DEFAULT_PIPELINE)


# ---------------------------------------------------------------------------
# promote_profile
# ---------------------------------------------------------------------------

def test_promote_copies_content(project_dir: Path) -> None:
    _save(project_dir, "dev", "KEY=value\n")
    dest = promote_profile(project_dir, "dev", "pw")
    assert dest == "staging"
    assert load_profile(project_dir, "staging", "pw") == "KEY=value\n"


def test_promote_explicit_target(project_dir: Path) -> None:
    _save(project_dir, "dev", "A=1\n")
    dest = promote_profile(project_dir, "dev", "pw", target_profile="production")
    assert dest == "production"
    assert load_profile(project_dir, "production", "pw") == "A=1\n"


def test_promote_with_different_target_password(project_dir: Path) -> None:
    _save(project_dir, "dev", "SECRET=xyz\n")
    promote_profile(project_dir, "dev", "pw", target_password="newpw")
    assert load_profile(project_dir, "staging", "newpw") == "SECRET=xyz\n"


def test_promote_existing_target_raises_without_overwrite(project_dir: Path) -> None:
    _save(project_dir, "dev", "K=1\n")
    _save(project_dir, "staging", "K=OLD\n")
    with pytest.raises(FileExistsError, match="already exists"):
        promote_profile(project_dir, "dev", "pw")


def test_promote_overwrite_replaces_target(project_dir: Path) -> None:
    _save(project_dir, "dev", "K=NEW\n")
    _save(project_dir, "staging", "K=OLD\n")
    promote_profile(project_dir, "dev", "pw", overwrite=True)
    assert load_profile(project_dir, "staging", "pw") == "K=NEW\n"


def test_promote_custom_pipeline(project_dir: Path) -> None:
    _save(project_dir, "alpha", "X=1\n")
    dest = promote_profile(project_dir, "alpha", "pw", pipeline=["alpha", "beta", "gamma"])
    assert dest == "beta"
