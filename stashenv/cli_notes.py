"""CLI commands for managing per-profile notes."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.notes import set_note, get_note, clear_note, list_notes


@click.group("notes")
def notes_cmd():
    """Manage notes attached to profiles."""


@notes_cmd.command("set")
@click.argument("profile")
@click.argument("note")
@click.option("--project", default=".", help="Project directory.")
def set_cmd(profile: str, note: str, project: str):
    """Set a note for a profile."""
    try:
        set_note(Path(project), profile, note)
        click.echo(f"Note set for profile '{profile}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@notes_cmd.command("get")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory.")
def get_cmd(profile: str, project: str):
    """Get the note for a profile."""
    note = get_note(Path(project), profile)
    if note is None:
        click.echo(f"No note set for profile '{profile}'.")
    else:
        click.echo(note)


@notes_cmd.command("clear")
@click.argument("profile")
@click.option("--project", default=".", help="Project directory.")
def clear_cmd(profile: str, project: str):
    """Clear the note for a profile."""
    clear_note(Path(project), profile)
    click.echo(f"Note cleared for profile '{profile}'.")


@notes_cmd.command("list")
@click.option("--project", default=".", help="Project directory.")
def list_cmd(project: str):
    """List all profile notes."""
    notes = list_notes(Path(project))
    if not notes:
        click.echo("No notes found.")
        return
    for profile, note in notes.items():
        click.echo(f"{profile}: {note}")
