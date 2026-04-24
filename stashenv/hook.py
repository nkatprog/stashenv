"""Profile lifecycle hooks — run shell commands before/after load/save."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Literal

HookEvent = Literal["pre_load", "post_load", "pre_save", "post_save"]


def _hooks_path(project_dir: Path) -> Path:
    return project_dir / ".stashenv" / "hooks.json"


def _load_hooks(project_dir: Path) -> dict[str, dict[str, str]]:
    p = _hooks_path(project_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_hooks(project_dir: Path, data: dict[str, dict[str, str]]) -> None:
    p = _hooks_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_hook(project_dir: Path, profile: str, event: HookEvent, command: str) -> None:
    """Register *command* to run on *event* for *profile*."""
    hooks = _load_hooks(project_dir)
    hooks.setdefault(profile, {})[event] = command
    _save_hooks(project_dir, hooks)


def remove_hook(project_dir: Path, profile: str, event: HookEvent) -> None:
    """Remove the hook for *event* on *profile* (no-op if absent)."""
    hooks = _load_hooks(project_dir)
    hooks.get(profile, {}).pop(event, None)
    if profile in hooks and not hooks[profile]:
        del hooks[profile]
    _save_hooks(project_dir, hooks)


def list_hooks(project_dir: Path, profile: str) -> dict[str, str]:
    """Return {event: command} mapping for *profile*."""
    return dict(_load_hooks(project_dir).get(profile, {}))


def run_hook(project_dir: Path, profile: str, event: HookEvent) -> bool:
    """Run the hook for *event* on *profile*. Returns True if a hook ran."""
    command = _load_hooks(project_dir).get(profile, {}).get(event)
    if not command:
        return False
    result = subprocess.run(command, shell=True, cwd=project_dir)
    if result.returncode != 0:
        raise RuntimeError(
            f"Hook '{event}' for profile '{profile}' exited with code {result.returncode}"
        )
    return True
