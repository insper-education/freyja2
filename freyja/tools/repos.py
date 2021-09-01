import click


@click.group()
def repos():
    pass


@repos.command()
def create():
    click.echo('This is the zone subcommand of the cloudflare command')


@repos.command()
def update():
    click.echo('This is the zone subcommand of the cloudflare command')
