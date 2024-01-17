import click
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from scherry.cli.gen import gen # noqa

@click.group()
def cli():
    pass

cli.add_command(gen)

def cli_main():
    cli()

if __name__ == "__main__":
    cli_main()
