"""CLI commands for managing inline env-key comments."""

from pathlib import Path

import click

from stashenv.env_comment import (
    CommentError,
    format_comments,
    get_comment,
    list_comments,
    remove_comment,
    set_comment,
)


@click.group("comment")
def comment_cmd() -> None:
    """Manage inline comments on profile keys."""


@comment_cmd.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("comment")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--project", default=".", show_default=True)
def set_cmd(profile: str, key: str, comment: str, password: str, project: str) -> None:
    """Attach COMMENT to KEY in PROFILE."""
    try:
        set_comment(Path(project), profile, key, comment, password)
        click.echo(f"Comment set on '{key}' in profile '{profile}'.")
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@comment_cmd.command("get")
@click.argument("profile")
@click.argument("key")
@click.option("--project", default=".", show_default=True)
def get_cmd(profile: str, key: str, project: str) -> None:
    """Show the comment for KEY in PROFILE."""
    value = get_comment(Path(project), profile, key)
    if value is None:
        click.echo(f"(no comment for '{key}')")
    else:
        click.echo(f"{key}: {value}")


@comment_cmd.command("remove")
@click.argument("profile")
@click.argument("key")
@click.option("--project", default=".", show_default=True)
def remove_cmd(profile: str, key: str, project: str) -> None:
    """Remove the comment for KEY in PROFILE."""
    remove_comment(Path(project), profile, key)
    click.echo(f"Comment removed from '{key}' in profile '{profile}'.")


@comment_cmd.command("list")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
def list_cmd(profile: str, project: str) -> None:
    """List all comments in PROFILE."""
    comments = list_comments(Path(project), profile)
    click.echo(format_comments(comments))
