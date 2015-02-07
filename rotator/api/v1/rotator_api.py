# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from json import dumps
from hashlib import md5

from twisted.internet import reactor, task

from txmongo import MongoConnectionPool
from txmongo.gridfs import GridFS

from rotator.api.v1 import RootResource
from rotator.api.v1.common import *


# Ref: http://en.wikipedia.org/wiki/List_of_file_signatures
IMAGE_SIGNATURES = {
    '\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
    '\xFF\xD8\xFF\xE0': 'image/jpeg'
}

mongo_connection = MongoConnectionPool()
rotator_database = mongo_connection.rotator
gridfs_instance = GridFS(rotator_database)


class RotatorResource(RootResource):
    isLeaf = True

    def render_GET(self, request):
        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        return_dict = {
            'images': list()
        }

        return dumps(return_dict)

    def render_POST(self, request):
        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        uploaded_files_metadata = list()
        md5hashes = set()

        # FIXME: Check out if this code blocks main thread

        for form_field_name, files in request.args.iteritems():
            for uploaded_file in files:
                for image_signature, file_content_type in IMAGE_SIGNATURES.iteritems():

                    # Image: PNG, JPEG, etc.
                    if uploaded_file.startswith(image_signature):

                        uploaded_file_hash = md5(uploaded_file).hexdigest()

                        uploaded_files_metadata.append({
                            '_id': uploaded_file_hash,
                            'form_field_name': form_field_name,
                            'file_content_type': file_content_type,
                            'status': 'new',
                            'href': form_resource_path(request.prepath, uploaded_file_hash)
                        })

                        if uploaded_file_hash not in md5hashes:
                            gridfs_instance.put(
                                uploaded_file,
                                content_type=file_content_type,
                                md5hash=uploaded_file_hash
                            )
                            md5hashes.add(uploaded_file_hash)

        rotator_database.metadata.insert(uploaded_files_metadata, safe=False)

        request.setResponseCode(201)

        return dumps({'images': uploaded_files_metadata})