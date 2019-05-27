import logging, traceback, urllib.request, urllib.parse, urllib.error

from twisted.internet import reactor
import cyclone.web
import treq

from rdfdb.patch import Patch

log = logging.getLogger('syncedgraph')


class PatchReceiver(object):
    """
    runs a web server in this process and registers it with the rdfdb
    master. See onPatch for what happens when the rdfdb master sends
    us a patch
    """

    def __init__(self, rdfdbRoot, host, label, onPatch):
        """
        label is what we'll call ourselves to the rdfdb server

        onPatch is what we call back when the server sends a patch
        """
        self.rdfdbRoot = rdfdbRoot
        listen = reactor.listenTCP(
            0,
            cyclone.web.Application(handlers=[
                (r'/update', makePatchEndpoint(onPatch)),
            ]))
        port = listen._realPortNumber  # what's the right call for this?

        self.updateResource = 'http://%s:%s/update' % (host, port)
        log.info("listening on %s" % port)
        self._register(label)

    def _register(self, label):
        url = (self.rdfdbRoot + 'graphClients').encode('utf8')
        body = urllib.parse.urlencode([(b'clientUpdate', self.updateResource),
                                       (b'label', label)]).encode('utf8')
        treq.post(url, data=body, headers={
            b'Content-Type': [b'application/x-www-form-urlencoded']
        }).addCallbacks(
            self._done,
            lambda err: self._registerError(err, url, body)
        )
        log.info("registering with rdfdb at %s", url)

    def _registerError(self, err, url, body):
        log.error('registering to url=%r body=%r', url, body)
        log.error(err)

    def _done(self, x):
        log.debug("registered with rdfdb")


def makePatchEndpointPutMethod(cb):

    def put(self):
        try:
            p = Patch(jsonRepr=self.request.body)
            log.debug("received patch -%d +%d" %
                      (len(p.delGraph), len(p.addGraph)))
            cb(p)
        except:
            traceback.print_exc()
            raise

    return put


def makePatchEndpoint(cb):

    class Update(cyclone.web.RequestHandler):
        put = makePatchEndpointPutMethod(cb)

    return Update
