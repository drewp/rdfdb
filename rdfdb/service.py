import sys, optparse, logging, json, os, time, itertools
from typing import Callable, Dict, List, Set, Optional, Union

from greplin.scales.cyclonehandler import StatsHandler
from greplin import scales
from twisted.internet import reactor, defer, task
from twisted.internet.inotify import IN_CREATE, INotify
from twisted.python.failure import Failure
from twisted.python.filepath import FilePath
import cyclone.web, cyclone.websocket
from rdflib import ConjunctiveGraph, URIRef, Graph
import twisted.internet.error

from rdfdb.file_vs_uri import correctToTopdirPrefix, fileForUri, uriFromFile, DirUriMap
from rdfdb.graphfile import GraphFile, PatchCb, GetSubgraph
from rdfdb.patch import Patch, ALLSTMTS
from rdfdb.patchreceiver import makePatchEndpointPutMethod
from rdfdb.patchsender import sendPatch
from rdfdb.rdflibpatch import patchQuads

# move this out
procStats = scales.collection('/process',
                              scales.DoubleStat('time'),
)
def updateTimeStat():
    procStats.time = round(time.time(), 3)
task.LoopingCall(updateTimeStat).start(.2)

stats = scales.collection('/webServer',
                          scales.IntStat('clients'),
                          scales.IntStat('liveClients'),
                          scales.PmfStat('setAttr'),
)
graphStats = scales.collection('/graph',
                          scales.IntStat('statements'),
                          scales.RecentFpsStat('patchFps'),
)
fileStats = scales.collection('/file',
                              scales.IntStat('mappedGraphFiles'),
                              )

log = logging.getLogger('rdfdb')


class WebsocketDisconnect(ValueError):
    pass


class Client(object):
    """
    one of our syncedgraph clients
    """

    def __init__(self, updateUri: URIRef, label: str):
        self.label = label
        # todo: updateUri is used publicly to compare clients. Replace
        # it with Client.__eq__ so WsClient doesn't have to fake an
        # updateUri.
        self.updateUri = updateUri

    def __repr__(self):
        return "<%s client at %s>" % (self.label, self.updateUri)

    def sendPatch(self, p: Patch) -> defer.Deferred:
        """
        returns deferred. error will be interpreted as the client being
        broken.
        """
        return sendPatch(self.updateUri, p)


class WsClient(object):

    def __init__(self, connectionId: str, sendMessage: Callable[[str], None]):
        self.updateUri = URIRef(connectionId)
        self.sendMessage = sendMessage

    def __repr__(self):
        return "<WsClient %s>" % self.updateUri

    def sendPatch(self, p: Patch) -> defer.Deferred:
        self.sendMessage(p.makeJsonRepr())
        return defer.succeed(None)


def sendGraphToClient(graph, client: Union[Client, WsClient]) -> None:
    """send the client the whole graph contents"""
    log.info("sending all graphs to %r..." % client)
    client.sendPatch(Patch(addQuads=graph.quads(ALLSTMTS), delQuads=[]))
    log.info("...sent.")


