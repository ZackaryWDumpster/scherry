import click
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from scherry.cli.appdata import appdata

@click.group()
def cli():
    pass

cli.add_command(appdata)

if __name__ == "__main__":
    cli()