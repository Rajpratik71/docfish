'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from django.core.files.storage import FileSystemStorage
from django.core.files.move import file_move_safe
from django.contrib.auth.models import User
from django.apps import apps

from fnmatch import fnmatch
from docfish.settings import (
    MEDIA_ROOT, 
    MEDIA_URL
)

import errno
import itertools
import os
import tempfile

############################################################################
# Storage Models
############################################################################

class docfishStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = MEDIA_ROOT
        if base_url is None:
            base_url = MEDIA_URL
        super(docfishStorage, self).__init__(location, base_url)

    def url(self, name):
        uid = None
        spath, file_name = os.path.split(name)
        urlsects = [v for v in spath.split('/') if v]
        for i in range(len(urlsects)):
            sect = urlsects.pop(0)
            if sect.isdigit():
                collection_id = sect
                break
        report_path = '/'.join(urlsects)
        coll_model = apps.get_model('docfish', 'Collection')
        collection = coll_model.objects.get(id=uid)
        #if collection.private:
        #    cid = collection.private_token
        #else:
        cid = collection.id
        return os.path.join(self.base_url, str(cid), cont_path, file_name)


class ImageStorage(docfishStorage):
    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, add an underscore and a number (before
        # the file extension, if one exists) to the filename until the generated
        # filename doesn't exist.
        count = itertools.count(1)
        while self.exists(name):
            # file_ext includes the dot.
            name = os.path.join(dir_name, "%s_%s%s" % (file_root, next(count), file_ext))

        return name
