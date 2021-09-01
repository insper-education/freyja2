import click
from .tools.repos import repos


@click.group()
def cli():
    pass


cli.add_command(repos)
