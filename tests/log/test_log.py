import os
import re
from collections.abc import Generator
from tempfile import mkstemp

import pytest

from mktech.log import DEBUG, INFO, log, log_args
from mktech.path import Path

# matches level, message:
# INFO     | log message\n

_log_regex = re.compile(r'([A-Z]*) *\| (.*)\n')

# matches time, level, location, message:
# 2025-08-26 09:39:44.262 | DEBUG    | tests.log.test_log:test_log_set_level:110 - log message  # noqa: E501

_log_regex_detail = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) \| ([A-Z]*) *' +
    r'\| tests.log.test_log:[a-z_].*:\d* - (.*)\n'
)

_format_level_message = '{level:<8} | {message}'


@pytest.fixture
def log_file() -> Generator[Path, None, None]:
    file = mkstemp()

    yield Path(file[1])

    os.close(file[0])
    os.remove(file[1])


class TestLog:
    def test_log(self, log_file: Path) -> None:
        log.remove()

        _ = log.add(log_file, level=DEBUG, format=_format_level_message)

        log.info('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            match = _log_regex.match(data[0])

            assert match is not None
            assert match.group(1) == 'INFO'
            assert match.group(2) == 'log message'

    def test_log_set_level(self, log_file: Path) -> None:
        log.remove()

        _ = log.add(log_file, level=INFO, format=_format_level_message)

        log.info('log message')
        log.debug('log message')

        _ = log.add(log_file, level=DEBUG, format=_format_level_message)

        log.debug('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 2

            match = _log_regex.match(data[0])

            assert match is not None
            assert match.group(1) == 'INFO'
            assert match.group(2) == 'log message'

            match = _log_regex.match(data[1])

            assert match is not None
            assert match.group(1) == 'DEBUG'
            assert match.group(2) == 'log message'

    def test_log_with_detail(self, log_file: Path) -> None:
        log.remove()

        _ = log.add(log_file, level=DEBUG)

        log.info('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            match = _log_regex_detail.match(data[0])

            assert match is not None
            assert match.group(2) == 'INFO'
            assert match.group(3) == 'log message'


@log_args(level=DEBUG)
def log_args_fn(arg_0: str, arg_1: int) -> None:
    _ = arg_0
    _ = arg_1


class TestLogArgs:
    def test_enabled(self, log_file: Path) -> None:
        log.remove()

        _ = log.add(log_file, level=DEBUG, format=_format_level_message)

        log_args_fn('arg_0 value', 1234)

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            assert data[
                0
            ] == "DEBUG    | log_args_fn(arg_0='arg_0 value', arg_1=1234)\n"

    def test_disabled(self, log_file: Path) -> None:
        log.remove()

        _ = log.add(log_file, level=INFO, format=_format_level_message)

        log_args_fn('arg_0 value', 1234)

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 0
