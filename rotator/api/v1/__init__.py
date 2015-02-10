# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps

from twisted.web.resource import Resource

from rotator.api import log_me
from rotator.api.v1.common import check_content_type, has_api_method, generate_link, \
    API_VERSION, RELS


class RootResource(Resource):
    # pylint: disable=too-few-public-methods

    def getChild(self, name, request):
        log_me('getChild', name, request)

        assert check_content_type(request)

        if name == '':
            return self

        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        # pylint: disable=invalid-name

        api_version = API_VERSION
        links_list = list()

        request.setHeader('content-type', 'application/json')

        for resource_name, child in self.children.iteritems():
            for method, rel_name in RELS.iteritems():

                if has_api_method(child, method):
                    links_list.append(
                        generate_link(request, resource_name, rel_name, method)
                    )

        return_dict = {
            'version': api_version,
            'links': links_list
        }

        log_me(return_dict)

        request.setResponseCode(200)

        return dumps(return_dict)


class V1Resource(RootResource):
    # pylint: disable=too-few-public-methods

    pass
