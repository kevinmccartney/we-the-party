import traceback
from types import MappingProxyType
from typing import Literal, Union

import click

LOG_LEVEL_COLOR_MAP = MappingProxyType(
    {
        "success": "green",
        "info": "reset",
        "callout": "magenta",
        "warning": "yellow",
        "error": "red",
    }
)

LogLevel = Literal["success", "info", "callout", "warning", "error"]


def log_message(
    msg: str,
    level: LogLevel = "info",
) -> None:
    """logs a message color-coded with the option of turning off the color"""
    fg: str = LOG_LEVEL_COLOR_MAP[level]
    is_err = level == "error"

    message: str = click.style(msg, fg=fg)

    click.echo(message, err=is_err)


def log_exception(
    ex: Exception,
    error_number: Union[int, None] = None,
    verbose: bool = False,
    message: str = "",
    additional_info: str = "",
) -> None:
    """Logs an exception with optional info and can exit the process."""
    if message:
        log_message(message, level="error")

    if additional_info:
        log_message(additional_info, level="error")

    if verbose:
        exit_code_message = ""

        try:
            exit_code_message = f": exit code {error_number}" if error_number else ""
        except AttributeError:
            pass

        ex_traceback = traceback.format_exc()

        log_message("Debug Info -", level="error")
        log_message(f"Type: {type(ex).__name__}{exit_code_message}", level="error")
        log_message(ex_traceback, level="error")
