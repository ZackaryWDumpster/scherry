import os


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