"""CLI commands for profile validation against a schema/rules file."""

import click
from pathlib import Path
from .validate import validate_profile, validate_all_profiles, format_results
from .store import list_profiles


@click.group("validate")
def validate_cmd():
    """Validate profiles against type and requirement rules."""
    pass


@validate_cmd.command("run")
@click.argument("profile")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
@click.option(
    "--schema",
    default=".env.schema.json",
    show_default=True,
    help="Path to JSON schema file defining required keys and types.",
)
def run_cmd(profile: str, project: str, password: str, schema: str):
    """Validate a single named profile against a schema file.

    The schema file should be a JSON object mapping key names to rule objects.
    Example schema entry: {"DATABASE_URL": {"type": "url", "required": true}}
    """
    project_path = Path(project).resolve()
    schema_path = Path(schema)

    if not schema_path.is_absolute():
        schema_path = project_path / schema

    if not schema_path.exists():
        click.echo(f"Schema file not found: {schema_path}", err=True)
        raise SystemExit(1)

    try:
        result = validate_profile(project_path, profile, password, schema_path)
    except FileNotFoundError:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_results({profile: result}))

    if not result.ok:
        raise SystemExit(1)


@validate_cmd.command("all")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
@click.option(
    "--schema",
    default=".env.schema.json",
    show_default=True,
    help="Path to JSON schema file.",
)
@click.option(
    "--fail-fast",
    is_flag=True,
    default=False,
    help="Stop after the first profile with validation errors.",
)
def all_cmd(project: str, password: str, schema: str, fail_fast: bool):
    """Validate all profiles in the project against a schema file."""
    project_path = Path(project).resolve()
    schema_path = Path(schema)

    if not schema_path.is_absolute():
        schema_path = project_path / schema

    if not schema_path.exists():
        click.echo(f"Schema file not found: {schema_path}", err=True)
        raise SystemExit(1)

    profiles = list_profiles(project_path)
    if not profiles:
        click.echo("No profiles found.")
        return

    try:
        results = validate_all_profiles(project_path, password, schema_path)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_results(results))

    any_failed = any(not r.ok for r in results.values())

    if fail_fast:
        for name, result in results.items():
            if not result.ok:
                click.echo(f"Stopping after first failure: '{name}'", err=True)
                raise SystemExit(1)

    if any_failed:
        raise SystemExit(1)
