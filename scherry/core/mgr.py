
from functools import cache
import os
import shutil
import typing
from venv import logger

from scherry.core.bucket import Bucket
from scherry.core import buckets_dir, cfg, bucket_cache_dir
from scherry.core.ctx import ScherryCtx, KeyPassObj
from scherry.utils.file import download_github_raw_content
from scherry.utils.hashing import check_hash, get_hash

class ScherryMgrMeta(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScherryMgrMeta, cls).__call__(*args, **kwargs)
        return cls._instance
    
class ScherryMgr(metaclass=ScherryMgrMeta):
    __bucketMaps : typing.Dict[str, Bucket]
    
    def __init__(self):
        self.__bucketMaps = Bucket.retrieve()
        self.__pushedScope : str = None
        self.__includedScopes : typing.List[str] = []
        self.__excludedScopes : typing.List[str] = []
        
    def bucket_list_collected(self):
        _map = {}
        
        for bk in self.__bucketMaps.values():
            _map.update(bk.buckets)
            
        return _map
    
    def bucket_list_installed(self):
        return list(self.__bucketMaps.keys())
        
    def bucket_is_installed(self, name : str):
        if not os.path.exists(os.path.join(buckets_dir, name)):
            return False
        
        if len(os.listdir(os.path.join(buckets_dir, name))) == 0:
            return False
        
        return True
    
    def bucket_install(self, name : str, url : str = None):
        if name in cfg.get("bucketsCheck"):
            return False
        
    def push_bucket_scope(self, name : str):
        if name not in self.__bucketMaps:
            return False
        
        if len(self.__excludedScopes) > 0 or len(self.__includedScopes) > 0:
            return False
        
        self.__pushedScope = name
        self.get_script.cache_clear()
        return True
        
    def clear_bucket_scope(self):
        self.__pushedScope = None
        self.get_script.cache_clear()
        return True
        
    def add_included_buckets(self, *names):
        if self.__pushedScope is not None or len(self.__excludedScopes) > 0:
            return False
        
        for name in names:
            if name not in self.__bucketMaps:
                return False
        
        self.__includedScopes.extend(names)
        self.get_script.cache_clear()
        return True
    
    def add_excluded_buckets(self, *names):
        if self.__pushedScope is not None or len(self.__includedScopes) > 0:
            return False
        
        for name in names:
            if name not in self.__bucketMaps:
                return False
        
        self.__excludedScopes.extend(names)
        self.get_script.cache_clear()
        return True
    
    def clear_bucket_filters(self):
        self.__pushedScope = None
        self.__includedScopes = []
        self.__excludedScopes = []
    
    
    def resolve_specified_bucket(self, key : str):
        splitted = key.split("/")
        bucketname = splitted[0]
        key = splitted[1]
        bucket = self.__bucketMaps[bucketname]
        return bucket, key
    
    @cache
    def get_script(self, key : str):
        if "/" in key:
            bucket, key = self.resolve_specified_bucket(key)
            if bucket is None:
                return None
            return bucket.get_script(key)
            
        for name, bucket in self.__bucketMaps.items():
            if self.__pushedScope is not None and self.__pushedScope != name:
                continue
            
            if self.__includedScopes and name not in self.__includedScopes:
                continue
            
            if self.__excludedScopes and name in self.__excludedScopes:
                continue
            
            val = bucket.get_script(key)
            if val is not None:
                return val
    
    def static_file(
        self, filename : str
    ):
        if "/" in filename:
            bucket, filename = self.resolve_specified_bucket(filename)
            if bucket is None:
                return None
            fileurl = bucket.get_file_url(filename)
            filemeta = bucket.get_file(filename)
            if fileurl is None:
                return None
        else:
            for bucket in self.__bucketMaps.values():
                fileurl = bucket.get_file_url(filename)
                if fileurl is not None:
                    filemeta = bucket.get_file(filename)
                    break
                    
        hashing = filemeta["hashing"]
        expected_path = os.path.join(bucket_cache_dir, hashing)
        if os.path.exists(expected_path):
            expected_bytes = open(expected_path, 'rb').read()
            if check_hash(expected_bytes, hashing):
                return shutil.copy(expected_path, filename)
            
        content = download_github_raw_content(fileurl)
        
        if (contentHash := get_hash(content)) != hashing:
            logger.error("expected hash %s, got %s", hashing, contentHash)
            raise RuntimeError(f"redownloaded hash for {filename} mismatch")
        
        with open(expected_path, 'wb') as f:
            f.write(content)

        shutil.copy(expected_path, filename)
        
    
    def run_multiple(
        self,
        *args,
        ctx :ScherryCtx = None,
    ):
        if ctx is None:
            ctx = ScherryCtx()
        
        for arg in args:
            script = self.get_script(arg)
            if script is None:
                raise RuntimeError(f"{arg} script not found")
            
            ctx.preSetup(arg)
            
            exec(script, ctx.getData(KeyPassObj))
            
            ctx.postSetup()
            
        return ctx
    