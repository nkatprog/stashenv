"""CLI commands for masked display of profile values."""
import click

from stashenv.env_mask import mask_profile, format_masked


@click.group("mask")
def mask_cmd() -> None:
    """Display profile values with sensitive fields masked."""


@mask_cmd.command("show")
@click.argument("profile")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Decryption password.")
@click.option(
    "--project-dir",
    default=".",
    show_default=True,
    help="Project directory.",
)
@click.option(
    "--reveal-chars",
    default=4,
    show_default=True,
    type=int,
    help="Number of leading characters to reveal for masked values.",
)
@click.option(
    "--pattern",
    "extra_patterns",
    multiple=True,
    help="Additional key substrings to treat as sensitive (repeatable).",
)
@click.option(
    "--show-all",
    is_flag=True,
    default=False,
    help="Reveal all values without masking.",
)
def show_cmd(
    profile: str,
    password: str,
    project_dir: str,
    reveal_chars: int,
    extra_patterns: tuple[str, ...],
    show_all: bool,
) -> None:
    """Show a profile with sensitive values masked."""
    try:
        result = mask_profile(
            profile=profile,
            password=password,
            project_dir=project_dir,
            reveal_chars=reveal_chars,
            extra_patterns=list(extra_patterns) if extra_patterns else None,
            show_all=show_all,
        )
    except FileNotFoundError:
        raise click.ClickException(f"Profile '{profile}' not found.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc))

    click.echo(format_masked(result))
    hidden = [k for k in result.masked if k not in result.revealed_keys]
    if hidden:
        click.echo(f"\n  ({len(hidden)} key(s) masked)")
