"""CLI commands for watching a .env file."""
import click
from pathlib import Path
from stashenv.watch import watch_env_file


@click.group("watch")
def watch_cmd():
    """Watch a .env file and auto-save changes to a profile."""


@watch_cmd.command("start")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--project-dir", type=click.Path(path_type=Path), default=Path("."), show_default=True)
@click.option("--profile", "-p", required=True, help="Profile name to save into.")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
@click.option("--interval", default=1.0, show_default=True, help="Polling interval in seconds.")
def start_cmd(env_file: Path, project_dir: Path, profile: str, password: str, interval: float):
    """Start watching ENV_FILE and save changes to PROFILE."""
    click.echo(f"Watching {env_file} → profile '{profile}' (interval={interval}s). Ctrl-C to stop.")

    def on_change(msg: str):
        click.echo(msg)

    try:
        watch_env_file(
            env_file=env_file,
            project_dir=project_dir,
            profile=profile,
            password=password,
            interval=interval,
            on_change=on_change,
        )
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
