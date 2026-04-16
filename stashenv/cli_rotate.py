"""CLI commands for password rotation."""

import click
from stashenv.rotate import rotate_profile, rotate_all_profiles


@click.command("rotate")
@click.argument("project")
@click.argument("profile", required=False, default=None)
@click.option("--old-password", prompt=True, hide_input=True, help="Current password.")
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New password.",
)
def rotate_cmd(project: str, profile: str | None, old_password: str, new_password: str):
    """Rotate encryption password for a profile or all profiles in a project.

    If PROFILE is omitted, all profiles in the project are rotated.
    """
    try:
        if profile:
            rotate_profile(project, profile, old_password, new_password)
            click.echo(f"Rotated password for profile '{profile}' in '{project}'.")
        else:
            rotated = rotate_all_profiles(project, old_password, new_password)
            if not rotated:
                click.echo(f"No profiles found in project '{project}'.")
            else:
                click.echo(
                    f"Rotated {len(rotated)} profile(s) in '{project}': "
                    + ", ".join(sorted(rotated))
                )
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"Rotation failed: {exc}") from exc
