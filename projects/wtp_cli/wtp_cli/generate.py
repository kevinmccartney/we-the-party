"""
Provides functionality for generating code/project configuration and templates

Currently only supports VS Code configuration
"""
import functools
import json
import os
import typing

import click
import orjson
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder

from wtp_cli.utils.data import open_json_file
from wtp_cli.utils.logging import log_message
from wtp_cli.utils.system import exit_process
from wtp_cli.utils.workspace import wtp_workspace_root

VS_CODE_SETTINGS_TYPE = typing.Literal["minimal", "recommended", "opinionated"]


class ArbitraryTypesAllowedConfig:
    arbitrary_types_allowed = True


@dataclass(frozen=True, config=ArbitraryTypesAllowedConfig)
class GenerateConfigVSCodeOpts:
    """
    Represents the options used to generate config for VS Code

    context     - this is passed in from the CLI
    directory   - directory to use for loading VS Code workspace conf template partials
    config_type - represents how opinionated you want your settings to be
    out_file    - where to write the generated VS Code conf
    extensions  - keys of extension groups you want to include from the extensions
                  template partial
    verbose     - print additional info/debug/error info
    """

    context: click.Context
    directory: str
    config_type: VS_CODE_SETTINGS_TYPE
    out_file: str
    extensions: tuple[str]
    verbose: bool


@dataclass(frozen=True)
class VSCodeConfigProject:
    """
    A "folder" (in the Microsoft terminology) or "project" (our term) that is a
    member of the workspace
    """

    path: str
    name: typing.Optional[str] = None


@dataclass(frozen=True)
class VSCodeConfigProjectsFile:
    """
    A collection of "folders" (in the Microsoft terminology) or "projects" (our term)
    that are members of the workspace. The structure of this object mirrors the
    JSON of the VS Code *.code-workspace file
    """

    folders: tuple[VSCodeConfigProject, ...]


def generate_vscode_config(
    options: GenerateConfigVSCodeOpts,
) -> None:
    """Generates the VS Code workplace setting file"""
    context: click.Context = options.context
    directory: str = options.directory
    config_type: VS_CODE_SETTINGS_TYPE = options.config_type
    out_file: str = options.out_file
    extensions: tuple[str] = options.extensions
    verbose: bool = options.verbose

    current_path: str = os.path.abspath(os.getcwd())
    conf_path: str = vscode_conf_path(current_path, directory, context)
    src_exists: bool = os.path.isdir(conf_path)

    if not src_exists:
        log_message(
            f"config source files directory '{conf_path}' does not exist",
            level="error",
        )

        exit_process(should_log=True)

    log_message("\nGenerating VS Code configuration...", level="success")

    if verbose:
        log_message(f"- Using configuration directory {conf_path}", level="success")

    generate_files(conf_path, config_type, out_file, extensions, verbose)


def vscode_conf_path(current_path: str, directory: str, context: click.Context) -> str:
    """Returns the path for the directory containing VS Code configuration files"""
    conf_path = ""

    if context.get_parameter_source("directory") == click.core.ParameterSource.DEFAULT:
        wtp_dir = wtp_workspace_root(current_path)
        conf_path = f"{wtp_dir}/{directory.replace('<workspace_root>/', '')}"
    else:
        conf_path = os.path.abspath(f"{current_path}/{directory}")

    return conf_path


def generate_files(
    path: str,
    config_type: str,
    out_file: str,
    requested_extensions: tuple[str],
    verbose: bool,
) -> None:
    """Generates and writes the VS Code workspace settings conf file"""
    extensions_raw = open_json_file(
        f"{path}/extensions.json",
        should_exit=True,
        verbose=verbose,
    )
    extensions = typing.cast(
        typing.Optional[typing.Dict[str, tuple[str, ...]]], extensions_raw
    )
    new_extensions: typing.Optional[tuple[str, ...]] = None

    if extensions:
        new_extensions = vscode_extensions(extensions, requested_extensions)

    new_settings = vscode_settings(config_type, path)
    new_folders = vscode_workspace_projects(path)

    workplace_settings = {
        "folders": orjson.dumps(new_folders, default=pydantic_encoder).decode("ASCII"),
        "settings": new_settings,
        "extensions": {"recommendations": new_extensions},
    }
    formatted_workplace_settings = json.dumps(workplace_settings, indent=1)

    log_message(formatted_workplace_settings)

    out_file_full_path = os.path.abspath(f"{os.getcwd()}/{out_file}")

    with open(out_file_full_path, "w", encoding="utf8") as out_file_instance:
        out_file_instance.write(formatted_workplace_settings)
        out_file_instance.close()


