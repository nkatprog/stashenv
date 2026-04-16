"""CLI commands for copy/rename profile operations."""

import click
from pathlib import Path
from stashenv.copy import copy_profile, rename_profile


@click.command("copy")
@click.argument("src_profile")
@click.argument("dst_profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--dst-project", default=None, help="Destination project directory (defaults to same).")
@click.option("--password", prompt=True, hide_input=True, help="Password for source profile.")
@click.option("--dst-password", default=None, hide_input=True, help="Password for destination (if different).")
def copy_cmd(src_profile, dst_profile, project, dst_project, password, dst_password):
    """Copy SRC_PROFILE to DST_PROFILE."""
    src = Path(project).resolve()
    dst = Path(dst_project).resolve() if dst_project else src
    try:
        copy_profile(src, src_profile, dst, dst_profile, password, dst_password or None)
        click.echo(f"Copied '{src_profile}' -> '{dst_profile}'.")
    except FileNotFoundError:
        click.echo(f"Error: profile '{src_profile}' not found.", err=True)
        raise SystemExit(1)
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@click.command("rename")
@click.argument("old_name")
@click.argument("new_name")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
def rename_cmd(old_name, new_name, project, password):
    """Rename OLD_NAME profile to NEW_NAME."""
    proj = Path(project).resolve()
    try:
        rename_profile(proj, old_name, new_name, password)
        click.echo(f"Renamed '{old_name}' -> '{new_name}'.")
    except FileNotFoundError:
        click.echo(f"Error: profile '{old_name}' not found.", err=True)
        raise SystemExit(1)
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
