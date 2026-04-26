"""CLI commands for managing per-project env key defaults."""
from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_default import (
    apply_defaults,
    get_default,
    list_defaults,
    remove_default,
    set_default,
)


@click.group("default")
def default_cmd() -> None:
    """Manage default values for env keys."""


@default_cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def set_cmd(key: str, value: str, project: str) -> None:
    """Register a default VALUE for KEY."""
    set_default(Path(project), key, value)
    click.echo(f"Default set: {key}={value}")


@default_cmd.command("remove")
@click.argument("key")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def remove_cmd(key: str, project: str) -> None:
    """Remove the registered default for KEY."""
    remove_default(Path(project), key)
    click.echo(f"Default removed for key: {key}")


@default_cmd.command("get")
@click.argument("key")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def get_cmd(key: str, project: str) -> None:
    """Show the registered default for KEY."""
    value = get_default(Path(project), key)
    if value is None:
        click.echo(f"No default registered for key: {key}")
    else:
        click.echo(f"{key}={value}")


@default_cmd.command("list")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(project: str) -> None:
    """List all registered defaults."""
    defaults = list_defaults(Path(project))
    if not defaults:
        click.echo("No defaults registered.")
        return
    for key, value in sorted(defaults.items()):
        click.echo(f"{key}={value}")


@default_cmd.command("apply")
@click.argument("profile")
@click.password_option("--password", prompt=True, confirmation_prompt=False)
@click.option("--project", default=".", show_default=True, help="Project directory.")
def apply_cmd(profile: str, password: str, project: str) -> None:
    """Apply registered defaults to PROFILE, filling missing keys."""
    filled = apply_defaults(Path(project), profile, password)
    if not filled:
        click.echo("No missing keys to fill.")
    else:
        click.echo(f"Filled {len(filled)} key(s): {', '.join(filled)}")
