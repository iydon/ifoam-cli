import click

from ..config import META, PYTEST
from ..util import last, pure


@click.command(name=last(__name__))
def api() -> None:
    '''Use pytest framework for unit testing'''
    package = META['tool']['poetry']['packages'][0]['include']
    pure(f'{PYTEST} --pyargs {package}')
