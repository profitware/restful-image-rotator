# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

API_VERSION = '1.0'
RELS = {
    'GET': 'list',
    'PUT': 'create',
    'POST': 'edit',
    'DELETE': 'delete'
}
ACCEPTABLE_CONTENT_TYPES = ( 'application/json', '*/*')


def has_api_method(child, method):
    class_attr = 'render_{method}'.format(method=method)
    is_not_leaf = method == 'GET' and not child.isLeaf

    return hasattr(child, class_attr) or is_not_leaf


def form_resource_path(prepath, resource_name):
    if prepath[-1] == '':
        prepath = prepath[:-1]

    format_string = '/{resource_name}'
    full_path = '/'.join(prepath)

    if full_path:
        format_string = '/{full_path}/{resource_name}'

    return format_string.format(full_path=full_path, resource_name=resource_name)


def check_content_type(request):
    content_type_presence = False

    for content_type in ACCEPTABLE_CONTENT_TYPES:
        content_type_presence |= content_type in request.getHeader('accept')

    return content_type_presence