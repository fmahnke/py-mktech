import os
import re
from tempfile import mkstemp
from typing import Generator

import pytest

from mktech import log1
from mktech.path import Path

log_regex = re.compile(r'([A-Z]*):(.*)\n')
log_regex_color = re.compile(
    r'\x1b\[38;2;110;110;110m([A-Z]*): (.*)\x1b\[0m\n'
)
log_regex_time = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}):([A-Z]*): (.*)\n'
)


@pytest.fixture
def log_file() -> Generator[Path]:
    file = mkstemp()

    yield Path(file[1])

    os.close(file[0])
    os.remove(file[1])


class TestLog:
    def test_log(self, log_file: Path) -> None:
        log1.init(
            'd',
            stream=False,
            log_file_path=log_file,
            log_file_mode='w',
            color=False
        )

        log1.info('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            match = log_regex.match(data[0])

            assert match is not None
            assert match.group(1) == 'INFO'
            assert match.group(2) == ' log message'

    def test_log_detail(self, log_file: Path) -> None:
        log1.init(
            'd',
            stream=False,
            log_file_path=log_file,
            log_file_mode='w',
            color=False
        )

        log1.set_detail(2)

        log1.info('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            match = log_regex.match(data[0])
            print(f'data {data}')

            assert match is not None
            assert match.group(1) == 'INFO'
            assert match.group(
                2
            ) == 'root:test_log1::test_log_detail: log message'

    def test_log_set_level(self, log_file: Path) -> None:
        log1.init(
            'i',
            stream=False,
            log_file_path=log_file,
            log_file_mode='w',
            color=False
        )

        log1.info('log message')
        log1.debug('log message')

        log1.set_level(log1.DEBUG)

        log1.debug('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 2

            match = log_regex.match(data[0])

            assert match is not None
            assert match.group(1) == 'INFO'
            assert match.group(2) == ' log message'

            match = log_regex.match(data[1])

            assert match is not None
            assert match.group(1) == 'DEBUG'
            assert match.group(2) == ' log message'

    def test_log_with_color(self, log_file: Path) -> None:
        log1.init(
            'd',
            stream=False,
            log_file_path=log_file,
            log_file_mode='w',
            color=True
        )

        log1.info('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            match = log_regex_color.match(data[0])

            assert match is not None
            assert match.group(1) == 'INFO'
            assert match.group(2) == 'log message'

    def test_log_with_time(self, log_file: Path) -> None:
        log1.init(
            'd',
            stream=False,
            log_file_path=log_file,
            log_file_mode='w',
            color=False
        )

        log1.set_detail(0, time=True)

        log1.info('log message')

        with open(log_file) as file:
            data = file.readlines()

            assert len(data) == 1

            match = log_regex_time.match(data[0])

            assert match is not None
            assert match.group(2) == 'INFO'
            assert match.group(3) == 'log message'
