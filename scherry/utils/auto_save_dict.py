import os
import shutil
import orjson

from scherry.utils.dictionary import setDeep as _setDeep
from scherry.utils.dictionary import getDeep as _getDeep
from scherry.utils.dictionary import ERROR

class AutoSaveDict(dict):
    def __init__(self, filename, *args, bkup : bool = False, **kwargs):
        self.filename = filename
        self.__bkup = bkup
        super().__init__(*args, **kwargs)
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                f.write('{}')
        try:
            self._load()
        except: # noqa
            raise RuntimeError("Failed to load AutoSaveDict")
            
    def _save(self):
        if self.__bkup and os.path.exists(self.filename):
            shutil.copyfile(self.filename, os.path.join(os.path.dirname(self.filename), f"{os.path.basename(self.filename)}.bkup"))
        
        with open(self.filename, 'wb') as f:
            f.write(orjson.dumps(self, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2))
            
    def _load(self):
        with open(self.filename, 'rb') as f:
            self.update(orjson.loads(f.read()))
        
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._save()

    def clear(self):
        super().clear()
        self._save()

    def pop(self, *args):
        result = super().pop(*args)
        self._save()
        return result

    def popitem(self):
        result = super().popitem()
        self._save()
        return result

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]
    
    def setDeep(self, *args):
        _setDeep(self, *args)
        self._save()
        
    def getDeep(self, *args):
        return _getDeep(self, *args)
    
    def setDefaultDeep(self, *args):
        res = self.getDeep(*args[:-1])
        if res is ERROR:
            self.setDeep(*args)
            self._save()    
        