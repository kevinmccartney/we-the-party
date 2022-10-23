"""
Exposes functionality to interact with the wtp workspace.

Includes
- Finding the workspace root
"""
import os
import pathlib


def wtp_workspace_root(current_path_location: str) -> str:
    """Returns the directory that contains the We The Party workspace configuration file"""  # noqa: E501 # pylint: disable=line-too-long
    dir_contents = os.listdir(current_path_location)

    if ".wtprc" in dir_contents:
        # check that we can open the file
        with open(f"{current_path_location}/.wtprc", encoding="utf8"):
            return current_path_location

    if current_path_location != "/":
        current_path = pathlib.Path(current_path_location)
        parent_dir_path = os.path.abspath(current_path.parent.absolute())

        os.chdir(parent_dir_path)

        return wtp_workspace_root(parent_dir_path)

    return ""
