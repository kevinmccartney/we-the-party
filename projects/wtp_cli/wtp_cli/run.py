"""
Allows running wtp projects, with debugging.

Currently supports
- wtp_cli
- aws lambda (this will later be abstracted out to project targets)
"""

import importlib
import os
import re
import types
import typing

import click
from flask import Flask, Response, request

from wtp_cli.utils.decorators import with_debug
from wtp_cli.utils.logging import log_exception, log_message
from wtp_cli.utils.system import exit_process


def get_root_command(ctx: click.Context) -> click.Command:
    if ctx.parent is not None:
        return get_root_command(ctx.parent)

    return ctx.command


def get_command_with_args(
    node: typing.Union[click.Group, click.Command], path: [str]
) -> (click.Command, (str)):
    if isinstance(node, click.Group):
        return get_command_with_args(node.commands[path[1]], path[1:])

    return (node, path[1:])


def get_args_and_opts(command_components: [str]) -> ((str, ...), (object, ...)):
    opts = []
    args = []
    arg_ignore_indexes = []
    for i, segment in enumerate(command_components):
        # for '--foo bar' format
        if re.match("^--?[^=\s]*$", segment):
            opts = [*opts, {f"{segment[2:]}": command_components[i + 1]}]
            arg_ignore_indexes = [*arg_ignore_indexes, i + 1]
        # for '--foo=bar' format
        elif re.match("^--[^=\s]*=[^=\s]*$", segment):
            (key, value) = segment.split("=")
            opts = [*opts, {f"{key[2:]}": value}]
        elif i not in arg_ignore_indexes:
            args = [*args, segment]

    return (tuple(args), tuple(opts))


@with_debug
def run_wtp_cli(_ctx: click.Context, _debug: bool, _debug_port: int) -> None:
    """runs the wtp_cli project with optional debugging"""
    wtp_args = list(_ctx.params["_command"][0].split())

    root_command = get_root_command(_ctx)

    (command, args) = get_command_with_args(root_command, wtp_args)

    command(args)


# @with_debug
def start_dev_server(
    handler: str, _debug_port: int, _debug: bool, port: int
) -> typing.Optional[object]:
    """Exposes a lambda handler as a Flask endpoint that accepts POST requests"""
    app = Flask(__name__)
    pid = os.getpid()
    pkg: types.ModuleType

    log_message("Starting...")
    log_message(f"-  {handler}")

    log_message(f"Debug process pid - {pid}")

    input("press any key to continue")

    print("hello")

    lambda_name = handler.split(".")[-1]

    try:
        pkg = importlib.import_module(handler)
    except ModuleNotFoundError as ex:
        log_exception(ex, message=f"Module {handler} not found")
        exit_process(should_log=True)

    @app.route(f"/lambdas/{lambda_name}", methods=["POST"])
    def post() -> Response:
        log_message(f"handler - {handler}")

        data: typing.Dict[str, object] = {}
        content_type = request.headers.get("Content-Type")

        if content_type == "application/json":
            data = typing.cast(typing.Dict[str, object], request.json)
        else:
            return Response({"body": "Content-Type not supported", "code": 400})

        try:
            result = pkg.lambda_handler(data["event"], data["context"])

            return result
        except AttributeError:
            log_message(
                (
                    f"module '{handler}'"
                    " does not have a lambda handler called 'lambda_handler'"
                ),
                level="error",
            )

            return None

    # app.run(
    #     port=port,
    # )


# cli configuration
@click.group(help="Run a project on a local dev server")
def run() -> None:
    """Acts as a container for the commands to run projects"""


@click.command(
    name="aws_lambda", help="Run an AWS lambda, isolated to the local environment"
)
@click.option(
    "--port", "-p", type=int, default=5000, help="port used to accept requests"
)
@click.option(
    "--debug",
    "-d",
    type=bool,
    default=False,
    is_flag=True,
    help="toggles debug mode. exposes PID to attach to by default",
)
@click.option(
    "--debug-port",
    type=int,
    help="port that exposes the debugger",
)
@click.argument("handler")
def aws_lambda(handler: str, port: int, debug: bool, debug_port: int) -> None:
    """Starts a dev server for an AWS lambda handler"""
    start_dev_server(handler=handler, port=port, _debug=debug, _debug_port=debug_port)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    name="wtp_cli",
    help="Run an AWS lambda, isolated to the local environment",
)
@click.option(
    "--debug",
    "-d",
    type=int,
    default=False,
    help=(
        "set debug mode. exposes port 5678 by default, "
        "if used in conjunction with '--debug_pid', a pid will be exposed instead."
    ),
)
@click.option(
    "--debug_port", type=int, default=5678, help="port used to expose debugger"
)
@click.option(
    "--debug_pid", type=bool, default=False, help="expose a pid for debugging"
)
@click.argument("_command", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def wtp_cli(ctx: click.Context, _command: str, debug: bool, debug_port: bool) -> None:
    """
    Run the wtp cli with optional debugging.

    Example: wtp run wtp_cli --debug wtp generate config vscode
    """
    print(ctx)
    run_wtp_cli(_ctx=ctx, _debug=debug, _debug_port=debug_port)


run.add_command(aws_lambda)
run.add_command(wtp_cli)
