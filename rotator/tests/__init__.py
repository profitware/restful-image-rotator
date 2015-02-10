# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import loads
from StringIO import StringIO

from twisted.internet import defer, reactor
from twisted.test.proto_helpers import StringTransport
from twisted.trial import unittest
from twisted.web.test.test_web import DummyRequest
from twisted.web.test._util import _render

from rotator.api import log_me


class Request(DummyRequest):
    def __init__(self, method, *args, **kwargs):
        DummyRequest.__init__(self, *args, **kwargs)
        self.method = method
        self.content = StringIO()
        self.transport = StringTransport()
        self.headers['accept'] = '*/*'
        self.uri = 'http://localhost:8080/'

    def writeContent(self, data):
        self.content.seek(0,2)
        self.content.write(data)
        self.content.seek(0,0)

    def write(self, data):
        DummyRequest.write(self, data)
        self.transport.write(''.join(self.written))
        self.written = list()

    def value(self):
        return self.transport.value()


class TestAPI(unittest.TestCase):
    def setUp(self):
        from rotator import get_site
        from rotator.api import mongo_connection, acquire_new_connection_pool, get_rotator_database

        if mongo_connection.get('connected'):
            mongo_connection.get('connection').disconnect()
        mongo_connection['connection'] = acquire_new_connection_pool()
        mongo_connection['rotator_database'] = get_rotator_database(mongo_connection['connection'], is_test=True)

        self.rotator_database = mongo_connection['rotator_database']
        self.site = get_site()

    @defer.inlineCallbacks
    def _test_request(self, *args, **kwargs):
        method, path = args

        request = Request(method, path)

        resource = yield self.site.getResourceFor(request)
        request.path = request.prepath + request.postpath

        if args:
            request.args = kwargs

        yield _render(resource, request)

        log_me(resource, request)

        defer.returnValue((resource, request))

    def _check_code(self, req, code, is_json):
        self.assertEquals(req.responseCode, code)

        if is_json:
            return loads(req.value())

        return req.value()

    def _check_200(self, req, is_json=False):
        return self._check_code(req, 200, is_json)

    def _check_404(self, req, is_json=False):
        return self._check_code(req, 404, is_json)

    def tearDown(self):
        log_me('tearDown')
        from rotator.api import mongo_connection

        mongo_connection.get('connection').disconnect()
        mongo_connection['connected'] = False


def sleep(secs):
    d = defer.Deferred()
    reactor.callLater(secs, d.callback, None)
    return d
