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

from six import string_types, get_function_globals, exec_
from six.moves import reload_module

from inspect import getargspec, isclass, isroutine, isfunction, ismethod

from traceback import format_exc

from b3j0f.utils.path import lookup
from b3j0f.utils.version import getcallargs
from b3j0f.annotation import PrivateInterceptor, Annotation

from ..model.conf import Configuration, configuration
from ..model.cat import Category, category
from ..model.param import Parameter, Array
from ..driver.base import ConfDriver
from ..driver.file.json import JSONFileConfDriver
from ..driver.file.ini import INIFileConfDriver
from ..driver.file.xml import XMLFileConfDriver
from ..parser.resolver.core import (
    DEFAULT_SAFE, DEFAULT_SCOPE, DEFAULT_BESTEFFORT
)

from random import random

from types import ModuleType


class Configurable(PrivateInterceptor):
    """Handle object configuration from configuration resources such as files.

    Based on a configuration model and configuration drivers, it is able to:

    - be used such as a decorator (see the b3j0f.annotation.Annotation).
        resources to configure are accessible from the ``targets`` property.
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
    PATHS = 'paths'  #: paths attribute name.
    DRIVERS = 'drivers'  #: drivers attribute name.
    FOREIGNS = 'foreigns'  #: not specified params setting attribute name.
    AUTOCONF = 'autoconf'  #: auto conf attribute name.
    SAFE = 'safe'  #: safe attribute name.
    SCOPE = 'scope'  #: scope attribute name.
    BESTEFFORT = 'besteffort'  #: best effort attribute name.
    MODULES = 'modules'  #: modules attribute name.
    RELOAD = 'rel'  #: module reload flag.
    CALLPARAMS = 'callparams'  #: call params attribute name.
    KEEPSTATE = 'keepstate'  #: reconfiguration keepstate level attribute name.
    DECOSUB = 'decosub'  #: decorate sub elment attribute name

    LOADED_MODULES = '_loadedmodules'  #: attribute for loaded modules.

    EXEC_CTX = '__CONFIGURABLE_EXEC_CTX' #: configurable execution context.

    DEFAULT_FOREIGNS = True  #: default value for setting not specified params.
    # default drivers which are json and ini.
    DEFAULT_DRIVERS = (
        JSONFileConfDriver(), INIFileConfDriver(), XMLFileConfDriver()
    )
    DEFAULT_AUTOCONF = True  #: default value for auto configuration.
    DEFAULT_CALLPARAMS = True  #: default value for callparams.
    DEFAULT_MODULES = None  #: default value for modules.
    DEFAULT_RELOAD = False  #: default reload modules flag (false by default).
    DEFAULT_SAFE = DEFAULT_SAFE  #: default value for safe.
    DEFAULT_SCOPE = DEFAULT_SCOPE  #: default value for scope.
    DEFAULT_BESTEFFORT = DEFAULT_BESTEFFORT  #: default value for besteffort.
    DEFAULT_KEEPSTATE = True  #: default keepstate value.
    DEFAULT_PATHS = ()  #: default paths value.
    DEFAULT_CONF = None  #: default conf value.
    DEFAULT_TARGETS = None  #: default targets value.
    DEFAULT_DECOSUB = True  #: default decosub value.

    SUB_CONF_PREFIX = ':'  #: sub conf prefix.

    def __init__(
            self,
            conf=DEFAULT_CONF, paths=DEFAULT_PATHS, drivers=DEFAULT_DRIVERS,
            foreigns=DEFAULT_FOREIGNS, autoconf=DEFAULT_AUTOCONF,
            targets=DEFAULT_TARGETS, keepstate=DEFAULT_KEEPSTATE,
            safe=DEFAULT_SAFE, scope=DEFAULT_SCOPE,
            besteffort=DEFAULT_BESTEFFORT,
            modules=DEFAULT_MODULES, rel=DEFAULT_RELOAD,
            callparams=DEFAULT_CALLPARAMS, decosub=DEFAULT_DECOSUB, logger=None,
            *args, **kwargs
    ):
        """
        :param conf: conf to use at instance level.
        :type conf: Configuration, Category or Parameter.
        :param Iterable paths: paths to parse.
        :param targets: object(s) to reconfigure. Such object may
            implement the methods configure applyconfiguration and configure.
        :param bool keepstate: if True (default), do not instanciate sub objects
            if they already exist.
        :type targets: list or instance.
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
        :param bool rel: reload modules. Default is False.
        :param bool callparams: if True (default), use parameters in the
            configured callable function.
        :param bool decosub: if True (default), decorate elements created by
            decorated types.
        :param Logger logger: this logger."""

        super(Configurable, self).__init__(*args, **kwargs)

        # init protected attributes
        self._paths = None
        self._conf = None
        self._targets = []
        self._modules = [] if modules is None else modules
        self._loadedmodules = set()

        # init public attributes

        # dirty hack: falsify autoconf in order to avoid auto applyconfiguration
        self.autoconf = False

        self.drivers = drivers
        self.foreigns = foreigns
        self.targets = [] if targets is None else targets
        self.keepstate = keepstate
        self.conf = self._toconf(conf)
        self.paths = paths
        self.safe = safe
        self.scope = scope
        self.besteffort = besteffort
        self.callparams = callparams
        self.logger = logger
        self.decosub = decosub
        self.rel = rel

        # generate an execution context name
        self.exec_ctx = '{0}{1}'.format(Configurable.EXEC_CTX, random())

        self.autoconf = autoconf  # end of dirty hack

    def _interception(self, joinpoint):

        target = joinpoint.target

        args, kwargs = joinpoint.args, joinpoint.kwargs

        if len(self.modules) != len(self._loadedmodules):
            self.loadmodules()

        if self.callparams:

            conf = self.getconf()

            args, kwargs = self.getcallparams(
                conf=conf, target=target, args=list(args), kwargs=kwargs,
                exec_ctx=joinpoint.exec_ctx.setdefault(self.exec_ctx, set())
            )

            joinpoint.args = list(args)
            joinpoint.kwargs = kwargs

        result = joinpoint.proceed()

        # configure parameters not already given in the constructor.
        if self.autoconf:

            cls = joinpoint.ctx if isclass(joinpoint.ctx) else target

            target2conf = result

            if target2conf is None:

                if isclass(cls):
                    # if target is the method __init__
                    if target.__name__ == '__init__':

                        if 'self' in kwargs:
                            target2conf = kwargs['self']

                        else:
                            target2conf = args[0]

            if not isclass(cls) or isinstance(target2conf, cls):

                if self.callparams:  # remove params already given in jp params.

                    params = conf.params

                    kwargs = joinpoint.kwargs

                    for pname in kwargs:
                        if pname in params:# and kwargs[pname] is not None:
                            del params[pname]

                    conf = self._toconf(list(params.values()))

                else:
                    conf = self.getconf()

                target2conf = self._configure(
                    target=target2conf, callconf=False, conf=conf
                )

                if self.decosub:
                    if target2conf not in self.targets:
                        self.targets.append(target2conf)

        return result

    def getcallparams(
            self, target, conf=None, args=None, kwargs=None, exec_ctx=None
    ):
        """Get target call parameters.

        :param list args: target call arguments.
        :param dict kwargs: target call keywords.
        :return: args, kwargs
        :rtype: tuple"""

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        if conf is None:
            conf = self.conf

        params = conf.params

        try:
            argspec = getargspec(target)

        except TypeError as tex:
            argspec = None
            callargs = {}

        else:
            try:
                callargs = getcallargs(target, *args, **kwargs)

            except TypeError as tex:
                if tex.args[0].endswith('\'{0}\''.format(argspec.args[0])):
                    args = [None]

                else:
                    raise

                try:
                    callargs = getcallargs(target, *args, **kwargs)

                except TypeError as tex:
                    if tex.args[0].endswith('\'{0}\''.format(argspec.args[0])):
                        args = []

                    else:
                        raise

                    callargs = getcallargs(target, *args, **kwargs)

                args = []

        pnames = set(params)

        for pname in pnames:

            if argspec and pname in argspec.args and (
                    (exec_ctx is not None and pname in exec_ctx)
                    or
                    callargs.get(pname) is None
            ):

                kwargs[pname] = params[pname].value

        if exec_ctx is not None:
            exec_ctx |= pnames

        return args, kwargs

    def loadmodules(self, modules=None, rel=None):
        """ry to (re)load modules and return loaded modules.

        :param modules: list of module (name) to load.
        :param bool rel: flag for forcing reload of module. Default is this
            rel flag (false by default).
        :rtype: list
        :return: loaded modules."""

        result = []

        if rel is None:
            rel = self.rel

        if modules is None:
            modules = self._modules

        for module in modules:

            if isinstance(module, string_types):
                name = module
                module = lookup(name)

            elif isinstance(module, ModuleType):
                name = module.__name__

            else:
                raise TypeError(
                    'wrong value {0} in {1}. List of str/module expected.'
                    .format(
                        module, modules
                    )
                )

            if not rel and module in self._loadedmodules:
                continue

            reload_module(module)
            result.append(module)
            self._loadedmodules.add(module)

        return result

    @property
    def modules(self):
        """Get this required modules."""

        return self._modules

    @modules.setter
    def modules(self, value):
        """Change required modules.

        Reload modules given in the value.

        :param list value: new modules to use."""

        modules = [module.__name__ for module in self.loadmodules(value)]

        self._modules = [
            module for module in self._modules + modules
            if module not in self._modules
        ]

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

        self._conf = self._toconf(value)

        if self.autoconf:
            self.applyconfiguration()

    def _toconf(self, conf):
        """Convert input parameter to a Configuration.

        :param conf: configuration to convert to a Configuration object.
        :type conf: Configuration, Category or Parameter.

        :rtype: Configuration"""

        result = conf

        if result is None:
            result = Configuration()

        elif isinstance(result, Category):
            result = configuration(result)

        elif isinstance(result, Parameter):
            result = configuration(category('', result))

        elif isinstance(result, list):
            result = configuration(category('', *result))

        return result

    @property
    def paths(self):
        """Get all type conf files and user files.

        :return: self conf files
        :rtype: tuple
        """

        return tuple(self._paths)

    @paths.setter
    def paths(self, value):
        """Change of paths in adding it in watching list."""

        if value is None:
            value = ()

        elif isinstance(value, string_types):
            value = (value, )

        self._paths = tuple(value)

        if self.autoconf:
            self.applyconfiguration()

    def applyconfiguration(
            self, conf=None, paths=None, drivers=None, logger=None,
            targets=None, scope=None, safe=None, besteffort=None,
            callconf=False, keepstate=None, modules=None
    ):
        """Apply conf on a destination in those phases:

        1. identify the right driver to use with paths to parse.
        2. for all paths, get conf which matches input conf.
        3. apply parsing rules on path parameters.
        4. fill input conf with resolved parameters.
        5. apply filled conf on targets.

        :param conf: conf from where get conf.
        :type conf: Configuration, Category or Parameter
        :param paths: conf files to parse. If paths is a str, it is
            automatically putted into a list.
        :type paths: list of str
        :param Iterable targets: objects to configure. this targets by default.
        :param dict scope: local variables to use for expression resolution.
        :param bool callconf: if True (False by default), the configuration is
            used in the callable target parameters while calling it.
        :param bool keepstate: if True (default), do not instanciate sub objects
            if they already exist.
        :param list modules: modules to load before configure this configurable.
        :return: configured targets.
        :rtype: list
        """

        result = []

        self.loadmodules(modules=modules)
        modules = []

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

        if keepstate is None:
            keepstate = self.keepstate

        # get conf from drivers and paths
        conf = self.getconf(
            conf=conf, paths=paths, logger=logger, drivers=drivers,
            modules=modules
        )
        if conf is not None:
            # resolve all values
            conf.resolve(
                configurable=self, scope=scope, safe=safe, besteffort=besteffort
            )
            # configure resolved configuration
            configured = self.configure(
                conf=conf, targets=targets, callconf=callconf,
                keepstate=keepstate, modules=modules
            )

            result += configured

        return result

    def getconf(
            self, conf=None, paths=None, drivers=None, logger=None, modules=None
    ):
        """Get a configuration from paths.

        :param conf: conf to update. Default this conf.
        :type conf: Configuration, Category or Parameter
        :param str(s) paths: list of conf files. Default this paths.
        :param Logger logger: logger to use for logging info/error messages.
        :param list drivers: ConfDriver to use. Default this drivers.
        :param list modules: modules to reload before.
        :return: not resolved configuration.
        :rtype: Configuration
        """

        result = None

        self.loadmodules(modules=modules)
        modules = []

        conf = self._toconf(conf)

        # start to initialize input params
        if conf is None:
            conf = self.conf.copy()

        else:
            selfconf = self.conf.copy()
            selfconf.update(conf)
            conf = selfconf

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

            rscconf = None

            for driver in drivers:  # find the best driver

                rscconf = driver.getconf(path=path, conf=conf, logger=logger)

                if rscconf is None:
                    continue

                conf.update(rscconf)

            if rscconf is None:
                # if no conf found, display a warning log message
                if logger is not None:
                    logger.warning(
                        'No driver found among {0} for processing {1}'.format(
                            drivers, path
                        )
                    )

        result = conf

        return result

    def configure(
            self, conf=None, targets=None, logger=None, callconf=False,
            keepstate=None, modules=None
    ):
        """Apply input conf on targets objects.

        Specialization of this method is done in the _configure method.

        :param conf: configuration model to configure. Default is this conf.
        :type conf: Configuration, Category or Parameter
        :param Iterable targets: objects to configure. self targets by default.
        :param Logger logger: specific logger to use.
        :param bool callconf: if True (False by default), the configuration is
            used in the callable target parameters while calling it.
        :param bool keepstate: if True (default), do not instanciate sub objects
            if they already exist.
        :param list modules: modules to reload before.
        :return: configured targets.
        :rtype: list
        :raises: Parameter.Error for any raised exception.
        """

        result = []

        self.loadmodules(modules=modules)
        modules = []

        conf = self._toconf(conf)

        if conf is None:
            conf = self.conf

        if targets is None:
            targets = self.targets

        if logger is None:
            logger = self.logger

        if keepstate is None:
            keepstate = self.keepstate

        for target in targets:

            try:
                configured = self._configure(
                    conf=conf, logger=logger, target=target, callconf=callconf,
                    keepstate=keepstate, modules=modules
                )

            except Exception:
                if logger is not None:
                    logger.error(
                        'Error {0} raised while configuring {1}/{2}'.format(
                            format_exc(), self, targets
                        )
                    )

            else:
                result.append(configured)

        return result

    def _configure(
            self, target, conf=None, logger=None, callconf=None, keepstate=None,
            modules=None
    ):
        """Configure this class with input conf only if auto_conf or
        configure is true.

        This method should be overriden for specific conf

        :param target: object to configure. self targets by default.
        :param Configuration conf: configuration model to configure. Default is
            this conf.
        :param Logger logger: logger to use.
        :param bool callconf: if True, use conf in target __call__ parameters.
        :param bool keepstate: if True recreate sub objects if they already
            exist.
        :param list modules: modules to reload before.
        :return: configured target.
        """

        result = target

        self.loadmodules(modules=modules)
        modules = []

        if conf is None:
            conf = self.conf

        if logger is None:
            logger = self.logger

        if callconf is None:
            callconf = self.callparams

        if keepstate is None:
            keepstate = self.keepstate

        subcats = {}  # store sub configurable categories
        params = []  # self parameters

        sub_conf_prefix = Configurable.SUB_CONF_PREFIX

        for cat in conf.values():  # separate sub params and params
            cname = cat.name

            if cname.startswith(sub_conf_prefix):

                subcnames = cname.split(sub_conf_prefix)

                pname = subcnames[1]
                fcname = cname[1 + len(pname):]

                if not fcname:
                    fcname = str(random())

                fcat = cat.copy(name=fcname)

                if pname in subcats:
                    subcats[pname].append(fcat)

                else:
                    subcats[pname] = [fcat]

            else:
                cparams = cat.params
                params += cparams.values()

        if callconf and callable(target):

            conf = self._toconf(params)

            args, kwargs = self.getcallparams(conf=conf, target=target)

            result = target = target(*args, **kwargs)

        for param in params:

            value, pname = param.value, param.name

            if pname in subcats:  # if sub param

                subcallconf = True

                if keepstate and hasattr(target, pname):
                    subcallconf = False
                    value = getattr(target, pname)

                cats = subcats[pname]

                subconf = configuration(*cats)

                targets = applyconfiguration(
                    targets=[value], conf=subconf, callconf=subcallconf,
                    keepstate=keepstate, modules=modules
                )
                value = targets[0]

            if param.error:
                continue

            elif self.foreigns or param.local:
                try:
                    setattr(target, pname, value)

                except Exception:
                    if logger is not None:
                        logger.error(
                            'Error while setting {0}({1}) on {2}: {3}'.format(
                                pname, value, target, format_exc()
                            )
                        )

        return result

    def _bind_target(self, target, ctx, *args, **kwargs):

        if callable(target):

            result = super(Configurable, self)._bind_target(
                target, ctx, *args, **kwargs
            )

            cls = target if ctx is None else ctx

            if isclass(cls):
                func = getattr(cls, '__init__', getattr(cls, '__new__', None))

            else:
                func = cls

            func = getattr(func, '__func__', func)

            try:
                fargs, _, _, defaults = getargspec(func)

            except TypeError:
                pass

            else:
                len_defaults = 0 if defaults is None else len(defaults)
                defaultstartindex = len(fargs) - len_defaults

                conf = self.getconf()
                params = conf.params

                if '_default' not in conf:
                    conf += Category(name='_default')

                for index, arg in enumerate(fargs):

                    if index >= defaultstartindex:
                        val = defaults[index - defaultstartindex]

                        if arg not in params:
                            param = Parameter(name=arg)
                            conf['_default'] += param

                        else:
                            param = params[arg]

                        if param.value is None:
                            param.value = val
                            if val is not None:
                                param.ptype = type(val)

        else:
            result = Annotation._bind_target(self, target, ctx, *args, **kwargs)

        return result

def applyconfiguration(targets, conf=None, *args, **kwargs):
    """Apply configuration on input targets.

    If targets are not annotated by a Configurable, a new one is instanciated.

    :param Iterable targets: targets to configurate.
    :param tuple args: applyconfiguration var args.
    :param dict kwargs: applyconfiguration keywords.
    :return: configured targets.
    :rtype: list
    """

    result = []

    for target in targets:

        configurables = Configurable.get_annotations(target)

        if not configurables:
            configurables = [Configurable()]

        for configurable in configurables:

            configuredtargets = configurable.applyconfiguration(
                targets=[target], conf=conf, *args, **kwargs
            )
            result += configuredtargets

    return result

#: Default Configurable conf.
_CONF = configuration(
    category(
        Configurable.CATEGORY,
        Parameter(
            name=Configurable.CONF, ptype=Configuration,
            value=Configurable.DEFAULT_CONF
        ),
        Parameter(
            name=Configurable.TARGETS, ptype=Array(),
            value=Configurable.DEFAULT_TARGETS
        ),
        Parameter(
            name=Configurable.DRIVERS, ptype=Array(ConfDriver),
            value=Configurable.DEFAULT_DRIVERS
        ),
        Parameter(
            name=Configurable.PATHS, ptype=Array(string_types),
            value=Configurable.DEFAULT_PATHS
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
            name=Configurable.MODULES, ptype=Array(str),
            value=Configurable.DEFAULT_MODULES
        ),
        Parameter(
            name=Configurable.AUTOCONF, ptype=bool,
            value=Configurable.DEFAULT_AUTOCONF
        ),
        Parameter(
            name=Configurable.FOREIGNS, ptype=bool,
            value=Configurable.DEFAULT_FOREIGNS
        ),
        Parameter(
            name=Configurable.KEEPSTATE, ptype=bool,
            value=Configurable.DEFAULT_KEEPSTATE
        )
    )
)

# apply the configurable on itself
Configurable(
    conf=_CONF, paths=['b3j0fconf-configurable.conf'], #autoconf=False
)(Configurable)
