import click

from ..config import POETRY
from ..util import last, run


@click.command(name=last(__name__))
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def api(username: str, password: str) -> None:
    '''Build and upload the package to PyPi'''
    run(f'{POETRY} build')
    run(f'{POETRY} publish --username="{username}" --password="{password}"')
