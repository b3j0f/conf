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

__all__ = ['MetaConfigurable', 'Configurable']

from six import string_types

from b3j0f.annotation import PrivateCallInterceptor

from ..model.conf import Configuration
from ..model.cat import Category
from ..model.param import Parameter
from ..driver.file.json import JSONConfDriver
from ..driver.file.ini import INIConfDriver


class MetaConfigurable(type):
    """Meta class for Configurable."""

    INIT_CAT = 'init_cat'  #: initialization category.

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
                init_category = Category(MetaConfigurable.INIT_CAT)
                for name in kwargs:
                    param = Parameter(name=name, value=kwargs[name])
                    init_category += param
                conf += init_category

            # apply configuration
            result.apply_configuration(conf=conf)

        return result


class Configurable(PrivateCallInterceptor):
    """Manage class conf synchronisation with conf resources.

    According to critical parameter updates, this class uses a dirty state.

    In such situation, it is possible to go back to a stable state in calling
    the method `restart`. Without failure, the dirty status is canceled."""

    #: ensure to applyconfiguration after instanciation of the configurable.
    __metaclass__ = MetaConfigurable

    # default drivers which are json and ini.
    DEFAULT_DRIVERS = (JSONConfDriver(), INIConfDriver())

    CONF_PATHS = ('b3j0fconf-configurable.conf', )  #: default conf path.

    CATEGORY = 'CONFIGURATION'  #: configuration category name.

    CONF_PATHS = 'paths'  #: paths attribute name.
    DRIVERS = 'drivers'  #: drivers attribute name.
    INHERITEDCONF = 'inheritedconf'  #: usecls conf attribute name.
    STORE = 'store'  #: store attribute name.

    DEFAULT_INHERITEDCONF = True  #: default inheritedconf value.
    DEFAULT_STORE = True  #: default store value.

    def __init__(
            self,
            conf=None, inheritedconf=DEFAULT_INHERITEDCONF,
            store=DEFAULT_STORE, paths=None, drivers=DEFAULT_DRIVERS,
            *args, **kwargs
    ):
        """
        :param Configuration conf: conf to use at instance level.
        :param bool inheritedconf: if True (default) add conf and paths to cls
            conf and paths.
        :param targets: object(s) to reconfigure. Such object may
            implement the methods configure apply_configuration and configure.
        :type targets: list or instance.
        :param bool store: if True (default) and targets is given,
            store this instance into targets instance with the attribute
            ``STORE_ATTR``.
        :param paths: paths to parse.
        :type paths: Iterable or str
        """

        super(Configurable, self).__init__(*args, **kwargs)

        # init protected attributes
        self._paths = None
        self._conf = None

        # init public attributes
        self.store = store

        self.inheritedconf = inheritedconf
        self.conf = conf
        self.drivers = drivers
        self.conf = conf
        self.paths = paths

    def _interception(self, jointpoint):

        targets = jointpoint.ctx

        self.apply_configuration(targets=targets)

        return jointpoint.proceed()

    @property
    def conf(self):
        """Get conf with parsers and self property values.

        :rtype: Configuration.
        """

        return self._conf

    @conf.setter
    def conf(self, value):
        """Change of configuration.

        :param Configuration value: new configuration to use.
        """

        if value is None:
            value = Configuration()

        if self.inheritedconf:
            self._conf = self.clsconf()
            self._conf += value

        else:
            self._conf = value

    def clsconf(self):
        """Method to override in order to specify class configuration."""

        result = Configuration(
            Category(
                Configurable.CATEGORY,
                Parameter(name=Configurable.DRIVERS, vtype=tuple),
                Parameter(name=Configurable.CONF_PATHS, vtype=tuple),
                Parameter(name=Configurable.INHERITEDCONF, vtype=bool),
                Parameter(name=Configurable.STORE, vtype=bool)
            )
        )

        return result

    @property
    def paths(self):
        """Get all type conf files and user files.

        :return: self conf files
        :rtype: tuple
        """

        result = tuple(self._paths)

        return result

    @paths.setter
    def paths(self, value):
        """Change of paths in adding it in watching list."""

        if value is None:
            value = ()

        elif isinstance(value, string_types):
            value = (value, )

        if self.inheritedconf:
            self._paths = self.clspaths() + tuple(value)

        else:
            self._paths = tuple(value)

    def clspaths(self):
        """Get class paths."""

        return tuple(self.CONF_PATHS)

    def apply_configuration(
            self, conf=None, paths=None, drivers=None, logger=None,
            targets=None, _locals=None, _globals=None
    ):
        """Apply conf on a destination in those phases:

        1. identify the right driver to use with paths to parse.
        2. for all paths, get conf which matches input conf.
        3. apply parsing rules on path parameters.
        4. fill input conf with resolved parameters.
        5. apply filled conf on targets.

        :param Configuration conf: conf from where get conf
        :param paths: conf files to parse. If paths is a str, it is
            automatically putted into a list.
        :type paths: list of str
        :param targets: object to configure. self by default.
        :param dict _locals: local variable to use for local python expression
            resolution.
        :param dict _globals: global variable to use for local python
            expression resolution.
        """

        if conf is None:
            conf = self.conf

        if targets is None:  # init targets
            targets = self.targets

        if type(targets) is tuple:

            for target in targets:
                self.apply_configuration(
                    conf=conf, paths=paths, drivers=drivers,
                    logger=logger, targets=target,
                    _locals=_locals, _globals=_globals
                )

        else:
            # get conf from drivers and paths
            conf = self.get_conf(
                conf=conf, paths=paths, logger=logger, drivers=drivers
            )
            # resolve all values
            conf.resolve(configurable=self, _globals=_globals, _locals=_locals)
            # configure resolved configuration
            self.configure(conf=conf, targets=targets)

    def get_conf(self, conf=None, paths=None, drivers=None, logger=None):
        """Get a configuration from paths.

        :param Configuration conf: conf to update. Default this conf.
        :param str(s) paths: list of conf files. Default this paths.
        :param Logger logger: logger to use for logging info/error messages.
        :param list drivers: ConfDriver to use. Default this drivers.
        """

        result = None

        # start to initialize input params
        if conf is None:
            conf = self.conf

        if paths is None:
            paths = self.paths

        if isinstance(paths, string_types):
            paths = [paths]

        if drivers is None:
            drivers = self.drivers

        # iterate on all paths
        for path in paths:

            for driver in drivers:  # find the best driver

                result = driver.get_conf(
                    path=path, conf=conf, logger=logger
                )

                if result:
                    break

            else:
                # if no conf found, display a warning log message
                if logger is not None:
                    logger.warning(
                        'No driver found among {0} for processing {1}'.format(
                            drivers, path
                        )
                    )

        return result

    def configure(self, conf=None, logger=None, targets=None):
        """Update self properties with input params only if:

        - self.configure is True
        - self.auto_conf is True
        - param conf 'configure' is True
        - param conf 'auto_conf' is True

        This method may not be overriden. see _configure instead

        :param Configuration conf: configuration model to configure. Default is
            this conf.
        :param targets: object to configure. self if equals None.
        :raises: Parameter.Error for any raised exception.
        """

        if conf is None:
            conf = self.conf

        if targets is None:  # init targets
            targets = self.targets

        if type(targets) is tuple:

            for target in targets:

                self.configure(conf=conf, logger=logger, targets=target)

        else:
            unified_conf = conf.unify()

            self._configure(
                unified_conf=unified_conf, logger=logger,
                targets=targets
            )

    def _configure(self, unified_conf=None, logger=None, targets=None):
        """Configure this class with input conf only if auto_conf or
        configure is true.

        This method should be overriden for specific conf

        :param Configuration unified_conf: unified configuration. Default is
            self.conf.unify().
        :param bool configure: if True, force full self conf
        :param targets: object to configure. self if equals None.
        """

        if unified_conf is None:
            unified_conf = self.conf.unify()

        if targets is None:  # init targets
            targets = self.targets

        if type(targets) is tuple:

            for target in targets:

                self._configure(
                    unified_conf=unified_conf, logger=logger,
                    targets=target
                )

            self._configure(
                unified_conf=unified_conf, logger=logger, targets=self
            )

        else:
            values = [p for p in unified_conf[Configuration.VALUES]]
            foreigns = [p for p in unified_conf[Configuration.FOREIGNS]]

            for parameter in values + foreigns:
                name = parameter.name

                pvalue = parameter.value
                setattr(targets, name, pvalue)
