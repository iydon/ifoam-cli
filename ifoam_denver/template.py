__all__ = ['Dockerfile']


import hashlib
import pathlib as p
import typing as t

import requests

from .type import Path

if t.TYPE_CHECKING:
    import typing_extensions as te


class Dockerfile:
    '''Template for Dockerfile
    '''

    def __init__(self, directory: Path) -> None:
        self._directory = p.Path(directory)
        self._src = self._directory / 'copy'
        self._dst = p.Path('denver')
        self._lines: t.List[str] = []

    def __repr__(self) -> str:
        return self.render()

    def render(self) -> str:
        return '\n\n'.join(self._lines) + '\n'

    def save(self, filename: str = 'Dockerfile') -> None:
        (self._directory/filename).write_text(self.render())

    def arg(self, *names: str) -> 'te.Self':
        return self._appends([f'ARG {name}' for name in names])

    def arg_default(self) -> 'te.Self':
        return self.arg('DEBIAN_FRONTEND=noninteractive')

    def copy(self, src: Path, dst: Path) -> 'te.Self':
        return self._append(f'COPY {self._as_posix(src)} {self._as_posix(dst)}')

    def copy_default(self) -> 'te.Self':
        return self.copy(self._src, self._dst)

    def entrypoint(self, *commands: str) -> 'te.Self':
        line = ' && \\\n    '.join(commands)
        return self._append(f'ENTRYPOINT {line}')

    def expose(self, *ports: t.Union[int, str]) -> 'te.Self':
        return self._appends([f'EXPOSE {port}' for port in ports])

    def from_(self, image: str) -> 'te.Self':
        return self._append(f'FROM {image}')

    def from_ubuntu(self, tag: str) -> 'te.Self':
        return self.from_(f'ubuntu:{tag}')

    def run(self, *commands: str) -> 'te.Self':
        line = ' && \\\n    '.join(commands)
        return self._append(f'RUN {line}')

    def workdir(self, path: Path) -> 'te.Self':
        return self._append(f'WORKDIR {self._as_posix(path)}')

    def workdir_default(self) -> 'te.Self':
        return self.workdir('/root/')

    def run_update(self) -> str:
        return 'apt-get update'

    def run_install(self, *packages: str) -> str:
        return f'apt-get -y install --no-install-recommends {" ".join(packages)}'

    def run_download(self, url: str, overwrite: bool = False) -> str:
        md5 = hashlib.md5(url.encode()).hexdigest()
        name = url.rsplit('/', maxsplit=1)[-1]
        path = self._src / md5 / name
        if overwrite or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(requests.get(url).content)
        return (self._dst/md5/name).as_posix()

    def run_download_bash(self, url: str, overwrite: bool = False) -> str:
        return self.run_download_other('bash', url, overwrite)

    def run_download_other(self, prefix: str, url: str, overwrite: bool = False) -> str:
        return f'{prefix} {self.run_download(url, overwrite)}'

    def _append(self, line: str) -> 'te.Self':
        self._lines.append(line)
        return self

    def _appends(self, lines: t.List[str]) -> 'te.Self':
        self._lines += lines
        return self

    def _as_posix(self, path: str) -> str:
        return p.Path(path).as_posix()
