import click

from ..config import META, PYTEST
from ..util import last, run


@click.command(name=last(__name__))
def api() -> None:
    '''Use pytest framework for unit testing'''
    package = META['tool']['poetry']['packages'][0]['include']
    run(f'{PYTEST} --pyargs {package}')
