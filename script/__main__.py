import click

from .command import publish


@click.group()
def cli() -> None:
    pass


cli.add_command(publish.api)


if __name__ == '__main__':
    cli()
