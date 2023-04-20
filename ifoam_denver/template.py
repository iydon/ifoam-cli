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

    Examples:
        >>> d = Dockerfile('todo')
        >>> text = d \\
        ...     .from_ubuntu('20.04') \\
        ...     .arg_default() \\
        ...     .expose(7101) \\
        ...     .workdir_default() \\
        ...     .copy_default() \\
        ...     .run(d.run_update(), d.run_install('curl', 'ca-certificates', 'vim')) \\
        ...     .run(
        ...         d.run_download_bash('https://dl.openfoam.com/add-debian-repo.sh'),
        ...         d.run_update(), d.run_install(f'openfoam2012-default'),
        ...     ) \\
        ...     .render()
        >>> print(text.strip())
        FROM ubuntu:20.04
        <BLANKLINE>
        ARG DEBIAN_FRONTEND=noninteractive
        <BLANKLINE>
        EXPOSE 7101
        <BLANKLINE>
        WORKDIR /root
        <BLANKLINE>
        COPY todo/copy denver
        <BLANKLINE>
        RUN apt-get update && \\
            apt-get -y install --no-install-recommends curl ca-certificates vim
        <BLANKLINE>
        RUN bash denver/968654f0cfe5785342356718fcfd1fb5/add-debian-repo.sh && \\
            apt-get update && \\
            apt-get -y install --no-install-recommends openfoam2012-default
    '''

    def __init__(self, directory: Path) -> None:
        self._directory = p.Path(directory)
        self._src = self._directory / 'copy'
        self._dst = p.Path('denver')
        self._lines: t.List[str] = []
        self._flag: t.Dict[str, bool] = {}

    def __repr__(self) -> str:
        return self.render()

    def render(self) -> str:
        return '\n\n'.join(self._lines) + '\n'

    def save(self, filename: str = 'Dockerfile') -> p.Path:
        path = self._directory / filename
        path.write_text(self.render())
        return path

    def arg(self, *names: str) -> 'te.Self':
        return self._appends([f'ARG {name}' for name in names])

    def arg_default(self) -> 'te.Self':
        return self.arg('DEBIAN_FRONTEND=noninteractive')

    def copy(self, src: Path, dst: Path) -> 'te.Self':
        return self._append(f'COPY {self._as_posix(src)} {self._as_posix(dst)}')

    def copy_default(self) -> 'te.Self':
        return self.copy(self._src, self._dst)

    def entrypoint(self, *commands: t.List[str]) -> 'te.Self':
        assert not self._flag.get('entrypoint', False)

        self._flag['entrypoint'] = True
        self.entrypoint_update(*commands, mode='w')
        return self._append(f'ENTRYPOINT bash {(self._dst/"startup.sh").as_posix()}')

    def entrypoint_update(self, *commands: t.List[str], mode: str = 'a+') -> 'te.Self':
        (self._src/'log').mkdir(parents=True, exist_ok=True)
        with open(self._src/'startup.sh', mode) as f:
            for command in map(' && \\\n    '.join, commands):
                md5 = self._md5(command)
                out, err = self._dst/'log'/f'{md5}.out', self._dst/'log'/f'{md5}.err'
                f.write(f'{command} \\\n    1>{out.as_posix()} 2>{err.as_posix()} &\n')
        return self

    def entrypoint_sleep(self) -> 'te.Self':
        with open(self._src/'startup.sh', 'a+') as f:
            f.write('sleep infinity\n')
        return self

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
        md5 = self._md5(url)
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

    def _as_posix(self, path: Path) -> str:
        return p.Path(path).as_posix()

    def _md5(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
