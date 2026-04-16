"""CLI commands for exporting and importing .env profiles."""

import os
import click

from stashenv.export import export_profile, import_profile


@click.command("export")
@click.argument("profile")
@click.argument("output", default=".env")
@click.option("--password", envvar="STASHENV_PASSWORD", prompt=True, hide_input=True,
              help="Encryption password.")
@click.option("--project", default=None, help="Project directory (default: cwd).")
def export_cmd(profile: str, output: str, password: str, project: str) -> None:
    """Decrypt PROFILE and write it to OUTPUT (default: .env)."""
    project = project or os.getcwd()
    try:
        export_profile(project, profile, password, output)
        click.echo(f"Exported '{profile}' to {output}")
    except FileNotFoundError:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@click.command("import")
@click.argument("profile")
@click.argument("input_file", default=".env")
@click.option("--password", envvar="STASHENV_PASSWORD", prompt=True, hide_input=True,
              help="Encryption password.")
@click.option("--project", default=None, help="Project directory (default: cwd).")
def import_cmd(profile: str, input_file: str, password: str, project: str) -> None:
    """Read INPUT_FILE (default: .env) and store it as PROFILE."""
    project = project or os.getcwd()
    try:
        import_profile(project, profile, password, input_file)
        click.echo(f"Imported '{input_file}' as profile '{profile}'")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
