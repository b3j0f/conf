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

"""JSON configuration file driver."""

from __future__ import absolute_import

__all__ = ['JSONFileConfDriver']

try:
    from json import load, dump

except ImportError:
    from simplejson import load, dump

from .base import FileConfDriver
from ..json import JSONConfDriver


class JSONFileConfDriver(FileConfDriver, JSONConfDriver):
    """Manage json resource configuration from json file."""

    def _pathresource(self, rscpath):

        result = None

        with open(rscpath, 'r') as fpr:

            result = load(fpr)

        return result

    def _setconf(self, conf, resource, rscpath):

        super(JSONFileConfDriver, self)._setconf(conf, resource, rscpath)

        with open(rscpath, 'w') as fpw:

            dump(resource, fpw)
