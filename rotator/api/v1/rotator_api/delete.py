# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps

from twisted.internet import defer
from twisted.web import server

from txmongo.gridfs import GridFS

from rotator.api import mongo_connection, log_me
from rotator.api.v1.common import check_content_type, cut_path
from rotator.api.v1.rotator_api.common import CommonMixin, ERROR_CHECK_BACK_LATER


class DELETEMixin(CommonMixin):
    # pylint: disable=too-few-public-methods

    def _image_get_info(self, value, request):
        d = mongo_connection.get('rotator_database').metadata.find({})

        d.addCallback(self._image_info_success, request, False)
        d.addErrback(self._image_info_failure, request)

        log_me('_image_get_info ', value)

        return server.NOT_DONE_YET

    def _output_delete_success(self, value, request):
        # pylint: disable=no-self-use

        log_me('_output_delete_success', value)

        request.setResponseCode(200)

        request.write(dumps({'error': ERROR_CHECK_BACK_LATER}))
        request.finish()

    def _image_delete_success(self, value, request, file_ids):
        dl = []
        for file_id in file_ids:
            dl.append(GridFS(mongo_connection['rotator_database']).delete(file_id))

        d = defer.DeferredList(dl)
        d.addCallback(self._output_delete_success, request)
        d.addErrback(self._image_delete_failure, request)

        log_me('_image_delete_success', value, file_ids)

        return server.NOT_DONE_YET

    def _remove_metadata(self, metadata, request, search_by):
        gridfs_image_ids = [value.get('gridfs_id') for value in metadata]

        d = mongo_connection.get('rotator_database').metadata.remove(search_by)

        d.addCallback(self._image_delete_success, request, gridfs_image_ids)
        d.addErrback(self._image_delete_failure, request)

        log_me('_remove_metadata ', search_by, gridfs_image_ids)

        return server.NOT_DONE_YET

    def _image_delete_failure(self, *args):
        if len(args) == 1:
            error, request = None, args[0]
        else:
            error, request = args

        log_me('_image_delete_failure', error)

        return self._image_get_info(None, request)

    def render_DELETE(self, request):
        # pylint: disable=invalid-name

        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        search_by = dict()

        postpath = cut_path(request.postpath)
        if postpath:
            search_by['_id'] = postpath[0]

        d = mongo_connection.get('rotator_database').metadata.find(search_by)

        d.addCallback(self._remove_metadata, request, search_by)
        d.addErrback(self._image_delete_failure, request)

        return server.NOT_DONE_YET
