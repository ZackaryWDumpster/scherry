import logging
import shutil
import typing
from scherry.core.bucket import Bucket, buckets_dir
from scherry.utils.dictionary import ERROR
from scherry.utils.indexes import indexes, refresh_indexes
from scherry.utils.cfg import cfg
from scherry.utils.git import check_retrieved, retrieve_file
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
    
    @property
    def buckets(self):
        return list(self.__bucketMaps.values())
    
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
        
    def __bucket_io_update(self,name, source):
        content = retrieve_file(source)
        if os.path.exists(os.path.join(buckets_dir, name)):
            shutil.rmtree(os.path.join(buckets_dir, name))
        
        os.makedirs(os.path.join(buckets_dir, name), exist_ok=True)
        bucket_path = os.path.join(buckets_dir, name)
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_ref:
            zip_ref.extractall(bucket_path)
        self.__bucketMaps[name] = Bucket(name, bucket_path)
        
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
        
        self.__bucket_io_update(name, source)
        
        refresh_indexes()
    
    def update_bucket(self, name : str):
        sourceMap : dict = indexes["buckets"]
        source = sourceMap.get(name, None)
        
        if check_retrieved(source):
            logging.info(f"{name} bucket already updated")
            return
        
        self.__bucket_io_update(name, source)
    
    def uninstall_bucket(self, name : str):
        shutil.rmtree(os.path.join(buckets_dir, name))
        self.__bucketMaps.pop(name)
        cfg["buckets"]["installed"].pop(name)
        refresh_indexes()

    def has_script(self, name : str):
        for bucket in self.__bucketMaps.values():
            if bucket.hasKey(name):
                return True
        return False    
    
    def get_script(self, name : str):
        for bucket in self.__bucketMaps.values():
            if bucket.hasKey(name):
                logging.info(f"Get script {name} from bucket {bucket.name}")
                return bucket.get(name)
    
    def __handle_entry(self, config : dict, seq : int):
        cwdIn = config.pop("cwdIn", None)
        if cwdIn is not None:
            os.chdir(cwdIn)
        
        cwdPush = config.pop("cwdPush", None)

        if cwdPush is not None:
            currCwd = os.getcwd()
            os.chdir(cwdPush)
            config["cwdPop"] = currCwd
            
        config["ScherrySeq"] = seq
    
    def __handle_exit(self, ctx : dict, cctx : dict):
        cwdOut = cctx.pop("cwdPop", None)
        if cwdOut is not None:
            os.chdir(cwdOut)
            
        cwdPop = cctx.pop("cwdPop", None)
        if cwdPop is not None:
            os.chdir(cwdPop)
            
        dataOut = cctx.pop("dataOut", ERROR)
        if dataOut is ERROR:
            ctx.update({k : v for k, v in cctx.items() if not k.startswith("Scherry")})
        elif dataOut is False:
            pass
        elif isinstance(dataOut, dict):
            ctx.update(dataOut)
        else:
            ctx["dataOut"] = dataOut
    
    def run_scripts(self, *keys, temp : dict= {}, reinit_ctx : bool = False):
        if os.path.exists("config.toml"):
            config = toml.load("config.toml")
        else:
            config = {}
            
        config.update(temp)
        
        if not hasattr(self, "ctx") or reinit_ctx:
            self.ctx = {}
        self.ctx.update(config.get("global", {}))
        
        for i, key in enumerate(keys):
            content = self.get_script(key)
            if content is None:
                raise RuntimeError(f"Cannot resolve script {key}")
            
            string = content.decode()

            entry_config = config.get(key, {})

            cctx = dict(**self.ctx, **entry_config)
            
            self.__handle_entry(cctx, i)
            
            exec(string, cctx)

            self.__handle_exit(self.ctx, cctx)
        
            logging.info(f"Run script {key} successfully")
            
    
