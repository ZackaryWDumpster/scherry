import click
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from scherry.cli.appdata import appdata
from scherry.cli.runner import run
from scherry.cli.bucket import bucket
from scherry.cli.script import script

@click.group()
def cli():
    pass

cli.add_command(appdata)
cli.add_command(run)
cli.add_command(bucket)
cli.add_command(script)

if __name__ == "__main__":
    cli()