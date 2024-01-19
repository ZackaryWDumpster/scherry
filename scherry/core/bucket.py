import datetime
from functools import cached_property, lru_cache
from types import MappingProxyType
import typing

import orjson
from scherry.core import buckets_dir
import os
from scherry.core.model import BucketIndexModel

from scherry.utils.hashing import check_hash

class BucketMeta(type):
    _instances = {}
    
    def __call__(cls, arg):
        if arg not in cls._instances:
            cls._instances[arg] = super(BucketMeta, cls).__call__(arg)
        else:
            cls._instances[arg].refresh()
        
        return cls._instances[arg]

class Bucket(metaclass=BucketMeta):
    def __init__(self, foldername : str) -> None:
        self.__name = foldername
        if not check_hash(self._indexBytes, os.path.basename(self._indexPath).split(".")[0]):
            raise RuntimeError("Hashes do not match")
    
    @cached_property
    def _path(self):
        return os.path.join(buckets_dir, self.__name)
    
    @cached_property
    def _indexMdate(self):
        f = os.path.getmtime(self._indexPath)
        return datetime.datetime.fromtimestamp(f)
    
    @cached_property
    def _indexPath(self):
        for f in os.listdir(self._path):
            f : str
            if f.endswith(".json"):
                return os.path.join(self._path, f)
        return None
    
    @property
    def _indexBytes(self):
        return open(self._indexPath, 'rb').read()
    
    @cached_property
    def _index(self) -> BucketIndexModel:
        return orjson.loads(self._indexBytes)
    
    def refresh(self):
        for k in dir(self):
            if not k.startswith("_"):
                continue
            
            if k.startswith("__"):
                continue
            
            if k not in self.__dict__:
                continue
            
            self.__dict__.pop(k, None)
            
    @cached_property
    def bucketDownloadPath(self):
        gitUrl = self._index["gitUrl"]
        bucketDir = self._index["bucketDir"]
        name = self._index["name"]
        return f"{gitUrl}/{bucketDir}/{name}.zip"
    
    @cached_property
    def bucketFilesPath(self):
        gitUrl = self._index["gitUrl"]
        branch = self._index.get("branch", "main")
        return f"{gitUrl}/{branch}/scherry_files"
    
    @lru_cache
    def get_file(self, filename : str):
        for hashing, filemeta in self.files.items():
            if filemeta["file"] != filename:
                continue
            
            return {
                **filemeta,
                "hashing" : hashing
            }
            
        return None
    
    def get_file_url(self, filename : str):
        filemeta = self.get_file(filename)
        if filemeta is None:
            return None
        return f"{self.bucketFilesPath}/{filemeta['hashing']}"

    @property
    def files(self):
        return MappingProxyType(self._index["files"])
    
    @property
    def scripts(self):
        return MappingProxyType(self._index["scripts"])
    
    @cached_property
    def _scriptNames(self):
        return [x.split(".")[0] for x in self.scripts.keys()]
    
    def get_script(self, name : str):
        noextname = name.split(".")[0] if "." in name else name
        
        target = None
        for k, v in self.scripts.items():
            knoext = k.split(".")[0] if "." in k else k
            if knoext == noextname:
                target = k, v
                break
        
        if target is None:
            return None
        
        hashing = target[1]["hashing"]
        fileBytes = open(os.path.join(self._path, "scripts", target[0]), 'rb').read()
        if not check_hash(fileBytes, hashing):
            raise RuntimeError("Hashes do not match")
        
        return fileBytes.decode()
    
    @property
    def buckets(self):
        return MappingProxyType(self._index["buckets"])
    
    @classmethod
    def retrieve(cls) -> typing.Dict[str, "Bucket"]:
        bk = {}
        for folder in os.listdir(buckets_dir):
            if not os.path.isdir(os.path.join(buckets_dir, folder)):
                continue
            
            try:
                bk[folder] = Bucket(folder)
            except: #noqa
                pass
            
        return bk
    
    