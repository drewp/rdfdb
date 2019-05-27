"""
note that if there are ambiguities in dirUriMap, you'll get
undefined results that depend on python's items() order.
"""
import os
from rdflib import URIRef
from typing import Dict

DirUriMap = Dict[bytes, URIRef]

def uriFromFile(dirUriMap: DirUriMap, filename: bytes) -> URIRef:
    assert filename.endswith(b'.n3'), filename
    for d, prefix in list(dirUriMap.items()):
        if filename.startswith(d):
            return URIRef(prefix + filename[len(d):-len(b'.n3')].decode('ascii'))
    raise ValueError("filename %s doesn't start with any of %s" %
                     (filename, list(dirUriMap.keys())))

def fileForUri(dirUriMap: DirUriMap, ctx: URIRef) -> bytes:
    assert isinstance(ctx, URIRef), ctx
    for d, prefix in dirUriMap.items():
        if ctx.startswith(prefix):
            return d + ctx[len(prefix):].encode('utf8') + b'.n3'
    raise ValueError("don't know what filename to use for %s" % ctx)

def correctToTopdirPrefix(dirUriMap: DirUriMap, inFile: bytes) -> bytes:
    if not any(inFile.startswith(prefix) for prefix in dirUriMap):
        for prefix in dirUriMap:
            prefixAbs = os.path.abspath(prefix)
            if inFile.startswith(prefixAbs):
                inFile = prefix + inFile[len(prefixAbs):]
                break
        else:
            raise ValueError("can't correct %s to start with one of %s" %
                             (inFile, list(dirUriMap.keys())))
    return inFile
