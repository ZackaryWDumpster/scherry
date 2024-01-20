import os
import shutil
import zipfile
import click
from scherry.core import appdata_dir
from scherry.utils.zip import extract_zip, make_zip

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

def resolve_import_path(path : str):
    # if zip file
    if path.endswith(".zip"):
        return path

    # if folder and contains appdata.zip
    if os.path.isdir(path) and os.path.exists(os.path.join(path, "appdata.zip")):
        return os.path.join(path, "appdata.zip")

    # if folder basename is appdata and contains buckets
    if os.path.basename(path) == "appdata" and os.path.isdir(os.path.join(path, "buckets")):
        return path

    # has sub folder
    for sub in os.listdir(path):
        sub_path = os.path.join(path, sub)
        if os.path.isdir(sub_path):
            return resolve_import_path(sub_path)
    
    return None

@appdata.command("import", help="import appdata folder")
@click.option("--path", "-p", default=os.getcwd())
@click.option("--mkbkup", "-m", is_flag=True, help="make backup before import")
def import_(path : str, mkbkup : bool):
    if mkbkup:
        make_zip(appdata_dir, targetPath=os.path.join(appdata_dir, "bkup"))
        
    shutil.rmtree(appdata_dir, ignore_errors=True)
        
    ipath = resolve_import_path(path)
    
    if ipath is None:
        return click.echo("invalid path")
    
    if os.path.dirname(ipath) != path and path != ipath:
        input(f"Please confirm the path is correct. {ipath}")
    
    if ipath.endswith(".zip"):
        with zipfile.ZipFile(ipath) as zipobj:
            extract_zip(zipobj, appdata_dir)
    else:
        shutil.copytree(ipath, appdata_dir, dirs_exist_ok=True)
    
    click.echo("done")