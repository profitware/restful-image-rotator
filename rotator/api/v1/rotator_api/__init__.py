# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from rotator.api.v1 import RootResource
from rotator.api.v1.rotator_api.get import GETMixin
from rotator.api.v1.rotator_api.post import POSTMixin
from rotator.api.v1.rotator_api.delete import DELETEMixin


class RotatorResource(GETMixin, POSTMixin, DELETEMixin, RootResource):
    isLeaf = True