def vscode_workspace_projects(
    src_dir: str,
) -> typing.Optional[tuple[VSCodeConfigProject, ...]]:
    """Returns the folders object from the folders.json file in the src_dir passed in"""
    project_raw = open_json_file(f"{src_dir}/folders.json")
    if project_raw:
        project_files = VSCodeConfigProjectsFile(
            folders=typing.cast(tuple[VSCodeConfigProject, ...], project_raw["folders"])
        )

        return project_files.folders

    return None


def vscode_extensions(
    all_extensions: typing.Dict[str, tuple[str, ...]],
    requested_extensions: tuple[str, ...],
) -> tuple[str, ...]:
    """Builds the extensions object.
    If 'all' is passed in, all extensions will be returned"""
    if "all" in requested_extensions:
        extensions: tuple[str, ...] = functools.reduce(
            lambda prev, current: (*prev, *current[1]), all_extensions.items(), ()
        )

        return extensions

    valid_extensions: typing.Dict[str, tuple[str, ...]] = functools.reduce(
        lambda prev, current: {**prev, f"{current}": all_extensions[current]},
        requested_extensions,
        {},
    )

    extension_names: tuple[str, ...] = functools.reduce(
        lambda prev, current: (*prev, *current[1]), valid_extensions.items(), ()
    )

    return extension_names


def vscode_settings(
    config_type: str, src_dir: str, verbose: bool = False
) -> typing.Dict[str, object]:
    """
    Returns a VS Code settings object based on the config type passed in

    """
    config_type_map = {"minimal": 0, "recommended": 1, "opinionated": 2}
    result: typing.Dict[str, object] = {}

    minimal_settings_path: str = f"{src_dir}/settings-minimal.json"

    log_message(f"- Using minimal settings source file {minimal_settings_path}")

    minimal_settings: typing.Optional[typing.Dict[str, object]] = open_json_file(
        minimal_settings_path, should_exit=True, verbose=verbose
    )

    if minimal_settings:
        result = {**minimal_settings}

    if config_type_map[config_type] >= 1:
        recommended_settings: typing.Optional[
            typing.Dict[str, object]
        ] = open_json_file(
            f"{src_dir}/settings-recommended.jsonc",
            should_exit=True,
            verbose=verbose,
        )

        if recommended_settings:
            result = {**result, **recommended_settings}

    if config_type_map[config_type] >= 2:
        opinionated_settings: typing.Optional[
            typing.Dict[str, object]
        ] = open_json_file(
            f"{src_dir}/settings-opinionated.jsonc", should_exit=True, verbose=verbose
        )

        if opinionated_settings:
            result = {**result, **opinionated_settings}

    return result


@click.group(help="Create code/project configuration and templates")
def generate() -> None:
    """Acts as a container for the generate command targets"""


@click.group(help="Service the wtp core and toolchain configuration")
def config() -> None:
    """Acts as a container for the commands to generate various types of configuration"""  # noqa: E501


@click.command(help="Generate VS Code workspace config files")
@click.option(
    "--directory",
    "-d",
    type=str,
    default="<workspace_root>/.wtp/config/vscode",
    help="Directory to read configuration files from",
)
@click.option(
    "--type",
    "-t",
    "config_type",
    type=click.Choice(["minimal", "recommended", "opinionated"], case_sensitive=False),
    default="recommended",
    help="What type of configuration to generate",
)
@click.option(
    "--outfile",
    "-o",
    "out_file",
    type=str,
    default="./wtp.code-workspace",
    help="Where to output the generated configuration",
)
@click.option(
    "--extensions",
    "-e",
    type=click.Choice(
        [
            "all",
            "general",
            "global_formatter",
            "theming",
            "monorepo",
            "a11y",
            "react_tsx",
            "css",
            "python",
            "typescript",
            "terraform",
            "yaml",
            "fun",
        ],
        case_sensitive=False,
    ),
    multiple=True,
    default=["all"],
    help="What extension groups to add",
)
@click.option(
    "--verbose",
    "-v",
    type=bool,
    default=False,
    is_flag=True,
    help="Print additional info to the stdout",
)
@click.pass_context
# I believe we have to pass all these arguments positionally to the handler
# Maybe there's a better way to do this?
# pylint: disable-next=too-many-arguments
def vscode(
    context: click.Context,
    directory: str,
    settings_profile: VS_CODE_SETTINGS_TYPE,
    out_file: str,
    extensions: tuple[str],
    verbose: bool,
) -> None:
    """
    The command for generating VS Code config with options to include settings
    a profile, extensions to include, and more.
    """
    generate_vscode_config(
        GenerateConfigVSCodeOpts(
            context=context,
            directory=directory,
            config_type=settings_profile,
            out_file=out_file,
            extensions=extensions,
            verbose=verbose,
        )
    )


generate.add_command(config)
config.add_command(vscode)
