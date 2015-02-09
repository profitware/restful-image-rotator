# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps

from twisted.internet import defer
from twisted.web import server

from rotator.api.v1.common import check_content_type, cut_path
from rotator.api.v1.rotator_api.common import rotator_database, gridfs_instance, CommonMixin, ERROR_CHECK_BACK_LATER


class DELETEMixin(CommonMixin):
    def _image_get_info(self, value, request):
        d = rotator_database.metadata.find({})

        d.addCallback(self._image_info_success, request, False)
        d.addErrback(self._image_info_failure, request)

        print '_image_get_info ', value

        return server.NOT_DONE_YET

    def _output_delete_success(self, value, request):
        print '_output_delete_success', value

        request.write(dumps({'error': ERROR_CHECK_BACK_LATER}))
        request.finish()

    def _image_delete_success(self, value, request, file_ids):
        dl = []
        for file_id in file_ids:
            dl.append(gridfs_instance.delete(file_id))

        d = defer.DeferredList(dl)
        d.addCallback(self._output_delete_success, request)
        d.addErrback(self._image_delete_failure, request)

        print '_image_delete_success', value, file_ids

        return server.NOT_DONE_YET

    def _remove_metadata(self, metadata, request, search_by):
        gridfs_image_ids = [value.get('gridfs_id') for value in metadata]

        d = rotator_database.metadata.remove(search_by)

        d.addCallback(self._image_delete_success, request, gridfs_image_ids)
        d.addErrback(self._image_delete_failure, request)

        print '_remove_metadata ', search_by, gridfs_image_ids

        return server.NOT_DONE_YET

    def _image_delete_failure(self, *args):
        if len(args) == 1:
            error, request = None, args[0]
        else:
            error, request = args

        print '_image_delete_failure', error

        return self._image_get_info(None, request)

    def render_DELETE(self, request):
        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        search_by = dict()

        postpath = cut_path(request.postpath)
        if postpath:
            search_by['_id'] = postpath[0]

        d = rotator_database.metadata.find(search_by)

        d.addCallback(self._remove_metadata, request, search_by)
        d.addErrback(self._image_delete_failure, request)

        return server.NOT_DONE_YET
