from functools import cached_property
import os
from types import MappingProxyType
from typing import Any
import typing
import toml

KeyPassObj = object()

class ScherryCtx:
    currentSeq : int = 0
    currentKey : str = None
    __runSequenece : typing.List[str]
    
    __globalData : dict
    __scopedData : typing.Dict[str, dict]
    __scopedDataX : typing.Dict[tuple, typing.List[dict]]
    
    cwdIn : str = None
    cwdPush : str = None
    __cwdPop : str = None
    
    __lastSnapShot : dict
    
    @property
    def runSequence(self):
        return tuple(self.__runSequenece)
    
    def __init__(self) -> None:
        self.reset()
        
    def reset(self):
        object.__setattr__(self, "currentKey", None)
        object.__setattr__(self, "currentSeq", 0)
        self.__globalData = dict()
        self.__scopedData = dict()
        self.__scopedDataX = dict()
        self.__runtimeConfigData()
        self.__globalData["ctx"] = self
        self.__runSequenece = []
        self.__lastSnapShot = None
        self.__dict__.pop("__scoped", None)
        
    def preSetup(self, key : str):
        object.__setattr__(self, "currentKey", key)
        if self.cwdIn is not None:
            os.chdir(self.cwdIn)
            self.cwdIn = None
            
        if self.cwdPush is not None:
            self.__cwdPop = os.getcwd()
            os.chdir(self.cwdPush)
            self.cwdPush = None
            
        self.__keyedShadowMap = self.__preSetupScopedData.get(key, None)
        if self.__keyedShadowMap is not None:
            self.__globalData.update(self.__keyedShadowMap)

        
    def postSetup(self):
        object.__setattr__(self, "currentSeq", self.currentSeq + 1)
        self.__runSequenece.append(self.currentKey)
        
        if self.__cwdPop is not None:
            os.chdir(self.__cwdPop)
            self.__cwdPop = None
        
        self.__lastSnapShot = self.__globalData.copy()
        if self.__keyedShadowMap is not None:
            # compare the values to global and pop all non changed
            for k, v in self.__keyedShadowMap.items():
                if k in self.__globalData and v == self.__globalData[k]:
                    self.__globalData.pop(k)
    
    def __runtimeConfigData(self):
        if not os.path.exists("config.toml"):
            return
        data = toml.load("config.toml")
        globalData = dict()
        for k, v in data.items():
            if isinstance(v, dict):
                if k not in self.__scopedData:
                    self.__scopedData[k] = dict()
                self.__scopedData[k].update(v)
            else:
                globalData[k] = v
        self.__globalData.update(globalData)
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ["currentSeq", "currentKey"]:
            raise AttributeError("cannot set attribute")
    
        super().__setattr__(__name, __value)

    @property
    def last(self):
        return MappingProxyType(self.__lastSnapShot)

    def getData(self, obj = None):
        if obj is KeyPassObj:
            return self.__globalData
        return MappingProxyType(self.__globalData)
    
    @cached_property
    def __preSetupScopedData(self):
        data = self.__scopedData.copy()
        for t, dicts in self.__scopedDataX.items():
            t : typing.Tuple[str]
            for tk in t:
                for dict_ in dicts:
                    if tk in data:
                        data[tk].update(dict_)
                    else:
                        data[tk] = dict_
        return data
    
    def setPersistent(self, *args, data : dict = None, **kwargs):
        if data is None:
            data = {}
            
        data.update(kwargs)
        
        if args not in self.__scopedDataX:
            self.__scopedDataX[args] = []
            
        if data in self.__scopedDataX[args]:
            return
            
        self.__scopedDataX[args].append(data)