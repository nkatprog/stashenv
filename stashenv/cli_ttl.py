"""CLI commands for managing profile TTLs."""

from __future__ import annotations

from pathlib import Path

import click

from stashenv.ttl import set_ttl, clear_ttl, get_ttl, is_expired, list_expired


@click.group("ttl")
def ttl_cmd() -> None:
    """Manage time-to-live settings for profiles."""


@ttl_cmd.command("set")
@click.argument("profile")
@click.argument("seconds", type=int)
@click.option("--project", default=".", show_default=True, help="Project directory.")
def set_cmd(profile: str, seconds: int, project: str) -> None:
    """Set a TTL of SECONDS for PROFILE."""
    try:
        set_ttl(Path(project), profile, seconds)
        click.echo(f"TTL of {seconds}s set for profile '{profile}'.")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@ttl_cmd.command("clear")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
def clear_cmd(profile: str, project: str) -> None:
    """Remove the TTL for PROFILE."""
    clear_ttl(Path(project), profile)
    click.echo(f"TTL cleared for profile '{profile}'.")


@ttl_cmd.command("status")
@click.argument("profile")
@click.option("--project", default=".", show_default=True)
def status_cmd(profile: str, project: str) -> None:
    """Show TTL status for PROFILE."""
    info = get_ttl(Path(project), profile)
    if info is None:
        click.echo(f"No TTL set for profile '{profile}'.")
        return
    expired = is_expired(Path(project), profile)
    remaining = max(0.0, info["ttl"] - (__import__("time").time() - info["created_at"]))
    status = "EXPIRED" if expired else f"{remaining:.0f}s remaining"
    click.echo(f"Profile '{profile}': TTL={info['ttl']}s, {status}")


@ttl_cmd.command("list-expired")
@click.option("--project", default=".", show_default=True)
def list_expired_cmd(project: str) -> None:
    """List all profiles whose TTL has elapsed."""
    expired = list_expired(Path(project))
    if not expired:
        click.echo("No expired profiles.")
    else:
        for name in expired:
            click.echo(name)
