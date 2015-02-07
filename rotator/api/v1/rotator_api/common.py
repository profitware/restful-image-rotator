# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps

from txmongo import MongoConnectionPool
from txmongo.gridfs import GridFS

from rotator.api.v1.common import cut_path, generate_link


# Ref: http://en.wikipedia.org/wiki/List_of_file_signatures
IMAGE_SIGNATURES = {
    '\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
    '\xFF\xD8\xFF\xE0': 'image/jpeg'
}

mongo_connection = MongoConnectionPool()
rotator_database = mongo_connection.rotator
gridfs_instance = GridFS(rotator_database)


class CommonMixin(object):
    def _image_info_success(self, value, request, is_one_item):
        images_list = list()
        for image_dict in value:

            image_dict['links'] = [
                generate_link(request, image_dict['_id'], 'self', 'GET'),
                generate_link(request, image_dict['_id'], 'delete', 'DELETE'),
                generate_link(request, cut_path([image_dict['_id'], 'content']), 'content', 'GET')
            ]

            image_dict['id'] = image_dict.pop('_id')

            print image_dict

            images_list.append(image_dict)

        if is_one_item:
            return_dict = {
                'image': images_list[0]
            }
        else:
            return_dict = {
                'images': images_list
            }

        request.write(dumps(return_dict))
        request.finish()

    def _image_info_failure(self, error, request):
        return_dict = {
            'error': str(error)
        }
        request.write(dumps(return_dict))
        request.finish()