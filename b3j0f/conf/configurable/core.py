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

__all__ = ['MetaConfigurable', 'Configurable', 'ConfigurableError']


from logging import Formatter, getLogger, FileHandler, Filter

from os.path import join, sep

from six import string_types

from b3j0f.utils.property import addproperties
from b3j0f.utils.iterable import ensureiterable

from ..model.conf import Configuration
from ..model.cat import Category
from ..model.param import Parameter

from ..driver.base import ConfDriver
from ..driver.file.json import JSONConfDriver
from ..driver.file.ini import INIConfDriver


class MetaConfigurable(type):
    """Meta class for Configurable."""

    def __call__(cls, *args, **kwargs):
        """Get a new instance of input cls class, and if instance.auto_conf or
        instance.reconf_once, then call instance.apply_configuration().
        """

        result = type.__call__(cls, *args, **kwargs)

        if result.auto_conf or result.reconf_once:
            # get configuration
            conf = result.conf

            # add a last category which contains args and kwargs as parameters
            if kwargs:
                init_category = Category(Configurable.INIT_CAT)
                for name in kwargs:
                    param = Parameter(name=name, value=kwargs[name])
                    init_category += param
                conf += init_category

            # apply configuration
            result.apply_configuration(conf=conf)

        return result


class ConfigurableError(Exception):
    """Handle Configurable errors."""


def _updatedrivers(self, *_):
    """Ensure drivers is a list of drivers."""

    drivers = self._drivers

    drivers = ensureiterable(drivers)

    self._drivers = [
        driver if isinstance(driver, ConfDriver) else driver()
        for driver in drivers
    ]


def _updatelogger(self, **_):
    """Renew self logger."""
    self._logger = self.newlogger()


@addproperties(
    names=[
        'log_debug_format', 'log_info_format', 'log_warning_format',
        'log_error_format', 'log_critical_format', 'log_name', 'log_path'
    ], afset=_updatelogger
)
@addproperties(names=['auto_conf', 'reconf_once', 'drivers', 'logger'])
@addproperties(names=['drivers'], afset=_updatedrivers)
class Configurable(object):
    """Manage class conf synchronisation with conf resources.

    According to critical parameter updates, this class uses a dirty state.

    In such situation, it is possible to go back to a stable state in calling
    the method `restart`. Without failure, the dirty status is canceled."""

    #: ensure to applyconfiguration after instanciation of the configurable.
    __metaclass__ = MetaConfigurable

    # default drivers which are json and ini.
    DEFAULT_DRIVERS = [JSONConfDriver(), INIConfDriver()]

    INIT_CAT = 'init_cat'  #: initialization category.

    CONF_PATH = 'b3j0fconf-configurable.conf'  #: default conf path.

    #: configurable storing attribute in configured objects.
    STORE_ATTR = '__configurable__'

    CONF = 'CONFIGURATION'  #: configuration attribute name.
    LOG = 'LOG'  #: log attribute name.

    AUTO_CONF = 'auto_conf'  #: auto_conf attribute name.
    RECONF_ONCE = 'reconf_once'  #: reconf_once attribute name.
    CONF_PATHS = 'paths'  #: paths attribute name.
    DRIVERS = 'drivers'  #: drivers attribute name.

    LOG_NAME = 'log_name'  #: logger name property name.
    LOG_LVL = 'log_lvl'  #: logging level property name.
    LOG_PATH = 'log_path'  #: logging path property name.
    LOG_DEBUG_FORMAT = 'log_debug_format'  #: debug log format property name.
    LOG_INFO_FORMAT = 'log_info_format'  #: info log format property name.
    LOG_WARNING_FORMAT = 'log_warning_format'  #: warn log format property name
    LOG_ERROR_FORMAT = 'log_error_format'  #: error log format property name.
    LOG_CRITICAL_FORMAT = 'log_critical_format'  #: crit log format property.

    DEFAULT_AUTO_CONF = True  #: default auto conf.
    DEFAULT_RECONF_ONCE = False  #: default reconf once.

    # log messages format.
    #: debug message format.
    DEBUG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] \
