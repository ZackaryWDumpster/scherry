import os
from typing import TypedDict
import typing
from scherry.utils.cfg import appdata_dir
from scherry.utils.git import retrieve_file
import orjson

class FileStruct(TypedDict):
    path : str
    hashing : str

class IndexStruct(TypedDict):
    buckets : typing.Dict[str, str]
    files : typing.Dict[str, FileStruct]

indexes_path = os.path.join(appdata_dir, "indexes")

retrieve_file("ZackaryW/scherry/main/scherry_indexes.json", indexes_path)

with open(indexes_path, 'r') as f:
    indexes : IndexStruct = orjson.loads(f.read())
    
