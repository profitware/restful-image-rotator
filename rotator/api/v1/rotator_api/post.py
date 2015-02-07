# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from hashlib import md5
from time import sleep
from io import BytesIO
from cStringIO import StringIO

from twisted.internet import reactor
from twisted.internet.task import deferLater
from twisted.internet.threads import deferToThread
from twisted.web import server

from PIL import Image

from rotator.api.v1.common import form_resource_path, check_content_type
from rotator.api.v1.rotator_api.common import rotator_database, gridfs_instance, CommonMixin, \
    IMAGE_SIGNATURES, IMAGE_PIL_FORMATS


class POSTMixin(CommonMixin):
    def _process_image(self, image_id, image_content, image_content_type):
        deferToThread(self._add_image_to_gridfs, image_id, image_content, image_content_type)

        image = Image.open(BytesIO(image_content))
        image.rotate(180)

        output = StringIO()
        image.save(output, format=IMAGE_PIL_FORMATS.get(image_content_type))
        rotated_contents = output.getvalue()
        output.close()

        return image_id, image_content, rotated_contents, image_content_type

    def _process_image_success(self, value):
        image_id, image_content, rotated_contents, image_content_type = value

        rotated_image_id = md5(rotated_contents).hexdigest()

        d = deferToThread(self._add_image_to_gridfs, rotated_image_id, rotated_contents, image_content_type)
        d.addCallback(self._update_image_status, image_id, rotated_image_id)

    def _update_image_status(self, value, image_id, rotated_image_id):
        rotator_database.metadata.find_and_modify(
            query={'_id': image_id},
            update={'$set': {
                'status': 'processed',
                'rotated_image_id': rotated_image_id
            }},
            upsert=True
        )

    def _add_image_to_gridfs(self, image_id, image_content, image_content_type):
        gridfs_instance.put(
            image_content,
            content_type=image_content_type,
            md5hash=image_id
        )

    def render_POST(self, request):
        assert check_content_type(request)

        request.setHeader('content-type', 'application/json')

        uploaded_files_metadata = list()
        md5hashes = set()

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
                            md5hashes.add(uploaded_file_hash)

                            d = deferToThread(
                                self._process_image,
                                uploaded_file_hash,
                                uploaded_file,
                                file_content_type
                            )
                            d.addCallback(self._process_image_success)

        rotator_database.metadata.insert(uploaded_files_metadata, safe=False)

        request.setResponseCode(201)

        d = deferLater(reactor, 0, lambda: uploaded_files_metadata)
        d.addCallback(self._image_info_success, request, False)

        return server.NOT_DONE_YET
