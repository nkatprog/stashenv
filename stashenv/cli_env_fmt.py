"""CLI commands for formatting .env profiles."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_fmt import FormatError, format_all_profiles, format_profile


@click.group("fmt")
def fmt_cmd() -> None:
    """Format (pretty-print) stored .env profiles."""


@fmt_cmd.command("run")
@click.argument("profile")
@click.option("--project-dir", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--no-sort", is_flag=True, default=False, help="Keep original key order.")
@click.option("--strip-comments", is_flag=True, default=False)
@click.option("--strip-blanks", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False, help="Print result without saving.")
def run_cmd(
    profile: str,
    project_dir: str,
    password: str,
    no_sort: bool,
    strip_comments: bool,
    strip_blanks: bool,
    dry_run: bool,
) -> None:
    """Format a single profile."""
    from stashenv.store import load_profile, save_profile
    from stashenv.env_fmt import format_env_text

    path = Path(project_dir)
    try:
        text = load_profile(path, profile, password)
        formatted = format_env_text(
            text,
            sort_keys=not no_sort,
            strip_comments=strip_comments,
            strip_blanks=strip_blanks,
        )
        if dry_run:
            click.echo(formatted)
        else:
            save_profile(path, profile, password, formatted)
            click.echo(f"Formatted profile '{profile}'.")
    except FormatError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except FileNotFoundError:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)


@fmt_cmd.command("all")
@click.option("--project-dir", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--no-sort", is_flag=True, default=False)
@click.option("--strip-comments", is_flag=True, default=False)
@click.option("--strip-blanks", is_flag=True, default=False)
def all_cmd(
    project_dir: str,
    password: str,
    no_sort: bool,
    strip_comments: bool,
    strip_blanks: bool,
) -> None:
    """Format all profiles in the project."""
    path = Path(project_dir)
    try:
        results = format_all_profiles(
            path,
            password,
            sort_keys=not no_sort,
            strip_comments=strip_comments,
            strip_blanks=strip_blanks,
        )
        for name in results:
            click.echo(f"  formatted: {name}")
        click.echo(f"Done — {len(results)} profile(s) formatted.")
    except FormatError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
