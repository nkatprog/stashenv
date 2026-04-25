"""CLI commands for managing profile groups."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_group import (
    GroupError,
    add_to_group,
    create_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)


@click.group("group")
def group_cmd():
    """Manage named profile groups."""


@group_cmd.command("create")
@click.argument("group")
@click.argument("profiles", nargs=-1, required=True)
@click.option("--project", default=".", show_default=True, help="Project directory.")
def create_cmd(group: str, profiles: tuple, project: str):
    """Create a named group containing PROFILES."""
    try:
        create_group(Path(project), group, list(profiles))
        click.echo(f"Group '{group}' created with profiles: {', '.join(profiles)}")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("group")
@click.option("--project", default=".", show_default=True)
def delete_cmd(group: str, project: str):
    """Delete a named group."""
    try:
        delete_group(Path(project), group)
        click.echo(f"Group '{group}' deleted.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("list")
@click.option("--project", default=".", show_default=True)
def list_cmd(project: str):
    """List all groups and their profiles."""
    groups = list_groups(Path(project))
    if not groups:
        click.echo("No groups defined.")
        return
    for name, profiles in groups.items():
        click.echo(f"{name}: {', '.join(profiles)}")


@group_cmd.command("show")
@click.argument("group")
@click.option("--project", default=".", show_default=True)
def show_cmd(group: str, project: str):
    """Show profiles in a group."""
    try:
        profiles = get_group(Path(project), group)
        click.echo("\n".join(profiles))
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("add")
@click.argument("group")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
def add_cmd(group: str, profile: str, project: str):
    """Add a profile to an existing group."""
    try:
        add_to_group(Path(project), group, profile)
        click.echo(f"Added '{profile}' to group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("remove")
@click.argument("group")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
def remove_cmd(group: str, profile: str, project: str):
    """Remove a profile from a group."""
    try:
        remove_from_group(Path(project), group, profile)
        click.echo(f"Removed '{profile}' from group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
