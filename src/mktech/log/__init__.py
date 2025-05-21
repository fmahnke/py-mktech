import logging
from logging import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    LogRecord,
    debug,
    error,
    info,
    warning,
)
from typing import TypeAlias

from mktech.os import environ
from mktech.path import Path

__all__ = [
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'debug',
    'info',
    'warning',
    'error',
    'init'
]

Level: TypeAlias = str | int

TRACE = 5

_detail_str = [
    '%(levelname)s: %(message)s',
    '%(levelname)s:%(module)s::%(funcName)s: %(message)s',
    '%(levelname)s:%(name)s:%(module)s::%(funcName)s: %(message)s'
]

_detail_formatter = [
    logging.Formatter(_detail_str[0]),
    logging.Formatter(_detail_str[1]),
    logging.Formatter(_detail_str[2])
]

# formatters


class Formatter(logging.Formatter):
    grey_0 = "\x1b[38;2;85;85;85m"
    grey_1 = "\x1b[38;2;110;110;110m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, color: bool = False) -> None:
        super().__init__()

        self.color = color

        format_str = _detail_str[0]

        self._make_formatters(format_str)

    def format_str(self, format_str: str) -> None:
        self._make_formatters(format_str)

    def format(self, record: LogRecord) -> str:
        if record.levelno >= 50:
            idx = 0
        elif record.levelno >= 40:
            idx = 1
        elif record.levelno >= 30:
            idx = 2
        elif record.levelno >= 20:
            idx = 3
        else:
            idx = 4

        formatter = self._formatters[idx]

        return formatter.format(record)

    def _make_formatters(self, format_str: str) -> None:
        formats = []

        if self.color:
            formats = [
                self.bold_red + format_str + self.reset,
                self.red + format_str + self.reset,
                self.yellow + format_str + self.reset,
                self.grey_1 + format_str + self.reset,
                self.grey_0 + format_str + self.reset,
            ]
        else:
            formats = [
                format_str,
            ] * 5

        self._formatters = [logging.Formatter(it) for it in formats]


def set_formatter(formatter: 'Formatter') -> None:
    global _root_logger

    for handler in _root_logger.handlers:
        handler.setFormatter(formatter)


# handlers


def _set_handlers(logger: logging.Logger) -> None:
    for handler in logger.handlers:
        logger.removeHandler(handler)

    for handler in _root_logger.handlers:
        logger.addHandler(handler)


# log levels


def set_detail(level: int, time: bool = False) -> None:
    if _formatter is None:
        raise RuntimeError('log is not initialized')

    if level < 0 or level > len(_detail_str) - 1:
        raise Exception()
    else:
        detail_str = _detail_str[level]

        if time:
            detail_str = f'%(asctime)s:{detail_str}'

        _formatter.format_str(detail_str)


def get_level() -> int:
    return _root_logger.level


def set_level(level: int | str) -> None:
    _root_logger.setLevel(level)


# loggers


def logger_init(
    logger: logging.Logger,
    level: Level | None = None,
    set_handlers: bool = True
) -> None:
    if level is not None:
        logger.setLevel(level)

    if set_handlers:
        _set_handlers(logger)


# Initialize the global logger

_formatter: Formatter | None = None
_root_logger = logging.getLogger('root')


def init(
    level: int | str,
    stream: bool = True,
    log_file_path: Path | None = None,
    log_file_mode: str | None = None,
    color: bool = True
) -> None:
    global _root_logger
    global _formatter

    _formatter = Formatter(color)

    handlers = _root_logger.handlers

    for handler in handlers:
        _root_logger.removeHandler(handler)

    if stream:
        stream_handler = logging.StreamHandler()

        _root_logger.addHandler(stream_handler)

    if log_file_path is not None:
        if log_file_mode is None:
            mode = 'a'
        else:
            mode = log_file_mode

        file_handler = logging.FileHandler(log_file_path, mode=mode)

        _root_logger.addHandler(file_handler)

    set_formatter(_formatter)

    env_level = environ('MK_LOG_LEVEL', required=False)

    if isinstance(level, str):
        if env_level != '':
            level = env_level

        level = level.upper()

        match level:
            case 'E':
                level = 'ERROR'
            case 'W':
                level = 'WARNING'
            case 'I':
                level = 'INFO'
            case 'D':
                level = 'DEBUG'

    set_level(level)
