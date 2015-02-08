# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

API_VERSION = '1.0'
RELS = {
    'GET': 'list',
    'PUT': 'create',
    'POST': 'edit',
    'DELETE': 'delete'
}
ACCEPTABLE_CONTENT_TYPES = ('application/json', '*/*', 'image/png', 'image/jpeg')


def has_api_method(child, method):
    class_attr = 'render_{method}'.format(method=method)
    is_not_leaf = method == 'GET' and not child.isLeaf

    return hasattr(child, class_attr) or is_not_leaf


def cut_path(path):
    if not path:
        return path

    if path[-1] == '':
        path = path[:-1]

    return path


def form_resource_path(prepath, resource_name):
    if not isinstance(resource_name, basestring):
        resource_name = '/'.join(cut_path(resource_name))

    format_string = '/{resource_name}'
    full_path = '/'.join(cut_path(prepath))

    if full_path:
        format_string = '/{full_path}/{resource_name}'

    return format_string.format(full_path=full_path, resource_name=resource_name)


def check_content_type(request):
    content_type_presence = False

    for content_type in ACCEPTABLE_CONTENT_TYPES:
        content_type_presence |= content_type in request.getHeader('accept')

    return content_type_presence


def generate_link(request, resource_name, rel_name, method):
    return_dict = {
        'href': form_resource_path(request.prepath, resource_name),
        'ref': rel_name,
        'method': method
    }
    return return_dict