class WatchedFiles(object):
    """
    find files, notice new files.

    This object watches directories. Each GraphFile watches its own file.
    """

    def __init__(self, dirUriMap: DirUriMap, patch: PatchCb,
                 getSubgraph: GetSubgraph, addlPrefixes: Dict[str, URIRef]):
        self.dirUriMap = dirUriMap  # {abspath : uri prefix}
        self.patch, self.getSubgraph = patch, getSubgraph
        self.addlPrefixes = addlPrefixes

        self.graphFiles: Dict[URIRef, GraphFile] = {}  # context uri : GraphFile

        self.notifier = INotify()
        self.notifier.startReading()

        self.findAndLoadFiles()

    def findAndLoadFiles(self) -> None:
        self.initialLoad = True
        try:
            for topdir in self.dirUriMap:
                for dirpath, dirnames, filenames in os.walk(topdir):
                    for base in filenames:
                        p = os.path.join(dirpath, base)
                        # why wasn't mypy catching this?
                        assert isinstance(p, bytes)
                        self.watchFile(p)
                    self.notifier.watch(FilePath(dirpath),
                                        autoAdd=True,
                                        callbacks=[self.dirChange])
        finally:
            self.initialLoad = False

    def dirChange(self, watch, path: FilePath, mask):
        if mask & IN_CREATE:
            if path.path.endswith((b'~', b'.swp', b'swx', b'.rdfdb-temp')):
                return

            log.debug("%s created; consider adding a watch", path)
            self.watchFile(path.path)

    def watchFile(self, inFile: bytes):
        """
        consider adding a GraphFile to self.graphFiles

        inFile needs to be a relative path, not an absolute (e.g. in a
        FilePath) because we use its exact relative form in the
        context URI
        """
        if not os.path.isfile(inFile):
            return

        inFile = correctToTopdirPrefix(self.dirUriMap, inFile)
        if os.path.splitext(inFile)[1] not in [b'.n3']:
            return

        if b'/capture/' in inFile:
            # smaller graph for now
            return

        # an n3 file with rules makes it all the way past this reading
        # and the serialization. Then, on the receiving side, a
        # SyncedGraph calls graphFromNQuad on the incoming data and
        # has a parse error. I'm not sure where this should be fixed
        # yet.
        if b'-rules' in inFile:
            return

        # for legacy versions, compile all the config stuff you want
        # read into one file called config.n3. New versions won't read
        # it.
        if inFile.endswith(b"config.n3"):
            return

        ctx = uriFromFile(self.dirUriMap, inFile)
        gf = self._addGraphFile(ctx, inFile)
        log.info("%s do initial read", inFile)
        gf.reread()

    def aboutToPatch(self, ctx: URIRef):
        """
        warn us that a patch is about to come to this context. it's more
        straightforward to create the new file now

        this is meant to make the file before we add triples, so we
        wouldn't see the blank file and lose those triples. But it
        didn't work, so there are other measures that make us not lose
        the triples from a new file. Calling this before patching the
        graph is still a reasonable thing to do, though.
        """
        if ctx not in self.graphFiles:
            outFile = fileForUri(self.dirUriMap, ctx)
            # mypy missed the next line because of
            # https://github.com/python/typeshed/issues/2937 ('str in
            # bytes' isn't an error)
            assert b'//' not in outFile, (outFile, self.dirUriMap, ctx)
            log.info("starting new file %r", outFile)
            self._addGraphFile(ctx, outFile)

    def _addGraphFile(self, ctx, path):
        self.addlPrefixes.setdefault(ctx, {})
        self.addlPrefixes.setdefault(None, {})
        gf = GraphFile(self.notifier,
                       path,
                       ctx,
                       self.patch,
                       self.getSubgraph,
                       globalPrefixes=self.addlPrefixes[None],
                       ctxPrefixes=self.addlPrefixes[ctx])
        self.graphFiles[ctx] = gf
        fileStats.mappedGraphFiles = len(self.graphFiles)
        return gf

    def dirtyFiles(self, ctxs):
        """mark dirty the files that we watch in these contexts.

        the ctx might not be a file that we already read; it might be
        for a new file we have to create, or it might be for a
        transient context that we're not going to save

        if it's a ctx with no file, error
        """
        for ctx in ctxs:
            g = self.getSubgraph(ctx)
            self.graphFiles[ctx].dirty(g)


