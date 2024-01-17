import pprint
import shutil
import click
import sys
import os
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from scherry.utils.cfg import appdata_dir # noqa

@click.group("bkup")
def _cli():
    pass

@_cli.command("export")
@click.option("--zip", "-z", is_flag=True)
@click.option("--dir", "-d", default=os.getcwd(), help="Specify the directory to export to")
def export(zip: bool, dir: str):
    if zip:
        export_zip_file = os.path.join(dir, "exported.zip")
        if os.path.exists(export_zip_file):
            shutil.move(export_zip_file, os.path.join(os.path.dirname(export_zip_file), f"{os.path.basename(export_zip_file)}.old"))

        with zipfile.ZipFile(export_zip_file, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(appdata_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create a relative path within the zip file
                    zip_path = os.path.relpath(file_path, start=appdata_dir)
                    z.write(file_path, zip_path)

    elif os.path.basename(dir) != "exported":
        target_dir = os.path.join(dir, "exported")
        os.makedirs(target_dir, exist_ok=True)
        shutil.copytree(appdata_dir, target_dir, dirs_exist_ok=True)
    else:
        shutil.copytree(appdata_dir, dir, dirs_exist_ok=True)

    print(f"exported to {dir}")

    
@_cli.command("import")
@click.option("--clean", "-c", is_flag=True)
@click.option("--path", "-p", default=os.getcwd(), help="Specify the directory to import from")
def import_(clean : bool, path : str):
    target_folder = path
    if clean:
        if os.path.exists(appdata_dir):
            shutil.rmtree(appdata_dir)
        os.makedirs(appdata_dir, exist_ok=True)    

    
    if path.endswith(".zip"):
        target_path = path
    elif os.path.exists(os.path.join(target_folder, "exported.zip")):
        target_path = os.path.join(target_folder, "exported.zip")
    
    if "target_path" in locals():
        with zipfile.ZipFile(target_path, "r") as zip_ref:
            pprint.pprint(zip_ref.filelist)
            pprint.pprint(zip_ref.namelist())
            zip_ref.extractall(appdata_dir)
        print("imported")
        return
    
    if os.path.exists(os.path.join(target_folder, "exported")):
        appdata_folder_path = os.path.join(target_folder, "exported")
    elif os.path.exists((appdata_folder_path :=os.path.join(target_folder, "scherry", "appdata"))):
        pass
    elif os.path.exists((appdata_folder_path :=os.path.join(target_folder, "appdata"))):
        pass
    
    print("set appdata to be imported as ", appdata_folder_path)
    shutil.copytree(appdata_folder_path, appdata_dir, dirs_exist_ok=True)
    
    print("imported")    
    
def cli():
    _cli()
    
if __name__ == "__main__":
    cli()