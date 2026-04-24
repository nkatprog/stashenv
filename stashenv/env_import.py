"""env_import.py — Import environment variables from system environment or shell into a profile.

Provides utilities to capture the current process environment (or a subset),
filter and sanitize the variables, and persist them as a named stashenv profile.
"""

from __future__ import annotations

import os
import re
from typing import Optional

from stashenv.store import save_profile, list_profiles

# Keys that are almost certainly not useful to store in a project profile.
_SYSTEM_KEY_PATTERNS = [
    re.compile(r"^(PATH|MANPATH|INFOPATH|DYLD_.*)$"),
    re.compile(r"^(TERM|TERM_PROGRAM|TERM_SESSION_ID|COLORTERM)$"),
    re.compile(r"^(SHELL|SHLVL|OLDPWD|PWD|HOME|USER|LOGNAME|TMPDIR|TEMPDIR)$"),
    re.compile(r"^(DISPLAY|XAUTHORITY|DBUS_SESSION_BUS_ADDRESS)$"),
    re.compile(r"^(APPLE_.*|__CF_.*)$"),
    re.compile(r"^(SSH_.*|GPG_AGENT_INFO)$"),
    re.compile(r"^(LS_COLORS|LSCOLORS|CLICOLOR.*)$"),
    re.compile(r"^(_$)"),  # last command
]


class EnvImportError(Exception):
    """Raised when an import operation cannot be completed."""


def _is_system_key(key: str) -> bool:
    """Return True if *key* looks like a system / shell bookkeeping variable."""
    return any(pat.match(key) for pat in _SYSTEM_KEY_PATTERNS)


def capture_env(
    *,
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
    skip_system: bool = True,
    prefix: Optional[str] = None,
    strip_prefix: bool = False,
) -> dict[str, str]:
    """Capture environment variables from the current process.

    Args:
        include: If given, only these keys are captured (exact match).
        exclude: Keys to always omit.
        skip_system: When True, well-known shell/system keys are filtered out.
        prefix: If given, only keys starting with this prefix are captured.
        strip_prefix: When True and *prefix* is set, the prefix is removed
            from the captured key names.

    Returns:
        A dict of captured key→value pairs.
    """
    exclude_set: set[str] = set(exclude or [])
    result: dict[str, str] = {}

    for key, value in os.environ.items():
        # Explicit include list takes priority.
        if include is not None:
            if key not in include:
                continue
        else:
            if skip_system and _is_system_key(key):
                continue
            if prefix and not key.startswith(prefix):
                continue

        if key in exclude_set:
            continue

        captured_key = key
        if prefix and strip_prefix and key.startswith(prefix):
            captured_key = key[len(prefix):]
            if not captured_key:  # key was exactly the prefix
                continue

        result[captured_key] = value

    return result


def import_from_env(
    project_dir: str,
    profile: str,
    password: str,
    *,
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
    skip_system: bool = True,
    prefix: Optional[str] = None,
    strip_prefix: bool = False,
    overwrite: bool = False,
) -> dict[str, str]:
    """Capture variables from the current environment and save them as a profile.

    Args:
        project_dir: Root directory of the project whose stash to write into.
        profile: Name of the profile to create or overwrite.
        password: Encryption password for the profile.
        include: Explicit list of keys to capture.
        exclude: Keys to omit.
        skip_system: Filter out well-known system variables.
        prefix: Only capture keys with this prefix.
        strip_prefix: Remove the prefix from key names before saving.
        overwrite: If False (default) and the profile already exists, raise.

    Returns:
        The dict of captured variables that were stored.

    Raises:
        EnvImportError: If the profile already exists and *overwrite* is False,
            or if no variables were captured.
    """
    if not overwrite and profile in list_profiles(project_dir):
        raise EnvImportError(
            f"Profile '{profile}' already exists. Pass overwrite=True to replace it."
        )

    captured = capture_env(
        include=include,
        exclude=exclude,
        skip_system=skip_system,
        prefix=prefix,
        strip_prefix=strip_prefix,
    )

    if not captured:
        raise EnvImportError(
            "No environment variables matched the given filters; nothing was saved."
        )

    # Encode as .env content: KEY=VALUE lines.
    env_content = "\n".join(f"{k}={v}" for k, v in sorted(captured.items())) + "\n"
    save_profile(project_dir, profile, password, env_content.encode())
    return captured
