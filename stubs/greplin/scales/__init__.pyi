# Stubs for greplin.scales (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import json
from collections import UserDict
from typing import Any, Optional

ID_KEY: str
NEXT_ID: Any

def statsId(obj: Any): ...
def init(obj: Any, context: Optional[Any] = ...): ...
def initChild(obj: Any, name: Any): ...
def initChildOfType(obj: Any, name: Any, subContext: Optional[Any] = ...): ...
def reset() -> None: ...
def getStats(): ...
def setCollapsed(path: Any): ...

class StatContainer(UserDict):
    def __init__(self) -> None: ...
    def setCollapsed(self, isCollapsed: Any) -> None: ...
    def isCollapsed(self): ...

class _Stats:
    stats: Any = ...
    parentMap: Any = ...
    containerMap: Any = ...
    subId: int = ...
    @classmethod
    def reset(cls) -> None: ...
    @classmethod
    def init(cls, obj: Any, context: Any): ...
    @classmethod
    def initChild(cls, obj: Any, name: Any, subContext: Any, parent: Optional[Any] = ...): ...
    @classmethod
    def getContainerForObject(cls, instanceId: Any): ...
    @classmethod
    def getStat(cls, obj: Any, name: Any): ...
    @classmethod
    def getAggregator(cls, instanceId: Any, name: Any): ...
    @classmethod
    def setCollapsed(cls, path: Any) -> None: ...

class Stat:
    def __init__(self, name: Any, value: str = ..., logger: Optional[Any] = ...) -> None: ...
    def getName(self): ...
    def __get__(self, instance: Any, _: Any): ...
    def __set__(self, instance: Any, value: Any) -> None: ...
    def updateItem(self, instance: Any, subKey: Any, value: Any) -> None: ...
    def logger(self, logger: Any): ...

class IntStat(Stat):
    def __init__(self, name: Any, value: int = ...) -> None: ...

class DoubleStat(Stat):
    def __init__(self, name: Any, value: float = ...) -> None: ...

class IntDict(UserDict):
    parent: Any = ...
    instance: Any = ...
    autoDelete: Any = ...
    def __init__(self, parent: Any, instance: Any, autoDelete: bool = ...) -> None: ...
    def __getitem__(self, item: Any): ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class IntDictStat(Stat):
    autoDelete: Any = ...
    def __init__(self, name: Any, autoDelete: bool = ...) -> None: ...

class StringDict(UserDict):
    parent: Any = ...
    instance: Any = ...
    def __init__(self, parent: Any, instance: Any) -> None: ...
    def __getitem__(self, item: Any): ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class StringDictStat(Stat): ...

class AggregationStat(Stat):
    def __init__(self, name: Any, value: Any) -> None: ...
    def update(self, instance: Any, oldValue: Any, newValue: Any) -> None: ...

class ChildAggregationStat(Stat):
    def __init__(self, name: Any, value: Any) -> None: ...
    def update(self, instance: Any, oldValue: Any, newValue: Any, subKey: Any) -> None: ...

class SumAggregationStat(AggregationStat):
    def __init__(self, name: Any) -> None: ...
    def update(self, instance: Any, oldValue: Any, newValue: Any) -> None: ...

class HistogramAggregationStat(AggregationStat):
    autoDelete: Any = ...
    def __init__(self, name: Any, autoDelete: bool = ...) -> None: ...
    def update(self, instance: Any, oldValue: Any, newValue: Any) -> None: ...

class IntDictSumAggregationStat(ChildAggregationStat):
    def __init__(self, name: Any) -> None: ...
    def update(self, instance: Any, oldValue: Any, newValue: Any, subKey: Any) -> None: ...

class PmfStatDict(UserDict):
    class TimeManager:
        container: Any = ...
        msg99: Any = ...
        start: Any = ...
        def __init__(self, container: Any) -> None: ...
        def __enter__(self): ...
        def __exit__(self, *_: Any) -> None: ...
        def warn99(self, logger: Any, msg: Any, *args: Any) -> None: ...
        def discard(self) -> None: ...
        def __call__(self, func: Any): ...
    percentile99: Any = ...
    def __init__(self, sample: Optional[Any] = ...) -> None: ...
    def __getitem__(self, item: Any): ...
    def addValue(self, value: Any) -> None: ...
    def time(self): ...

class PmfStat(Stat):
    def __init__(self, name: Any, _: Optional[Any] = ...) -> None: ...
    def __set__(self, instance: Any, value: Any) -> None: ...

class NamedPmfDict(UserDict):
    def __init__(self) -> None: ...
    def __getitem__(self, item: Any): ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class NamedPmfDictStat(Stat): ...

class RecentFpsStat(Stat): ...

class StateTimeStatDict(UserDict):
    parent: Any = ...
    instance: Any = ...
    def __init__(self, parent: Any, instance: Any) -> None: ...
    def __getitem__(self, item: Any): ...
    def incr(self, item: Any, value: Any) -> None: ...
    def acquire(self) -> None: ...

class StateTimeStat(Stat):
    state: int = ...
    time: Any = ...
    def __init__(self, name: Any, _: Optional[Any] = ...) -> None: ...
    def __set__(self, instance: Any, value: Any) -> None: ...

def filterCollapsedItems(data: Any): ...

class StatContainerEncoder(json.JSONEncoder):
    def default(self, obj: Any): ...

def dumpStatsTo(filename: Any) -> None: ...
def collection(path: Any, *stats: Any): ...
