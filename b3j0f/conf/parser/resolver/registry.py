# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""Resolver registry.

This module aims to manage several resolvers in a registry.

This module defines expression resolvers for dedicated programming languages.

An expression resolver is a function which takes in parameters:

- expr: string expression to resolve.
- safe: boolean flag for a safe execution context.
- tostr: boolean flag about format the expression into a string representation.
- scope: dict of variables for execution context (contain variables).

A resolver is registered with the function ``register``.
And is loaded in three ways:

- in setting the environment variable 'B3J0F_EXPRRES_PATH' (for example,
    `b3j0f.conf.parser.lang.js,custom.c` could load both modules `js` and `c`
    containing programming language parsers).
- in using the function `loadresolvers`.
- in simply importing a dedicated module with the import keyword.
"""

__all__ = [
    'ResolverRegistry',
    'names', 'resolve', 'register', 'loadresolvers', 'defaultname', 'getname'
]

from b3j0f.utils.path import lookup

from inspect import isroutine, isclass

from future.moves.collections import OrderedDict

from six import string_types

from os import getenv

#: env variable name of exprres modules.
B3J0F_EXPRRES_PATH = 'B3J0F_EXPRRES_PATH'

EXPRRES_PATH = getenv(B3J0F_EXPRRES_PATH)  #: expression resolver modules.


if EXPRRES_PATH:  # load modules
    loadresolvers(EXPRRES_PATH.split(','))


__RESOLVER__ = '__resolver__'  #: resolver name for class resolvers.


class ResolverRegistry(object):
    """Resolver registry."""

    __slots__ = ('resolvers', '_default')

    def __init__(self, default=None, **resolvers):

        self._default = None

        self.resolvers = OrderedDict(resolvers)
        self.default = default

    @property
    def default(self):
        """Get default resolver name."""

        return self._default

    @default.setter
    def default(self, value):
        """Change of resolver name.

        :param str value: new default value to use.
        :raises: NameError if value is not registered."""

        if value is None:
            if self.resolvers:
                value = list(self.resolvers.keys())[0]

        elif not isinstance(value, string_types):
            value = register(exprresolver=value, reg=self)

        elif value not in self.resolvers:
            raise NameError(
                '{0} not registered in {1}'.format(value, self.resolvers)
            )

        self._default = value

    @property
    def names(self):
        """Get all resolver names.

        :rtype: list"""

        return list(self.resolvers.keys())

    def resolve(self, expr, name=None, safe=True, tostr=False, scope=None):
        """Resolve an expression with possibly a dedicated expression resolvers.

        :param str name: expression resolver registered name. Default is the
            first registered expression resolver.
        :param bool safe: if True (Default), resolve in a safe context
            (without I/O).
        :param bool tostr: if True (False by default), transform the result into
            a string format.
        :param dict scope: scope execution resolution.
        :return: a string if tostr, otherwise, a python object.

        :raises: KeyError if no expression resolver has been registered or if
            name does not exist in expression resolvers.
        """

        resolver = None

        if name is None:
            name = self.default

        resolver = self.resolvers[name]

        result = resolver(expr=expr, safe=safe, tostr=tostr, scope=scope)

        return result

_RESOLVER_REGISTRY = ResolverRegistry()  #: default registry

def loadresolvers(paths):
    """Load input path modules in order to register external resolvers.

    :param list paths: list of paths to load."""

    for path in paths:
        lookup(path)

def register(name=None, exprresolver=None, params=None, reg=None):
    """Register an expression resolver.

    Can be used such as a decorator.

    For example all remainding expressions are the same.

    .. code-block:: python

        @register('myresolver')
        def myresolver(**kwargs): pass

    .. code-block:: python

        def myresolver(**kwargs): pass

        register('myresolver', myresolver)

    .. code-block:: python

        @register('myresolver')
        class MyResolver():
            def __call__(**kwargs): pass

    .. code-block:: python

        class MyResolver():
            def __call__(**kwargs): pass

        register('myresolver', MyResolver)

    .. code-block:: python

        class MyResolver():
            def __call__(**kwargs): pass

        register('myresolver', MyResolver())


    :param str name: register name to use. Default is the function/class
        name.
    :param exprresolver: function able to resolve an expression.
    :param dict kwargs: parameters of resolver instanciation if exprresolver
        is a class and this function is used such as a decorator.
    :param ResolverRegistry reg: registry to use. Default is the global registry
    .
    """

    def _register(exprresolver, _name=name, _params=params):
        """Local registration for better use in a decoration context.

        :param exprresolver: function/class able to resolve an expression.
        :param str _name: private parameter used to set the name.
        :param dict _params: private parameter used to set resolver class
            constructor parameters.
        """

        if _name is None:
            _name = getname(exprresolver)

        if isclass(exprresolver):  # try to instanciate exprresolver
            if _params is None:
                _params = {}
            exprresolver = exprresolver(**_params)

        reg.resolvers[_name] = exprresolver

        return exprresolver

    if reg is None:
        reg = _RESOLVER_REGISTRY

    if exprresolver is None:
        return _register

    else:
        if name is None:
            name = getname(exprresolver)
        _register(exprresolver)

    reg.resolvers[name] = exprresolver

    return name


def defaultname(name=None):
    """Get default resolver name.

    :param str name: if given, change the default name.
    :raises: NameError if name given and not in registered resolvers.
    :rtype: str"""

    if name is None:
        name = _RESOLVER_REGISTRY.default

    else:
        _RESOLVER_REGISTRY.default = name

    return name

def names():
    """Get resolver names.

    :rtype: list"""

    return _RESOLVER_REGISTRY.names

def resolve(**kwargs):
    """Resolve an expression with possibly a dedicated expression resolvers.

    :param str name: expression resolver registered name. Default is the
        first registered expression resolver.
    :param bool safe: if True (Default), resolve in a safe context
        (without I/O).
    :param bool tostr: if True (False by default), transform the result into
        a string format.
    :param dict scope: scope execution resolution.

    :raises: KeyError if no expression resolver has been registered or if
        name does not exist in expression resolvers.
    """

    return _RESOLVER_REGISTRY.resolve(**kwargs)

def getname(exprresolver):
    """Get expression resolver name.

    :raises: TypeError if exprresolver is not callable."""

    result = None

    if isroutine(exprresolver):
        result = exprresolver.__name__

    elif isclass(exprresolver):
        result = getattr(exprresolver, __RESOLVER__, exprresolver.__name__)

    elif callable(exprresolver):
        cls = exprresolver.__class__
        result = getname(cls)

    else:
        raise TypeError('Expression resolver must be a callable object.')

    return result
