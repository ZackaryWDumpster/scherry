from setuptools import setup

setup(
    name="scherry",
    version="0.1.1",
    packages=[
        "scherry",
        "scherry.utils",
        "scherry.core",
        "scherry.cli",
        "scherry.helper",
    ],
    install_requires=[
        "requests",
        "click",
        "orjson",
        "parse",
        "toml"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "scherry=scherry.cli.__main__:cli",
            "schry=scherry.cli.__main__:cli",
            "scherry-helper=scherry.helper.__main__:helper",
            "schryh=scherry.helper.__main__:helper",
        ]
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)