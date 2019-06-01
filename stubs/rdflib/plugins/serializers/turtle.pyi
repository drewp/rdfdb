# Stubs for rdflib.plugins.serializers.turtle (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from rdflib.serializer import Serializer
from typing import Any, Optional, Callable

class RecursiveSerializer(Serializer):
    topClasses: Any = ...
    predicateOrder: Any = ...
    maxDepth: int = ...
    indentString: str = ...
    stream: Any = ...
    def __init__(self, store: Any) -> None: ...
    def addNamespace(self, prefix: Any, uri: Any) -> None: ...
    def checkSubject(self, subject: Any): ...
    def isDone(self, subject: Any): ...
    def orderSubjects(self): ...
    def preprocess(self) -> None: ...
    def preprocessTriple(self, xxx_todo_changeme: Any) -> None: ...
    depth: int = ...
    lists: Any = ...
    namespaces: Any = ...
    def reset(self) -> None: ...
    def buildPredicateHash(self, subject: Any): ...
    def sortProperties(self, properties: Any): ...
    def subjectDone(self, subject: Any) -> None: ...
    def indent(self, modifier: int = ...): ...
    def write(self, text: Any) -> None: ...

class TurtleSerializer(RecursiveSerializer):
    short_name: str = ...
    indentString: str = ...
    keywords: Any = ...
    stream: Any = ...
    def __init__(self, store: Any) -> None: ...
    def addNamespace(self, prefix: Any, namespace: Any): ...
    def reset(self) -> None: ...
    base: Any = ...
    def serialize(self, stream: Any, base: Optional[Any] = ..., encoding: Optional[Any] = ..., spacious: Optional[Any] = ..., **args: Any) -> None: ...
    def preprocessTriple(self, triple: Any) -> None: ...
    def getQName(self, uri: Any, gen_prefix: bool = ...): ...
    def startDocument(self) -> None: ...
    def endDocument(self) -> None: ...
    def statement(self, subject: Any): ...
    def s_default(self, subject: Any): ...
    def s_squared(self, subject: Any): ...
    def path(self, node: Any, position: Any, newline: bool = ...) -> None: ...
    def p_default(self, node: Any, position: Any, newline: bool = ...): ...
    def label(self, node: Any, position: Any): ...
    def p_squared(self, node: Any, position: Any, newline: bool = ...): ...
    def isValidList(self, l: Any): ...
    def doList(self, l: Any) -> None: ...
    def predicateList(self, subject: Any, newline: bool = ...) -> None: ...
    def verb(self, node: Any, newline: bool = ...) -> None: ...
    def objectList(self, objects: Any) -> None: ...

OBJECT: Any
VERB: Any
_GEN_QNAME_FOR_DT: Callable
