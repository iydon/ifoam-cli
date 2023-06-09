import click

from .command import mypy, publish, pytest


@click.group()
def cli() -> None:
    pass


cli.add_command(mypy.api)
cli.add_command(publish.api)
cli.add_command(pytest.api)


if __name__ == '__main__':
    cli()
