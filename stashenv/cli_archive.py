"""CLI commands for archiving and unarchiving profiles."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.archive import archive_profile, unarchive_profile, list_archived_profiles


@click.group("archive")
def archive_cmd() -> None:
    """Archive and restore profiles."""


@archive_cmd.command("store")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.option(
    "--project", default=".", show_default=True, help="Project directory."
)
def store_cmd(profile: str, password: str, project: str) -> None:
    """Archive PROFILE (moves it out of active use)."""
    try:
        archive_profile(Path(project), profile, password)
        click.echo(f"Profile '{profile}' archived.")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except FileExistsError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_cmd.command("restore")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def restore_cmd(profile: str, password: str, project: str) -> None:
    """Restore PROFILE from the archive back to active profiles."""
    try:
        unarchive_profile(Path(project), profile, password)
        click.echo(f"Profile '{profile}' restored from archive.")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except FileExistsError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_cmd.command("list")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(project: str) -> None:
    """List all archived profiles."""
    profiles = list_archived_profiles(Path(project))
    if not profiles:
        click.echo("No archived profiles.")
    else:
        for name in profiles:
            click.echo(name)
