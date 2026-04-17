import pytest
from pathlib import Path
from stashenv.store import save_profile
from stashenv.search import search_profiles, format_search_results

PASSWORD = "searchpass"


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, content):
    save_profile(project_dir, profile, content, PASSWORD)


def test_search_finds_key(project_dir):
    _save(project_dir, "dev", "DATABASE_URL=postgres://localhost\nDEBUG=true\n")
    results = search_profiles(project_dir, PASSWORD, "DATABASE")
    assert "dev" in results
    assert any(k == "DATABASE_URL" for k, _ in results["dev"])


def test_search_no_match(project_dir):
    _save(project_dir, "dev", "FOO=bar\n")
    results = search_profiles(project_dir, PASSWORD, "NONEXISTENT")
    assert results == {}


def test_search_across_multiple_profiles(project_dir):
    _save(project_dir, "dev", "API_KEY=abc\nHOST=localhost\n")
    _save(project_dir, "prod", "API_KEY=xyz\nPORT=443\n")
    results = search_profiles(project_dir, PASSWORD, "API_KEY")
    assert "dev" in results
    assert "prod" in results


def test_search_values(project_dir):
    _save(project_dir, "dev", "SECRET=mysecretvalue\n")
    results = search_profiles(project_dir, PASSWORD, "mysecret", search_values=True)
    assert "dev" in results


def test_search_values_disabled_by_default(project_dir):
    _save(project_dir, "dev", "SECRET=mysecretvalue\n")
    results = search_profiles(project_dir, PASSWORD, "mysecret", search_values=False)
    assert results == {}


def test_format_results_no_matches():
    assert format_search_results({}) == "No matches found."


def test_format_results_hides_values():
    results = {"dev": [("API_KEY", "secret123")]}
    output = format_search_results(results, reveal_values=False)
    assert "***" in output
    assert "secret123" not in output


def test_format_results_reveals_values():
    results = {"dev": [("API_KEY", "secret123")]}
    output = format_search_results(results, reveal_values=True)
    assert "secret123" in output


def test_search_wrong_password_skips_profile(project_dir):
    _save(project_dir, "dev", "KEY=val\n")
    results = search_profiles(project_dir, "wrongpass", "KEY")
    assert results == {}
