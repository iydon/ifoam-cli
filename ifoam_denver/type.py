__all__ = ['Path']


import pathlib as p
import typing as t


Path = t.Union[str, p.Path]
