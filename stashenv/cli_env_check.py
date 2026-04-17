"""CLI commands for env-check feature."""
import click
from pathlib import Path
from stashenv.env_check import check_profile, format_check


@click.group("check")
def check_cmd():
    """Validate profiles against a .env.example template."""


@check_cmd.command("run")
@click.argument("profile")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
@click.option(
    "--example",
    default=None,
    help="Path to .env.example (default: <project-dir>/.env.example).",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Also report keys present in profile but absent from example.",
)
def run_cmd(profile: str, project_dir: str, password: str, example: str, strict: bool):
    """Check PROFILE against the .env.example file."""
    pdir = Path(project_dir)
    example_path = Path(example) if example else None
    try:
        result = check_profile(pdir, profile, password, example_path, strict)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))

    click.echo(format_check(result))
    if not result.ok:
        raise SystemExit(1)
