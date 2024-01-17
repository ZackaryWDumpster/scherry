import os
import click
import orjson
from scherry.utils.hashing import get_hash
import zipfile

_excluded_vars = [
    "inputPath", # list
    "outputPath",# list
    "inputCwd",
    "outputCwd",
    "debugLv" # int
]
def _parse_global_vars(lines):
    
    vars = []
    for line in lines:
        line : str
        if line.startswith("_"):
            continue
        
        stripedLine = line.replace(" ", "")
        if "=globals().get(" not in stripedLine:
            continue
        
        split1 = stripedLine.split('=globals().get(')
        firstPortion = split1[0]
        secondPortion = split1[1]
        
        if ":" in firstPortion:
            firstVar = firstPortion.split(":")[0]
        else:
            firstVar = firstPortion

        firstVarLength = len(firstVar)
        if firstVarLength > 0 and firstVar == secondPortion[1:firstVarLength+1]:
            vars.append(firstVar)
    
    return [x for x in vars if x not in _excluded_vars]

def _parse_toml(path : str):
    # replace extension 
    if not path.endswith(".toml"):
        path = os.path.splitext(path)[0] + ".toml"

    if not os.path.exists(path):
        return None
    
    return get_hash(open(path, 'rb').read())

@click.command()
@click.argument("folder", type=click.Path(exists=True))
@click.option("--name", "-n", help="name of the script")
def gen(folder, name):
    name = os.path.basename(folder) if name is None else name
    
    gendict = {}
    index_write = gendict["index"] = {}
    scripts_dir = os.path.join(folder, 'scripts')

    if not os.path.exists(scripts_dir):
        click.echo("missing scripts folder, terminating")
        return
    
    # delete all json files at root level
    for file in os.listdir(folder):
        if file.endswith(".json"):
            os.remove(os.path.join(folder, file))
    
    for file in os.listdir(scripts_dir):
        path = os.path.join(scripts_dir, file)
        
        with open(path, 'r') as f:
            readContents = f.readlines()

            # replace crlf with lf
            readContents = [x.replace('\r\n', '\n') if x.endswith('\r\n') else x for x in readContents]

        with open(path, 'w') as f:
            f.writelines(readContents)

        with open(path, 'rb') as f:
            hashed = get_hash(f.read())
            index_write[hashed] = {
                "filename" : file
            }
            
        if not any("globals()" in x for x in readContents):
            continue
            
        global_vars = _parse_global_vars(readContents)
            
        if len(global_vars) > 0:
            index_write[hashed]["vars"] = global_vars

    gendict["name"] = name
    
    bytesData = orjson.dumps(gendict, option=orjson.OPT_INDENT_2) 
    index_write_hash = get_hash(bytesData)

    with open(os.path.join(folder, str(index_write_hash)+".json"), 'wb') as f:
        f.write(bytesData)
        
    _zipfile = os.path.join(os.path.dirname(folder), folder+".zip")
    if os.path.exists(_zipfile):
        os.remove(_zipfile)                            
        
    # create zip to the parent level of the folder
    with zipfile.ZipFile(_zipfile, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(folder):
            for filename in filenames:
                # exclude files start with _ and folder with __
                if filename.startswith("_") or os.path.basename(folderName).startswith("__"):
                    continue
                
                filePath = os.path.join(folderName, filename)
                archiveName = os.path.relpath(filePath,folder)

                zipObj.write(filePath, archiveName)
        
    click.echo("done")

