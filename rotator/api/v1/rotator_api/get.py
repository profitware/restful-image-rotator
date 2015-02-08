# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from io import BytesIO
from json import dumps

from twisted.protocols.basic import FileSender
from twisted.web import server

from rotator.api.v1.common import check_content_type, cut_path
from rotator.api.v1.rotator_api.common import rotator_database, gridfs_instance, CommonMixin


class GETMixin(CommonMixin):

    def _output_content_success(self, *args):
        _value, open_file, request = args

        print '_output_content_success', open_file

        open_file.close()
        request.finish()

    def _output_content(self, value, request):
        open_file = BytesIO(value)

        print '_output_content', open_file

        d = FileSender().beginFileTransfer(open_file, request)

        d.addCallback(self._output_content_success, open_file, request)
        d.addErrback(self._get_image_content_failure, request)

        return server.NOT_DONE_YET

    def _get_gridfs_info(self, value, request):
        print '_get_gridfs_info', value

        request.setHeader('content-type', str(value.contentType))

        d = value.read()

        d.addCallback(self._output_content, request)
        d.addErrback(self._get_image_content_failure, request)

        return server.NOT_DONE_YET

    def _get_image_content_success(self, value, request):
        print '_get_image_content_success', value
        if value and len(value):
            d = gridfs_instance.get(value[0].get('gridfs_id'))

            d.addCallback(self._get_gridfs_info, request)
            d.addErrback(self._get_image_content_failure, request)

            return server.NOT_DONE_YET

        else:
            return self._get_image_content_failure('Image not found in GridFS', request)

    def _get_image_content_failure(self, error, request):
        print '_get_image_content_failure', error

        request.setResponseCode(404)

        request.setHeader('content-type', 'application/json')
        request.write(dumps({'error': error}))
        request.finish()

    def render_GET(self, request):
        assert check_content_type(request)

        search_by = dict()
        is_one_item = False
        get_content = False

        postpath = cut_path(request.postpath)

        print request.prepath, request.path, request.uri, postpath

        if postpath:
            search_by['_id'] = postpath[0]
            is_one_item = True

            if len(postpath) > 1:
                if postpath[1] == 'content':
                    get_content = True

        d = rotator_database.metadata.find(search_by)

        if get_content:
            d.addCallback(self._get_image_content_success, request)
            d.addErrback(self._get_image_content_failure, request)
        else:
            request.setHeader('content-type', 'application/json')

            d.addCallback(self._image_info_success, request, is_one_item)
            d.addErrback(self._image_info_failure, request)

        return server.NOT_DONE_YET
