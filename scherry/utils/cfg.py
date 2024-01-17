
import os

from scherry.utils.autoSaveDict import AutoSaveDict

core_dir = os.path.dirname(os.path.realpath(__file__))
mod_dir = os.path.dirname(core_dir)

appdata_dir= os.path.join(mod_dir, "appdata")

os.makedirs(appdata_dir, exist_ok=True)

cfg = AutoSaveDict(os.path.join(appdata_dir, "cfg.json"))
