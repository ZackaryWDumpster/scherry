
import json
import os
import click
from scherry.core.mgr import ScherryMgr

@click.command("runs")
@click.argument("cmds", nargs=-1)
@click.option("--cfg")
def run_cmd(cmds, cfg : str):
    # parse cfg into dict
    if cfg is not None and cfg.startswith("{"):
        cfg = json.loads(cfg)
    elif cfg is not None:
        par = cfg.split(",")
        base = {x.split("=")[0]:x.split("=")[1] for x in par}
        cfg = {}
        for k, v in base.items():
            if "/" in k:
                _s = k.split("/")
                base = _s[0]
                key = _s[1]
                if base not in cfg:
                    cfg[base] = {}
                cfg[base][key] = v
            else:
                if "global" not in cfg:
                    cfg["global"] = {}
                cfg["global"][k] = v
    else:
        cfg = {}
        
    from scherry.utils.expose import mgr
    mgr.run_scripts(*cmds, temp=cfg)
    
@click.group("bucket", invoke_without_command=True)
@click.pass_context
def bucket(ctx : click.Context):
    ctx.ensure_object(ScherryMgr)
    
@bucket.command("update")
@click.argument("name")
@click.pass_obj
def update_bucket(mgr : ScherryMgr, name : str): 
    mgr.update_bucket(name)
    
@bucket.command("uninstall")
@click.argument("name")
@click.pass_obj
def uninstall_bucket(mgr : ScherryMgr, name : str):
    mgr.uninstall_bucket(name)
    
@click.group("list", invoke_without_command=True)
@click.pass_context
def list_(ctx : click.Context):
    ctx.ensure_object(ScherryMgr)
    if ctx.invoked_subcommand is None:
        # do help
        print(ctx.get_help())
    
@list_.command("bucket")
@click.pass_obj
def list_buckets(mgr : ScherryMgr):
    for key in mgr.installed_buckets():
        print(key)
        
@list_.command("script")
@click.pass_obj
def list_scripts(mgr : ScherryMgr):
    for bucket in mgr.buckets:
        for script in bucket.fileNameNoExtensionIndex.keys():
            print(script)
            
            
@click.command("appdata")
def open_appdata():
    from scherry.utils.cfg import appdata_dir
    os.startfile(appdata_dir)