"""Tag profiles with labels for easier organization and filtering."""
from __future__ import annotations
import json
from pathlib import Path
from stashenv.store import _stash_dir, list_profiles


def _tags_path(project_dir: str) -> Path:
    return _stash_dir(project_dir) / "tags.json"


def _load_tags(project_dir: str) -> dict[str, list[str]]:
    path = _tags_path(project_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_tags(project_dir: str, tags: dict[str, list[str]]) -> None:
    path = _tags_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tags, indent=2))


def add_tag(project_dir: str, profile: str, tag: str) -> None:
    profiles = list_profiles(project_dir)
    if profile not in profiles:
        raise FileNotFoundError(f"Profile '{profile}' not found.")
    tags = _load_tags(project_dir)
    profile_tags = tags.setdefault(profile, [])
    if tag not in profile_tags:
        profile_tags.append(tag)
    _save_tags(project_dir, tags)


def remove_tag(project_dir: str, profile: str, tag: str) -> None:
    tags = _load_tags(project_dir)
    profile_tags = tags.get(profile, [])
    if tag not in profile_tags:
        raise ValueError(f"Tag '{tag}' not found on profile '{profile}'.")
    profile_tags.remove(tag)
    tags[profile] = profile_tags
    _save_tags(project_dir, tags)


def list_tags(project_dir: str, profile: str) -> list[str]:
    tags = _load_tags(project_dir)
    return tags.get(profile, [])


def profiles_by_tag(project_dir: str, tag: str) -> list[str]:
    tags = _load_tags(project_dir)
    return [profile for profile, ptags in tags.items() if tag in ptags]
