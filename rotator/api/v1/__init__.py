# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from pprint import pprint
from json import dumps

from twisted.web.resource import Resource
from rotator.api.v1.common import *


class RootResource(Resource):
    def getChild(self, name, request):
        print 'getChild', name, request

        assert check_content_type(request)

        if name == '':
            return self

        return Resource.getChild(self, name, request)

    def render_GET(self, request):
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

        pprint(return_dict)

        return dumps(return_dict)


class V1Resource(RootResource):
    pass

