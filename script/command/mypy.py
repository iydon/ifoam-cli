import click

from ..config import META, MYPY
from ..util import last, pure


@click.command(name=last(__name__))
def api() -> None:
    '''Check static type for Python'''
    package = META['tool']['poetry']['packages'][0]['include']
    pure(f'{MYPY} --warn-unused-ignores {package}')
