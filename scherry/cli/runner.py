import click
from scherry.core.ctx import ScherryCtx
from scherry.core.mgr import ScherryMgr
import json
mgr = ScherryMgr()

def parse_keyval(arg : str):
    # parse arg name=value separated by ,
    if "," not in arg:
        splitted = arg.split("=")
        return {splitted[0] : splitted[1]}
    
    splitted = arg.split(",")
    splitted = [x.strip() for x in splitted]
    return {x.split("=")[0] : x.split("=")[1] for x in splitted}

def parse_cmds(*args):
    ctx = ScherryCtx(mgr)
    sequence = []
    
    for arg in args:
        match arg:
            case "[]":
                sequence.extend(mgr.list_script_names())
            case "$":
                mgr.clear_bucket_filters()
            case str() if arg.startswith("$:"):
                mgr.push_bucket_scope(arg[2:])
            case str() if arg.startswith("(") and arg.endswith(")"):
                # parse arg name=value separated by ,
                kdict = parse_keyval(arg[1:-1])
                ctx.setPersistent(*mgr.current_bucket_scopes(), data=kdict)
            case str() if arg.startswith("{") and arg.endswith("}"):
                # parse as dict
                kdict = json.loads(arg)
                ctx.setPersistent(*mgr.current_bucket_scopes(), data=kdict)
            case _:
                sequence.append(arg)
                
    return ctx, sequence
            
        
@click.command("run")
@click.argument("args", nargs=-1)
def run(args):
    ctx, sequence = parse_cmds(*args)
    mgr.run_multiple(*sequence, ctx=ctx)
    