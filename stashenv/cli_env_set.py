"""CLI commands for bulk set/unset of env vars in a profile."""
from __future__ import annotations

from pathlib import Path

import click

from stashenv.env_set import set_vars, unset_vars, set_from_file, EnvSetError


@click.group("env-set")
def env_set_cmd():
    """Bulk set or unset variables in a profile."""


@env_set_cmd.command("set")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--profile", required=True, help="Profile name.")
@click.password_option("--password", prompt=True, confirmation_prompt=False)
@click.argument("pairs", nargs=-1, required=True, metavar="KEY=VALUE...")
def set_cmd(project: str, profile: str, password: str, pairs: tuple):
    """Set KEY=VALUE pairs in a profile."""
    updates = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got {pair!r}")
        k, _, v = pair.partition("=")
        updates[k.strip()] = v.strip()
    try:
        env = set_vars(Path(project), profile, password, updates)
        click.echo(f"Set {len(updates)} key(s) in '{profile}'. Profile now has {len(env)} key(s).")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@env_set_cmd.command("unset")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--profile", required=True, help="Profile name.")
@click.password_option("--password", prompt=True, confirmation_prompt=False)
@click.argument("keys", nargs=-1, required=True, metavar="KEY...")
def unset_cmd(project: str, profile: str, password: str, keys: tuple):
    """Remove one or more keys from a profile."""
    try:
        env = unset_vars(Path(project), profile, password, list(keys))
        click.echo(f"Unset {len(keys)} key(s) from '{profile}'. Profile now has {len(env)} key(s).")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


@env_set_cmd.command("from-file")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--profile", required=True, help="Profile name.")
@click.password_option("--password", prompt=True, confirmation_prompt=False)
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already exist.")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
def from_file_cmd(project: str, profile: str, password: str, no_overwrite: bool, env_file: str):
    """Import KEY=VALUE pairs from a plain .env file into a profile."""
    try:
        env = set_from_file(
            Path(project), profile, password, Path(env_file), overwrite=not no_overwrite
        )
        click.echo(f"Imported into '{profile}'. Profile now has {len(env)} key(s).")
    except EnvSetError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
