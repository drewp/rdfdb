# Stubs for twisted.internet.task (Python 3)
#

from typing import Any, Optional

__metaclass__ = type

class LoopingCall:
    call: Any = ...
    running: bool = ...
    interval: Any = ...
    starttime: Any = ...
    f: Any = ...
    a: Any = ...
    kw: Any = ...
    clock: Any = ...
    def __init__(self, f: Any, *a: Any, **kw: Any) -> None: ...
    @property
    def deferred(self): ...
    withCount: Any = ...
    def start(self, interval: Any, now: bool = ...): ...
    def stop(self) -> None: ...
    def reset(self) -> None: ...
    def __call__(self) -> None: ...

class SchedulerError(Exception): ...
class SchedulerStopped(SchedulerError): ...
class TaskFinished(SchedulerError): ...
class TaskDone(TaskFinished): ...
class TaskStopped(TaskFinished): ...
class TaskFailed(TaskFinished): ...
class NotPaused(SchedulerError): ...

class _Timer:
    MAX_SLICE: float = ...
    end: Any = ...
    def __init__(self) -> None: ...
    def __call__(self): ...

class CooperativeTask:
    def __init__(self, iterator: Any, cooperator: Any) -> None: ...
    def whenDone(self): ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def stop(self) -> None: ...

class Cooperator:
    def __init__(self, terminationPredicateFactory: Any = ..., scheduler: Any = ..., started: bool = ...) -> None: ...
    def coiterate(self, iterator: Any, doneDeferred: Optional[Any] = ...): ...
    def cooperate(self, iterator: Any): ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    @property
    def running(self): ...

def coiterate(iterator: Any): ...

class Clock:
    rightNow: float = ...
    calls: Any = ...
    def __init__(self) -> None: ...
    def seconds(self): ...
    def callLater(self, when: Any, what: Any, *a: Any, **kw: Any): ...
    def getDelayedCalls(self): ...
    def advance(self, amount: Any) -> None: ...
    def pump(self, timings: Any) -> None: ...

def deferLater(clock: Any, delay: Any, callable: Any, *args: Any, **kw: Any): ...
def react(main: Any, argv: Any = ..., _reactor: Optional[Any] = ...) -> None: ...