[%(process)d] [%(thread)d] [%(pathname)s] [%(lineno)d] %(message)s"
    #: info message format.
    INFO_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    WARNING_FORMAT = INFO_FORMAT  #: warning message format.
    ERROR_FORMAT = WARNING_FORMAT  #: error message format.
    CRITICAL_FORMAT = ERROR_FORMAT  #: critical message format.

    def __init__(
            self,
            conf=None, usecls_conf=True, unified_conf=True,
            to_configure=None, store=False,
            paths=None, drivers=DEFAULT_DRIVERS,
            auto_conf=DEFAULT_AUTO_CONF, reconf_once=DEFAULT_RECONF_ONCE,
            log_lvl='INFO', log_name=None, log_path='.',
            log_info_format=INFO_FORMAT,
            log_debug_format=DEBUG_FORMAT, log_warning_format=WARNING_FORMAT,
            log_error_format=ERROR_FORMAT, log_critical_format=CRITICAL_FORMAT,
            *args, **kwargs
    ):
        """
        :param Configuration conf: conf to use at instance level.
        :param bool usecls_conf: if True (default) add conf to cls conf.
        :param bool unified_conf: if True (default) enrich instance conf with
            unified cls conf (all cls parameters will be copied in instance
            conf).
        :param to_configure: object(s) to reconfigure. Such object may
            implement the methods configure apply_configuration and configure.
        :type to_configure: list or instance.
        :param bool store: if True (default False) and to_configure is given,
            store this instance into to_configure instance with the attribute
            ``STORE_ATTR``.
        :param paths: paths to parse.
        :type paths: Iterable or str
        :param bool auto_conf: True (default) force auto conf as soon as param
            change.
        :param bool reconf_once: True (default) force auto conf reconf_once as
            soon as param change.
        :param str log_lvl: logging level. Default is INFO.
        :param str log_name: logger name. Default is configurable class lower
            name.
        :param str log_path: logging file path. Default is current directory.
        :param str log_info_format: info logging level format.
        :param str log_debug_format: debug logging level format.
        :param str log_warning_format: warning logging level format.
        :param str log_error_format: error logging level format.
        :param str log_critical_format: critical logging level format.
        """

        super(Configurable, self).__init__(*args, **kwargs)

        # init protected attributes
        self._auto_conf = auto_conf
        self._reconf_once = reconf_once
        self._paths = None
        self._drivers = None
        self._paths = None
        self._to_configure = None
        self._conf = None

        self.store = store

        self.usecls_conf = usecls_conf
        self.unified_conf = unified_conf
        self.conf = conf

        self.to_configure = to_configure

        self.auto_conf = auto_conf
        self.reconf_once = reconf_once

        # set conf files
        self._init_paths(paths)

        # set drivers
        self.drivers = drivers

        # set logging properties
        self._log_lvl = log_lvl
        self._log_path = log_path
        self._log_name = log_name if log_name else type(self).__name__.lower()
        self._log_debug_format = log_debug_format
        self._log_info_format = log_info_format
        self._log_warning_format = log_warning_format
        self._log_error_format = log_error_format
        self._log_critical_format = log_critical_format

        self._logger = self.newlogger()

    def newlogger(self):
        """Get a new logger related to self properties."""

        result = getLogger(self.log_name)
        result.setLevel(self.log_lvl)

        def sethandler(logger, lvl, path, _format):
            """Set right handler related to input lvl, path and format.

            :param Logger logger: logger on which add an handler.
            :param str lvl: logging level.
            :param str path: file path.
            :param str _format: logging message format.
            """

            class _Filter(Filter):
                """Ensure message will be given for specific lvl"""

                def filter(self, record):

                    return record.levelname == lvl

            # get the rights formatter and filter to set on a file handler
            handler = FileHandler(path, mode='a+')
            handler.addFilter(_Filter())
            handler.setLevel(lvl)
            formatter = Formatter(_format)
            handler.setFormatter(formatter)

            # if an old handler exist, remove it from logger
            if hasattr(logger, lvl):
                old_handler = getattr(logger, lvl)
                logger.removeHandler(old_handler)

            logger.addHandler(handler)
            setattr(logger, lvl, handler)

        filename = self.log_name.replace('.', sep)
        path = join(self.log_path, '{0}.log'.format(filename))

        sethandler(result, 'DEBUG', path, self.log_debug_format)
        sethandler(result, 'INFO', path, self.log_info_format)
        sethandler(result, 'WARNING', path, self.log_warning_format)
        sethandler(result, 'ERROR', path, self.log_error_format)
        sethandler(result, 'CRITICAL', path, self.log_critical_format)

        return result

    @property
    def conf(self):
        """Get conf with parsers and self property values.

        :rtype: Configuration.
        """

        result = self._conf

        if result is None:

            if self.usecls_conf:  # use cls conf if specified
                result = self._clsconf()

            else:
                result = Configuration()

        return self._conf

    @conf.setter
    def conf(self, value):
        """Change of configuration.

        :param Configuration value: new configuration to use.
        """

        # get cls conf if specified
        self._conf = self._clsconf() if self.usecls_conf else Configuration()

        if value is not None:

            if self.unified_conf:

                for cname in value:
                    category = value[cname]

                    self._conf.add_unified_category(category)

            else:
                self._conf += value

    def _clsconf(self):
        """Method to override in order to specify class configuration."""

        result = Configuration(
            Category(
                Configurable.CONF,
                Parameter(name=Configurable.AUTO_CONF, vtype=bool),
                Parameter(name=Configurable.DRIVERS, vtype=tuple),
                Parameter(name=Configurable.RECONF_ONCE, vtype=bool),
                Parameter(name=Configurable.CONF_PATHS, vtype=tuple)
            ),
            Category(
                Configurable.LOG,
                Parameter(name=Configurable.LOG_NAME),
                Parameter(name=Configurable.LOG_PATH),
                Parameter(name=Configurable.LOG_LVL),
                Parameter(name=Configurable.LOG_DEBUG_FORMAT),
                Parameter(name=Configurable.LOG_INFO_FORMAT),
                Parameter(name=Configurable.LOG_WARNING_FORMAT),
                Parameter(name=Configurable.LOG_ERROR_FORMAT),
                Parameter(name=Configurable.LOG_CRITICAL_FORMAT)
            )
        )

        return result

    @property
    def to_configure(self):
        """Get resources to configure.

        :rtype: list
        """

        return self._to_configure

    @to_configure.setter
    def to_configure(self, value):
        """Change of resource(s) to configure.

        If value is literally a list (without inheritance), this configurable
        will be associated to all its items.

        :param value: new object(s) to configure by default. List of objects to
            configure is used only if value is a literally list (not a
            subclass of list).
        :type value: list or object.
        """

        if value is None:

            value = [self]

        elif type(value) is not list:

            value = [value]

        if self._to_configure is not None:

            for to_configure in self._to_configure:
                if to_configure not in value:
                    try:  # remove old configurable storing
                        delattr(to_configure, Configurable.STORE_ATTR)

                    except AttributeError:
                        pass

        if self.store:

            for to_configure in value:

                try:
                    setattr(to_configure, Configurable.STORE_ATTR, self)

                except AttributeError:
                    self.logger.warning(
                        'Impossible to store configurable in {0}.'.format(
                            to_configure
                        )
                    )

        # add self to value in order to synchronize this configurable with
        # to_configure objects
        if self not in value:
            value.append(self)

        self._to_configure = value

    @property
    def log_lvl(self):
        """Get this logger lvl.

        :return: self logger lvl.
        :rtype: str
        """

        return self._log_lvl

    @log_lvl.setter
    def log_lvl(self, value):
        """Change of logging level.

        :param str value: new log_lvl to set up.
        """

        self._log_lvl = value

        self._logger.setLevel(self._log_lvl)

    @property
    def log_name(self):
        """Get this logger name.

        :return: self logger name.
        :rtype: str
        """

        return self._log_name

    @log_name.setter
    def log_name(self, value):
        """Change of logging name.

        :param str value: new log_name to set up.
        """

        self._log_name = value

        self._logger.setLevel(self._log_name)

    @property
    def paths(self):
        """Get all type conf files and user files.

        :return: self conf files
        :rtype: tuple
        """

        result = self._paths

        return result

    @paths.setter
    def paths(self, value):
        """Change of paths in adding it in watching list."""

        self._paths = tuple(value)

    def apply_configuration(
            self, conf=None, paths=None, drivers=None, logger=None,
            to_configure=None, _locals=None, _globals=None
    ):
        """Apply conf on a destination in those phases:

        1. identify the right driver to use with paths to parse.
        2. for all paths, get conf which matches input conf.
        3. apply parsing rules on path parameters.
        4. fill input conf with resolved parameters.
        5. apply filled conf on to_configure.

        :param Configuration conf: conf from where get conf
        :param paths: conf files to parse. If paths is a str, it is
            automatically putted into a list.
        :type paths: list of str
        :param to_configure: object to configure. self by default.
        :param dict _locals: local variable to use for local python expression
            resolution.
        :param dict _globals: global variable to use for local python
            expression resolution.
        """

        if conf is None:
            conf = self.conf

        if to_configure is None:  # init to_configure
            to_configure = self.to_configure

        if type(to_configure) is list:

            for to_conf in to_configure:
                self.apply_configuration(
                    conf=conf, paths=paths, drivers=drivers,
                    logger=logger, to_configure=to_conf
                )

        else:
            # get conf from drivers and paths
            conf = self.get_conf(
                conf=conf, paths=paths, logger=logger, drivers=drivers
            )
            # resolve all values
            conf.resolve(configurable=self, _globals=_globals, _locals=_locals)
            # configure resolved configuration
            self.configure(conf=conf, to_configure=to_configure)

    def get_conf(self, conf=None, paths=None, drivers=None, logger=None):
        """Get a configuration from paths.

        :param Configuration conf: conf to update. Default this conf.
        :param str(s) paths: list of conf files. Default this paths.
        :param Logger logger: logger to use for logging info/error messages.
            Default self logger.
        :param list drivers: ConfDriver to use. Default this drivers.
        """

        result = None

        # start to initialize input params
        if logger is None:
            logger = self.logger

        if conf is None:
            conf = self.conf

        if paths is None:
            paths = self._paths

        if isinstance(paths, string_types):
            paths = [paths]

        if drivers is None:
            drivers = self.drivers

        # iterate on all paths
        for path in paths:

            for driver in drivers:

                result = driver.get_conf(
                    path=path, conf=conf, logger=logger
                )

                if result:
                    break

            else:
                # if no conf found, display a warning log message
                logger.warning(
                    'No driver found among {0} for processing {1}'.format(
                        drivers, path
                    )
                )

        return result

    def set_conf(self, driver, rscpath, conf=None, logger=None):
        """Set params on input path.

        :param ConfDriver driver: specific driver to use.
        :param str rscpath: specific driver resource path to use.
        :param Configuration conf: configuration to save in resource. Default
            this conf.
        :param Logger logger: logger to use to set params. Default this logger.
        """

        if conf is None:
            conf = self.conf

        if logger is None:
            logger = self.logger

        driver.set_conf(conf=conf, rscpath=rscpath, logger=logger)

    def configure(self, conf=None, logger=None, to_configure=None):
        """Update self properties with input params only if:

        - self.configure is True
        - self.auto_conf is True
        - param conf 'configure' is True
        - param conf 'auto_conf' is True

        This method may not be overriden. see _configure instead

        :param Configuration conf: configuration model to configure. Default is
            this conf.
        :param to_configure: object to configure. self if equals None.
        :raises: Parameter.Error for any raised exception.
        """

        if conf is None:
            conf = self.conf

        if to_configure is None:  # init to_configure
            to_configure = self.to_configure

        if type(to_configure) is list:
            for to_conf in to_configure:
                self.configure(conf=conf, logger=logger, to_configure=to_conf)

        else:
            if logger is None:
                logger = self.logger

            unified_conf = conf.unify()

            values = unified_conf[Configuration.VALUES]

            # set configure
            reconf_once = values.get(Configurable.RECONF_ONCE)

            if reconf_once is not None:
                self.reconf_once = reconf_once.value

            # set auto_conf
            auto_conf_parameter = values.get(Configurable.AUTO_CONF)

            if auto_conf_parameter is not None:
                self.auto_conf = auto_conf_parameter.value

            if self.reconf_once or self.auto_conf:
                self._configure(
                    unified_conf=unified_conf, logger=logger,
                    to_configure=to_configure
                )
                # when conf succeed, deactive reconf_once
                self.reconf_once = False

    def _is_local(self, to_configure, name):
        """True iif input name parameter can be handled by to_configure."""

        return hasattr(to_configure, name)

    def _configure(self, unified_conf=None, logger=None, to_configure=None):
        """Configure this class with input conf only if auto_conf or
        configure is true.

        This method should be overriden for specific conf

        :param Configuration unified_conf: unified configuration. Default is
            self.conf.unify().
        :param bool configure: if True, force full self conf
        :param to_configure: object to configure. self if equals None.
        """

        if unified_conf is None:
            unified_conf = self.conf.unify()

        if to_configure is None:  # init to_configure
            to_configure = self._to_configure

        if type(to_configure) is list:
            for to_conf in to_configure:
                self._configure(
                    unified_conf=unified_conf, logger=logger,
                    to_configure=to_conf
                )

        else:

            values = [p for p in unified_conf[Configuration.VALUES]]
            foreigns = [p for p in unified_conf[Configuration.FOREIGNS]]

            for parameter in values + foreigns:
                name = parameter.name
                # if parameter is local, to_configure must a related name
                if self._is_local(to_configure, name):
                    if hasattr(to_configure, name):

                        pvalue = parameter.value
                        setattr(to_configure, name, pvalue)

                else:  # else log the warning
                    message = 'Param {0} does not exist in {1}.'
                    self.logger.warning(message.format(name, to_configure))

    def _init_paths(self, paths):

        if paths is None:
            self.paths = self._get_paths()

        else:
            self.paths = paths

    def _get_paths(self):

        result = [Configurable.CONF_PATH]

        return result
