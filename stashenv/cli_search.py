"""CLI commands for searching profiles."""
import click
from stashenv.search import search_profiles, format_search_results


@click.command("search")
@click.argument("query")
@click.option("--project", default=".", show_default=True, help="Project directory.")
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
@click.option(
    "--values",
    is_flag=True,
    default=False,
    help="Also search inside values.",
)
@click.option(
    "--reveal",
    is_flag=True,
    default=False,
    help="Show matched values in plaintext.",
)
def search_cmd(query: str, project: str, password: str, values: bool, reveal: bool):
    """Search all profiles for keys (or values) matching QUERY."""
    results = search_profiles(project, password, query, search_values=values)
    output = format_search_results(results, reveal_values=reveal)
    click.echo(output)
