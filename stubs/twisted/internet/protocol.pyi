# Stubs for twisted.internet.protocol (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from twisted.python import components
from typing import Any, Optional

class Factory:
    protocol: Any = ...
    numPorts: int = ...
    noisy: bool = ...
    @classmethod
    def forProtocol(cls, protocol: Any, *args: Any, **kwargs: Any): ...
    def logPrefix(self): ...
    def doStart(self) -> None: ...
    def doStop(self) -> None: ...
    def startFactory(self) -> None: ...
    def stopFactory(self) -> None: ...
    def buildProtocol(self, addr: Any): ...

class ClientFactory(Factory):
    def startedConnecting(self, connector: Any) -> None: ...
    def clientConnectionFailed(self, connector: Any, reason: Any) -> None: ...
    def clientConnectionLost(self, connector: Any, reason: Any) -> None: ...

class _InstanceFactory(ClientFactory):
    noisy: bool = ...
    pending: Any = ...
    reactor: Any = ...
    instance: Any = ...
    deferred: Any = ...
    def __init__(self, reactor: Any, instance: Any, deferred: Any) -> None: ...
    def buildProtocol(self, addr: Any): ...
    def clientConnectionFailed(self, connector: Any, reason: Any) -> None: ...
    def fire(self, func: Any, value: Any) -> None: ...

class ClientCreator:
    reactor: Any = ...
    protocolClass: Any = ...
    args: Any = ...
    kwargs: Any = ...
    def __init__(self, reactor: Any, protocolClass: Any, *args: Any, **kwargs: Any) -> None: ...
    def connectTCP(self, host: Any, port: Any, timeout: int = ..., bindAddress: Optional[Any] = ...): ...
    def connectUNIX(self, address: Any, timeout: int = ..., checkPID: bool = ...): ...
    def connectSSL(self, host: Any, port: Any, contextFactory: Any, timeout: int = ..., bindAddress: Optional[Any] = ...): ...

class ReconnectingClientFactory(ClientFactory):
    maxDelay: int = ...
    initialDelay: float = ...
    factor: float = ...
    jitter: float = ...
    delay: Any = ...
    retries: int = ...
    maxRetries: Any = ...
    connector: Any = ...
    clock: Any = ...
    continueTrying: int = ...
    def clientConnectionFailed(self, connector: Any, reason: Any) -> None: ...
    def clientConnectionLost(self, connector: Any, unused_reason: Any) -> None: ...
    def retry(self, connector: Optional[Any] = ...) -> None: ...
    def stopTrying(self) -> None: ...
    def resetDelay(self) -> None: ...

class ServerFactory(Factory): ...

class BaseProtocol:
    connected: int = ...
    transport: Any = ...
    def makeConnection(self, transport: Any) -> None: ...
    def connectionMade(self) -> None: ...

connectionDone: Any

class Protocol(BaseProtocol):
    def logPrefix(self): ...
    def dataReceived(self, data: Any) -> None: ...
    def connectionLost(self, reason: Any) -> None: ...

class ProtocolToConsumerAdapter(components.Adapter):
    def write(self, data: Any) -> None: ...
    def registerProducer(self, producer: Any, streaming: Any) -> None: ...
    def unregisterProducer(self) -> None: ...

class ConsumerToProtocolAdapter(components.Adapter):
    def dataReceived(self, data: Any) -> None: ...
    def connectionLost(self, reason: Any) -> None: ...
    def makeConnection(self, transport: Any) -> None: ...
    def connectionMade(self) -> None: ...

class ProcessProtocol(BaseProtocol):
    def childDataReceived(self, childFD: Any, data: Any) -> None: ...
    def outReceived(self, data: Any) -> None: ...
    def errReceived(self, data: Any) -> None: ...
    def childConnectionLost(self, childFD: Any) -> None: ...
    def inConnectionLost(self) -> None: ...
    def outConnectionLost(self) -> None: ...
    def errConnectionLost(self) -> None: ...
    def processExited(self, reason: Any) -> None: ...
    def processEnded(self, reason: Any) -> None: ...

class AbstractDatagramProtocol:
    transport: Any = ...
    numPorts: int = ...
    noisy: bool = ...
    def doStart(self) -> None: ...
    def doStop(self) -> None: ...
    def startProtocol(self) -> None: ...
    def stopProtocol(self) -> None: ...
    def makeConnection(self, transport: Any) -> None: ...
#    def datagramReceived(self, datagram: Any, addr: Any) -> None: ...

class DatagramProtocol(AbstractDatagramProtocol):
    def logPrefix(self): ...
    def connectionRefused(self) -> None: ...

class ConnectedDatagramProtocol(DatagramProtocol):
#    def datagramReceived(self, datagram: Any) -> None: ...
    def connectionFailed(self, failure: Any) -> None: ...

class FileWrapper:
    closed: int = ...
    disconnecting: int = ...
    producer: Any = ...
    streamingProducer: int = ...
    file: Any = ...
    def __init__(self, file: Any) -> None: ...
    def write(self, data: Any) -> None: ...
    def registerProducer(self, producer: Any, streaming: Any) -> None: ...
    def unregisterProducer(self) -> None: ...
    def stopConsuming(self) -> None: ...
    def writeSequence(self, iovec: Any) -> None: ...
    def loseConnection(self) -> None: ...
    def getPeer(self): ...
    def getHost(self): ...
    def handleException(self) -> None: ...
    def resumeProducing(self) -> None: ...
    def pauseProducing(self) -> None: ...
    def stopProducing(self) -> None: ...
