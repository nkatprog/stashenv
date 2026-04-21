"""CLI commands for promoting profiles through environment tiers."""

from pathlib import Path

import click

from stashenv.promote import DEFAULT_PIPELINE, promote_profile


@click.group("promote")
def promote_cmd() -> None:
    """Promote a profile to the next environment tier."""


@promote_cmd.command("run")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True, help="Password for the source profile.")
@click.option("--target", default=None, help="Explicit target profile name (overrides pipeline).")
@click.option(
    "--target-password",
    default=None,
    hide_input=True,
    help="Password for the target profile (defaults to source password).",
)
@click.option(
    "--pipeline",
    default=",".join(DEFAULT_PIPELINE),
    show_default=True,
    help="Comma-separated ordered list of tier names.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing target profile.")
@click.option(
    "--project-dir",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False),
    help="Project directory.",
)
def run_cmd(
    profile: str,
    password: str,
    target: str | None,
    target_password: str | None,
    pipeline: str,
    overwrite: bool,
    project_dir: str,
) -> None:
    """Promote PROFILE to the next tier in the pipeline."""
    tiers = [t.strip() for t in pipeline.split(",") if t.strip()]
    try:
        dest = promote_profile(
            project_dir=Path(project_dir),
            source_profile=profile,
            password=password,
            target_profile=target,
            target_password=target_password,
            pipeline=tiers,
            overwrite=overwrite,
        )
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Promoted '{profile}' -> '{dest}'")
