import click

from scherry.core import mgr

_mgr = mgr.ScherryMgr()

@click.group("script", help="everything related to scripts")
def script():
    pass

@script.command("list", help="list scripts")
def list_():
    for x in _mgr.list_script_names():
        click.echo(x)