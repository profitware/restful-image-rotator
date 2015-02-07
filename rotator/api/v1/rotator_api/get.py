# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from twisted.web import server

from rotator.api.v1.common import check_content_type, cut_path
from rotator.api.v1.rotator_api.common import rotator_database, CommonMixin


class GETMixin(CommonMixin):
    def render_GET(self, request):
        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        search_by = dict()
        is_one_item = False

        postpath = cut_path(request.postpath)
        if postpath:
            search_by['_id'] = postpath[0]
            is_one_item = True

        print request.prepath, request.path, request.uri, postpath

        d = rotator_database.metadata.find(search_by)

        d.addCallback(self._image_info_success, request, is_one_item)
        d.addErrback(self._image_info_failure, request)

        return server.NOT_DONE_YET
