# Stubs for twisted.python.failure (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional

count: int
traceupLength: int

class DefaultException(Exception): ...

def format_frames(frames: Any, write: Any, detail: str = ...) -> None: ...

EXCEPTION_CAUGHT_HERE: str

class NoCurrentExceptionError(Exception): ...

class _TracebackFrame:
    tb_frame: Any = ...
    tb_lineno: Any = ...
    tb_next: Any = ...
    def __init__(self, frame: Any, tb_next: Any) -> None: ...

class _Frame:
    f_code: Any = ...
    f_globals: Any = ...
    f_locals: Any = ...
    def __init__(self, name: Any, filename: Any) -> None: ...

class _Code:
    co_name: Any = ...
    co_filename: Any = ...
    def __init__(self, name: Any, filename: Any) -> None: ...

class Failure(BaseException):
    pickled: int = ...
    stack: Any = ...
    count: Any = ...
    type: Any = ...
    captureVars: Any = ...
    value: Any = ...
    tb: Any = ...
    parents: Any = ...
    def __init__(self, exc_value: Optional[Any] = ..., exc_type: Optional[Any] = ..., exc_tb: Optional[Any] = ..., captureVars: bool = ...) -> None: ...
    def trap(self, *errorTypes: Any): ...
    def check(self, *errorTypes: Any): ...
    def raiseException(self) -> None: ...
    def throwExceptionIntoGenerator(self, g: Any): ...
    __dict__: Any = ...
    def cleanFailure(self) -> None: ...
    def getTracebackObject(self): ...
    def getErrorMessage(self): ...
    def getBriefTraceback(self): ...
    def getTraceback(self, elideFrameworkCode: int = ..., detail: str = ...): ...
    def printTraceback(self, file: Optional[Any] = ..., elideFrameworkCode: bool = ..., detail: str = ...) -> None: ...
    def printBriefTraceback(self, file: Optional[Any] = ..., elideFrameworkCode: int = ...) -> None: ...
    def printDetailedTraceback(self, file: Optional[Any] = ..., elideFrameworkCode: int = ...) -> None: ...

DO_POST_MORTEM: bool

def startDebugMode() -> None: ...