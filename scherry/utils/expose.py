from scherry.core.mgr import ScherryMgr

mgr = ScherryMgr()

def run(key : str):
    mgr.run_scripts(key)
    
def runs(*keys : list):
    mgr.run_scripts(*keys)