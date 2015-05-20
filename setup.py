#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

from setuptools import setup, find_packages

from os.path import abspath, dirname, join

# get setup directory abspath
_path = dirname(abspath(__file__))

# get long description
with open(join(_path, 'README.rst')) as f:
    desc = f.read()

keywords = [
    'conf', 'configuration', 'configurable', 'class', 'ini', 'json', 'xml',
    'tools', 'property', 'dynamic', 'reflection', 'reflect', 'runtime'
]

description = 'python class configuration tools useful in python projects.'

setup(
    name='b3j0f.conf',
    version='0.1.2',
    packages=find_packages(exclude=['test.*', '*.test.*']),
    author='b3j0f',
    author_email='jlabejof@yahoo.fr',
    description=description,
    long_description=desc,
    include_package_data=True,
    url='https://github.com/b3j0f/conf/',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    test_suite='b3j0f',
    keywords=keywords
)