class Db(object):
    """
    the master graph, all the connected clients, all the files we're watching
    """

    def __init__(self, dirUriMap: DirUriMap, addlPrefixes):
        self.clients: List[Union[Client, WsClient]] = []
        self.graph = ConjunctiveGraph()
        stats.graphLen = len(self.graph)
        stats.clients = len(self.clients)

        self.watchedFiles = WatchedFiles(dirUriMap, self.patch,
                                         self.getSubgraph, addlPrefixes)

        self.summarizeToLog()

    @graphStats.patchFps.rate()
    def patch(self, patch: Patch, dueToFileChange: bool = False) -> None:
        """
        apply this patch to the master graph then notify everyone about it

        dueToFileChange if this is a patch describing an edit we read
        *from* the file (such that we shouldn't write it back to the file)

        if p has a senderUpdateUri attribute, we won't send this patch
        back to the sender with that updateUri
        """
        ctx = patch.getContext()
        log.info("patching graph %s -%d +%d" %
                 (ctx, len(patch.delQuads), len(patch.addQuads)))

        if hasattr(self, 'watchedFiles'):  # not available during startup
            self.watchedFiles.aboutToPatch(ctx)

        patchQuads(self.graph, patch.delQuads, patch.addQuads, perfect=True)
        stats.graphLen = len(self.graph)
        self._sendPatch(patch)
        if not dueToFileChange:
            self.watchedFiles.dirtyFiles([ctx])
        sendToLiveClients(asJson=patch.jsonRepr)
        graphStats.statements = len(self.graph)

    def _sendPatch(self, p: Patch):
        senderUpdateUri: Optional[URIRef] = getattr(p, 'senderUpdateUri', None)

        for c in self.clients:
            if c.updateUri == senderUpdateUri:
                # this client has self-applied the patch already
                log.debug("_sendPatch: don't resend to %r", c)
                continue
            log.debug('_sendPatch: send to %r', c)
            d = c.sendPatch(p)
            d.addErrback(self.clientErrored, c)

    def clientErrored(self, err, c) -> None:
        err.trap(twisted.internet.error.ConnectError, WebsocketDisconnect)
        log.info("%r %r - dropping client", c, err.getErrorMessage())
        if c in self.clients:
            self.clients.remove(c)
        stats.clients = len(self.clients)
        self.sendClientsToAllLivePages()

    def summarizeToLog(self):
        log.info("contexts in graph (%s total stmts):" % len(self.graph))
        for c in self.graph.contexts():
            log.info("  %s: %s statements" %
                     (c.identifier, len(self.getSubgraph(c.identifier))))

    def getSubgraph(self, uri: URIRef) -> Graph:
        """
        this is meant to return a live view of the given subgraph, but
        if i'm still working around an rdflib bug, it might return a
        copy

        and it's returning triples, but I think quads would be better
        """
        # this is returning an empty Graph :(
        #return self.graph.get_context(uri)

        g = Graph()
        for s in self.graph.triples(ALLSTMTS, uri):
            g.add(s)
        return g

    def addClient(self, newClient: Union[Client, WsClient]) -> None:
        for c in self.clients:
            if c.updateUri == newClient.updateUri:
                self.clients.remove(c)

        log.info("new client %r" % newClient)
        sendGraphToClient(self.graph, newClient)
        self.clients.append(newClient)
        self.sendClientsToAllLivePages()
        stats.clients = len(self.clients)

    def sendClientsToAllLivePages(self) -> None:
        sendToLiveClients({
            "clients": [
                dict(updateUri=c.updateUri.toPython(), label=repr(c))
                for c in self.clients
            ]
        })


class GraphResource(cyclone.web.RequestHandler):

    def get(self):
        accept = self.request.headers.get('accept', '')
        format = 'n3'
        if accept == 'text/plain':
            format = 'nt'
        elif accept == 'application/n-quads':
            format = 'nquads'
        elif accept == 'pickle':
            # don't use this; it's just for speed comparison
            import pickle as pickle
            pickle.dump(self.settings.db.graph, self, protocol=2)
            return
        elif accept == 'msgpack':
            self.write(repr(self.settings.db.graph.__getstate__))
            return
        self.write(self.settings.db.graph.serialize(format=format))


class Patches(cyclone.web.RequestHandler):

    def __init__(self, *args, **kw):
        cyclone.web.RequestHandler.__init__(self, *args, **kw)
        p = makePatchEndpointPutMethod(self.settings.db.patch)
        self.put = lambda: p(self)

    def get(self):
        pass


class GraphClients(cyclone.web.RequestHandler):

    def get(self):
        pass

    def post(self) -> None:
        upd = URIRef(self.get_argument("clientUpdate"))
        try:
            self.settings.db.addClient(Client(upd, self.get_argument("label")))
        except:
            import traceback
            traceback.print_exc()
            raise


