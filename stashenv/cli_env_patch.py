"""CLI commands for patching individual keys in a profile."""

from __future__ import annotations

import click

from stashenv.env_patch import PatchError, format_patch_result, patch_profile


@click.group("patch")
def patch_cmd() -> None:
    """Apply incremental key-value patches to a profile."""


@patch_cmd.command("run")
@click.argument("profile")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Profile password.")
@click.option(
    "--set",
    "set_pairs",
    multiple=True,
    metavar="KEY=VALUE",
    help="Set KEY to VALUE (repeatable).",
)
@click.option(
    "--remove",
    "remove_keys",
    multiple=True,
    metavar="KEY",
    help="Remove KEY from profile (repeatable).",
)
def run_cmd(
    profile: str,
    project_dir: str,
    password: str,
    set_pairs: tuple,
    remove_keys: tuple,
) -> None:
    """Patch PROFILE by setting and/or removing individual keys."""
    set_keys: dict[str, str] = {}
    for pair in set_pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair!r}", param_hint="--set")
        k, _, v = pair.partition("=")
        set_keys[k.strip()] = v

    try:
        result = patch_profile(
            project_dir,
            profile,
            password,
            set_keys=set_keys,
            remove_keys=list(remove_keys),
        )
    except PatchError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Patched profile '{profile}':")
    click.echo(format_patch_result(result))
    click.echo(f"\n{result.total_changes} change(s) applied.")
