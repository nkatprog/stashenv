"""Tests for stashenv/template.py"""

import pytest
from pathlib import Path

from stashenv.store import save_profile
from stashenv.template import render_template, render_profile, list_placeholders


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, password, content):
    save_profile(project_dir, profile, password, content)


def test_render_template_basic():
    result = render_template("Hello {{NAME}}!", {"NAME": "world"})
    assert result == "Hello world!"


def test_render_template_multiple_placeholders():
    result = render_template("{{A}} and {{B}}", {"A": "foo", "B": "bar"})
    assert result == "foo and bar"


def test_render_template_missing_key_raises():
    with pytest.raises(KeyError, match="MISSING"):
        render_template("{{MISSING}}", {})


def test_render_template_no_placeholders():
    text = "DB_HOST=localhost"
    assert render_template(text, {}) == text


def test_list_placeholders_returns_sorted_unique():
    text = "{{B}} {{A}} {{B}}"
    assert list_placeholders(text) == ["A", "B"]


def test_list_placeholders_empty():
    assert list_placeholders("no placeholders here") == []


def test_render_profile_self_substitution(project_dir):
    env_text = "BASE_URL=https://example.com\nAPI_URL={{BASE_URL}}/api"
    _save(project_dir, "prod", "secret", env_text)
    rendered = render_profile(project_dir, "prod", "secret")
    assert "API_URL=https://example.com/api" in rendered


def test_render_profile_with_extra_context(project_dir):
    env_text = "GREETING=Hello {{USER}}"
    _save(project_dir, "dev", "secret", env_text)
    rendered = render_profile(project_dir, "dev", "secret", context={"USER": "alice"})
    assert "GREETING=Hello alice" in rendered


def test_render_profile_missing_placeholder_raises(project_dir):
    env_text = "VALUE={{UNDEFINED_VAR}}"
    _save(project_dir, "bad", "secret", env_text)
    with pytest.raises(KeyError):
        render_profile(project_dir, "bad", "secret")
