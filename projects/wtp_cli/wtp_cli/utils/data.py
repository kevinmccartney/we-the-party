"""
Shared utilities to be used across the application

Has functionality around
- logging
- process management
- wtp config acquisition
- opening files
"""
import io
import typing

from wtp_cli.utils.decorators import with_file_not_found, with_load_json


# TODO: make generic?
def open_json_file(
    path: str,
    should_exit: bool = False,
    verbose: bool = False,
) -> typing.Optional[typing.Dict[str, object]]:
    """Opens a JSON file with file not found and JSON parse error handling"""

    @with_load_json(path=path, should_exit=should_exit, verbose=verbose)
    @with_file_not_found(path=path, should_exit=should_exit, verbose=verbose)
    def open_file(inner_path: str) -> io.TextIOWrapper:
        return open(inner_path, encoding="utf-8")

    return open_file(path)
