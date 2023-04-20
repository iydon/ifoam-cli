import pathlib as p

import tomli

ROOT = p.Path(__file__).parents[1]

META = tomli.loads((ROOT/'pyproject.toml').read_text())

POETRY = 'poetry'
PYTHON = f'{POETRY} run python'
MYPY = f'{PYTHON} -m mypy'
PYTEST = f'{PYTHON} -m pytest'
