"""Main CLI entry point for stashenv."""

import click
from pathlib import Path
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile
from stashenv.cli_export import export_cmd, import_cmd
from stashenv.cli_copy import copy_cmd, rename_cmd


@click.group()
def cli():
    """stashenv — securely store and switch between .env profiles."""


@cli.command("save")
@click.argument("profile")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--project", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def save(profile, env_file, project, password):
    """Save ENV_FILE as PROFILE."""
    data = Path(env_file).read_bytes()
    save_profile(Path(project).resolve(), profile, data, password)
    click.echo(f"Saved profile '{profile}'.")


@cli.command("load")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
@click.option("--output", default=".env", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def load(profile, project, output, password):
    """Load PROFILE into OUTPUT file."""
    try:
        data = load_profile(Path(project).resolve(), profile, password)
        Path(output).write_bytes(data)
        click.echo(f"Loaded profile '{profile}' into '{output}'.")
    except FileNotFoundError:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Error: decryption failed. Wrong password?", err=True)
        raise SystemExit(1)


@cli.command("list")
@click.option("--project", default=".", show_default=True)
def list_cmd(project):
    """List saved profiles."""
    profiles = list_profiles(Path(project).resolve())
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(p)


@cli.command("delete")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
@click.confirmation_option(prompt="Are you sure?")
def delete(profile, project):
    """Delete a PROFILE."""
    try:
        delete_profile(Path(project).resolve(), profile)
        click.echo(f"Deleted profile '{profile}'.")
    except FileNotFoundError:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)


@cli.command("show")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def show(profile, project, password):
    """Decrypt and print PROFILE contents to stdout."""
    try:
        data = load_profile(Path(project).resolve(), profile, password)
        click.echo(data.decode())
    except FileNotFoundError:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Error: decryption failed. Wrong password?", err=True)
        raise SystemExit(1)


cli.add_command(export_cmd)
cli.add_command(import_cmd)
cli.add_command(copy_cmd)
cli.add_command(rename_cmd)


if __name__ == "__main__":
    cli()
