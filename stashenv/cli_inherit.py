"""CLI commands for profile inheritance."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.inherit import apply_base_to_all, inherit_profile


@click.group("inherit")
def inherit_cmd() -> None:
    """Apply a base profile's values as defaults to child profiles."""


@inherit_cmd.command("apply")
@click.argument("base_profile")
@click.argument("child_profile")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Child profile password.")
@click.option("--base-password", default=None, hide_input=True, help="Base profile password (if different).")
@click.option("--override", is_flag=True, default=False, help="Base values overwrite child values.")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
def apply_cmd(
    base_profile: str,
    child_profile: str,
    password: str,
    base_password: str | None,
    override: bool,
    project_dir: str,
) -> None:
    """Merge BASE_PROFILE defaults into CHILD_PROFILE."""
    project = Path(project_dir).resolve()
    try:
        merged = inherit_profile(
            project,
            base_profile=base_profile,
            child_profile=child_profile,
            password=password,
            base_password=base_password,
            override=override,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Merged '{base_profile}' into '{child_profile}' ({len(merged)} keys total)."
    )


@inherit_cmd.command("apply-all")
@click.argument("base_profile")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Shared profile password.")
@click.option("--override", is_flag=True, default=False, help="Base values overwrite child values.")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
def apply_all_cmd(
    base_profile: str,
    password: str,
    override: bool,
    project_dir: str,
) -> None:
    """Apply BASE_PROFILE defaults to all other profiles in the project."""
    project = Path(project_dir).resolve()
    try:
        results = apply_base_to_all(
            project,
            base_profile=base_profile,
            password=password,
            override=override,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if not results:
        click.echo("No other profiles found to update.")
        return

    for name, merged in results.items():
        click.echo(f"  Updated '{name}' ({len(merged)} keys).")
    click.echo(f"Applied '{base_profile}' to {len(results)} profile(s).")
