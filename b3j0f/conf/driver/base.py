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
- _getconf(rscpath, logger): get one configuration from one resource path.
- _setconf(rscpath, logger): put one configuration from one resource path.
"""

__all__ = ['ConfDriver']

from ..model.conf import Configuration
from ..model.cat import Category

from traceback import format_exc

from six import reraise


class ConfDriver(object):
    """Driver dedicated to get/set configuration from relative paths.

    A driver associate a configuration path to

    - a specific configuration resource.
    - specific resource paths.
    """

    class Error(Exception):
        """Handle conf driver errors."""

    def rscpaths(self, path):
        """Get resource paths related to input configuration path.

        :param str path: configuration path.
        :return: resource paths which could be used by the method setconf.
        :rtype: list
        """

        raise NotImplementedError()

    def resource(self):
        """Get a default and empty resource.

        :return: default specific resource.
        """

        raise NotImplementedError()

    def pathresource(self, rscpath=None, logger=None):
        """Returns specific resource.

        :param str rscpath: resource path.
        :param Logger logger: logger to use.
        :param bool error: raise internal error if True (False by default).
        :param bool force: create the resource even if rscpath does not exist.
        :return: specific configuration resource.
        """

        result = None

        try:
            result = self._pathresource(rscpath=rscpath)

        except Exception as ex:
            if logger is not None:
                msg = 'Error while getting resource from {0}.'.format(rscpath)
                full_msg = '{0} {1}: {2}'.format(msg, ex, format_exc())
                logger.error(full_msg)

        return result

    def getconf(self, path, conf=None, logger=None):
        """Parse a configuration path with input conf and returns
        parameters by param name.

        :param str path: conf resource path to parse and from get parameters.
        :param Configuration conf: conf to fill with path values and
            conf param names.
        :param Logger logger: logger to use in order to trace
            information/error.
        :rtype: Configuration
        """

        result = conf

        pathconf = None

        rscpaths = self.rscpaths(path=path)

        for rscpath in rscpaths:

            pathconf = self._getconf(rscpath=rscpath, logger=logger, conf=conf)

            if pathconf is not None:

                if result is None:
                    result = pathconf

                else:
                    result.update(pathconf)

        return result

    def setconf(self, conf, rscpath, logger=None):
        """Set input conf in input path.

        :param Configuration conf: conf to write to path.
        :param str rscpath: specific resource path to use.
        :param Logger logger: used to log info/errors.
        :param bool error: raise catched errors.
        :raises: ConfDriver.Error in case of error and input error.
        """

        resource = self.pathresource(rscpath=rscpath, logger=logger)

        if resource is None:
            resource = self.resource()

        try:
            self._setconf(conf=conf, resource=resource, rscpath=rscpath)

        except Exception as ex:
            if logger is not None:
                msg = 'Error while setting conf to {0}.'.format(rscpath)
                full_msg = '{0} {1}: {2}'.format(msg, ex, format_exc())
                logger.error(full_msg)
                reraise(self.Error, self.Error(msg))

    def _getconf(self, rscpath, logger=None, conf=None):
        """Get specific conf from one driver path.

        :param str rscpath: resource path.
        :param Logger logger: logger to use.
        """

        result = None

        resource = self.pathresource(rscpath=rscpath, logger=logger)

        if resource is not None:

            for cname in self._cnames(resource=resource):

                category = Category(name=cname)

                if result is None:
                    result = Configuration()

                result += category

                for param in self._params(resource=resource, cname=cname):

                    if conf is not None:
                        confparam = None

                        if cname in conf and param.name in conf[cname]:
                            confparam = conf[cname][param.name]

                        else:
                            confparam = conf.param(pname=param.name)

                        if confparam is not None:
                            svalue = param.svalue

                            param.update(confparam)

                            if svalue is not None:
                                param.svalue = svalue
                                param.resolve()

                    category += param

        return result

    def _setconf(self, conf, resource, rscpath):
        """Set input conf to input resource.

        :param Configuration conf: conf to write to path.
        :param resource: driver configuration resource.
        :param str rscpath: specific resource path to use.
        :param Logger logger: used to log info/errors.
        :raises: ConfDriver.Error if input error and an error has been raised.
        """

        raise NotImplementedError()

    def _pathresource(self, rscpath):
        """Method to override in order to get specific conf resource from a
        resource path.

        :param str rscpath: resource path.
        :param Logger logger: logger to use.
        :param bool error: if True (False by default), raise a ConfDriver Error.
        :param bool force: create resource even if rscpath does not exist.
        :return: specific configuration resource.
        """

        raise NotImplementedError()

    def _cnames(self, resource):
        """Get resource category names.

        :param resource: resource from where get category names.
        :param Logger logger: logger to use.
        :return: resource category names.
        :rtype: list
        """

        raise NotImplementedError()

    def _params(self, resource, cname):
        """Get list of category parameters.

        :param resource: resource from where get parameters.
        :param str cname: related category name.
        :param Logger logger: logger to use.
        :return: list of category parameters.
        :rtype: list
        """

        raise NotImplementedError()
