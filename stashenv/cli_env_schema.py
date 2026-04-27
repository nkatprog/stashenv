"""CLI commands for schema validation of env profiles."""
import click
from pathlib import Path

from stashenv.env_schema import (
    validate_against_schema,
    validate_all_against_schema,
    format_schema_result,
)


@click.group("schema")
def schema_cmd() -> None:
    """Validate profiles against a JSON schema."""


@schema_cmd.command("check")
@click.argument("profile")
@click.argument("schema_file", type=click.Path(exists=True, path_type=Path))
@click.option("--password", "-p", prompt=True, hide_input=True, help="Decryption password.")
@click.option("--project", default=".", type=click.Path(path_type=Path), show_default=True)
def run_cmd(profile: str, schema_file: Path, password: str, project: Path) -> None:
    """Validate a single PROFILE against SCHEMA_FILE."""
    try:
        result = validate_against_schema(project, profile, password, schema_file)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    click.echo(format_schema_result(result))
    if not result.ok:
        raise SystemExit(1)


@schema_cmd.command("check-all")
@click.argument("schema_file", type=click.Path(exists=True, path_type=Path))
@click.option("--password", "-p", prompt=True, hide_input=True, help="Decryption password.")
@click.option("--project", default=".", type=click.Path(path_type=Path), show_default=True)
@click.option("--fail-fast", is_flag=True, default=False, help="Stop on first failure.")
def all_cmd(schema_file: Path, password: str, project: Path, fail_fast: bool) -> None:
    """Validate ALL profiles in the project against SCHEMA_FILE."""
    try:
        results = validate_all_against_schema(project, password, schema_file)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    if not results:
        click.echo("No profiles found.")
        return

    any_failed = False
    for result in results:
        click.echo(format_schema_result(result))
        if not result.ok:
            any_failed = True
            if fail_fast:
                raise SystemExit(1)

    if any_failed:
        raise SystemExit(1)
