"""CLI commands for snapshot management."""

from pathlib import Path

import click

from stashenv.snapshot import create_snapshot, delete_snapshot, list_snapshots, restore_snapshot


@click.group("snapshot")
def snapshot_cmd():
    """Manage project env snapshots."""


@snapshot_cmd.command("create")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--label", default=None, help="Optional snapshot label.")
@click.password_option("--password", prompt="Password")
def create_cmd(project, label, password):
    """Capture all profiles into a snapshot."""
    try:
        sid = create_snapshot(Path(project), password, label)
        click.echo(f"Snapshot created: {sid}")
    except FileExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(project):
    """List available snapshots."""
    snaps = list_snapshots(Path(project))
    if not snaps:
        click.echo("No snapshots found.")
    else:
        for s in snaps:
            click.echo(s)


@snapshot_cmd.command("restore")
@click.argument("snapshot_id")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.password_option("--password", prompt="Password")
def restore_cmd(snapshot_id, project, password):
    """Restore profiles from a snapshot."""
    try:
        restored = restore_snapshot(Path(project), snapshot_id, password)
        click.echo(f"Restored profiles: {', '.join(restored)}")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("snapshot_id")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def delete_cmd(snapshot_id, project):
    """Delete a snapshot."""
    try:
        delete_snapshot(Path(project), snapshot_id)
        click.echo(f"Snapshot '{snapshot_id}' deleted.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
