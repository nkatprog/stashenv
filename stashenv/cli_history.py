"""CLI commands for profile change history."""
import click
from pathlib import Path

from stashenv.history import get_history, clear_history, format_history


@click.group("history")
def history_cmd():
    """View and manage profile change history."""


@history_cmd.command("show")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--profile", default=None, help="Filter by profile name.")
def show_cmd(project: str, profile: str | None):
    """Show change history for the project."""
    records = get_history(Path(project), profile=profile)
    click.echo(format_history(records))


@history_cmd.command("clear")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--profile", default=None, help="Clear history only for this profile.")
@click.confirmation_option(prompt="Are you sure you want to clear history?")
def clear_cmd(project: str, profile: str | None):
    """Clear change history."""
    removed = clear_history(Path(project), profile=profile)
    target = f"profile '{profile}'" if profile else "all profiles"
    click.echo(f"Cleared {removed} record(s) for {target}.")
