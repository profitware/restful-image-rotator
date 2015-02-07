# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from hashlib import md5

from twisted.internet import reactor
from twisted.internet.task import deferLater
from twisted.web import server

from rotator.api.v1.common import form_resource_path, check_content_type
from rotator.api.v1.rotator_api.common import rotator_database, gridfs_instance, IMAGE_SIGNATURES, CommonMixin


class POSTMixin(CommonMixin):
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

        d = deferLater(reactor, 0, lambda: uploaded_files_metadata)
        d.addCallback(self._image_info_success, request, False)

        return server.NOT_DONE_YET