# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from twisted.web import server

from rotator.api.v1.common import check_content_type, cut_path
from rotator.api.v1.rotator_api.common import rotator_database, gridfs_instance, CommonMixin


class DELETEMixin(CommonMixin):
    def _image_get_info(self, value, request):
        print '_image_get_info ', value
        d = rotator_database.metadata.find({})

        d.addCallback(self._image_info_success, request, False)
        d.addErrback(self._image_info_failure, request)

        return server.NOT_DONE_YET

    def _image_delete_success(self, value, request, file_id):
        d = gridfs_instance.delete(file_id)
        d.addCallback(self._image_get_info, request)
        d.addErrback(self._image_get_info, request)

        return server.NOT_DONE_YET

    def _image_delete_failure(self, *args):
        if len(args) == 1:
            error, request = None, args[0]
        else:
            error, request = args

        return self._image_get_info(None, request)

    def render_DELETE(self, request):
        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        search_by = dict()

        postpath = cut_path(request.postpath)
        if postpath:
            search_by['_id'] = postpath[0]
        else:  # FIXME: Trying to delete all files will eventually fail
            return self._image_delete_failure(request)

        d = rotator_database.metadata.remove(search_by)

        d.addCallback(self._image_delete_success, request, search_by)
        d.addErrback(self._image_delete_failure, request)

        return server.NOT_DONE_YET
