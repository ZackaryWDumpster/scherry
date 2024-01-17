import hashlib

def get_hash(filebytes : bytes):
    return hashlib.sha256(filebytes).hexdigest()

def check_hash(content : bytes, hash : str):
    return get_hash(content) == hash