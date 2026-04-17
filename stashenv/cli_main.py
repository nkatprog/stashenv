"""Main CLI entry point aggregating all command groups."""
import click
from stashenv.cli import cli, save, load, list_cmd, delete
from stashenv.cli_export import export_cmd, import_cmd
from stashenv.cli_copy import copy_cmd, rename_cmd
from stashenv.cli_rotate import rotate_cmd
from stashenv.cli_search import search_cmd


# Register core commands
cli.add_command(save)
cli.add_command(load)
cli.add_command(list_cmd)
cli.add_command(delete)

# Register import/export commands
cli.add_command(export_cmd)
cli.add_command(import_cmd)

# Register copy/rename commands
cli.add_command(copy_cmd)
cli.add_command(rename_cmd)

# Register utility commands
cli.add_command(rotate_cmd)
cli.add_command(search_cmd)


if __name__ == "__main__":
    cli()
