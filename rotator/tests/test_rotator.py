# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from base64 import b64decode, b64encode

from twisted.internet import defer

from rotator.api import log_me
from rotator.api.v1.rotator_api.common import \
    ERROR_IMAGE_NOT_FOUND, ERROR_CHECK_BACK_LATER
from rotator.tests import TestAPI, sleep
from rotator.tests.images import IMAGE_TRIANGLE, IMAGE_TRIANGLE_ROTATED


class TestRotator(TestAPI):
    def _check_version(self, value):
        self.assertEqual(value.get('version'), '1.0')

    @defer.inlineCallbacks
    def step01_rotator_nonexistent(self, global_dict):
        res, req = yield self._test_request('GET', ['v1', 'rotator', 'nonexistent'])

        value = self._check_404(req, is_json=True)

        self._check_version(value)
        self.assertEqual(value.get('error'), ERROR_IMAGE_NOT_FOUND)

        defer.returnValue(dict(test='step01_rotator_nonexistent'))

    @defer.inlineCallbacks
    def step02_rotator_empty(self, global_dict):
        res, req = yield self._test_request('GET', ['v1', 'rotator'])

        value = self._check_200(req, is_json=True)

        self._check_version(value)
        self.assertIsInstance(value.get('images'), list)
        self.assertEqual(len(value.get('images')), 0)

        defer.returnValue(dict(test='step02_rotator_empty'))

    @defer.inlineCallbacks
    def step03_rotator_empty_post(self, global_dict):
        res, req = yield self._test_request('POST', ['v1', 'rotator'])

        value = self._check_code(req, 201, is_json=True)

        self._check_version(value)
        self.assertIsInstance(value.get('images'), list)
        self.assertEqual(len(value.get('images')), 0)
        self.assertEqual(value.get('error'), ERROR_CHECK_BACK_LATER)

        defer.returnValue(dict(test='step03_rotator_empty_post'))

    @defer.inlineCallbacks
    def step04_rotator_post(self, global_dict):
        res, req = yield self._test_request('POST', ['v1', 'rotator'], triangle=[b64decode(IMAGE_TRIANGLE)])

        value = self._check_code(req, 201, is_json=True)

        self._check_version(value)
        self.assertIsInstance(value.get('images'), list)
        self.assertEqual(len(value.get('images')), 1)
        self.assertEqual(value.get('error'), ERROR_CHECK_BACK_LATER)

        triangle_image_id = value.get('images')[0].get('id')

        yield sleep(1)  # Give one second for background task to finish

        defer.returnValue(dict(test='step04_rotator_post', triangle_image_id=triangle_image_id))

    @defer.inlineCallbacks
    def step05_rotator_get_triangle(self, global_dict):
        triangle_id = global_dict.get('triangle_image_id')

        res, req = yield self._test_request('GET', ['v1', 'rotator', triangle_id])

        value = self._check_200(req, is_json=True)

        self._check_version(value)

        image = value.get('image')
        self.assertEqual(image.get('id'), triangle_id)
        self.assertEqual(image.get('status'), 'processed')
        self.assertEqual(image.get('file_content_type'), 'image/png')

        triangle_rotated_image_id = image.get('rotated_image_id')

        links = image.get('links')

        refs = dict()
        for link in links:
            refs[link.get('ref')] = link.get('href')

        defer.returnValue(dict(
            test='step05_rotator_get_triangle',
            triangle_rotated_image_id=triangle_rotated_image_id,
            refs=refs
        ))

    @defer.inlineCallbacks
    def step06_rotator_get_triangle_content(self, global_dict):
        triangle_id = global_dict.get('triangle_image_id')

        res, req = yield self._test_request('GET', ['v1', 'rotator', triangle_id, 'content'])

        value = self._check_code(req, 200, is_json=False)
        self.assertEqual(b64encode(value), IMAGE_TRIANGLE)

        defer.returnValue(dict(test='step06_rotator_get_triangle_content'))

    @defer.inlineCallbacks
    def step07_rotator_get_rotated_triangle_content(self, global_dict):
        triangle_rotated_image_id = global_dict.get('triangle_rotated_image_id')

        res, req = yield self._test_request('GET', ['v1', 'rotator', triangle_rotated_image_id, 'content'])

        value = self._check_code(req, 200, is_json=False)
        self.assertEqual(b64encode(value), IMAGE_TRIANGLE_ROTATED)

        defer.returnValue(dict(test='step07_rotator_get_rotated_triangle_content'))


    @defer.inlineCallbacks
    def step08_rotator_delete_all(self, global_dict):
        res, req = yield self._test_request('DELETE', ['v1', 'rotator'])

        value = self._check_code(req, 200, is_json=True)
        self.assertEqual(value.get('error'), ERROR_CHECK_BACK_LATER)

        defer.returnValue(dict(test='step08_rotator_delete_all'))

    @defer.inlineCallbacks
    def step09_rotator_empty(self, global_dict):
        res, req = yield self._test_request('GET', ['v1', 'rotator'])

        value = self._check_200(req, is_json=True)

        self._check_version(value)
        self.assertIsInstance(value.get('images'), list)
        self.assertEqual(len(value.get('images')), 0)

        defer.returnValue(dict(test='step09_rotator_empty'))

    @defer.inlineCallbacks
    def init_mongodb(self):
        log_me('init_mongodb')
        collections = yield self.rotator_database.collection_names()

        for collection_name in collections:
            yield self.rotator_database.drop_collection(collection_name)

        defer.returnValue(True)

    @defer.inlineCallbacks
    def test_rotator(self):
        yield self.init_mongodb()

        global_dict = dict()

        for name in sorted(dir(self)):
            if name.startswith('step'):

                step = getattr(self, name)
                try:
                    d = yield step(global_dict)
                    log_me(d)
                    global_dict.update(d)
                except Exception as e:
                    self.fail("{} failed ({}: {})".format(step, type(e), e))
