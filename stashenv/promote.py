"""Promote a profile from one environment tier to another (e.g. dev -> staging -> prod)."""

from __future__ import annotations

from pathlib import Path

from stashenv.store import load_profile, save_profile, list_profiles

DEFAULT_PIPELINE = ["dev", "staging", "prod"]


def _next_tier(current: str, pipeline: list[str]) -> str:
    """Return the next tier after *current* in *pipeline*."""
    try:
        idx = pipeline.index(current)
    except ValueError:
        raise ValueError(f"Profile '{current}' is not part of the pipeline: {pipeline}")
    if idx + 1 >= len(pipeline):
        raise ValueError(f"Profile '{current}' is already the last tier in the pipeline.")
    return pipeline[idx + 1]


def promote_profile(
    project_dir: Path,
    source_profile: str,
    password: str,
    target_profile: str | None = None,
    target_password: str | None = None,
    pipeline: list[str] | None = None,
    overwrite: bool = False,
) -> str:
    """Copy *source_profile* to the next tier (or *target_profile*) and return the target name.

    Parameters
    ----------
    project_dir:     Root directory of the project.
    source_profile:  Name of the profile to promote.
    password:        Password used to decrypt *source_profile*.
    target_profile:  Explicit target name; inferred from *pipeline* when omitted.
    target_password: Password for the target profile; reuses *password* when omitted.
    pipeline:        Ordered list of tier names; defaults to DEFAULT_PIPELINE.
    overwrite:       Allow overwriting an existing target profile.
    """
    pipeline = pipeline or DEFAULT_PIPELINE
    if target_profile is None:
        target_profile = _next_tier(source_profile, pipeline)

    if not overwrite and target_profile in list_profiles(project_dir):
        raise FileExistsError(
            f"Profile '{target_profile}' already exists. Use overwrite=True to replace it."
        )

    env_text = load_profile(project_dir, source_profile, password)
    save_profile(project_dir, target_profile, env_text, target_password or password)
    return target_profile
