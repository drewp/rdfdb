from rdflib import ConjunctiveGraph

from rdfdb.currentstategraphapi import CurrentStateGraphApi
from rdfdb.autodepgraphapi import AutoDepGraphApi
from rdfdb.grapheditapi import GraphEditApi
from rdfdb.rdflibpatch import patchQuads

class LocalSyncedGraph(CurrentStateGraphApi, AutoDepGraphApi, GraphEditApi):
    """for tests"""
    def __init__(self, files=None):
        self._graph = ConjunctiveGraph()
        for f in files or []:
            self._graph.parse(f, format='n3')
            

    def patch(self, p):
        patchQuads(self._graph,
                   deleteQuads=p.delQuads,
                   addQuads=p.addQuads,
                   perfect=True)
        # no deps
