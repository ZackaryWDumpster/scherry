import os
import requests

baseurl= "https://raw.githubusercontent.com/{url}"

def download_github_raw_content(url : str):
    url = baseurl.format(url=url)
    res = requests.get(url)
    return res.content

def touch_file(path : str, content :str = None):
    f = open(path, 'a')
    if content:
        f.write(content)
    f.close()
    
def get_files(path : str, types : list = []):
    if len(types) == 0:
        return []
    
    files = []
    for file in os.listdir(path):
        if any([file.endswith(t) for t in types]):
            files.append(file)
        
    return files