class Prefixes(cyclone.web.RequestHandler):

    def post(self):
        suggestion = json.loads(self.request.body)
        addlPrefixes = self.settings.db.watchedFiles.addlPrefixes
        addlPrefixes.setdefault(URIRef(suggestion['ctx']),
                                {}).update(suggestion['prefixes'])


_wsClientSerial = itertools.count(0)


class WebsocketClient(cyclone.websocket.WebSocketHandler):

    wsClient: Optional[WsClient] = None

    def connectionMade(self, *args, **kwargs) -> None:
        connectionId = f'WS{next(_wsClientSerial)}'

        self.wsClient = WsClient(connectionId, self.sendMessage)
        self.sendMessage(json.dumps({'connectedAs': connectionId}))
        log.info("new ws client %r", self.wsClient)
        self.settings.db.addClient(self.wsClient)

    def connectionLost(self, reason):
        log.info("bye ws client %r", self.wsClient)
        self.settings.db.clientErrored(Failure(WebsocketDisconnect(reason)),
                                       self.wsClient)

    def messageReceived(self, message: bytes):
        if message == b'PING':
            self.sendMessage('PONG')
            return
        log.info("got message from %r: %s", self.wsClient, message)
        p = Patch(jsonRepr=message.decode('utf8'))
        assert self.wsClient is not None
        p.senderUpdateUri = self.wsClient.updateUri
        self.settings.db.patch(p)


class Live(cyclone.websocket.WebSocketHandler):

    def connectionMade(self, *args, **kwargs):
        log.info("websocket opened")
        liveClients.add(self)
        stats.liveClients = len(liveClients)
        self.settings.db.sendClientsToAllLivePages()

    def connectionLost(self, reason):
        log.info("websocket closed")
        liveClients.remove(self)
        stats.liveClients = len(liveClients)

    def messageReceived(self, message: bytes):
        log.info("got message %s" % message)
        # this is just a leftover test?
        self.sendMessage(message.decode('utf8'))


liveClients: Set[Live] = set()
stats.liveClients = len(liveClients)

def sendToLiveClients(d: Optional[Dict]=None, asJson: Optional[str]=None):
    msg: str = asJson or json.dumps(d)
    assert isinstance(msg, str), repr(msg)
    for c in liveClients:
        c.sendMessage(msg)


class NoExts(cyclone.web.StaticFileHandler):
    # .html pages can be get() without .html on them
    def get(self, path, *args, **kw):
        if path and '.' not in path:
            path = path + ".html"
        cyclone.web.StaticFileHandler.get(self, path, *args, **kw)


def main(dirUriMap: Optional[DirUriMap] = None,
         prefixes: Optional[Dict[str, URIRef]] = None,
         port=9999):

    if dirUriMap is None:
        dirUriMap = {b'data/': URIRef('http://example.com/data/')}
    if prefixes is None:
        prefixes = {
            'rdf': URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
            'rdfs': URIRef('http://www.w3.org/2000/01/rdf-schema#'),
            'xsd': URIRef('http://www.w3.org/2001/XMLSchema#'),
        }

    logging.basicConfig()
    log = logging.getLogger()

    parser = optparse.OptionParser()
    parser.add_option("-v",
                      "--verbose",
                      action="store_true",
                      help="logging.DEBUG")
    (options, args) = parser.parse_args()

    log.setLevel(logging.DEBUG if options.verbose else logging.INFO)

    db = Db(dirUriMap=dirUriMap, addlPrefixes={None: prefixes})

    from twisted.python import log as twlog
    twlog.startLogging(sys.stdout)

    reactor.listenTCP(
        port,
        cyclone.web.Application(handlers=[
            (r'/live', Live),
            (r'/graph', GraphResource),
            (r'/patches', Patches),
            (r'/graphClients', GraphClients),
            (r'/syncedGraph', WebsocketClient),
            (r'/prefixes', Prefixes),
            (r'/stats/(.*)', StatsHandler, {'serverName': 'rdfdb'}),
            (r'/(.*)', NoExts, {
                "path": FilePath(__file__).sibling("web").path,
                "default_filename": "index.html"
            }),
        ],
                                debug=True,
                                db=db))
    log.info("serving on %s" % port)
    reactor.run()
