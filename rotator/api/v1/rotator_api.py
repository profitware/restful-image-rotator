# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps

from rotator.api.v1 import RootResource


class RotatorResource(RootResource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader('content-type', 'application/json')

        return_dict = {
            'images': list()
        }

        return dumps(return_dict)
