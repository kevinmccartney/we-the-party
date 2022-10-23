# pylint: skip-file

from setuptools import find_packages, setup

setup(
    name="wtp",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "flask"],
    entry_points={
        "console_scripts": [
            "wtp = wtp_cli.cli:cli",
        ],
    },
)
