"""CLI commands for renaming keys within a profile."""

from __future__ import annotations

import click

from stashenv.env_rename import KeyRenameError, rename_key


@click.group("rename-key")
def rename_key_cmd() -> None:
    """Rename keys within a stored profile."""


@rename_key_cmd.command("run")
@click.argument("profile")
@click.argument("old_key")
@click.argument("new_key")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    help="Profile encryption password.",
)
@click.option(
    "--project-dir",
    default=".",
    show_default=True,
    help="Project directory containing the stashenv store.",
)
def run_cmd(
    profile: str,
    old_key: str,
    new_key: str,
    password: str,
    project_dir: str,
) -> None:
    """Rename OLD_KEY to NEW_KEY inside PROFILE."""
    try:
        rename_key(project_dir, profile, old_key, new_key, password)
    except KeyRenameError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Renamed '{old_key}' → '{new_key}' in profile '{profile}'.")
