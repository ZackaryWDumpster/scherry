from functools import cache, cached_property
import os
from typing import TypedDict
from scherry.utils.cfg import appdata_dir
from scherry.utils.hashing import check_hash
import orjson
buckets_dir = os.path.join(appdata_dir, "buckets")
os.makedirs(buckets_dir, exist_ok=True)

class BucketMeta(TypedDict, total=False):
    filename : str
    vars : list

class Bucket:
    def __init__(self, name : str, source : str):
        self.__name = name
        self.__source = source
        
        if not os.path.exists(self.bucketPath):
            raise RuntimeError(f"{self.__name} bucket not found")
        
        if not os.path.exists(self.indexJsonPath):
            raise RuntimeError(f"{self.__name} index not found")
        
        if not self.indexHashConsistent:
            raise RuntimeError(f"{self.__name} index hash is not consistent")
        
    @cached_property
    def bucketPath(self):
        return os.path.join(buckets_dir, self.__name)    
    
    @cached_property
    def indexJsonPath(self):
        for f in os.listdir(self.bucketPath):
            if f.endswith(".json"):
                return os.path.join(self.bucketPath, f)
        return None
    
    @cached_property
    def indexHash(self):
        return os.path.basename(self.indexJsonPath).split(".")[0]
    
    @cached_property
    def indexHashConsistent(self):
        return check_hash(open(self.indexJsonPath, 'rb').read(), self.indexHash)
    
    @cached_property
    def contents(self):
        with open(self.indexJsonPath, 'rb') as f:
            return orjson.loads(f.read())
    
    @cached_property
    def index(self) -> dict:
        return self.contents["index"]
        
    @cached_property
    def fileNameIndex(self):
        return {v["filename"]: k for k, v in self.index.items()}
    
    @cached_property
    def fileNameNoExtensionIndex(self):
        return {v["filename"].split(".")[0]: k for k, v in self.index.items()}
    
    @cache
    def getMeta(self, key : str) -> BucketMeta:
        if "/" in key:
            splitted =key.split("/")
            if splitted[0] != self.__name:
                return None
            
            key = splitted[1]
            
        if "." in key and key in self.fileNameIndex:
            return self.index[self.fileNameIndex[key]]
        
        if "." not in key and key in self.index:
            return self.index[key]
        
        if key in self.fileNameNoExtensionIndex:
            return self.index[self.fileNameNoExtensionIndex[key]]
        return None
    
    def hasKey(self, key : str) -> bool:
        return self.getMeta(key) is not None
    
    @cache
    def get(self, key : str) -> bytes:
        meta = self.getMeta(key)

        if meta is None:
            return None
        
        with open(os.path.join(self.bucketPath,"scripts", meta["filename"]), 'rb') as f:
            contents =  f.read()
            if check_hash(contents, self.fileNameIndex[meta["filename"]]):
                return contents
            
            raise RuntimeError(f"{meta['filename']} hash is not consistent")
            
        
    