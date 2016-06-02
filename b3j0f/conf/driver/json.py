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

"""JSON configuration driver."""

from __future__ import absolute_import

__all__ = ['JSONConfDriver']

try:
    from json import loads, dumps

except ImportError:
    from simplejson import loads, dumps

from six import string_types

from .base import ConfDriver
from ..model.param import Parameter


class JSONConfDriver(ConfDriver):
    """Manage json resource configuration."""

    def rscpaths(self, path):

        return [path]

    def resource(self):

        return {}

    def _pathresource(self, rscpath):

        result = loads(rscpath)

        return result

    def _cnames(self, resource):

        return resource.keys()

    def _params(self, resource, cname):

        params = resource[cname]

        result = [
            Parameter(name=key, svalue=params[key])
                if isinstance(params[key], string_types) else
                    Parameter(name=key, value=params[key])
            for key in params
        ]

        return result

    def _setconf(self, conf, resource, rscpath):

        for category in conf.values():

            cat = resource.setdefault(category.name, {})

            for parameter in category.values():

                cat[parameter.name] = parameter.svalue

        result = dumps(resource)

        return result
