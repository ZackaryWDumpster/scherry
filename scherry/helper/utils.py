
import io
import zipfile
import os

def crlf_to_lf_1(text : str):
    return text.replace("\r\n", "\n")

def crlf_to_lf_2(file : str):
    with open(file, 'r') as f:
        content = f.read()
        
    with open(file, 'w') as f:
        f.write(crlf_to_lf_1(content))
        
def crlf_to_lf_3(file : io.TextIOWrapper):
    file.seek(0)
    
    content = file.read()
    #
    file.seek(0)
    
    file.write(crlf_to_lf_1(content))
    
    file.truncate()
    
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