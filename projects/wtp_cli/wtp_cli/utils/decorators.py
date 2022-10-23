"""
Various decorators to apply behavior to functions. Delicious meta programming.

Includes
- File opening with handling for files not found
- Parsing JSO
"""
import io
import os
import pprint
import sys
import typing

import debugpy
import pyjson5

from wtp_cli.utils.logging import log_exception, log_message
from wtp_cli.utils.system import exit_process

IOBase_Type_Var = typing.TypeVar("IOBase_Type_Var", bound=typing.Optional[io.IOBase])
T = typing.TypeVar("T")
V = typing.TypeVar("V")
P = typing.ParamSpec("P")


def with_file_not_found(
    path: str = "",
    should_exit: bool = False,
    verbose: bool = False,
    additional_info: str = "",
) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, typing.Optional[T]]]:
    """
    A decorator that tries to open a file. On exception, can also optionally log
    detailed error information and exit the process
    """

    def decorator(
        func: typing.Callable[P, T]
    ) -> typing.Callable[P, typing.Optional[T]]:
        def wrapper(*args: P.args, **kw: P.kwargs) -> typing.Optional[T]:
            try:
                return func(*args, **kw)
            except FileNotFoundError as ex:
                log_exception(
                    ex,
                    verbose=verbose,
                    message=f"ERROR: '{path}' not found",
                    additional_info=additional_info,
                    error_number=ex.errno,
                )

                if should_exit:
                    exit_process(should_log=True)

            return None

        return wrapper

    return decorator


def with_load_json(
    path: str = "",
    should_exit: bool = False,
    verbose: bool = False,
    additional_info: str = "",
) -> typing.Callable[
    [typing.Callable[P, IOBase_Type_Var]],
    typing.Callable[P, typing.Optional[typing.Dict[str, object]]],
]:
    """
    A decorator that serializes JSON from a file. On exception, can also optionally
    log detailed error information and exit the process
    """

    def decorator(
        func: typing.Callable[P, typing.Optional[IOBase_Type_Var]]
    ) -> typing.Callable[P, typing.Optional[typing.Dict[str, object]]]:
        def wrapper(
            *args: P.args, **kw: P.kwargs
        ) -> typing.Optional[typing.Dict[str, object]]:
            try:
                result: typing.Optional[IOBase_Type_Var] = func(*args, **kw)
                if isinstance(result, io.IOBase):
                    return typing.cast(
                        typing.Dict[str, object], pyjson5.decode_io(result)
                    )
            except pyjson5.Json5Exception as ex:
                log_exception(
                    ex,
                    verbose=verbose,
                    message=f"ERROR: parsing JSON from '{path}' failed",
                    additional_info=additional_info,
                )

                if should_exit:
                    exit_process(should_log=True)

            return None

        return wrapper

    return decorator


def with_debug(func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    """
    Prints a debug message and runs debugpy, which will wait for a debugger
    to connect on the given port
    """

    def wrapper(*args: P.args, **kw: P.kwargs) -> T:
        print("path")
        pprint.pprint(sys.path)
        if kw["_debug"]:
            log_message("Debugging...", level="callout")
            if kw["_debug_port"]:
                log_message(f"Port - {kw['_debug_port']}", level="callout")
                debugpy.listen(("localhost", kw["_debug_port"]))
            else:
                pid = os.getpid()
                log_message(f"Pid - {pid}")

                input("press any key to continue")

                print("hello")

        return func(*args, **kw)

    return wrapper
