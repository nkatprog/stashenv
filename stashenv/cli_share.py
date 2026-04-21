"""CLI commands for sharing profiles as encrypted bundles."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.share import write_share_bundle, import_share_bundle


@click.group("share")
def share_cmd() -> None:
    """Share encrypted profile bundles with others."""


@share_cmd.command("export")
@click.argument("profile")
@click.argument("output", type=click.Path())
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.password_option("--password", prompt="Profile password", confirmation_prompt=False)
@click.password_option("--share-password", prompt="Share password", confirmation_prompt=True)
@click.option("--recipient", default=None, help="Optional recipient label.")
def export_cmd(
    profile: str, output: str, project: str, password: str, share_password: str, recipient: str
) -> None:
    """Export PROFILE as an encrypted share bundle to OUTPUT file."""
    project_dir = Path(project).resolve()
    output_path = Path(output)
    try:
        write_share_bundle(project_dir, profile, password, share_password, output_path, recipient)
        click.echo(f"Profile '{profile}' exported to '{output_path}'.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:
        raise click.ClickException(f"Export failed: {exc}")


@share_cmd.command("import")
@click.argument("bundle", type=click.Path(exists=True))
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--profile", default=None, help="Override profile name.")
@click.password_option("--share-password", prompt="Share password", confirmation_prompt=False)
@click.password_option("--password", prompt="New profile password", confirmation_prompt=True)
def import_cmd(
    bundle: str, project: str, profile: str, share_password: str, password: str
) -> None:
    """Import an encrypted share bundle into this project."""
    project_dir = Path(project).resolve()
    bundle_path = Path(bundle)
    try:
        name = import_share_bundle(bundle_path, share_password, project_dir, password, profile)
        click.echo(f"Profile '{name}' imported successfully.")
    except Exception as exc:
        raise click.ClickException(f"Import failed: {exc}")
