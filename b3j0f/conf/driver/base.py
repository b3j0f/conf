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

"""Module of configuration drivers.

A configuration driver resolve a configuration path with conf resources paths.

A conf path is a configuration path understandable by several drivers.
A resource path is a configuration path understandable only by one type of
driver (and all its sub types of course...).

In order to implement your self drivers, you have to implement those methods:

- rscpaths(path): get resource paths from one configuration path.
- _get_conf(rscpath, logger): get one configuration from one resource path.
- _set_conf(rscpath, logger): put one configuration from one resource path.
"""

__all__ = ['ConfDriver']

from ..model.conf import Configuration
from ..model.cat import Category
from ..model.param import Parameter

from six import reraise

from sys import exc_info


class ConfDriver(object):
    """Base class for managing conf."""

    class Error(Exception):
        """Handle conf driver errors."""

    @staticmethod
    def _log(logger, msg, kind='info'):
        """Private logging function.

        :param Logger logger: logger to use if not None.
        :param str msg: message to log.
        :param str kind: logger method name to use.
        """

        if logger is not None:
            getattr(logger, kind)(msg)

    def _resource(self, rscpath, logger=None):
        """Get configuration resource from resource path.

        :param str rscpath: resource path.
        :param Logger logger: logger to use.
        """

        raise NotImplementedError()

    def _cnames(self, resource, logger=None):
        """Get resource category names.

        :param resource: resource from where get category names.
        :param Logger logger: logger to use.
        :return: resource category names.
        :rtype: list
        """

        raise NotImplementedError()

    def _params(self, resource, cname, logger=None):
        """Get list of (parameter name, parameter value) from a category name
        and a specific configuration resource.

        :param resource: resource from where get parameter names and values.
        :param str cname: related category name.
        :param Logger logger: logger to use.
        :return: list of resource parameter
        :rtype: list
        """

        raise NotImplementedError()

    def _get_conf(self, rscpath, logger=None):
        """Get specific conf from one driver path.

        :param str path: relative path from where driver paths are calculated.
        :param Logger logger: logger to use.
        :raises: ConfDriver if any parsing errors occures.
        """

        result = None

        try:
            resource = self._resource(rscpath=rscpath, logger=logger)

        except Exception as ex:
            msg = 'Error while getting resource from {0}. {1}: {2}.'.format(
                rscpath, ex, exc_info()[2]
            )
            self._log(logger=logger, msg=msg, kind='warning')

        else:
            for cname in self._cnames(resource=resource, logger=logger):

                category = Category(name=cname)

                if result is None:
                    result = Configuration()

                result += category

                for pname, value in self._params(
                        resource=resource, cname=cname, logger=logger
                ):

                    parameter = Parameter(name=pname, svalue=value)

                    category += parameter

        return result

    def rscpaths(self, path, logger=None):
        """Get resource paths related to input configuration path.

        :param str path: configuration path.
        :rtype: list
        """

        raise NotImplementedError()

    def get_conf(self, path, logger=None, conf=None, override=True, error=False):
        """Parse a configuration path with input conf and returns
        parameters by param name.

        :param str path: conf resource path to parse and from get parameters.
        :param Configuration conf: conf to fill with path values and
            conf param names.
        :param Logger logger: logger to use in order to trace
            information/error.
        :param bool override: if True (by default), override self
            configuration.
        :param bool error: if True (default: False), stop to get conf when a
            first error is catched.
        :rtype: Configuration
        """

        result = conf

        pathconf = None

        rscpaths = self.rscpaths(path=path, logger=logger)

        for rscpath in rscpaths:

            try:
                pathconf = self._get_conf(rscpath=rscpath, logger=logger)

            except Exception as ex:
                msg = 'Error while getting configuration from {0}.'.format(
                    rscpath
                )
                full_msg = '{0} {1}: {2}'.format(msg, ex, exc_info()[2])
                self._log(logger=logger, msg=full_msg, kind='warning')
                if error:
                    reraise(ConfDriver.Error, ConfDriver.Error(msg))

            else:
                if pathconf is None:  # do something only if pathconf exists
                    continue

                elif result is None:
                    result = pathconf

                else:
                    result.update(other=pathconf)

        return result

    def set_conf(self, conf, rscpath, logger=None):
        """Set input conf in input path.

        :param Configuration conf: conf to write to path.
        :param str rscpath: specific resource path to use.
        :param Logger logger: used to log info/errors
        """

        try:
            resource = self._resource(rscpath=rscpath, logger=logger)

        except Exception as ex:
            msg = 'Error while getting resource from {0}'.format(rscpath)
            log_msg = '{0} {1}: {2}.'.format(msg, ex, exc_info()[2])
            self._log(logger=logger, msg=log_msg, kind='warning')
            reraise(self.Error, self.Error(msg))

        else:
            self._set_conf(
                conf=conf, resource=resource, rscpath=rscpath, logger=logger
            )

    def _set_conf(self, conf, resource, rscpath, logger=None):
        """Set input conf to input resource.

        :param Configuration conf: conf to write to path.
        :param resource: driver configuration resource.
        :param str rscpath: specific resource path to use.
        :param Logger logger: used to log info/errors
        """

        raise NotImplementedError()
