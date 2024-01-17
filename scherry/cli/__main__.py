import click
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from scherry.cli.gen import gen
from scherry.cli.exe import run_cmd, list_, bucket

@click.group(invoke_without_command=True)
@click.option("--debug", "-d", is_flag=True)
def cli(debug):
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

cli.add_command(gen)
cli.add_command(run_cmd)
cli.add_command(list_)
cli.add_command(bucket)

def cli_main():
    cli()

if __name__ == "__main__":
    cli_main()
