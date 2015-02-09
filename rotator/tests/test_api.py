# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from StringIO import StringIO
from twisted.web.test.test_web import DummyRequest
from twisted.test.proto_helpers import StringTransport
from twisted.trial import unittest


class Request(DummyRequest):
    def __init__(self, method, *args, **kwargs):
        DummyRequest.__init__(self, *args, **kwargs)
        self.method = method
        self.content = StringIO()
        self.transport = StringTransport()

    def writeContent(self, data):
        self.content.seek(0,2) # Go to end of content
        self.content.write(data) # Write the data
        self.content.seek(0,0) # Go back to beginning of content

    def write(self, data):
        DummyRequest.write(self, data)
        self.transport.write("".join(self.written))
        self.written = []

    def value(self):
        return self.transport.value()



class TestAPI(unittest.TestCase):
    def setUp(self):
        from rotator import get_site
        from rotator.api import mongo_connection

        self.site = get_site()
        self.mongo_connection = mongo_connection

    def test_root(self):
        req = Request('GET', [])
        res = self.site.getResourceFor(req)
        self.assertEqual(1, 1)

    def tearDown(self):
        from rotator.api import mongo_connection
        mongo_connection.disconnect()
