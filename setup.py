from setuptools import setup

setup(
    name="scherry",
    version="0.0.1",
    packages=[
        "scherry",
        "scherry.utils",
        "scherry.core",
        "scherry.cli",
    ],
    install_requires=[
        "requests",
        "click",
        "orjson",
        "parse"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "scherry=scherry.cli.__main__:cli",
            "schry=scherry.cli.__main__:cli",
            "scherry-bkup=scherry.cli.bkup:cli",
        ]
    }
)