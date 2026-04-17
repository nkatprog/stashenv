"""Main CLI entry point for stashenv."""
import click
from stashenv.cli import cli
from stashenv.cli_export import export_cmd, import_cmd
from stashenv.cli_copy import copy_cmd, rename_cmd
from stashenv.cli_rotate import rotate_cmd
from stashenv.cli_search import search_cmd
from stashenv.cli_snapshot import snapshot_cmd
from stashenv.cli_tag import tag_cmd
from stashenv.cli_lock import lock_cmd
from stashenv.cli_history import history_cmd
from stashenv.cli_compare import compare_cmd
from stashenv.cli_env_check import check_cmd

cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(copy_cmd, "copy")
cli.add_command(rename_cmd, "rename")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(search_cmd, "search")
cli.add_command(snapshot_cmd, "snapshot")
cli.add_command(tag_cmd, "tag")
cli.add_command(lock_cmd, "lock")
cli.add_command(history_cmd, "history")
cli.add_command(compare_cmd, "compare")
cli.add_command(check_cmd, "check")

if __name__ == "__main__":
    cli()
