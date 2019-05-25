# Stubs for twisted.python.filepath (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import base64
import os
from twisted.python.util import FancyEqMixin
from typing import Any, Optional
from zope.interface import Interface

islink: Any
randomBytes = os.urandom
armor = base64.urlsafe_b64encode

class IFilePath(Interface):
    def child(self, name: Any) -> None: ...
    def open(self, mode: str = ...) -> None: ...
    def changed(self, ) -> None: ...
    def getsize(self, ) -> None: ...
    def getModificationTime(self, ) -> None: ...
    def getStatusChangeTime(self, ) -> None: ...
    def getAccessTime(self, ) -> None: ...
    def exists(self, ) -> None: ...
    def isdir(self, ) -> None: ...
    def isfile(self, ) -> None: ...
    def children(self, ) -> None: ...
    def basename(self, ) -> None: ...
    def parent(self, ) -> None: ...
    def sibling(self, name: Any) -> None: ...

class InsecurePath(Exception): ...
class LinkError(Exception): ...

class UnlistableError(OSError):
    originalException: Any = ...
    def __init__(self, originalException: Any) -> None: ...

class _WindowsUnlistableError(UnlistableError, WindowsError): ...

class AbstractFilePath:
    def getContent(self): ...
    def parents(self) -> None: ...
    def children(self): ...
    def walk(self, descend: Optional[Any] = ...) -> None: ...
    def sibling(self, path: Any): ...
    def descendant(self, segments: Any): ...
    def segmentsFrom(self, ancestor: Any): ...
    def __hash__(self): ...
    def getmtime(self): ...
    def getatime(self): ...
    def getctime(self): ...

class RWX(FancyEqMixin):
    compareAttributes: Any = ...
    read: Any = ...
    write: Any = ...
    execute: Any = ...
    def __init__(self, readable: Any, writable: Any, executable: Any) -> None: ...
    def shorthand(self): ...

class Permissions(FancyEqMixin):
    compareAttributes: Any = ...
    def __init__(self, statModeInt: Any) -> None: ...
    def shorthand(self): ...

class _SpecialNoValue: ...

class FilePath(AbstractFilePath):
    path: Any = ...
    alwaysCreate: Any = ...
    def __init__(self, path: Any, alwaysCreate: bool = ...) -> None: ...
    @property
    def sep(self): ...
    def asBytesMode(self, encoding: Optional[Any] = ...): ...
    def asTextMode(self, encoding: Optional[Any] = ...): ...
    def child(self, path: Any): ...
    def preauthChild(self, path: Any): ...
    def childSearchPreauth(self, *paths: Any): ...
    def siblingExtensionSearch(self, *exts: Any): ...
    def realpath(self): ...
    def siblingExtension(self, ext: Any): ...
    def linkTo(self, linkFilePath: Any) -> None: ...
    def open(self, mode: str = ...): ...
    def restat(self, reraise: bool = ...) -> None: ...
    def changed(self) -> None: ...
    def chmod(self, mode: Any) -> None: ...
    def getsize(self): ...
    def getModificationTime(self): ...
    def getStatusChangeTime(self): ...
    def getAccessTime(self): ...
    def getInodeNumber(self): ...
    def getDevice(self): ...
    def getNumberOfHardLinks(self): ...
    def getUserID(self): ...
    def getGroupID(self): ...
    def getPermissions(self): ...
    def exists(self): ...
    def isdir(self): ...
    def isfile(self): ...
    def isBlockDevice(self): ...
    def isSocket(self): ...
    def islink(self): ...
    def isabs(self): ...
    def listdir(self): ...
    def splitext(self): ...
    def touch(self) -> None: ...
    def remove(self) -> None: ...
    def makedirs(self, ignoreExistingDirectory: bool = ...): ...
    def globChildren(self, pattern: Any): ...
    def basename(self): ...
    def dirname(self): ...
    def parent(self): ...
    def setContent(self, content: Any, ext: bytes = ...) -> None: ...
    def __cmp__(self, other: Any): ...
    def createDirectory(self) -> None: ...
    def requireCreate(self, val: int = ...) -> None: ...
    def create(self): ...
    def temporarySibling(self, extension: bytes = ...): ...
    def copyTo(self, destination: Any, followLinks: bool = ...) -> None: ...
    def moveTo(self, destination: Any, followLinks: bool = ...) -> None: ...
    def statinfo(self, value: Any = ...): ...
