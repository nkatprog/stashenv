import click
from stashenv.alias import set_alias, remove_alias, list_aliases, resolve_alias


@click.group("alias")
def alias_cmd():
    """Manage profile aliases."""
    pass


@alias_cmd.command("set")
@click.argument("alias_name")
@click.argument("profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def set_cmd(alias_name, profile, project):
    """Create an alias for a profile."""
    try:
        set_alias(project, alias_name, profile)
        click.echo(f"Alias '{alias_name}' -> '{profile}' set.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_cmd.command("remove")
@click.argument("alias_name")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def remove_cmd(alias_name, project):
    """Remove an alias."""
    remove_alias(project, alias_name)
    click.echo(f"Alias '{alias_name}' removed.")


@alias_cmd.command("list")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def list_cmd(project):
    """List all aliases."""
    aliases = list_aliases(project)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for name, profile in sorted(aliases.items()):
        click.echo(f"  {name} -> {profile}")


@alias_cmd.command("resolve")
@click.argument("alias_name")
@click.option("--project", default=".", show_default=True, help="Project directory.")
def resolve_cmd(alias_name, project):
    """Resolve an alias to its profile name."""
    profile = resolve_alias(project, alias_name)
    if profile is None:
        click.echo(f"No alias '{alias_name}' found.", err=True)
        raise SystemExit(1)
    click.echo(profile)
