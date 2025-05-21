# pyright: reportUnknownMemberType=false

from collections.abc import Generator, Sequence
from dataclasses import dataclass
from typing import Any, cast

import pexpect
import sarge
from sarge import Capture, Pipeline

from mktech.error import Err, Ok, Result, todo
from mktech.log import DEBUG, log, log_args

__all__ = [
    'Capture',
    'Pipeline',
    'SubprocessIsAliveError',
    'TerminatedStatus',
    'Subprocess',
    'run',
]

sarge.logger = log
sarge.parse_logger = log


class SubprocessIsAliveError(Exception):
    def __init__(self) -> None:
        self.message: str = 'subprocess is still alive'
        super().__init__(self.message)


@dataclass
class TerminatedStatus:
    condition: str
    code: int
    stdout: str | bytes


class Subprocess:
    def __init__(self, command: str, *args: Any, **kwargs: Any) -> None:
        self.stdout_str: str | bytes

        self._pexpect_spawn: pexpect.spawn = pexpect.spawn(  # type: ignore  # pyright: ignore[reportMissingTypeArgument]  # noqa: E501
            command, timeout=None, *args, **kwargs
        )

        log.info(f'run: {command}')

        if self._pexpect_spawn.encoding is None:
            self.stdout_str = b''
        else:
            self.stdout_str = ''

    def close(self, force: bool = True) -> None:
        self._pexpect_spawn.close(force)

    def wait(self) -> int:
        return self._pexpect_spawn.wait()

    def readline(
        self,
        size: int = -1,
    ) -> Generator[str | bytes, str | bytes | None]:
        while True:
            line: str | bytes = self._pexpect_spawn.readline(  # pyright: ignore[reportUnknownVariableType]  # noqa: E501
                size
            )

            if (self._pexpect_spawn.encoding is None and line != b''):
                assert isinstance(self.stdout_str, bytes)
                assert isinstance(line, bytes)

                self.stdout_str += line

                yield line.rstrip()
            elif (self._pexpect_spawn.encoding is not None and line != ''):

                assert isinstance(self.stdout_str, str)
                assert isinstance(line, str)

                self.stdout_str += line

                yield line.rstrip()
            else:
                break

    @property
    def terminated_status(
        self
    ) -> Result[TerminatedStatus, SubprocessIsAliveError]:
        result: Result[TerminatedStatus, SubprocessIsAliveError]

        if self._pexpect_spawn.isalive():
            result = Err(SubprocessIsAliveError())
        elif self._pexpect_spawn.exitstatus is not None:
            result = Ok(
                TerminatedStatus(
                    'exit', self._pexpect_spawn.exitstatus, self.stdout
                )
            )
        elif self._pexpect_spawn.signalstatus is not None:
            result = Ok(
                TerminatedStatus(
                    'signal', self._pexpect_spawn.signalstatus, self.stdout
                )
            )
        else:
            todo()

        return result

    @property
    def stdout(self) -> str | bytes:
        return self.stdout_str

    @property
    def exit_status(self) -> Result[int, SubprocessIsAliveError]:
        if self._pexpect_spawn.exitstatus is None:
            return Err(SubprocessIsAliveError())
        else:
            return Ok(self._pexpect_spawn.exitstatus)

    @property
    def signal_status(self) -> Result[int, SubprocessIsAliveError]:
        if self._pexpect_spawn.signalstatus is None:
            return Err(SubprocessIsAliveError())
        else:
            return Ok(self._pexpect_spawn.signalstatus)


def pipeline_exit_code(self: sarge.Pipeline) -> int:
    result = cast(int, self.returncode)

    assert result is not None

    return result


setattr(sarge.Pipeline, 'exit_code', property(fget=pipeline_exit_code))


@log_args(level=DEBUG)
def run(command: Sequence[str] | str, **kwargs: Any) -> Pipeline:
    return sarge.run(command, **kwargs)
