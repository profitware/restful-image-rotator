# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps

from rotator.api import log_me
from rotator.api.v1.common import cut_path, generate_link, API_VERSION


# Ref: http://en.wikipedia.org/wiki/List_of_file_signatures
IMAGE_SIGNATURES = {
    '\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
    '\xFF\xD8\xFF\xE0': 'image/jpeg'
}

IMAGE_PIL_FORMATS = {
    'image/png': 'PNG',
    'image/jpeg': 'JPEG'
}

ERROR_CHECK_BACK_LATER = 'CHECK_BACK_LATER'
ERROR_IMAGE_NOT_FOUND = 'ERROR_IMAGE_NOT_FOUND'
ERROR_IMAGE_NOT_FOUND_IN_GRIDFS = 'ERROR_IMAGE_NOT_FOUND_IN_GRIDFS'


class CommonMixin(object):
    # pylint: disable=too-few-public-methods

    def _image_info_success(self, value, request, is_one_item, is_posted=False):
        # pylint: disable=no-self-use

        images_list = list()
        for image_dict in value:

            image_dict['links'] = [
                generate_link(request, image_dict['_id'], 'self', 'GET'),
                generate_link(request, image_dict['_id'], 'delete', 'DELETE'),
                generate_link(request, cut_path([image_dict['_id'], 'content']), 'content', 'GET')
            ]

            if image_dict.get('status') == 'processed':
                image_dict['links'].append(
                    generate_link(request, cut_path(
                        [image_dict['rotated_image_id'], 'content']
                    ), 'rotated', 'GET')
                )

            image_dict['id'] = image_dict.pop('_id')
            try:
                image_dict.pop('gridfs_id')
            except KeyError:
                pass

            log_me(image_dict)

            images_list.append(image_dict)

        if is_one_item:
            try:
                return_dict = {
                    'image': images_list[0]
                }
                request.setResponseCode(200)
            except IndexError:
                return_dict = {
                    'error': ERROR_IMAGE_NOT_FOUND
                }
                request.setResponseCode(404)
        else:
            return_dict = {
                'images': images_list
            }
            if is_posted:
                return_dict['error'] = ERROR_CHECK_BACK_LATER
                request.setResponseCode(201)
            else:
                request.setResponseCode(200)

        return_dict['version'] = API_VERSION

        request.write(dumps(return_dict))
        request.finish()

    def _image_info_failure(self, error, request):
        # pylint: disable=no-self-use

        return_dict = {
            'error': str(error)
        }
        request.write(dumps(return_dict))
        request.finish()
