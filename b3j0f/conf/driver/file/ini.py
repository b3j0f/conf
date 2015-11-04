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

__all__ = ['INIConfDriver']

from b3j0f.utils.version import configparser

from .core import FileConfDriver


class INIConfDriver(FileConfDriver):
    """Manage ini resource configuration."""

    def _resource(self, rscpath, logger):

        result = configparser.RawConfigParser()

        try:
            result.read(rscpath)

        except configparser.MissingSectionHeaderError as mshe:
            msg = 'Missing section header in {0}.'.format(rscpath)
            logger.error(
                '{0} {1}: {2}'.format(msg, mshe, mshe.__traceback__)
            )
            raise self.Error(msg).with_traceback(mshe.__traceback__)

        return result

    def _cnames(self, resource, logger):

        return resource.categories()

    def _params(self, resource, cname, logger):

        pnames = resource.options(cname)

        result = [
            (pname, resource.get_option(cname, pname)) for pname in pnames
        ]

        return result

    def _set_conf(self, conf, resource, rscpath, logger):

        for category in conf:

            if not resource.has_section(category.name):
                resource.add_section(category.name)

            for param in category:
                resource.set(category.name, param.name, param.svalue)

        try:
            with open(rscpath, 'wb') as fps:
                resource.write(fps)

        except OSError as ose:
            msg = 'Error while putting resource to {0}'.format(rscpath)
            full_msg = '{0} {1}: {2}'.format(
                msg, ose, ose.__traceback__
            )
            logger.error(full_msg)
            raise self.Error(msg).with_traceback(ose.__traceback__)
