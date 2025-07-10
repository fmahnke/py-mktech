import functools
import inspect
import logging
from collections.abc import Callable, Sequence
from typing import Any, TypeAlias

from mktech import log1 as log

Level: TypeAlias = str | int


def log_args(
    level: Level = log.DEBUG,
    args_to_log: Sequence[Any] | None = None,
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def log_args(*func_args: Any, **func_kwargs: Any) -> Any:
            bound_args = inspect.signature(func
                                           ).bind(*func_args, **func_kwargs)
            bound_args.apply_defaults()
            log_data: dict[str, Any] = {}

            for arg in args_to_log or bound_args.arguments.keys():
                if arg in bound_args.arguments:
                    log_data[arg] = repr(bound_args.arguments[arg])

            log_data_str = ', '.join([f'{k}={v}' for k, v in log_data.items()])

            if isinstance(level, str):
                level_int = logging.getLevelNamesMapping()[level]
            else:
                level_int = level

            log.log(level_int, f"{func.__name__}({log_data_str})")

            return func(*func_args, **func_kwargs)

        return log_args

    return decorator
