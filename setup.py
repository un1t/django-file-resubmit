#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2011 Ilya Shalyapin
#
#  django-file-resubmit is free software under terms of the MIT License.
#

import os
from setuptools import setup


readme = open(os.path.join(os.path.dirname(__file__), 'README.markdown')).read()

setup(
    name     = 'django-file-resubmit',
    version  = '0.3',
    packages = ['file_resubmit'],

    requires = ['python (>= 2.5)', 'django (>= 1.3)', 'sorl.thumbnail (>=11.0)'],

    description  = 'Keeps submited files when validation errors occure.',
    long_description = readme,
    author       = 'Ilya Shalyapin',
    author_email = 'ishalyapin@gmail.com',
    url          = 'https://github.com/un1t/django-file-resubmit',
    download_url = 'https://github.com/un1t/django-file-resubmit/tarball/master',
    license      = 'MIT License',
    keywords     = 'django form filefield resubmit',
    classifiers  = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
