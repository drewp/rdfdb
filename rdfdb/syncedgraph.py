"""
client code uses a SyncedGraph, which has a few things:

AutoDepGraphApi - knockoutjs-inspired API for querying the graph in a
way that lets me call you again when there were changes to the things
you queried

CurrentStateGraphApi - a way to query the graph that doesn't gather
your dependencies like AutoDepGraphApi does

GraphEditApi - methods to write patches to the graph for common
operations, e.g. replacing a value, or editing a mapping

WsClientProtocol one connection with the rdfdb server.
"""

import json, logging, traceback
from typing import Optional
import urllib.parse

from rdfdb.autodepgraphapi import AutoDepGraphApi
from rdfdb.currentstategraphapi import CurrentStateGraphApi
from rdfdb.grapheditapi import GraphEditApi
from rdfdb.patch import Patch
from rdfdb.rdflibpatch import patchQuads
from rdflib import ConjunctiveGraph, URIRef
from twisted.internet import defer
from twisted.internet import reactor
import autobahn.twisted.websocket
import treq

# everybody who writes literals needs to get this
from rdfdb.rdflibpatch_literal import patch
patch()

log = logging.getLogger('syncedgraph')



class WsClientProtocol(autobahn.twisted.websocket.WebSocketClientProtocol):
    def __init__(self, sg):
        super().__init__()
        self.sg = sg
        self.sg.currentClient = self
        self.connectionId = None

    def onConnect(self, response):
        log.info('conn %r', response)

    def onOpen(self):
        log.info('ws open')
        
    def onMessage(self, payload, isBinary):
        msg = json.loads(payload)
        if 'connectedAs' in msg:
            self.connectionId = msg['connectedAs']
            log.info(f'rdfdb calls us {self.connectionId}')
        elif 'patch' in msg:
            p = Patch(jsonRepr=payload.decode('utf8'))
            log.debug("received patch %s", p.shortSummary())
            self.sg.onPatchFromDb(p)
        else:
            log.warn('unknown msg from websocket: %s...', payload[:32])

    def sendPatch(self, p: Patch):
        # this is where we could concatenate little patches into a
        # bigger one. Often, many statements will cancel each
        # other out.

        # also who's going to accumulate patches when server is down,
        # or is that not allowed?
        if self.connectionId is None:
            raise ValueError("can't send patches before we get an id")
        body = p.makeJsonRepr()
        log.debug(f'connectionId={self.connectionId} sending patch {len(body)} bytes')
        self.sendMessage(body.encode('utf8'))

    def onClose(self, wasClean, code, reason):
        log.info("WebSocket connection closed: {0}".format(reason))

class SyncedGraph(CurrentStateGraphApi, AutoDepGraphApi, GraphEditApi):
    """
    graph for clients to use. Changes are synced with the master graph
    in the rdfdb process. 

    self.patch(p: Patch) is the only way to write to the graph.

    Reading can be done with the AutoDepGraphApi methods which set up
    watchers to call you back when the results of the read have
    changed (like knockoutjs). Or you can read with
    CurrentStateGraphApi which doesn't have watchers, but you have to
    opt into using it so it's clear you aren't in an auto-dep context
    and meant to set up watchers.

    You may want to attach to self.initiallySynced deferred so you
    don't attempt patches before we've heard the initial contents of
    the graph. It would be ok to accumulate some patches of new
    material, but usually you won't correctly remove the existing
    statements unless we have the correct graph.

    If we get out of sync, we abandon our local graph (even any
    pending local changes) and get the data again from the server.
    """

    def __init__(self,
                 rdfdbRoot: URIRef,
                 label: str,
                 receiverHost: Optional[str] = None):
        """
        label is a string that the server will display in association
        with your connection

        receiverHost is the hostname other nodes can use to talk to me
        """

        self.connectSocket(rdfdbRoot)
        self.rdfdbRoot = rdfdbRoot
        self.initiallySynced: defer.Deferred[None] = defer.Deferred()
        self._graph = ConjunctiveGraph()

        AutoDepGraphApi.__init__(self)
        # this needs more state to track if we're doing a resync (and
        # everything has to error or wait) or if we're live

    def connectSocket(self, rdfdbRoot: URIRef):
        factory = autobahn.twisted.websocket.WebSocketClientFactory(
            rdfdbRoot.replace('http://', 'ws://') + 'syncedGraph',
            # Don't know if this is required by spec, but
            # cyclone.websocket breaks with no origin header.
            origin='foo')
        factory.protocol = lambda: WsClientProtocol(self)

        rr = urllib.parse.urlparse(rdfdbRoot)
        reactor.connectTCP(rr.hostname.encode('ascii'), rr.port, factory)
        #WsClientProtocol sets our currentClient. Needs rewrite using agents.

    def resync(self):
        """
        get the whole graph again from the server (e.g. we had a
        conflict while applying a patch and want to return to the
        truth).

        To avoid too much churn, we remember our old graph and diff it
        against the replacement. This way, our callers only see the
        corrections.

        Edits you make during a resync will surely be lost, so I
        should just fail them. There should be a notification back to
        UIs who want to show that we're doing a resync.
        """
        log.info('resync')
        self.currentClient.dropConnection()

    def _resyncGraph(self, response):
        log.warn("new graph in")

        self.currentClient.dropConnection()
        #diff against old entire graph
        #broadcast that change

    def patch(self, p: Patch) -> None:
        """send this patch to the server and apply it to our local
        graph and run handlers"""

        if p.isNoop():
            log.info("skipping no-op patch")
            return

        # these could fail if we're out of sync. One approach:
        # Rerequest the full state from the server, try the patch
        # again after that, then give up.
        debugKey = '[id=%s]' % (id(p) % 1000)
        log.debug("\napply local patch %s %s", debugKey, p)
        try:
            self._applyPatchLocally(p)
        except ValueError as e:
            log.error(e)
            self.resync()
            return
        log.debug('runDepsOnNewPatch')
        self.runDepsOnNewPatch(p)
        log.debug('sendPatch')
        self.currentClient.sendPatch(p)
        log.debug('patch is done %s', debugKey)

    def suggestPrefixes(self, ctx, prefixes):
        """
        when writing files for this ctx, try to use these n3
        prefixes. async, not guaranteed to finish before any
        particular file flush
        """
        treq.post(self.rdfdbRoot + 'prefixes',
                  json.dumps({
                      'ctx': ctx,
                      'prefixes': prefixes
                  }).encode('utf8'))

    def _applyPatchLocally(self, p: Patch):
        # .. and disconnect on failure
        patchQuads(self._graph, p.delQuads, p.addQuads, perfect=True)
        log.debug("graph now has %s statements" % len(self._graph))

    def onPatchFromDb(self, p):
        """
        central server has sent us a patch
        """
        log.debug('server has sent us %s', p)
        self._applyPatchLocally(p)
        try:
            self.runDepsOnNewPatch(p)
        except Exception:
            # don't reflect this error back to the server; we did
            # receive its patch correctly. However, we're in a bad
            # state since some dependencies may not have rerun
            traceback.print_exc()
            log.warn("some graph dependencies may not have completely run")

        if self.initiallySynced:
            self.initiallySynced.callback(None)
            self.initiallySynced = None
