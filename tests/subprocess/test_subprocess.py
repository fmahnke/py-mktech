import sys
from signal import SIGHUP

import pytest

from mktech import subprocess
from mktech.error import Err, Ok
from mktech.resources import resource_path
from mktech.subprocess import Capture, Subprocess

_count_path = resource_path('tests.subprocess.resources', 'count.py').unwrap()

_count_command = f'{sys.executable} {_count_path}'


class TestSubprocess:
    def test_terminated_with_exit_0(self) -> None:
        process = Subprocess(f'{_count_command} 4 0', encoding='utf-8')

        assert [line for line in process.readline()] == ['0', '1', '2', '3']

        match process.terminated_status:
            case Err(error):
                raise AssertionError(error)
            case Ok(status):
                assert status.condition == 'exit'
                assert status.code == 0
            case _:
                raise AssertionError()

    def test_terminated_with_exit_1(self) -> None:
        process = Subprocess(f'{_count_command} 0 0', encoding='utf-8')

        [line for line in process.readline()]

        match process.terminated_status:
            case Err(error):
                raise AssertionError(error)
            case Ok(status):
                assert status.condition == 'exit'
                assert status.code == 1
            case _:
                raise AssertionError()

    @pytest.mark.skip('Does not work in Jenkins build')
    def test_terminated_with_signal(self) -> None:
        process = Subprocess(f'{_count_command} 4 0', encoding='utf-8')

        next(process.readline())

        process.close()

        match process.terminated_status:
            case Err(error):
                raise AssertionError(error)
            case Ok(status):
                assert status.condition == 'signal'
                assert status.code == SIGHUP
            case _:
                raise AssertionError()


class TestRun:
    def test_returncode(self) -> None:
        result = subprocess.run('true')

        assert result.exit_code == 0

    def test_capture(self) -> None:
        result = subprocess.run(
            'printf "%s %d" "string arguments" 1', stdout=Capture()
        )

        assert result.stdout.text == 'string arguments 1'

        assert result.exit_code == 0

    def test_lines(self) -> None:
        process = subprocess.run(f'{_count_command} 4 0', stdout=Capture())

        assert [line.decode('utf8')
                for line in process.stdout] == ['0\n', '1\n', '2\n', '3\n']

        assert process.exit_code == 0

    def test_async(self) -> None:
        process = subprocess.run(
            f'{_count_command} 4 0.25', stdout=Capture(), async_=True
        )

        lines: list[str] = []

        while process.poll_last() is None:
            lines += [line.decode('utf8') for line in process.stdout]

        lines += [line.decode('utf8') for line in process.stdout]

        assert lines == ['0\n', '1\n', '2\n', '3\n']

        assert process.exit_code == 0

    def test_async_wait(self) -> None:
        process = subprocess.run(
            f'{_count_command} 4 0.25', stdout=Capture(), async_=True
        )

        process.wait()

        lines = [line.decode('utf8') for line in process.stdout]

        assert lines == ['0\n', '1\n', '2\n', '3\n']

        assert process.exit_code == 0
