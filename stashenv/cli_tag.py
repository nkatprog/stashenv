"""CLI commands for tagging profiles."""
import click
from stashenv.tag import add_tag, remove_tag, list_tags, profiles_by_tag


@click.group("tag")
def tag_cmd():
    """Manage tags on profiles."""


@tag_cmd.command("add")
@click.argument("profile")
@click.argument("tag")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def add_cmd(profile: str, tag: str, project: str):
    """Add a tag to a profile."""
    try:
        add_tag(project, profile, tag)
        click.echo(f"Tag '{tag}' added to profile '{profile}'.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tag_cmd.command("remove")
@click.argument("profile")
@click.argument("tag")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def remove_cmd(profile: str, tag: str, project: str):
    """Remove a tag from a profile."""
    try:
        remove_tag(project, profile, tag)
        click.echo(f"Tag '{tag}' removed from profile '{profile}'.")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tag_cmd.command("list")
@click.argument("profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(profile: str, project: str):
    """List tags on a profile."""
    tags = list_tags(project, profile)
    if tags:
        click.echo("\n".join(tags))
    else:
        click.echo(f"No tags on profile '{profile}'.")


@tag_cmd.command("find")
@click.argument("tag")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def find_cmd(tag: str, project: str):
    """Find profiles with a given tag."""
    profiles = profiles_by_tag(project, tag)
    if profiles:
        click.echo("\n".join(profiles))
    else:
        click.echo(f"No profiles found with tag '{tag}'.")
