"""CLI commands for freezing/unfreezing profiles."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_freeze import (
    FreezeError,
    freeze_profile,
    is_frozen,
    list_frozen,
    unfreeze_profile,
)


@click.group("freeze")
def freeze_cmd() -> None:
    """Freeze or unfreeze profiles to prevent accidental changes."""


@freeze_cmd.command("set")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory.", show_default=True)
def set_cmd(profile: str, project: str) -> None:
    """Freeze a profile."""
    try:
        freeze_profile(Path(project), profile)
        click.echo(f"Profile '{profile}' is now frozen.")
    except FreezeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@freeze_cmd.command("unset")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory.", show_default=True)
def unset_cmd(profile: str, project: str) -> None:
    """Unfreeze a profile."""
    unfreeze_profile(Path(project), profile)
    click.echo(f"Profile '{profile}' has been unfrozen.")


@freeze_cmd.command("status")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory.", show_default=True)
def status_cmd(profile: str, project: str) -> None:
    """Show freeze status of a profile."""
    frozen = is_frozen(Path(project), profile)
    state = "frozen" if frozen else "not frozen"
    click.echo(f"Profile '{profile}' is {state}.")


@freeze_cmd.command("list")
@click.option("--project", default=".", help="Project directory.", show_default=True)
def list_cmd(project: str) -> None:
    """List all frozen profiles."""
    profiles = list_frozen(Path(project))
    if not profiles:
        click.echo("No frozen profiles.")
    else:
        for name in profiles:
            click.echo(name)
