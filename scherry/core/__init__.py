
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

# [appdata/tracked.json]
tracked_index_path = os.path.join(appdata_dir, "tracked.json")
tracked_index = AutoSaveDict(tracked_index_path)

# [appdata/cache]
cache_dir = os.path.join(appdata_dir, "cache")
os.makedirs(cache_dir, exist_ok=True)

# [appdata/bucket_cache]
bucket_cache_dir = os.path.join(appdata_dir, "bucket_cache")
os.makedirs(bucket_cache_dir, exist_ok=True)

# [appdata/cfg.json]
cfg = AutoSaveDict(os.path.join(appdata_dir, "cfg.json"))
cfg.setdefault("bucketsCheck", {})