
import datetime
from functools import cache
import logging
import os
import shutil
import typing
from venv import logger

from scherry.core.bucket import Bucket
from scherry.core import buckets_dir, bucket_cache_dir, tracked_index, cache_dir
from scherry.core.ctx import ScherryCtx, KeyPassObj
from scherry.core.model import TrackedIndexEntry
from scherry.utils.git import download_github_raw_content, git_last_commit_date
from scherry.utils.hashing import check_hash, get_hash
from scherry.utils.zip import extract_zip

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
        self.__localFileCache : typing.Dict[str, bytes] = {}
        
        
        if len(self.__bucketMaps) == 0:
            logging.info("no bucket found, defaulting to install main")
            self.bucket_install("main", "zackaryw/scherry")
        
    def bucket_list_collected(self):
        _map = {}
        
        for bk in self.__bucketMaps.values():
            _map.update(bk.buckets)
            
        return _map
    
    def get_bucket(self, name :str) -> Bucket | None:
        if name not in self.__bucketMaps:
            return None
        
        return self.__bucketMaps[name]
    
    def bucket_list_installed(self):
        return list(self.__bucketMaps.keys())
        
    def bucket_is_installed(self, name : str):
        if not os.path.exists(os.path.join(buckets_dir, name)):
            return False
        
        if len(os.listdir(os.path.join(buckets_dir, name))) == 0:
            return False
        
        return True
    
    def bucket_install(self, name : str, gitUrl : str = None, forced : bool = False):
        if name in self.bucket_list_installed():
            return 0
        
        if gitUrl is None:
            bucketCtxes =  self.bucket_list_collected()
            if name not in bucketCtxes:
                return -1
            gitUrl = bucketCtxes[name]
            
        res = self.file(
            gitUrl,
            dirPath="buckets",
            fileName=name+".zip",
            pullOnceEvery=None if forced else 24*60*60,
            commitCheck=False if forced else True,
            overwrite=True
        )
        os.makedirs(os.path.join(buckets_dir, name), exist_ok=True)
        extract_zip(res, os.path.join(buckets_dir, name))
        self.__bucketMaps = Bucket.retrieve()
        
    def bucket_uninstall(self, name : str):
        if name not in self.bucket_list_installed():
            return 0
        
        shutil.rmtree(os.path.join(buckets_dir, name))
        self.__bucketMaps = Bucket.retrieve()
        
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
    
    def current_bucket_scopes(self):
        if self.__pushedScope is not None:
            return (self.__pushedScope,)
    
        if len(self.__includedScopes) > 0:
            return tuple(self.__includedScopes)
        
        if len(self.__excludedScopes) > 0:
            return tuple(self.__excludedScopes)
        
        return tuple(self.__bucketMaps.keys())
    
    def all_bucket_scopes(self):
        return tuple(self.__bucketMaps.keys())
    
    def resolve_specified_bucket(self, key : str):
        splitted = key.split("/")
        bucketname = splitted[0]
        key = splitted[1]
        bucket = self.__bucketMaps[bucketname]
        return bucket, key
    
    def list_scripts(self):
        ret = []
        for name, bucket in self.__bucketMaps.items():
            if self.__pushedScope is not None and self.__pushedScope != name:
                continue
            
            if self.__includedScopes and name not in self.__includedScopes:
                continue
            
            if self.__excludedScopes and name in self.__excludedScopes:
                continue
            
            ret.extend(bucket.scripts.keys())
    
        return ret
    
    def list_script_names(self):
        ret = []
        for name, bucket in self.__bucketMaps.items():
            if self.__pushedScope is not None and self.__pushedScope != name:
                continue
            
            if self.__includedScopes and name not in self.__includedScopes:
                continue
            
            if self.__excludedScopes and name in self.__excludedScopes:
                continue
            
            ret.extend(bucket._scriptNames)
            
        return ret
    
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
            ctx = ScherryCtx(self)
        
        for arg in args:
            script = self.get_script(arg)
            if script is None:
                raise RuntimeError(f"{arg} script not found")
            
            ctx.preSetup(arg)
            
            exec(script, ctx.getData(KeyPassObj))
            
            ctx.postSetup()
            
        return ctx
    
    def __fileNeedsRepull(self, pullOnceEvery : int, downloadUrl : str):
        if pullOnceEvery is None:
            return True
        
        lastDate = tracked_index[downloadUrl].get("lastPulled", None)
        if lastDate is None:
            return True
        
        lastDate = datetime.datetime.fromisoformat(lastDate)
        
        return lastDate + datetime.timedelta(seconds = pullOnceEvery) < datetime.datetime.now()
    
    def __fileCommitCheck(
        self, downloadUrl : str, gitUrl : str, fileName : str
    ):
        lastCommitChecked = tracked_index[downloadUrl].get("lastCommitChecked", None)
        if lastCommitChecked is None:
            return False, None
        
        lastCommitChecked = datetime.datetime.fromisoformat(lastCommitChecked)
        commitCheck = git_last_commit_date(gitUrl, fileName)
        
        return lastCommitChecked == commitCheck, commitCheck
    
    def _retrieveLocalCache(self, downloadUrl : str):
        res = self.__localFileCache.get(downloadUrl, None)
        if res is not None:
            return res
        
        trackingEntry : TrackedIndexEntry = tracked_index[downloadUrl]
        if "hashing" not in trackingEntry:
            return None
        
        hashing = trackingEntry["hashing"]
        expected_path = os.path.join(cache_dir, hashing)
        if not os.path.exists(expected_path):
            return None
        
        content = open(expected_path, 'rb').read()
        if not check_hash(content, hashing):
            logging.error("local hash mismatch for %s", downloadUrl)
            return None
        
        self.__localFileCache[downloadUrl] = content
        return content
        
    
    def file(
        self, 
        gitUrl : str,
        branch : str = "main",
        dirPath : str = None,
        fileName : str = "",
        pullOnceEvery : int = None,
        commitCheck : bool = False,
        targetPath : str = None,
        overwrite : bool = False
    ):
        if not fileName:
            raise RuntimeError("fileName cannot be empty")
        
        if not overwrite and os.path.exists(os.path.join(targetPath, fileName)):
            return
        
        downloadUrl = f"{gitUrl}/{branch}/{dirPath[:-1] if "/" in dirPath else dirPath}/{fileName}"
        retrieveLocal = True
        
        if downloadUrl not in tracked_index:
            dict.__setitem__(tracked_index, downloadUrl, {})
            
        if self.__fileNeedsRepull(pullOnceEvery, downloadUrl):
            self.__localFileCache.pop(downloadUrl, None)
            retrieveLocal = False
            
        commitTuple= None
        if commitCheck and not retrieveLocal:
            commitTuple =self.__fileCommitCheck(downloadUrl, gitUrl, fileName)
            if not commitTuple[0]:
                self.__localFileCache.pop(downloadUrl, None)
                retrieveLocal = False
    
        if retrieveLocal:
            res = self._retrieveLocalCache(downloadUrl)
            if res is not None and targetPath is not None:
                with open(os.path.join(targetPath, fileName), 'wb') as f:
                    f.write(res)
                return res
            elif res is not None:
                return res
            
        # retrieve from remote
        content = download_github_raw_content(downloadUrl)
        downloadedHash = get_hash(content)
        cachePath = os.path.join(cache_dir, downloadedHash)
        
        with open(cachePath, 'wb') as f:
            f.write(content)
            
        self.__localFileCache[downloadUrl] = content
        tracked_index.setDeep(downloadUrl, "hashing", downloadedHash)
        tracked_index.setDeep(downloadUrl, "lastPulled", datetime.datetime.now())
        if commitTuple is not None:
            tracked_index.setDeep(downloadUrl, "lastCommitChecked", commitTuple[1])
        
        if targetPath is not None:
            shutil.copy(cachePath, targetPath)
            os.rename(os.path.join(targetPath, downloadedHash), os.path.join(targetPath, fileName))
        
        return content