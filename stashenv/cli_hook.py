"""CLI commands for managing profile lifecycle hooks."""
from __future__ import annotations

import click
from pathlib import Path

from stashenv.hook import set_hook, remove_hook, list_hooks, HookEvent

VALID_EVENTS: list[HookEvent] = ["pre_load", "post_load", "pre_save", "post_save"]


@click.group("hook")
def hook_cmd() -> None:
    """Manage lifecycle hooks for profiles."""


@hook_cmd.command("set")
@click.argument("profile")
@click.argument("event", type=click.Choice(VALID_EVENTS))
@click.argument("command")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def set_cmd(profile: str, event: str, command: str, project: str) -> None:
    """Register COMMAND to run on EVENT for PROFILE."""
    project_dir = Path(project).resolve()
    set_hook(project_dir, profile, event, command)  # type: ignore[arg-type]
    click.echo(f"Hook set: [{event}] {profile} -> {command!r}")


@hook_cmd.command("remove")
@click.argument("profile")
@click.argument("event", type=click.Choice(VALID_EVENTS))
@click.option("--project", default=".", show_default=True, help="Project directory.")
def remove_cmd(profile: str, event: str, project: str) -> None:
    """Remove the hook for EVENT on PROFILE."""
    project_dir = Path(project).resolve()
    remove_hook(project_dir, profile, event)  # type: ignore[arg-type]
    click.echo(f"Hook removed: [{event}] {profile}")


@hook_cmd.command("list")
@click.argument("profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(profile: str, project: str) -> None:
    """List all hooks registered for PROFILE."""
    project_dir = Path(project).resolve()
    hooks = list_hooks(project_dir, profile)
    if not hooks:
        click.echo(f"No hooks registered for profile '{profile}'.")
        return
    for event, command in sorted(hooks.items()):
        click.echo(f"  {event:<12} {command}")
