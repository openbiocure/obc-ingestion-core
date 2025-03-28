import click
from . import engine
from .__version__ import __version__

@click.group()
@click.version_option(version=__version__)
def cli():
    """HerpAI-Lib CLI tool."""
    pass

@cli.command()
def info():
    """Display information about HerpAI-Lib."""
    click.echo(f"HerpAI-Lib version: {__version__}")
    click.echo("HerpAI-Lib is the foundational core library for the HerpAI platform.")

if __name__ == "__main__":
    cli()
