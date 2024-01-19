
import os
from scherry.utils.auto_save_dict import AutoSaveDict

# [appdata]
core_dir = os.path.dirname(os.path.realpath(__file__))
mod_dir = os.path.dirname(core_dir)

appdata_dir= os.path.join(mod_dir, "appdata")

os.makedirs(appdata_dir, exist_ok=True)

# [appdata/buckets]
buckets_dir = os.path.join(appdata_dir, "buckets")
os.makedirs(buckets_dir, exist_ok=True)

# [appdata/file_cache]
file_cache_dir = os.path.join(appdata_dir, "file_cache")
os.makedirs(file_cache_dir, exist_ok=True)

# [appdata/file_cache.json]
file_cache_index_path = os.path.join(appdata_dir, "file_cache.json")
file_cache_index = AutoSaveDict(file_cache_index_path)

