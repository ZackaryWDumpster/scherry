import os
import shutil
import typing
import orjson
from scherry.utils.dictionary import setDeep as _setDeep
from scherry.utils.dictionary import getDeep as _getDeep
from scherry.utils.dictionary import ERROR

class _Shared(dict):
    def ensure_child(self, *args):
        return self.ensure_type(*args, type_=AutoSaveDictChild)
        
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
            
    def ensure_type(self, *args, type_ : typing.Type[dict]):
        res = self.getDeep(*args[:-1])
        if res is ERROR:
            ret = type_()
            self.setDeep(*args[:-1], ret)   
            return ret
        elif not isinstance(res, dict):
            raise RuntimeError(f"expected dict, got {type(res)}")
        elif type_ == AutoSaveDictChild:
            res[args[-1]] = AutoSaveDictChild(self, *args[:-1])
            return res[args[-1]]
        else:
            res[args[-1]] = type_(res[args[-1]])
            return res[args[-1]]

class AutoSaveDict(_Shared):
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
            
        
class AutoSaveDictChild(_Shared):
    def __init__(self, parent : AutoSaveDict, *args, **kwargs):
        self.parent = parent
        self.__referenceDict = None
        super().__init__(*args, **kwargs)
        
        
    def _save(self):
        self.parent._save()
    
    def __getitem__(self, __key):
        if self.__referenceDict is not None and __key not in self.__referenceDict:
            raise KeyError(__key)
        
        if __key not in self:
            self[__key] = self.__referenceDict[__key]
            
        return super().__getitem__(__key)
        
    def __setitem__(self, key, value):
        if self.__referenceDict is not None and key not in self.__referenceDict:
            raise KeyError(key)
        
        return super().__setitem__(key, value)    
    
    def setReference(self, referenceDict):
        self.__referenceDict = referenceDict