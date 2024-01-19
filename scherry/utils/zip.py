import os
import zipfile
import io
def make_zip(folder : str, exclusions : list = []):
    _zipfile = folder+".zip"
    if os.path.exists(_zipfile):
        os.remove(_zipfile)                            
    
    with zipfile.ZipFile(_zipfile, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(folder):
            for filename in filenames:
                # exclude files start with _ and folder with __
                if filename.startswith("_") or os.path.basename(folderName).startswith("__"):
                    continue
                
                # check exclusion
                basename = os.path.basename(folderName)
                if basename in exclusions:
                    continue
                
                filePath = os.path.join(folderName, filename)
                if any(x in filePath for x in exclusions):
                    continue
                
                archiveName = os.path.relpath(filePath,folder)

                zipObj.write(filePath, archiveName)
                
def extract_zip(zipobj : zipfile.ZipFile, folder : str):
    if isinstance(zipobj, bytes):
        zipobj = zipfile.ZipFile(io.BytesIO(zipobj))
    
    zipobj.extractall(folder)