import os

BASE_DIR = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'file_resubmit',
    'tests',
]

MIDDLEWARE_CLASSES = []

SECRET_KEY = '123'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    "file_resubmit": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}
