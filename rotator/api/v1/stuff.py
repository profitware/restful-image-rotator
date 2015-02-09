# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from rotator.api.v1 import RootResource


class HTMLResource(RootResource):
    isLeaf = True

    def render_GET(self, request):
        return_html = """
            <html>
                <body>
                    <form action="/v1/rotator" enctype="multipart/form-data" method="post">
                        angle: <input type="text" name="angle" value="180"><br/>
                        file_foo: <input type="file" name="file_foo"><br/>
                        file_bar: <input type="file" name="file_bar"><br/>
                        <input type="submit" value="submit">
                    </form>
                </body>
            </html>
        """
        return return_html
