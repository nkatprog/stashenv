"""CLI commands for applying a profile diff onto another profile."""

from __future__ import annotations

import click

from stashenv.env_diff_apply import apply_diff


@click.group("apply-diff")
def apply_diff_cmd() -> None:
    """Apply changes from one profile onto another."""


@apply_diff_cmd.command("run")
@click.argument("base_profile")
@click.argument("target_profile")
@click.option("--base-project", default=".", show_default=True, help="Source project directory.")
@click.option("--target-project", default=".", show_default=True, help="Target project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
@click.option(
    "--strategy",
    type=click.Choice(["ours", "theirs"]),
    default="ours",
    show_default=True,
    help="Conflict resolution strategy.",
)
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without saving.")
def run_cmd(
    base_profile: str,
    target_profile: str,
    base_project: str,
    target_project: str,
    password: str,
    strategy: str,
    dry_run: bool,
) -> None:
    """Apply diff from BASE_PROFILE onto TARGET_PROFILE."""
    try:
        result = apply_diff(
            base_project,
            base_profile,
            target_project,
            target_profile,
            password,
            strategy=strategy,
            dry_run=dry_run,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    tag = " [dry-run]" if dry_run else ""
    click.echo(f"Applied{tag}: {', '.join(result.applied) or '(none)'}")
    click.echo(f"Skipped (identical): {', '.join(result.skipped) or '(none)'}")
    if result.conflicts:
        click.echo(f"Conflicts (kept {strategy}): {', '.join(result.conflicts)}")
    else:
        click.echo("No conflicts.")
