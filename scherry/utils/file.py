import os
import shutil
import typing
from scherry.utils.indexes import indexes
from scherry.utils.cfg import appdata_dir
from scherry.utils.git import download_github_raw_content
from scherry.utils.hashing import check_hash
files_dir= os.path.join(appdata_dir, "files")

os.makedirs(files_dir, exist_ok=True)

def extra_file(
    path : str, 
    collection : typing.Literal["github"] = "github",
    hashing : str = None,
    useIndex : bool = True
):
    if hashing is None and useIndex and path in indexes["files"]:
        hashing = indexes["files"][path]["hashing"]
        path = indexes["files"][path]["path"]
    
    file = os.path.basename(path)
    
    if hashing is not None:
        caching_path = os.path.join(files_dir, hashing)
        if os.path.exists(caching_path):
            return shutil.copy(os.path.join(files_dir, hashing), file)
    
    if collection == "github":
        content = download_github_raw_content(url=path)

    if hashing is None:
        with open(file, 'wb') as f:
            f.write(content)
            
        return

    if not check_hash(content, hashing):
        raise RuntimeError(f"{file} hash is not consistent")
    
    with open(caching_path, 'wb') as f:
        f.write(content)
        
    shutil.copy(caching_path, file)
    
