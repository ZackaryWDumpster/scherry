
import os
import shutil
import click
from scherry.core import appdata_dir
from scherry.utils.zip import make_zip

@click.group("appdata", help="everything related to appdata")
def appdata():
    pass

@appdata.command("open", help="open appdata folder")
def open():
    os.startfile(appdata_dir)
    
@appdata.command("prune", help="prune appdata folder")
def prune():
    shutil.rmtree(appdata_dir)
    
@appdata.command("export", help="export appdata folder")  
@click.option("--zip", "-z", is_flag=True)
@click.option("--path", "-p", default=os.getcwd())
def export(zip : bool, path : str):
    if zip:
        make_zip(appdata_dir, targetPath=path)
    else:
        if len(os.listdir(path)) > 0:
            path = os.path.join(path, "appdata")
        os.makedirs(path, exist_ok=True)
        shutil.copytree(appdata_dir, path, dirs_exist_ok=True)
