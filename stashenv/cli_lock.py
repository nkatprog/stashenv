"""CLI commands for profile locking."""

import click
from pathlib import Path

from stashenv.lock import acquire_lock, release_lock, get_lock_info, list_locks


@click.group("lock")
def lock_cmd():
    """Manage profile locks."""


@lock_cmd.command("acquire")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory")
@click.option("--owner", default=None, help="Lock owner label")
def acquire_cmd(profile, project, owner):
    """Acquire a lock on a profile."""
    project_dir = Path(project).resolve()
    success = acquire_lock(project_dir, profile, owner=owner)
    if success:
        click.echo(f"Lock acquired on profile '{profile}'.")
    else:
        info = get_lock_info(project_dir, profile)
        click.echo(
            f"Profile '{profile}' is already locked by '{info['owner']}' "
            f"({info['age_seconds']}s ago).",
            err=True,
        )
        raise SystemExit(1)


@lock_cmd.command("release")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory")
def release_cmd(profile, project):
    """Release a lock on a profile."""
    project_dir = Path(project).resolve()
    release_lock(project_dir, profile)
    click.echo(f"Lock released on profile '{profile}'.")


@lock_cmd.command("status")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory")
def status_cmd(profile, project):
    """Show lock status for a profile."""
    project_dir = Path(project).resolve()
    info = get_lock_info(project_dir, profile)
    if info:
        click.echo(f"Locked by '{info['owner']}' ({info['age_seconds']}s ago).")
    else:
        click.echo(f"Profile '{profile}' is not locked.")


@lock_cmd.command("list")
@click.option("--project", default=".", help="Project directory")
def list_cmd(project):
    """List all active locks in a project."""
    project_dir = Path(project).resolve()
    locks = list_locks(project_dir)
    if not locks:
        click.echo("No active locks.")
    else:
        for lock in locks:
            click.echo(f"{lock['profile']}: owner='{lock['owner']}', age={lock['age_seconds']}s")
