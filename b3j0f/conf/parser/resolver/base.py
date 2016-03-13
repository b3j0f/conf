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

"""Programming language expression resolver module.

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

__all__ = ['ExprResolver']

from six import add_metaclass

from .registry import register

from .core import (
    DEFAULT_BESTEFFORT, DEFAULT_SAFE, DEFAULT_TOSTR, DEFAULT_SCOPE
)


class _MetaExprResolver(type):
    """Expression Resolver meta class.

    Register automatically ExprResolver classes."""

    def __new__(cls, *args, **kwargs):

        result = super(_MetaExprResolver, cls).__new__(cls, *args, **kwargs)

        if result.__register__:
            register(exprresolver=result)

        return result


@add_metaclass(_MetaExprResolver)
class ExprResolver(object):
    """Expression resolver class.

    All sub classes are automatically registered."""

    __register__ = False  #: class registration flag.

    def __call__(
            self, expr,
            safe=DEFAULT_SAFE, tostr=DEFAULT_TOSTR, scope=DEFAULT_SCOPE,
            besteffort=DEFAULT_BESTEFFORT
    ):
        """Resolve input expression.

        :param str expr: configuration expression to resolve in this language.
        :param bool safe: safe run execution context (True by default).
        :param bool tostr: format the result.
        :param dict scope: execution scope (contains references to expression
            objects).
        :param bool besteffort: try to resolve unknown variable name from
            runtime context.
        """

        raise NotImplementedError()
