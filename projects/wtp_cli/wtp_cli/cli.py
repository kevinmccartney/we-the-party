"""
The main CLI module.

Exports the click instance that makes up the wtp CLI
"""
import sys

import click

from wtp_cli.generate import generate
from wtp_cli.run import run

print(sys.path)


@click.group()
def cli() -> None:
    """Acts as root for the rest of the CLI command tree"""


# building run command tree
cli.add_command(run)

# building config command tree
cli.add_command(generate)
