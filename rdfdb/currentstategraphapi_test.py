import unittest
from rdflib import URIRef
from rdfdb.syncedgraph import SyncedGraph


class TestSequentialUri(unittest.TestCase):

    def test_returnsSequentialUris(self):
        g = SyncedGraph(URIRef('http://example.com/db/'), label='test')
        self.assertEqual(g.sequentialUri(URIRef('http://example.com/foo')),
                         URIRef('http://example.com/foo1'))
        self.assertEqual(g.sequentialUri(URIRef('http://example.com/foo')),
                         URIRef('http://example.com/foo2'))
