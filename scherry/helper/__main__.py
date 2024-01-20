
import os
import click
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from scherry.helper.bucket import bk

@click.group()
def helper():
    pass

helper.add_command(bk)

if __name__ == "__main__":
    helper()