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
    'names', 'resolve', 'register', 'unregister', 'loadresolvers',
    'defaultname', 'getname'
]

from b3j0f.utils.path import lookup
from b3j0f.utils.version import OrderedDict

from inspect import isclass

from six import string_types

from os import getenv

from .core import (
    DEFAULT_BESTEFFORT, DEFAULT_SAFE, DEFAULT_TOSTR, DEFAULT_SCOPE
)


def loadresolvers(paths):
    """Load input path modules in order to register external resolvers.

    :param list paths: list of paths to load."""

    for path in paths:
        lookup(path)

#: env variable name of exprres modules.
B3J0F_EXPRRES_PATH = 'B3J0F_EXPRRES_PATH'

EXPRRES_PATH = getenv(B3J0F_EXPRRES_PATH)  #: expression resolver modules.

if EXPRRES_PATH:  # load modules
    loadresolvers(EXPRRES_PATH.split(','))

__RESOLVER__ = '__resolver__'  #: resolver name for class IoC


class ResolverRegistry(OrderedDict):
    """Resolver registry."""

    __slots__ = ('_default')

    def __init__(self, default=None, **resolvers):

        super(ResolverRegistry, self).__init__(resolvers)

        self._default = None

        self.default = default

    @property
    def default(self):
        """Get default resolver name."""

        if self._default is None or self._default not in self:
            self._default = list(self.keys())[0] if self else None

        return self._default

    @default.setter
    def default(self, value):
        """Change of resolver name.

        :param value: new default value to use.
        :type value: str or callable
        :raises: KeyError if value is a string not already registered."""

        if value is None:
            if self:
                value = list(self.keys())[0]

        elif not isinstance(value, string_types):
            value = register(exprresolver=value, reg=self)

        elif value not in self:
            raise KeyError(
                '{0} not registered in {1}'.format(value, self)
            )

        self._default = value

    def resolve(
            self, expr, name,
            safe=DEFAULT_SAFE, tostr=DEFAULT_TOSTR, scope=DEFAULT_SCOPE,
            besteffort=DEFAULT_BESTEFFORT
    ):
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

        resolver = self[name]

        result = resolver(
            expr=expr,
            safe=safe, tostr=tostr, scope=scope, besteffort=besteffort
        )

        return result

_RESOLVER_REGISTRY = ResolverRegistry()  #: default registry


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
            constructor parameters."""

        _exprresolver = exprresolver

        if isclass(exprresolver):  # try to instanciate exprresolver
            if _params is None:
                _params = {}

            _exprresolver = _exprresolver(**_params)

        if _name is None:
            _name = getname(exprresolver)

        reg[_name] = _exprresolver

        if reg.default is None:
            reg.default = _name

        return exprresolver

    if name is None:
        name = getname(exprresolver)

    if reg is None:
        reg = _RESOLVER_REGISTRY

    if exprresolver is None:
        result = _register

    else:
        result = name
        _register(exprresolver)

    return result


def unregister(name):
    """Unregister resolver.

    :param str name: resolver name to unregister.
    :return: named resolver.
    :rtype: callable"""

    return _RESOLVER_REGISTRY.pop(name)


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

    return list(_RESOLVER_REGISTRY.keys())

def resolve(
        expr, name=None,
        safe=DEFAULT_SAFE, tostr=DEFAULT_TOSTR, scope=DEFAULT_SCOPE,
        besteffort=DEFAULT_BESTEFFORT
):
    """Resolve an expression with possibly a dedicated expression resolvers.

    :param str name: expression resolver registered name. Default is the
        first registered expression resolver.
    :param bool safe: if True (Default), resolve in a safe context
        (without I/O).
    :param bool tostr: if True (False by default), transform the result into
        a string format.
    :param dict scope: scope execution resolution.
    :param bool besteffort: if True (default) auto import unknown var.

    :raises: KeyError if no expression resolver has been registered or if
        name does not exist in expression resolvers.
    """

    return _RESOLVER_REGISTRY.resolve(
        expr=expr, name=name, safe=safe, tostr=tostr, scope=scope,
        besteffort=besteffort
    )

def getname(exprresolver):
    """Get expression resolver name.

    Expression resolver name is given by the attribute __resolver__.
    If not exist, then the it is given by the attribute __name__.
    Otherwise, given by the __class__.__name__ attribute.

    :raises: TypeError if exprresolver is not callable."""

    result = None

    if not callable(exprresolver):
        raise TypeError('Expression resolver must be a callable object.')

    result = getattr(
        exprresolver, __RESOLVER__, getattr(
            exprresolver, '__name__', getattr(
                exprresolver.__class__, '__name__'
            )
        )
    )

    return result
