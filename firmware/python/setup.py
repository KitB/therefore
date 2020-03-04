#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

packages = [
    'therefore',
]

package_data = {
}

requires = [
]

classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
]

setup(
    name='therefore-firmware',
    version='0.0.1', # TODO: check this
    description='',
    long_description=readme,
    packages=packages,
    package_data=package_data,
    install_requires=requires,
    author='Kit Barnes',
    author_email='k.barnes@mhnltd.co.uk',
    url='', # TODO: input here
    license='MIT',
    classifiers=classifiers,
)
