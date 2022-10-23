"""
Exposes functionality to interact with the system the wtp CLI is running on.
"""
import sys

from wtp_cli.utils.logging import log_message


def exit_process(should_log: bool = False) -> None:
    """End the process with an optional message."""
    if should_log:
        log_message("Exiting...", level="error")

    sys.exit(1)
