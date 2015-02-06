# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from twisted.web import server
from twisted.internet import reactor, endpoints

from rotator.api.v1 import RootResource, V1Resource
from rotator.api.v1.rotator_api import RotatorResource


def create_api():
    root_resource = RootResource()
    v1_resource = V1Resource()

    root_resource.putChild('v1', v1_resource)
    v1_resource.putChild('rotator', RotatorResource())

    return root_resource


if __name__ == '__main__':
    endpoints.serverFromString(reactor, "tcp:8080").listen(server.Site(create_api()))
    reactor.run()
