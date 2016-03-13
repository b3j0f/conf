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

"""Specification of the class Configurable."""

__all__ = ['Configurable']

from six import string_types
from six.moves import reload_module

from inspect import getargspec, isclass, isroutine

from traceback import format_exc

from b3j0f.utils.path import lookup
from b3j0f.utils.version import getcallargs, PY2
from b3j0f.annotation import PrivateInterceptor, Annotation

from ..model.conf import Configuration, configuration
from ..model.cat import Category, category
from ..model.param import Parameter
from ..driver.file.json import JSONFileConfDriver
from ..driver.file.ini import INIFileConfDriver
from ..driver.file.xml import XMLFileConfDriver
from ..parser.resolver.core import (
    DEFAULT_SAFE, DEFAULT_SCOPE, DEFAULT_BESTEFFORT
)


class Configurable(PrivateInterceptor):
    """Handle object configuration from configuration resources such as files.

    Based on a configuration model and configuration drivers, it is able to:

    - be used such as a decorator (see the b3j0f.annotation.Annotation). resources to configure are accessible from the
        ``targets`` property.
    - inject configuration parameters at call time (for function/method calls).
    - preload required modules.
    - be used with several objects.

    Usage :

    .. code-block:: python

        from b3j0f.conf import category
        from b3j0f.conf import Configurable
        from b3j0f.conf getconfigurables, applyconfiguration

        # class configuration
        @Configurable(conf=category('land', Parameter('country', value='fr')))
        class World(object):
            pass

        world = World()
        assert world.country == 'fr'

        # reuse the configuration on several objects
        land = getconfigurables(world)[0]

        @land
        class World2(object):
            pass

        assert World2().country == 'fr'

        land.conf['land']['country'].value = 'en'

        # update all configuration on an object
        applyconfiguration([world])

        assert world.country == 'en'

        # inject configuration in the constructor and on object
        class World3(object):
            def __init__(self, country=None):
                self.safecountry = country

        world3 = World3()
        land(world3)

        assert world3.country == 'en'
        assert world3.safecountry = 'en'

        # inject configuration in function parameters
        @land
        def getcountry(country=None):
            print(country)
            return country

        assert getcountry() == 'en'
    """

    CATEGORY = 'CONFIGURABLE'  #: configuration category name.

    CONF = 'conf'  #: self configuration attribute name.
    CONFPATHS = 'paths'  #: paths attribute name.
    DRIVERS = 'drivers'  #: drivers attribute name.
    INHERITEDCONF = 'inheritedconf'  #: usecls conf attribute name.
    FOREIGNS = 'foreigns'  #: not specified params setting attribute name.
    AUTOCONF = 'autoconf'  #: auto conf attribute name.
    SAFE = 'safe'  #: safe attribute name.
    SCOPE = 'scope'  #: scope attribute name.
    BESTEFFORT = 'besteffort'  #: best effort attribute name.
    MODULES = 'modules'  #: modules attribute name.
    CALLPARAMS = 'callparams'  #: call params attribute name.

    DEFAULT_CONFPATHS = ('b3j0fconf-configurable.conf', )  #: default conf path.
    DEFAULT_INHERITEDCONF = True  #: default inheritedconf value.
    DEFAULT_FOREIGNS = True  #: default value for setting not specified params.
    # default drivers which are json and ini.
    DEFAULT_DRIVERS = (
        JSONFileConfDriver(), INIFileConfDriver(), XMLFileConfDriver()
    )
    DEFAULT_AUTOCONF = True  #: default value for auto configuration.
    DEFAULT_CALLPARAMS = True  #: default value for callparams.
    DEFAULT_MODULES = None  #: default value for modules.
    DEFAULT_SAFE = DEFAULT_SAFE  #: default value for safe.
    DEFAULT_SCOPE = DEFAULT_SCOPE  #: default value for scope.
    DEFAULT_BESTEFFORT = DEFAULT_BESTEFFORT  #: default value for besteffort.

    SUB_CONF_PREFIX = ':'  #: sub conf prefix.

    def __init__(
            self,
            conf=None, inheritedconf=DEFAULT_INHERITEDCONF, paths=None,
            drivers=DEFAULT_DRIVERS, foreigns=DEFAULT_FOREIGNS,
            autoconf=DEFAULT_AUTOCONF, targets=None, safe=DEFAULT_SAFE,
            scope=DEFAULT_SCOPE, besteffort=DEFAULT_BESTEFFORT,
            modules=DEFAULT_MODULES, callparams=DEFAULT_CALLPARAMS, logger=None,
            *args, **kwargs
    ):
        """
        :param Configuration conf: conf to use at instance level.
        :param bool inheritedconf: if True (default) add conf and paths to cls
            conf and paths.
        :param targets: object(s) to reconfigure. Such object may
            implement the methods configure applyconfiguration and configure.
        :type targets: list or instance.
        :param paths: paths to parse.
        :type paths: Iterable or str
        :param bool foreigns: if True (default), set parameters not specified by
            this conf but given by conf resources.
        :param ConfDriver(s) drivers: list of drivers to use. Default
            Configurable.DEFAULT_DRIVERS.
        :param list targets: objects to configure.
        :param bool autoconf: if autoconf, configurate this `targets`
            objects as soon as possible. (at targets instanciation or after
            updating this paths/conf/targets).
        :param bool safe: if True (default), expression parser are used in a
            safe context to resolve python object. For example, if safe,
            builtins function such as `open` are not resolvable.
        :param dict scope: expression resolver scope.
        :param bool besteffort: expression resolver best effort flag.
        :param list modules: required modules.
        :param bool callparams: if True (default), use parameters in the
            configured callable function.
        :param bool autoresolve: if True (default), call auto resolve on
            retrieved configurations.
        :param Logger logger: this logger."""

        super(Configurable, self).__init__(*args, **kwargs)

        # init protected attributes
        self._paths = None
        self._conf = None
        self._targets = set()
        self._modules = []

        # init public attributes

        # dirty hack: falsify autoconf in order to avoid auto applyconfiguration
        self.autoconf = False

        self.inheritedconf = inheritedconf
        self.drivers = drivers
        self.foreigns = foreigns
        self.targets = set() if targets is None else targets
        self.conf = conf
        self.paths = paths
        self.safe = safe
        self.scope = scope
        self.besteffort = besteffort
        self.modules = modules
        self.callparams = callparams
        self.logger = logger

        self.autoconf = autoconf  # end of dirty hack

        if self.autoconf:
            self.applyconfiguration()

    def _interception(self, joinpoint):

        target = joinpoint.target

        args, kwargs = joinpoint.args, joinpoint.kwargs

        if self.callparams:

            args, kwargs = self.getcallparams(
                conf=self.conf, target=target, args=list(args), kwargs=kwargs
            )

            joinpoint.args = list(args)
            joinpoint.kwargs = kwargs

        result = joinpoint.proceed()

        if self.autoconf:

            targets = [result]

            cls = joinpoint.ctx if isclass(joinpoint.ctx) else target

            if isclass(cls):

                if target.__name__ == '__init__':  # if target is the method __init__
                    if 'self' in kwargs:
                        targets = [kwargs['self']]

                    else:
                        targets = [args[0]]

                if isinstance(targets[0], cls):

                    self.applyconfiguration(targets=targets)

        return result

    @staticmethod
    def getcallparams(target, conf, args=None, kwargs=None):
        """Get target call parameters.

        :param list args: target call arguments.
        :param dict kwargs: target call keywords.
        :return: args, kwargs
        :rtype: tuple"""

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        params = conf.params.values()

        try:
            argspec = getargspec(target)

        except TypeError as tex:
            argspec = None
            callargs = {}

        else:
            try:
                callargs = getcallargs(target, *args, **kwargs)

            except TypeError as tex:
                if tex.args[0].endswith('\'self\''):
                    args = [None]

                callargs = getcallargs(target, *args, **kwargs)

                args = []

        for param in params:

            pname = param.name

            if argspec and callargs.get(pname) is None and pname in argspec.args:

                kwargs[pname] = param.value

        return args, kwargs

    @property
    def modules(self):
        """Get this required modules."""

        return self._modules

    @modules.setter
    def modules(self, value):
        """Change required modules.

        Reload modules given in the value.

        :param list value: new modules to use."""

        self._modules = value

        if value:
            for module in value:
                reload_module(lookup(module))

    @property
    def conf(self):
        """Get conf with parsers and self property values.

        :rtype: Configuration.
        """

        return self._conf

    @conf.setter
    def conf(self, value):
        """Change of configuration.

        :param value: new configuration to use.
        :type value: Category or Configuration
        """

        if value is None:
            value = Configuration()

        elif isinstance(value, Category):
            value = configuration(value)

        if self.inheritedconf:
            self._conf = self.clsconf()
            self._conf.update(value)

        else:
            self._conf = value

        if self.autoconf:
            self.applyconfiguration()

    @classmethod
    def clsconf(cls):
        """Method to override in order to specify class configuration."""

        result = configuration(
            category(
                Configurable.CATEGORY,
                Parameter(name=Configurable.CONF, ptype=Configuration),
                Parameter(
                    name=Configurable.DRIVERS, ptype=tuple,
                    value=Configurable.DEFAULT_DRIVERS
                ),
                Parameter(
                    name=Configurable.CONFPATHS, ptype=tuple,
                    value=Configurable.DEFAULT_CONFPATHS
                ),
                Parameter(
                    name=Configurable.INHERITEDCONF, ptype=bool,
                    value=Configurable.DEFAULT_INHERITEDCONF
                ),
                Parameter(
                    name=Configurable.SCOPE, ptype=dict,
                    value=Configurable.DEFAULT_SCOPE
                ),
                Parameter(
                    name=Configurable.SAFE, ptype=bool,
                    value=Configurable.DEFAULT_SAFE
                ),
                Parameter(
                    name=Configurable.BESTEFFORT, ptype=bool,
                    value=Configurable.DEFAULT_BESTEFFORT
                ),
                Parameter(
                    name=Configurable.CALLPARAMS, ptype=bool,
                    value=Configurable.DEFAULT_CALLPARAMS
                ),
                Parameter(
                    name=Configurable.MODULES, ptype=tuple,
                    value=Configurable.DEFAULT_MODULES
                ),
                Parameter(
                    name=Configurable.AUTOCONF, ptype=bool,
                    value=Configurable.DEFAULT_AUTOCONF
                ),
                Parameter(
                    name=Configurable.FOREIGNS, ptype=bool,
                    value=Configurable.DEFAULT_FOREIGNS
                )
            )
        )

        result[Configurable.CATEGORY][Configurable.CONF].value = result

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

        if self.autoconf:
            self.applyconfiguration()

    def clspaths(self):
        """Get class paths."""

        return tuple(self.DEFAULT_CONFPATHS)

    def applyconfiguration(
            self, conf=None, paths=None, drivers=None, logger=None,
            targets=None, scope=None, safe=None, besteffort=None
    ):
        """Apply conf on a destination in those phases:

        1. identify the right driver to use with paths to parse.
        2. for all paths, get conf which matches input conf.
        3. apply parsing rules on path parameters.
        4. fill input conf with resolved parameters.
        5. apply filled conf on targets.

        :param Configuration conf: conf from where get conf.
        :param paths: conf files to parse. If paths is a str, it is
            automatically putted into a list.
        :type paths: list of str
        :param Iterable targets: object(s) to configure. self targets by default.
        :param dict scope: local variables to use for expression resolution.
        """

        if scope is None:
            scope = self.scope

        if safe is None:
            safe = self.safe

        if besteffort is None:
            besteffort = self.besteffort

        if targets is None:
            targets = self.targets

        if logger is None:
            logger = self.logger

        # get conf from drivers and paths
        conf = self.getconf(
            conf=conf, paths=paths, logger=logger, drivers=drivers
        )
        if conf is not None:
            # resolve all values
            conf.resolve(
                configurable=self,
                scope=scope, safe=safe, besteffort=besteffort
            )
            # configure resolved configuration
            self.configure(conf=conf, targets=targets)

    def getconf(self, conf=None, paths=None, drivers=None, logger=None):
        """Get a configuration from paths.

        :param Configuration conf: conf to update. Default this conf.
        :param str(s) paths: list of conf files. Default this paths.
        :param Logger logger: logger to use for logging info/error messages.
        :param list drivers: ConfDriver to use. Default this drivers.
        :return: not resolved configuration.
        :rtype: Configuration
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

        if logger is None:
            logger = self.logger

        # iterate on all paths
        for path in paths:

            for driver in drivers:  # find the best driver

                rscconf = driver.getconf(
                    path=path, conf=conf, logger=logger
                )

                if rscconf is None:
                    continue

                if result is None:
                    result = rscconf

                else:
                    result.update(rscconf)

            if result is None:
                # if no conf found, display a warning log message
                if logger is not None:
                    logger.warning(
                        'No driver found among {0} for processing {1}'.format(
                            drivers, path
                        )
                    )

        return result

    def configure(self, conf=None, targets=None, logger=None):
        """Apply input conf on targets objects.

        Specialization of this method is done in the _configure method.

        :param Configuration conf: configuration model to configure. Default is
            this conf.
        :param Iterable targets: objects to configure. self targets by default.
        :param Logger logger: specific logger to use.
        :raises: Parameter.Error for any raised exception.
        """

        if conf is None:
            conf = self.conf

        if targets is None:
            targets = self.targets

        if logger is None:
            logger = self.logger

        for target in targets:

            autoconf = self.autoconf
            self.autoconf = False

            try:
                self._configure(
                    conf=conf, logger=logger, target=target
                )

            except Exception:
                if logger is not None:
                    logger.error(
                        'Error {0} raised while configuring {1}/{2}'.format(
                            format_exc(), self, targets
                        )
                    )

            else:
                self.autoconf = autoconf

    def _configure(self, target, conf=None, logger=None):
        """Configure this class with input conf only if auto_conf or
        configure is true.

        This method should be overriden for specific conf

        :param Configuration conf: configuration model to configure. Default is
            this conf.
        :param bool configure: if True, force full self conf
        :param target: object to configure. self targets by default.
        """

        if conf is None:
            conf = self.conf

        if logger is None:
            logger = self.logger

        sub_confs = []  # sort local configuration and sub configurations
        params = []  # self parameters

        autoconf = self.autoconf
        self.autoconf = False

        for cat in conf.values():  # separate sub params and params
            if cat.name.startswith(self.SUB_CONF_PREFIX):
                sub_confs.append(cat.name)

            else:
                cparams = cat.params
                params += cparams.values()

        for param in params:

            sub_conf_name = '{0}{1}'.format(
                self.SUB_CONF_PREFIX, param.name
            )

            value = param.value

            if sub_conf_name in sub_confs:  # if sub param

                cat = conf[sub_conf_name]

                extendedcat = cat.copy(name='extended')

                subconf = configuration(extendedcat)

                subparams = conf.params

                if isclass(value) or isroutine(value):
                    args, kwargs = self.getcallparams(
                        conf=configuration(extendedcat), target=value
                    )
                    try:
                        value = value(*args, **kwargs)

                    except TypeError:
                        value = value()

                    else:
                        if len(subparams) < (len(args) + len(kwargs)):
                            subparams = False

                if subparams:
                    applyconfiguration(targets=[value], conf=subconf)

            if param.error:
                continue

            if self.foreigns or param.local:
                if param.name == Configurable.AUTOCONF:
                    autoconf = param.value

                else:
                    setattr(target, param.name, value)

        self.autoconf = autoconf

    def _bind_target(self, target, ctx=None, *args, **kwargs):
        """Allow to bind to not callable objects."""

        newtarget = target not in self.targets

        if not callable(target):
            result = Annotation._bind_target(
                self, target=target, ctx=ctx, *args, **kwargs
            )

        else:
            result = super(Configurable, self)._bind_target(
                target=target, ctx=ctx, *args, **kwargs
            )

        if newtarget and self.autoconf:
            self.applyconfiguration(targets=[target])

        return result


def applyconfiguration(targets, *args, **kwargs):
    """Apply configuration on input targets.

    If targets are not annotated by a Configurable, a new one is instanciated.

    :param Iterable targets: targets to configurate.
    :param tuple args: applyconfiguration var args.
    :param dict kwargs: applyconfiguration keywords.
    """

    for target in targets:

        configurables = Configurable.get_annotations(target)

        if not configurables:
            configurables = [Configurable()]

        for configurable in configurables:

            configurable.applyconfiguration(
                targets=[target], *args, **kwargs
            )
