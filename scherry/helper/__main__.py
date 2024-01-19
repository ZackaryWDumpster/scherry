import json
import os
import shutil
import click
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from scherry.utils.file import get_files, touch_file
from scherry.helper.gen_parse import parse_scripts, parse_files, parse_config
from scherry.utils.hashing import get_hash
from scherry.helper.utils import make_zip

_config_content= """
name="{val}"
bucketDir = "buckets"
gitUrl = "[input]"

"""

_v_validation_res = None

@click.group()
def helper():
    pass

@helper.command("init")
def _init():
    input("allow current working directory (git repo) as scherry bucket?")
    os.makedirs("buckets", exist_ok=True)
    os.makedirs("scherry_files", exist_ok=True)

@helper.command("init-bucket")
@click.argument("name")
def init_bucket(name : str):
    if not os.path.exists("buckets") or not os.path.exists("scherry_files"):
        _init()
    
    path = os.path.join("buckets", name)
    
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(os.path.join(path, "scripts"))
        os.makedirs(os.path.join(path, "files"))
        touch_file(os.path.join(path, "config.toml"), content=_config_content.format(val=name))
        
        return click.echo(f"created bucket at {path}")

    click.echo("bucket already exists")
    
@helper.command("gen")
@click.argument("name")
@click.option("--zip", "-z", is_flag=True)
@click.option("--copy", "-c")
@click.pass_context
def gen(ctx : click.Context, name : str, zip : bool, copy : str):
    path = os.path.join("buckets", name)
    
    if not os.path.exists(path):
        return ctx.invoke(init_bucket, name=name)
    
    # disable click echo
    originalMethod = click.echo 
    click.echo = lambda x: None
    ctx.invoke(validate, name=name)
    click.echo = originalMethod
    
    if not _v_validation_res:
        click.echo("validation failed")
        return

    json_files = get_files(path, [".json"])
    # remove all
    for file in json_files:
        os.remove(os.path.join(path, file))
    
    # parse
    scripts_cfg = parse_scripts(os.path.join(path, "scripts"))
    files_cfg = parse_files(os.path.join(path, "files"))
    config = parse_config(os.path.join(path, "config.toml"))
    config["scripts"] = scripts_cfg
    config["files"] = files_cfg
    
    cfg_bytes = json.dumps(config, indent=2).encode()
    cfg_hashing =get_hash(cfg_bytes)
    with open(f"{path}/{cfg_hashing}.json", "wb") as f:
        f.write(cfg_bytes)
        
    if zip:
        make_zip(path, ["config.toml", "files"])
    
    if copy:
        if os.path.exists(os.path.join(copy, name)):
            shutil.rmtree(os.path.join(copy, name))
            
        shutil.copytree(
            path, os.path.join(copy, name), dirs_exist_ok=True,
            #exclude config.toml
            ignore=shutil.ignore_patterns("config.toml")
        )
    
    click.echo("done")
    
@helper.command("validate")
@click.argument("name")
def validate(name : str):
    global _v_validation_res
    _v_validation_res = False
    
    path = os.path.join("buckets", name)
    if not os.path.exists(path):
        return click.echo("false")
    
    if not os.path.exists(os.path.join(path, "config.toml")):
        return click.echo("false")
    
    if not os.path.exists(os.path.join(path, "scripts")):
        return click.echo("false")
    
    for file in os.listdir(os.path.join(path, "scripts")):
        if not os.path.isfile(os.path.join(path, "scripts", file)):
            return click.echo("false")
    
    if not os.path.exists(os.path.join(path, "files")):
        return click.echo("false")
    
    json_files = get_files(path, [".json"])
    
    if len(json_files) == 0:
        _v_validation_res = True
        return click.echo("true")
    
    if len(json_files) > 1:
        return click.echo("false")
    
    json_hash = get_hash(open(os.path.join(path, json_files[0]), 'rb').read())
    
    parse_config(os.path.join(path, "config.toml"))
    
    if json_hash != json_files[0].split(".")[0]:
        return click.echo("false")
    
    _v_validation_res = True
    
    return click.echo("true")

if __name__ == "__main__":
    helper()