import os
import shutil
import click
import toml
from scherry.helper.utils import crlf_to_lf_1, crlf_to_lf_2
from scherry.utils.hashing import get_hash

def parse_scripts(path : str):
    ret = {}
    
    for file in os.listdir(path):
        crlf_to_lf_2(os.path.join(path, file))
        click.echo(f"parsing {file}")
        hashing = get_hash(open(os.path.join(path, file), 'rb').read())
        ret[file] = {
            "hashing" : hashing
        }
        
    return ret

def parse_files(path : str, collectionPath : str = os.getcwd()):
    ret = {}
    
    scherry_files =os.path.join(collectionPath, "scherry_files")
    if not os.path.exists(scherry_files):
        input("Please confirm it is okay to create scherry_files folder in the current cwd path")
        os.makedirs(scherry_files, exist_ok=True)
        
    for file in os.listdir(path):
        click.echo(f"indexing {file}")
        bytesData = open(os.path.join(path, file), 'rb').read()
        bytesData = crlf_to_lf_1(bytesData)
        hashing = get_hash(bytesData)
    
        with open(os.path.join(path, file), 'wb') as f:
            f.write(bytesData)
            f.truncate()
        
        ret[hashing] = {
            "file" : file,
        }
        
        with open(os.path.join(scherry_files, hashing), 'wb') as f:
            f.write(bytesData)
            f.truncate()
        
    return ret

def parse_config(path : str):
    ret= {}
    
    tomldata = toml.load(path)

    if not tomldata:
        return ret

    try:
        ret["name"] = tomldata.get("name")
        ret["bucketDir"] = tomldata.get("bucketDir")
        ret["gitUrl"] = tomldata.get("gitUrl")
    except: #noqa
        click.echo("config.toml invalid")
        
    ret["buckets"] = tomldata.get("buckets", {})
    
    return ret
    
    