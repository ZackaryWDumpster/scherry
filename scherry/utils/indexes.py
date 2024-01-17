import os
from typing import TypedDict
import typing
from scherry.utils.cfg import appdata_dir, cfg
from scherry.utils.dictionary import ERROR
from scherry.utils.git import retrieve_file
import orjson

class FileStruct(TypedDict):
    path : str
    hashing : str

class IndexStruct(TypedDict):
    buckets : typing.Dict[str, str]
    files : typing.Dict[str, FileStruct]

indexes_dir = os.path.join(appdata_dir, "indexes")
os.makedirs(indexes_dir, exist_ok=True)

installedBuckets = cfg.getDeep("buckets", "installed")
if installedBuckets is ERROR:
    installedBuckets = {}

indexes = {
    "buckets" : {
        "test": "ZackaryW/scherry/main/scherry_bucket_test.zip",
        "main" : "ZackaryW/scherry/main/scherry_bucket_main.zip"
    },
    "files" : {}
}

def refresh_indexes():
    global indexes
    for bucketName, bucketMeta in installedBuckets.items():
        indexPath = os.path.join(indexes_dir, bucketName)
        indexUrl = os.path.dirname(bucketMeta.get("source"))
        indexUrl = f"{indexUrl}/scherry_indexes.json"
        content = retrieve_file(indexUrl, indexPath)
        contentDict = orjson.loads(content)
        if "buckets" in contentDict:
            indexes["buckets"].update(contentDict.get("buckets"))
        if "files" in contentDict:
            indexes["files"].update(contentDict.get("files"))

refresh_indexes()

__all__ = ["indexes", "FileStruct", "IndexStruct", "refresh_indexes"]