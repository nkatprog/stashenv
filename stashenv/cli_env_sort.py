"""CLI commands for sorting profile keys."""

from __future__ import annotations

import click

from stashenv.env_sort import preview_sort, sort_profile


@click.group("sort")
def sort_cmd() -> None:
    """Sort keys within a profile."""


@sort_cmd.command("run")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
@click.option("--reverse", is_flag=True, default=False, help="Sort in descending order.")
@click.option(
    "--group-prefixes",
    is_flag=True,
    default=False,
    help="Group keys by shared prefix before sorting.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview sorted key order without saving.",
)
def run_cmd(
    profile: str,
    password: str,
    project_dir: str,
    reverse: bool,
    group_prefixes: bool,
    dry_run: bool,
) -> None:
    """Sort keys in PROFILE alphabetically."""
    if dry_run:
        keys = preview_sort(
            project_dir,
            profile,
            password,
            reverse=reverse,
            group_prefixes=group_prefixes,
        )
        click.echo(f"Sorted key order for '{profile}' (dry run):")
        for key in keys:
            click.echo(f"  {key}")
        return

    sorted_data = sort_profile(
        project_dir,
        profile,
        password,
        reverse=reverse,
        group_prefixes=group_prefixes,
    )
    click.echo(
        f"Sorted {len(sorted_data)} keys in profile '{profile}'."
        + (" (reversed)" if reverse else "")
    )
