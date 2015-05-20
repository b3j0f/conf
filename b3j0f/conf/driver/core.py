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

__all__ = ['MetaConfDriver', 'ConfDriver']


from b3j0f.utils.path import lookup, getpath

from b3j0f.conf.params import Configuration, Parameter, Category, ParamList


class MetaConfDriver(type):
    """ConfDriver meta class which register all driver in a global
    set of drivers.
    """

    def __init__(self, name, bases, attrs):

        super(MetaConfDriver, self).__init__(name, bases, attrs)

        # if the class claims to be registered
        if self.__register__:
            # add it among drivers
            ConfDriver._MANAGERS[getpath(self)] = self


class ConfDriver(object):
    """Base class for managing conf.
    """

    """Apply meta class for registering automatically it among global drivers
    if __register__ is True
    """
    __metaclass__ = MetaConfDriver

    """Static param which allows this class to be automatically registered
    among drivers.
    """
    __register__ = False

    CONF_FILE = 'CONF_FILE'

    _MANAGERS = {}  #: Private set of shared driver types.

    def handle(self, conf_path, logger):
        """True iif input conf_path can be handled by self.

        :return: True iif input conf_path can be handled by self.
        :rtype: bool
        """

        conf_resource = self._get_conf_resource(
            conf_path=conf_path, logger=logger)

        result = conf_resource is not None

        return result

    def exists(self, conf_path):
        """True if conf_path exist related to this driver behaviour.
        """

        raise NotImplementedError()

    def get_conf(
        self, conf_path, logger, conf=None, override=True
    ):
        """Parse a configuration_files with input conf and returns
        parameters and errors by param name.

        :param str conf_path: conf file to parse and from get parameters.
        :param Configuration conf: conf to fill with conf_path values and
            conf param names.
        :param Logger logger: logger to use in order to trace
            information/error.
        :param bool override: if True (by default), override self
            configuration.
        """

        conf_resource = None

        result = None
        # ensure conf_path exists and is not empty.
        if self.exists(conf_path):
            try:
                # first, read conf file
                conf_resource = self._get_conf_resource(
                    conf_path=conf_path,
                    logger=logger
                )

            except Exception as e:
                # if an error occured, log it
                logger.error(
                    'Impossible to parse conf_path {0} with {1}: {2}'.format(
                        conf_path,
                        type(self),
                        e
                    )
                )

            else:  # else process conf file
                if conf_resource is None:
                    return result

                result = Configuration() if conf is None else conf

                categories = self._get_categories(
                    conf_resource=conf_resource,
                    logger=logger
                )

                for category_name in categories:
                    # do something only for referenced categories
                    if category_name in result:
                        category = result.setdefault(
                            category_name,
                            Category(category_name)
                        )

                        if isinstance(category, Category):
                            parameters = self._get_parameters(
                                conf_resource=conf_resource,
                                category=category,
                                logger=logger
                            )

                            for name in parameters:
                                # if param name exists in conf
                                if name in category:
                                    # copy parameter
                                    param = category[name].copy()

                                # else create not local parameter
                                else:
                                    param = Parameter(name, local=False)

                                param = category.setdefault(name, param)

                                value = self._get_value(
                                    conf_resource=conf_resource,
                                    category=category,
                                    param=param,
                                    logger=logger
                                )

                                if value not in (None, ''):
                                    if override or param.value in (None, ''):
                                        param.value = value

                        elif isinstance(category, ParamList):
                            paramlist = category
                            category = Category(category_name)
                            result.categories[category_name] = category

                            parameters = self._get_parameters(
                                conf_resource=conf_resource,
                                category=category,
                                logger=logger
                            )

                            for name in parameters:
                                param = Parameter(
                                    name,
                                    local=False,
                                    parser=paramlist.parser,
                                    asitem=category
                                )

                                param = category.setdefault(name, param)

                                value = self._get_value(
                                    conf_resource=conf_resource,
                                    category=category,
                                    param=param,
                                    logger=logger
                                )

                                if value not in (None, ''):
                                    if override or param.value in (None, ''):
                                        param.value = value

        return result

    def set_conf(self, conf_path, conf, logger):
        """Set input conf in input conf_path.

        :param str conf_path: conf file to parse and from get parameters.
        :param Configuration conf: conf to write to conf_path.
        :param Logger logger: used to log info/errors
        """

        result = None
        conf_resource = None

        try:  # get conf_resource
            conf_resource = self._get_conf_resource(
                conf_path=conf_path,
                logger=logger)

        except Exception as e:
            # if an error occured, stop processing
            logger.error(
                'Impossible to parse conf_path {0}: {1}'.format(
                    conf_path, e))
            result = e

        # if conf_path can not be loaded, get default config conf_resource
        if conf_resource is None:
            conf_resource = self._get_conf_resource(logger=logger)

        # iterate on all conf items
        for category in conf:

            # set category
            self._set_category(
                conf_resource=conf_resource, category=category,
                logger=logger)

            # iterate on parameters
            for param in category:

                # set param
                self._set_parameter(
                    conf_resource=conf_resource,
                    category=category,
                    param=param,
                    logger=logger)

        # write conf_resource in conf file
        self._update_conf_resource(
            conf_resource=conf_resource, conf_path=conf_path)

        return result

    @staticmethod
    def get_drivers():
        """Get global defined drivers.
        """

        return set(ConfDriver._MANAGERS.values())

    @staticmethod
    def get_driver(path):
        """Add a conf driver by its path definition.

        :param str path: driver path to add. Must be a full path from a known
            package/module.
        """

        # try to get if from global definition
        result = ConfDriver._MANAGERS.get(path)

        # if not already added
        if result is None:
            # resolve it and add it in global definition
            result = lookup(path)
            ConfDriver._MANAGERS[path] = result

        return result

    def _get_categories(self, conf_resource, logger):
        """Get a list of category names in conf_resource.
        """

        raise NotImplementedError()

    def _get_parameters(self, conf_resource, category, logger):
        """Get a list of param names in conf_resource related to category.
        """

        raise NotImplementedError()

    def _has_category(self, conf_resource, category, logger):
        """True iif input conf_resource contains input category.
        """

        raise NotImplementedError()

    def _has_parameter(self, conf_resource, category, param, logger):
        """True iif input conf_resource has input parameter_name in input
            category.
        """

        raise NotImplementedError()

    def _get_conf_resource(self, logger, conf_path=None):
        """Get config conf_resource.

        :param str conf_path: if not None, the config conf_resource is
            conf_path content.
        :param Logger logger: logger used to log processing information
        :return: empty config conf_resource if conf_path is None, else
            conf_path content.
        """

        raise NotImplementedError()

    def _get_value(self, conf_resource, category, param):
        """Get a param related to input conf_resource, category and param
        """

        raise NotImplementedError()

    def _set_category(self, conf_resource, category, logger):
        """Set category on conf_resource.
        """

        raise NotImplementedError()

    def _set_parameter(self, conf_resource, category, param, logger):
        """Set param on conf_resource.
        """

        raise NotImplementedError()

    def _update_conf_resource(self, conf_resource, conf_path):
        """Write conf_resource into conf_path.
        """

        raise NotImplementedError()
