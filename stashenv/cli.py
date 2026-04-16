import sys
import os
import click
from stashenv.store import save_profile, load_profile, list_profiles, delete_profile


@click.group()
def cli():
    """stashenv — securely store and switch between .env profiles."""
    pass


@cli.command("save")
@click.argument("name")
@click.option("--env-file", default=".env", show_default=True, help="Path to .env file to stash.")
@click.password_option(prompt="Encryption password", help="Password to encrypt the profile.")
def save(name, env_file, password):
    """Save a .env file as a named profile."""
    env_path = os.path.abspath(env_file)
    if not os.path.exists(env_path):
        click.echo(f"Error: file '{env_file}' not found.", err=True)
        sys.exit(1)
    with open(env_path, "rb") as f:
        data = f.read()
    project_dir = os.getcwd()
    save_profile(project_dir, name, data, password)
    click.echo(f"Profile '{name}' saved.")


@cli.command("load")
@click.argument("name")
@click.option("--env-file", default=".env", show_default=True, help="Path to write the .env file.")
@click.password_option(prompt="Encryption password", confirmation_prompt=False, help="Password to decrypt the profile.")
def load(name, env_file, password):
    """Load a named profile into a .env file."""
    project_dir = os.getcwd()
    try:
        data = load_profile(project_dir, name, password)
    except FileNotFoundError:
        click.echo(f"Error: profile '{name}' not found.", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    with open(env_file, "wb") as f:
        f.write(data)
    click.echo(f"Profile '{name}' loaded into '{env_file}'.")


@cli.command("list")
def list_cmd():
    """List saved profiles for the current project."""
    project_dir = os.getcwd()
    profiles = list_profiles(project_dir)
    if not profiles:
        click.echo("No profiles saved for this project.")
    else:
        click.echo("Saved profiles:")
        for p in profiles:
            click.echo(f"  - {p}")


@cli.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
def delete(name):
    """Delete a named profile."""
    project_dir = os.getcwd()
    try:
        delete_profile(project_dir, name)
        click.echo(f"Profile '{name}' deleted.")
    except FileNotFoundError:
        click.echo(f"Error: profile '{name}' not found.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
