# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from rotator.tests import TestAPI


class TestRoot(TestAPI):
    def test_root(self):
        def rendered(_ignored, res, req):
            value = self._check_200(req, is_json=True)

            self.assertEqual(value.get('version'), '1.0')
            self.assertIn({'href': '/v1', 'method': 'GET', 'ref': 'list'}, value.get('links'))

        return self._test_request('GET', [], rendered)

    def test_v1(self):
        def rendered(_ignored, res, req):
            value = self._check_200(req, is_json=True)

            self.assertEqual(value.get('version'), '1.0')

            refs = ('edit', 'delete', 'list')
            for link in value.get('links'):
                self.assertIn(link.get('ref'), refs)

        return self._test_request('GET', ['v1'], rendered)

    def test_nonexistent(self):
        def rendered(_ignored, res, req):
            self._check_404(req)

        return self._test_request('GET', ['nonexistent'], rendered)
