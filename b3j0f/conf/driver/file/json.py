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

__all__ = ['JSONConfDriver']

from builtins import open

try:
    from json import load, dump

except ImportError:
    from simplejson import load, dump

from .core import FileConfDriver

from six import reraise

from sys import exc_info


class JSONConfDriver(FileConfDriver):
    """Manage json resource configuration."""

    def _resource(self, rscpath, logger):

        result = None

        try:
            msg = 'Error while getting resource from {0}.'.format(rscpath)
            with open(rscpath, 'rb') as fpr:

                try:
                    result = load(fpr)

                except ValueError as vex:
                    logger.error('{0} {1}: {2}'.format(msg, vex, exc_info()[2]))
                    reraise(self.Error, self.Error(msg))

        except OSError as oex:
            logger.error('{0} {1}: {2}'.format(msg, oex, exc_info()[2]))
            reraise(self.Error, self.Error(msg))

        return result

    def _cnames(self, resource, logger):

        return resource.keys()

    def _cparams(self, resource, cname, logger):

        params = resource[cname]

        result = [
            (key, params[key]) for key in params
        ]

        return result

    def _set_conf(self, conf, resource, rscpath, logger):

        for category in conf:

            cat = resource.setdefault(category.name, {})

            for parameter in category:

                cat[parameter.name] = parameter.svalue

        msg = 'Error while putting conf in {0}'.format(rscpath)

        try:

            with open(rscpath, 'wb') as fpw:
                try:
                    dump(fpw, resource)

                except ValueError as vex:
                    logger.error('{0} {1}: {2}'.format(msg, vex, exc_info()[2]))
                    reraise(self.Error, self.Error(msg))

        except OSError as oex:
            logger.error('{0} {1}: {2}'.format(msg, oex, exc_info()[2]))
            reraise(self.Error, self.Error(msg))
