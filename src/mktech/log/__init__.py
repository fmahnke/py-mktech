from loguru import logger as log

from .callable import log_args

DEBUG = 'DEBUG'
ERROR = 'ERROR'
INFO = 'INFO'
WARNING = 'WARNING'

__all__ = [
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'log',
    'log_args',
]
