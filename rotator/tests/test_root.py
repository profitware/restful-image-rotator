# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from twisted.internet import defer

from rotator.tests import TestAPI


class TestRoot(TestAPI):
    @defer.inlineCallbacks
    def test_root(self):
        _, req = yield self._test_request('GET', [])

        value = self._check_200(req, is_json=True)

        self.assertEqual(value.get('version'), '1.0')
        self.assertIn({'href': '/v1', 'method': 'GET', 'ref': 'list'}, value.get('links'))

    @defer.inlineCallbacks
    def test_v1(self):
        _, req = yield self._test_request('GET', ['v1'])

        value = self._check_200(req, is_json=True)

        self.assertEqual(value.get('version'), '1.0')

        refs = ('edit', 'delete', 'list')
        for link in value.get('links'):
            self.assertIn(link.get('ref'), refs)

    @defer.inlineCallbacks
    def test_nonexistent(self):
        _, req = yield self._test_request('GET', ['nonexistent'])

        self._check_404(req)
