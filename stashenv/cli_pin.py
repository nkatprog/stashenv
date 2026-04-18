"""CLI commands for profile pinning."""
import click
from pathlib import Path
from stashenv.pin import pin_profile, unpin_profile, get_pinned


@click.group("pin")
def pin_cmd():
    """Pin or inspect the active profile for a project."""


@pin_cmd.command("set")
@click.argument("profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def set_cmd(profile: str, project: str):
    """Pin PROFILE as the active profile."""
    try:
        pin_profile(Path(project), profile)
        click.echo(f"Pinned '{profile}' as active profile.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@pin_cmd.command("unset")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def unset_cmd(project: str):
    """Remove the pinned profile."""
    unpin_profile(Path(project))
    click.echo("Pinned profile removed.")


@pin_cmd.command("status")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def status_cmd(project: str):
    """Show the currently pinned profile."""
    pinned = get_pinned(Path(project))
    if pinned:
        click.echo(f"Pinned profile: {pinned}")
    else:
        click.echo("No profile is currently pinned.")
