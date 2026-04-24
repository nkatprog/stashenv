"""Entry-point that assembles all sub-command groups into one CLI."""
from __future__ import annotations

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
from stashenv.cli_pin import pin_cmd
from stashenv.cli_alias import alias_cmd
from stashenv.cli_notes import notes_cmd
from stashenv.cli_watch import watch_cmd
from stashenv.cli_validate import validate_cmd
from stashenv.cli_share import share_cmd
from stashenv.cli_promote import promote_cmd
from stashenv.cli_inherit import inherit_cmd
from stashenv.cli_archive import archive_cmd
from stashenv.cli_hook import hook_cmd

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
cli.add_command(pin_cmd, "pin")
cli.add_command(alias_cmd, "alias")
cli.add_command(notes_cmd, "notes")
cli.add_command(watch_cmd, "watch")
cli.add_command(validate_cmd, "validate")
cli.add_command(share_cmd, "share")
cli.add_command(promote_cmd, "promote")
cli.add_command(inherit_cmd, "inherit")
cli.add_command(archive_cmd, "archive")
cli.add_command(hook_cmd, "hook")

if __name__ == "__main__":
    cli()
