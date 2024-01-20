import os
import click
from scherry.core import buckets_dir, mgr as _mgr

mgr = _mgr.ScherryMgr()

@click.group("bucket", help="everything related to buckets")
def bucket():
    pass

@bucket.command("open", help="open bucket folder")
def open():
    os.startfile(buckets_dir)
    
@bucket.command("list", help="list buckets")
@click.option("--installed", "-i", is_flag=True)
@click.option("--indexed", "-x", is_flag=True)
def list_(installed, indexed):
    if installed:
        entries = mgr.bucket_list_installed()
    elif indexed:
        entries = mgr.bucket_list_collected().keys()
    else:
        entries = mgr.bucket_list_collected().keys()
        
    for x in entries:
        click.echo(x)
        
@bucket.command("install", help="install bucket")
@click.argument("name")
@click.option("--url", "-u")
@click.option("--force", "-f", is_flag=True)
def _install(name, url, force):
    mgr.bucket_install(name, url, force=force)
    
@bucket.command("update", help="update bucket")
@click.argument("name")
def _update(name):
    mgr.bucket_install(name, force=True)
    
@bucket.command("uninstall", help="uninstall bucket")
@click.argument("name")
def _uninstall(name):
    mgr.bucket_uninstall(name)
    
@bucket.command("info", help="info about bucket")
@click.argument("name")
def _info(name):
    bk = mgr.get_bucket(name)
    if bk is None:
        click.echo("bucket not found")
        return
    
    click.echo(f"name: {bk.name}")
    
    click.echo("---buckets---")
    for x in bk.buckets:
        click.echo(x)
    
    click.echo("---files---")
    for x in bk.files.values():
        click.echo(x["file"])
    
    click.echo("---scripts---")
    for x in bk.scripts:
        click.echo(x)