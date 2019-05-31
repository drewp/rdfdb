# Stubs for autobahn.websocket.interfaces (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import abc
from typing import Any, Optional

class IWebSocketClientAgent(metaclass=abc.ABCMeta):
    def open(self, transport_config: Any, options: Any, protocol_class: Optional[Any] = ...) -> None: ...

class IWebSocketServerChannelFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, url: Optional[Any] = ..., protocols: Optional[Any] = ..., server: Optional[Any] = ..., headers: Optional[Any] = ..., externalPort: Optional[Any] = ...): ...
    @abc.abstractmethod
    def setSessionParameters(self, url: Optional[Any] = ..., protocols: Optional[Any] = ..., server: Optional[Any] = ..., headers: Optional[Any] = ..., externalPort: Optional[Any] = ...) -> Any: ...
    @abc.abstractmethod
    def setProtocolOptions(self, versions: Optional[Any] = ..., webStatus: Optional[Any] = ..., utf8validateIncoming: Optional[Any] = ..., maskServerFrames: Optional[Any] = ..., requireMaskedClientFrames: Optional[Any] = ..., applyMask: Optional[Any] = ..., maxFramePayloadSize: Optional[Any] = ..., maxMessagePayloadSize: Optional[Any] = ..., autoFragmentSize: Optional[Any] = ..., failByDrop: Optional[Any] = ..., echoCloseCodeReason: Optional[Any] = ..., openHandshakeTimeout: Optional[Any] = ..., closeHandshakeTimeout: Optional[Any] = ..., tcpNoDelay: Optional[Any] = ..., perMessageCompressionAccept: Optional[Any] = ..., autoPingInterval: Optional[Any] = ..., autoPingTimeout: Optional[Any] = ..., autoPingSize: Optional[Any] = ..., serveFlashSocketPolicy: Optional[Any] = ..., flashSocketPolicy: Optional[Any] = ..., allowedOrigins: Optional[Any] = ..., allowNullOrigin: bool = ..., maxConnections: Optional[Any] = ..., trustXForwardedFor: int = ...) -> Any: ...
    @abc.abstractmethod
    def resetProtocolOptions(self) -> Any: ...

class IWebSocketClientChannelFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, url: Optional[Any] = ..., origin: Optional[Any] = ..., protocols: Optional[Any] = ..., useragent: Optional[Any] = ..., headers: Optional[Any] = ..., proxy: Optional[Any] = ...): ...
    @abc.abstractmethod
    def setSessionParameters(self, url: Optional[Any] = ..., origin: Optional[Any] = ..., protocols: Optional[Any] = ..., useragent: Optional[Any] = ..., headers: Optional[Any] = ..., proxy: Optional[Any] = ...) -> Any: ...
    @abc.abstractmethod
    def setProtocolOptions(self, version: Optional[Any] = ..., utf8validateIncoming: Optional[Any] = ..., acceptMaskedServerFrames: Optional[Any] = ..., maskClientFrames: Optional[Any] = ..., applyMask: Optional[Any] = ..., maxFramePayloadSize: Optional[Any] = ..., maxMessagePayloadSize: Optional[Any] = ..., autoFragmentSize: Optional[Any] = ..., failByDrop: Optional[Any] = ..., echoCloseCodeReason: Optional[Any] = ..., serverConnectionDropTimeout: Optional[Any] = ..., openHandshakeTimeout: Optional[Any] = ..., closeHandshakeTimeout: Optional[Any] = ..., tcpNoDelay: Optional[Any] = ..., perMessageCompressionOffers: Optional[Any] = ..., perMessageCompressionAccept: Optional[Any] = ..., autoPingInterval: Optional[Any] = ..., autoPingTimeout: Optional[Any] = ..., autoPingSize: Optional[Any] = ...) -> Any: ...
    @abc.abstractmethod
    def resetProtocolOptions(self) -> Any: ...

class IWebSocketChannel(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def onConnect(self, request_or_response: Any) -> Any: ...
    @abc.abstractmethod
    def onConnecting(self, transport_details: Any) -> Any: ...
    @abc.abstractmethod
    def onOpen(self) -> Any: ...
    @abc.abstractmethod
    def sendMessage(self, payload: Any, isBinary: Any) -> Any: ...
    @abc.abstractmethod
    def onMessage(self, payload: Any, isBinary: Any) -> Any: ...
    @abc.abstractmethod
    def sendClose(self, code: Optional[Any] = ..., reason: Optional[Any] = ...) -> Any: ...
    @abc.abstractmethod
    def onClose(self, wasClean: Any, code: Any, reason: Any) -> Any: ...
    @abc.abstractmethod
    def sendPing(self, payload: Optional[Any] = ...) -> Any: ...
    @abc.abstractmethod
    def onPing(self, payload: Any) -> Any: ...
    @abc.abstractmethod
    def sendPong(self, payload: Optional[Any] = ...) -> Any: ...
    @abc.abstractmethod
    def onPong(self, payload: Any) -> Any: ...

class IWebSocketChannelFrameApi(IWebSocketChannel, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def onMessageBegin(self, isBinary: Any) -> Any: ...
    @abc.abstractmethod
    def onMessageFrame(self, payload: Any) -> Any: ...
    @abc.abstractmethod
    def onMessageEnd(self) -> Any: ...
    @abc.abstractmethod
    def beginMessage(self, isBinary: bool = ..., doNotCompress: bool = ...) -> Any: ...
    @abc.abstractmethod
    def sendMessageFrame(self, payload: Any, sync: bool = ...) -> Any: ...
    @abc.abstractmethod
    def endMessage(self) -> Any: ...

class IWebSocketChannelStreamingApi(IWebSocketChannelFrameApi, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def onMessageFrameBegin(self, length: Any) -> Any: ...
    @abc.abstractmethod
    def onMessageFrameData(self, payload: Any) -> Any: ...
    @abc.abstractmethod
    def onMessageFrameEnd(self) -> Any: ...
    @abc.abstractmethod
    def beginMessageFrame(self, length: Any) -> Any: ...
    @abc.abstractmethod
    def sendMessageFrameData(self, payload: Any, sync: bool = ...) -> Any: ...