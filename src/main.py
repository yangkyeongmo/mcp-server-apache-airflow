import click

from src.server import app


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(transport: str) -> None:
    if transport == "sse":
        app.run(transport="sse")
    else:
        app.run(transport="stdio")
