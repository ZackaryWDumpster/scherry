import shutil
import typing
from scherry.core.bucket import Bucket, buckets_dir
from scherry.utils.cfg import cfg
from scherry.utils.git import download_github_raw_content
import os
import zipfile
import io

class ScherryMgr:
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
        
        for bucketName, bucketSrc in self.installed_buckets().items():
            self.__bucketMaps[bucketName] = Bucket(bucketName, bucketSrc)
        
    def install_bucket(self, name : str, source : str):
        cfg.setDeep("buckets", "installed", name, source)
        content = download_github_raw_content(url=source)
        os.makedirs(os.path.join(buckets_dir, name), exist_ok=True)
        bucket_path = os.path.join(buckets_dir, name)
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_ref:
            zip_ref.extractall(bucket_path)
        
        self.__bucketMaps[name] = Bucket(name, bucket_path)
    
    def uninstall_bucket(self, name : str):
        shutil.rmtree(os.path.join(buckets_dir, name))
        self.__bucketMaps.pop(name)

    def has_script(self, name : str):
        for bucket in self.__bucketMaps.values():
            if bucket.hasKey(name):
                return True
        return False    
    
    def get_script(self, name : str):
        for bucket in self.__bucketMaps.values():
            if bucket.hasKey(name):
                return bucket.get(name)
    
    def run_scripts(self, *keys, data= {}):
        for key in keys:
            content = self.get_script(key)
            string = content.decode()
            
            exec(string, data)
            
            print(f"Run script {key} successfully")
            
    
    
