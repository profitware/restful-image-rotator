# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from rotator.tests import TestAPI
from rotator.api.v1.rotator_api.common import \
    ERROR_IMAGE_NOT_FOUND, ERROR_IMAGE_NOT_FOUND_IN_GRIDFS, ERROR_CHECK_BACK_LATER


class TestRotator(TestAPI):
    def test_rotator_nonexistent(self):
        def rendered(_ignored, res, req):
            value = self._check_404(req, is_json=True)

            self.assertEqual(value.get('error'), ERROR_IMAGE_NOT_FOUND)

        return self._test_request('GET', ['v1', 'rotator', 'nonexistent'], rendered)

    def test_rotator_empty(self):
        def rendered(_ignored, res, req):
            value = self._check_200(req, is_json=True)

            self.assertEqual(value.get('version'), '1.0')
            self.assertIsInstance(value.get('images'), list)
            self.assertEqual(len(value.get('images')), 0)

        return self._test_request('GET', ['v1', 'rotator'], rendered)
