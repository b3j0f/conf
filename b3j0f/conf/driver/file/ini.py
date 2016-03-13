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

"""Ini configuration file driver."""

__all__ = ['INIFileConfDriver']

from six.moves.configparser import RawConfigParser

from .base import FileConfDriver
from ...model.param import Parameter


class INIFileConfDriver(FileConfDriver):
    """Manage ini resource configuration."""

    def resource(self):

        return RawConfigParser()

    def _pathresource(self, rscpath):

        result = RawConfigParser()

        result.read(rscpath)

        if not result.sections():
            result = None

        return result

    def _cnames(self, resource):

        return resource.sections()

    def _params(self, resource, cname):

        return list(
            Parameter(item[0], svalue=item[1]) for item in resource.items(cname)
        )

    def _setconf(self, conf, resource, rscpath):

        for category in conf.values():

            if not resource.has_section(category.name):
                resource.add_section(category.name)

            for param in category.values():
                resource.set(category.name, param.name, param.svalue)

        with open(rscpath, 'w') as fps:
            resource.write(fps)
