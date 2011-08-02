# -*- coding: utf-8 -*-
from cStringIO import StringIO

from django.core.cache import get_cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


CACHE_BACKEND = settings.CACHES.get('file_resubmit', "file:///tmp/file_resubmit")


class FileCache(object):
    
    def __init__(self):
        self.backend = get_cache(CACHE_BACKEND)

    def put(self, key, upload):
        state = {
            "name": upload.name,
            "size": upload.size,
            "content_type": upload.content_type,
            "charset": upload.charset,
            "content": upload.file.read()}
        upload.file.seek(0)
        self.backend.set(key, state)

    def get(self, key, field_name):
        upload = None
        state = self.backend.get(key)
        if state: 
            f = StringIO()
            f.write(state["content"])
            upload = InMemoryUploadedFile(
                    file=f,
                    field_name=field_name,
                    name=state["name"],
                    content_type=state["content_type"],
                    size=state["size"],
                    charset=state["charset"])
            upload.file.seek(0)
        return upload

