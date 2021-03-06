# Stubs for twisted.protocols.basic (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from twisted.internet import protocol
from typing import Any, Optional

DEBUG: int

class NetstringParseError(ValueError): ...
class IncompleteNetstring(Exception): ...

class NetstringReceiver(protocol.Protocol):
    MAX_LENGTH: int = ...
    brokenPeer: int = ...
    def makeConnection(self, transport: Any) -> None: ...
    def sendString(self, string: Any) -> None: ...
    def dataReceived(self, data: Any) -> None: ...
    def stringReceived(self, string: Any) -> None: ...

class LineOnlyReceiver(protocol.Protocol):
    delimiter: bytes = ...
    MAX_LENGTH: int = ...
    def dataReceived(self, data: Any): ...
    def lineReceived(self, line: Any) -> None: ...
    def sendLine(self, line: Any): ...
    def lineLengthExceeded(self, line: Any): ...

class _PauseableMixin:
    paused: bool = ...
    def pauseProducing(self) -> None: ...
    def resumeProducing(self) -> None: ...
    def stopProducing(self) -> None: ...

class LineReceiver(protocol.Protocol, _PauseableMixin):
    line_mode: int = ...
    delimiter: bytes = ...
    MAX_LENGTH: int = ...
    def clearLineBuffer(self): ...
    def dataReceived(self, data: Any): ...
    def setLineMode(self, extra: bytes = ...): ...
    def setRawMode(self) -> None: ...
    def rawDataReceived(self, data: Any) -> None: ...
    def lineReceived(self, line: Any) -> None: ...
    def sendLine(self, line: Any): ...
    def lineLengthExceeded(self, line: Any): ...

class StringTooLongError(AssertionError): ...

class _RecvdCompatHack:
    def __get__(self, oself: Any, type: Optional[Any] = ...): ...

class IntNStringReceiver(protocol.Protocol, _PauseableMixin):
    MAX_LENGTH: int = ...
    recvd: Any = ...
    def stringReceived(self, string: Any) -> None: ...
    def lengthLimitExceeded(self, length: Any) -> None: ...
    def dataReceived(self, data: Any) -> None: ...
    def sendString(self, string: Any) -> None: ...

class Int32StringReceiver(IntNStringReceiver):
    structFormat: str = ...
    prefixLength: Any = ...

class Int16StringReceiver(IntNStringReceiver):
    structFormat: str = ...
    prefixLength: Any = ...

class Int8StringReceiver(IntNStringReceiver):
    structFormat: str = ...
    prefixLength: Any = ...

class StatefulStringProtocol:
    state: str = ...
    def stringReceived(self, string: Any) -> None: ...

class FileSender:
    CHUNK_SIZE: Any = ...
    lastSent: str = ...
    deferred: Any = ...
    file: Any = ...
    consumer: Any = ...
    transform: Any = ...
    def beginFileTransfer(self, file: Any, consumer: Any, transform: Optional[Any] = ...): ...
    def resumeProducing(self) -> None: ...
    def pauseProducing(self) -> None: ...
    def stopProducing(self) -> None: ...
