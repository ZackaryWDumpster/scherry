import logging
import shutil
import typing
from scherry.core.bucket import Bucket, buckets_dir
from scherry.utils import indexes
from scherry.utils.cfg import cfg
from scherry.utils.git import download_github_raw_content
import os
import zipfile
import io
import toml

class ScherryMgrMeta(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScherryMgrMeta, cls).__call__(*args, **kwargs)
        return cls._instance

class ScherryMgr(metaclass=ScherryMgrMeta):
    __bucketMaps : typing.Dict[str, Bucket]
    
    def __init__(self):
        self.refresh_buckets()
    
    def installed_buckets(self):
        cfg.setDefaultDeep("buckets", "installed", {})
        res =  cfg.getDeep("buckets", "installed")
        assert isinstance(res, dict)
        return res
        
    def refresh_buckets(self):
        self.__bucketMaps = {}
        
        for bucketName, bucketMeta in self.installed_buckets().items():
            bucketSrc = bucketMeta.get("source")
            self.__bucketMaps[bucketName] = Bucket(bucketName, bucketSrc)
        
    def install_bucket(self, name : str, source : str = None):
        installedIndexes = cfg.getDeep("buckets", "installed")
        if name in installedIndexes:
            raise RuntimeError(f"{name} bucket already installed")
        
        if source is None:
            sourceMap : dict = indexes["buckets"]
            source = sourceMap.get(name, None)
            
        if source is None:
            raise RuntimeError(f"{name} bucket not found")
        
        cfg.setDeep("buckets", "installed", name, "source", source)
        content = download_github_raw_content(url=source)
        os.makedirs(os.path.join(buckets_dir, name), exist_ok=True)
        bucket_path = os.path.join(buckets_dir, name)
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_ref:
            zip_ref.extractall(bucket_path)
        
        self.__bucketMaps[name] = Bucket(name, bucket_path)
    
    def uninstall_bucket(self, name : str):
        shutil.rmtree(os.path.join(buckets_dir, name))
        self.__bucketMaps.pop(name)
        cfg["buckets"]["installed"].pop(name)

    def has_script(self, name : str):
        for bucket in self.__bucketMaps.values():
            if bucket.hasKey(name):
                return True
        return False    
    
    def get_script(self, name : str):
        for bucket in self.__bucketMaps.values():
            if bucket.hasKey(name):
                return bucket.get(name)
    
    def __handle_entry(self, config : dict):
        pass
    
    def __handle_exit(self, ctx : dict, cctx : dict):
        pass
    
    def run_scripts(self, *keys, temp : dict= {}, reinit_ctx : bool = False):
        if os.path.exists("config.toml"):
            config = toml.load("config.toml")
        else:
            config = {}
            
        config.update(temp)
        
        if not hasattr(self, "ctx") or reinit_ctx:
            self.ctx = {}
        self.ctx.update(config.get("global", {}))
        
        for key in keys:
            content = self.get_script(key)
            if content is None:
                raise RuntimeError(f"Cannot resolve script {key}")
            
            string = content.decode()

            entry_config = config.get(key, {})

            cctx = dict(**self.ctx, **entry_config)
            
            exec(string, cctx)

            self.__handle_exit(self.ctx, cctx)
        
            logging.info(f"Run script {key} successfully")
            
    
