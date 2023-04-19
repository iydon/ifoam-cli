import subprocess as sp
import typing as t

if t.TYPE_CHECKING:
    import typing_extensions as te

    P = te.ParamSpec('P')
    Kwargs = te.ParamSpecKwargs(P)


def last(text: str, sep: str = '.') -> str:
    return text.rsplit(sep, maxsplit=1)[-1]

def run(command: str, **kwargs: 'Kwargs') -> None:
    cp = sp.run(command, shell=True, **kwargs)

    assert cp.returncode == 0, cp.stderr
