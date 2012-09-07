#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2011 Ilya Shalyapin
#
#  django-file-resubmit is free software under terms of the MIT License.
#

import os
from setuptools import setup, find_packages

setup(
    name     = 'django-file-resubmit',
    version  = '0.4',
    packages = find_packages(),

    requires = ['python (>= 2.5)', 'django (>= 1.2)'],

    description  = 'Keeps submited files when validation errors occure.',
    long_description = open('README.markdown').read(),
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
