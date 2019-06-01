import sys, optparse, logging, json, os, time, itertools
from typing import Dict, List, Optional

from greplin.scales.cyclonehandler import StatsHandler
from greplin import scales
from twisted.internet import reactor, task
from twisted.internet.inotify import IN_CREATE, INotify
from twisted.python.failure import Failure
from twisted.python.filepath import FilePath
import cyclone.web, cyclone.websocket
from rdflib import ConjunctiveGraph, URIRef, Graph
import twisted.internet.error

from rdfdb.file_vs_uri import correctToTopdirPrefix, fileForUri, uriFromFile, DirUriMap
from rdfdb.graphfile import GraphFile, PatchCb, GetSubgraph
from rdfdb.patch import Patch, ALLSTMTS
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


_wsClientSerial = itertools.count(0)


class WebsocketClient(cyclone.websocket.WebSocketHandler):
    """
    Send patches to the client (starting with a client who has 0
    statements) to keep it in sync with the graph.

    Accept patches from the client, and assume that the client has
    already applied them to its local graph.

    Treat a disconnect as 'out of sync'. Either the client thinks it
    is out of sync and wants to start over, or we can't apply a patch
    correctly therefore we disconnect to make the client start over.

    This socket may also carry some special messages meant for the
    rdfdb web UI, e.g. about who is connected, etc.
    """
    connectionId: str

    def connectionMade(self, *args, **kwargs) -> None:
        self.connectionId = f'WS{next(_wsClientSerial)}'

        self.sendMessage(json.dumps({'connectedAs': self.connectionId}))
        log.info("new ws client %r", self)
        self.settings.db.addClient(self)

    def connectionLost(self, reason):
        log.info("bye ws client %r: %s", self, reason)
        self.settings.db.clientErrored(Failure(WebsocketDisconnect(reason)),
                                       self)

    def messageReceived(self, message: bytes):
        if message == b'PING':
            self.sendMessage('PONG')
            return
        log.debug("got message from %r: %s", self, message[:32])
        p = Patch(jsonRepr=message.decode('utf8'))
        self.settings.db.patch(p, sender=self.connectionId)

    def sendPatch(self, p: Patch):
        self.sendMessage(p.makeJsonRepr())

    def __repr__(self):
        return f"<SyncedGraph client {self.connectionId}>"

class Db(object):
    """
    the master graph, all the connected clients, all the files we're watching
    """

    def __init__(self, dirUriMap: DirUriMap, addlPrefixes):
        self.clients: List[WebsocketClient] = []
        self.graph = ConjunctiveGraph()
        stats.graphLen = len(self.graph)
        stats.clients = len(self.clients)

        self.watchedFiles = WatchedFiles(dirUriMap, self.patch,
                                         self.getSubgraph, addlPrefixes)

        self.summarizeToLog()

    @graphStats.patchFps.rate()
    def patch(self, patch: Patch, sender: Optional[str]=None, dueToFileChange: bool = False) -> None:
        """
        apply this patch to the master graph then notify everyone about it

        dueToFileChange if this is a patch describing an edit we read
        *from* the file (such that we shouldn't write it back to the file)
        """
        ctx = patch.getContext()
        log.info("patching graph %s -%d +%d" %
                 (ctx, len(patch.delQuads), len(patch.addQuads)))

        if hasattr(self, 'watchedFiles'): # todo: eliminate this
            self.watchedFiles.aboutToPatch(ctx)

        # an error here needs to drop the sender, and reset everyone
        # else if we can't rollback the failing patch.
        patchQuads(self.graph, patch.delQuads, patch.addQuads, perfect=True)
        stats.graphLen = len(self.graph)
        
        self._syncPatchToOtherClients(patch, sender)
        if not dueToFileChange:
            self.watchedFiles.dirtyFiles([ctx])
        graphStats.statements = len(self.graph)

    def _syncPatchToOtherClients(self, p: Patch, sender: Optional[str]=None):
        for c in self.clients:
            if sender is not None and c.connectionId == sender:
                # this client has self-applied the patch already
                log.debug("_syncPatchToOtherClients: don't resend to %r", c)
                continue
            log.debug('_syncPatchToOtherClients: send to %r', c)
            c.sendPatch(p)
            
    def clientErrored(self, err, c) -> None:
        err.trap(twisted.internet.error.ConnectError, WebsocketDisconnect)
        log.info("%r %r - dropping client", c, err.getErrorMessage())
        if c in self.clients:
            self.clients.remove(c)
        stats.clients = len(self.clients)

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

    def addClient(self, newClient: WebsocketClient) -> None:
        log.info("new connection: sending all graphs to %r..." % newClient)
        newClient.sendPatch(Patch(addQuads=self.graph.quads(ALLSTMTS), delQuads=[]))

        self.clients.append(newClient)
        stats.clients = len(self.clients)


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


class Prefixes(cyclone.web.RequestHandler):

    def post(self):
        suggestion = json.loads(self.request.body)
        addlPrefixes = self.settings.db.watchedFiles.addlPrefixes
        addlPrefixes.setdefault(URIRef(suggestion['ctx']),
                                {}).update(suggestion['prefixes'])


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
            (r'/graph', GraphResource),
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
