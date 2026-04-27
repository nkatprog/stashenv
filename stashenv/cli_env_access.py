"""CLI commands for profile access control."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_access import (
    AccessDeniedError,
    check_permission,
    get_permissions,
    list_access,
    revoke_access,
    set_access,
)


@click.group("access")
def access_cmd() -> None:
    """Manage read/write access control for profiles."""


@access_cmd.command("grant")
@click.argument("profile")
@click.argument("actor")
@click.argument("permissions", nargs=-1, required=True)
@click.option("--project-dir", default=".", show_default=True)
def grant_cmd(profile: str, actor: str, permissions: tuple, project_dir: str) -> None:
    """Grant ACTOR permissions (read/write) on PROFILE."""
    try:
        set_access(Path(project_dir), profile, actor, list(permissions))
        click.echo(f"Granted {list(permissions)} to '{actor}' on '{profile}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@access_cmd.command("revoke")
@click.argument("profile")
@click.argument("actor")
@click.option("--project-dir", default=".", show_default=True)
def revoke_cmd(profile: str, actor: str, project_dir: str) -> None:
    """Revoke all permissions for ACTOR on PROFILE."""
    revoke_access(Path(project_dir), profile, actor)
    click.echo(f"Revoked access for '{actor}' on '{profile}'.")


@access_cmd.command("show")
@click.argument("profile", required=False)
@click.option("--project-dir", default=".", show_default=True)
def show_cmd(profile: str | None, project_dir: str) -> None:
    """Show access control list, optionally filtered to PROFILE."""
    acl = list_access(Path(project_dir), profile)
    if not any(acl.values()):
        click.echo("No access rules defined.")
        return
    for prof, actors in acl.items():
        for actor, perms in actors.items():
            click.echo(f"{prof}  {actor}  {', '.join(perms)}")


@access_cmd.command("check")
@click.argument("profile")
@click.argument("actor")
@click.argument("permission")
@click.option("--project-dir", default=".", show_default=True)
def check_cmd(profile: str, actor: str, permission: str, project_dir: str) -> None:
    """Exit 0 if ACTOR has PERMISSION on PROFILE, else exit 1 with message."""
    try:
        check_permission(Path(project_dir), profile, actor, permission)
        click.echo(f"'{actor}' has '{permission}' on '{profile}'.")
    except AccessDeniedError as exc:
        raise click.ClickException(str(exc)) from exc
