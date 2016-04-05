# -*- coding: utf-8 -*-
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

# Django 1.9 removes support for django.core.cache.get_cache
try:
    from django.core.cache import get_cache
except ImportError:
    from django.core.cache import caches
    get_cache = lambda cache_name: caches[cache_name]

from django.core.files.uploadedfile import InMemoryUploadedFile


class FileCache(object):
    def __init__(self):
        self.backend = self.get_backend()

    def get_backend(self):
        return get_cache('file_resubmit')

    def set(self, key, upload):
        params_state = {
            "name": upload.name,
            "size": upload.size,
            "content_type": upload.content_type,
            "charset": upload.charset,
        }
        upload.file.seek(0)
        self.backend.set(key + '_params', params_state)

        file_state = upload.file.read()
        upload.file.seek(0)
        self.backend.set(key + '_value', file_state)

    def get(self, key, field_name):
        upload = None
        params_state = self.backend.get(key + '_params')
        value_state = self.backend.get(key + '_value')
        if params_state and value_state:
            f = BytesIO()
            f.write(value_state)
            upload = InMemoryUploadedFile(
                file=f,
                field_name=field_name,
                name=params_state["name"],
                content_type=params_state["content_type"],
                size=params_state["size"],
                charset=params_state["charset"],
            )
            upload.file.seek(0)
        return upload

    def delete(self, key):
        self.backend.delete(key)
