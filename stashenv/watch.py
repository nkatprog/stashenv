"""Watch a .env file for changes and auto-save to a profile."""
from __future__ import annotations
import time
import os
from pathlib import Path
from typing import Callable, Optional
from stashenv.store import save_profile
from stashenv.export import env_to_dict


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def watch_env_file(
    env_file: Path,
    project_dir: Path,
    profile: str,
    password: str,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
    on_change: Optional[Callable[[str], None]] = None,
) -> None:
    """Poll *env_file* and save to *profile* whenever it changes.

    Args:
        env_file: Path to the .env file to watch.
        project_dir: Project directory for the stash store.
        profile: Profile name to save changes under.
        password: Encryption password.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (useful for testing).
        on_change: Optional callback called with a status message on each save.
    """
    last_mtime = _mtime(env_file)
    iterations = 0

    while True:
        time.sleep(interval)
        current_mtime = _mtime(env_file)

        if current_mtime != last_mtime:
            last_mtime = current_mtime
            try:
                env_text = env_file.read_text()
                env_dict = env_to_dict(env_text)
                from stashenv.export import dict_to_env
                save_profile(project_dir, profile, password, dict_to_env(env_dict))
                msg = f"[watch] Saved '{profile}' from {env_file}"
            except Exception as exc:
                msg = f"[watch] Error saving '{profile}': {exc}"
            if on_change:
                on_change(msg)

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
