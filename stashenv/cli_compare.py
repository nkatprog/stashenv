"""CLI commands for comparing two profiles."""
import click
from stashenv.compare import compare_profiles, format_compare


@click.group("compare")
def compare_cmd():
    """Compare two profiles side-by-side."""


@compare_cmd.command("run")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--project-a", default=".", show_default=True, help="Project dir for profile A")
@click.option("--project-b", default=".", show_default=True, help="Project dir for profile B")
@click.option("--password-a", prompt="Password for profile A", hide_input=True)
@click.option("--password-b", prompt="Password for profile B", hide_input=True)
@click.option("--reveal", is_flag=True, default=False, help="Show actual values")
def run_cmd(profile_a, profile_b, project_a, project_b, password_a, password_b, reveal):
    """Compare PROFILE_A and PROFILE_B."""
    try:
        report = compare_profiles(
            project_a, profile_a, password_a,
            project_b, profile_b, password_b,
        )
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except ValueError as e:
        raise click.ClickException(f"Decryption failed: {e}")

    summary = {s: 0 for s in ("equal", "differs", "only_in_a", "only_in_b")}
    for info in report.values():
        summary[info["status"]] += 1

    click.echo(f"Comparing '{profile_a}' (A) vs '{profile_b}' (B):")
    click.echo(format_compare(report, reveal=reveal))
    click.echo(
        f"\nSummary: {summary['equal']} equal, {summary['differs']} differ, "
        f"{summary['only_in_a']} only in A, {summary['only_in_b']} only in B"
    )
