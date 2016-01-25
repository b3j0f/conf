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

from .registry import register


class _MetaExprResolver(type):
    """Expression Resolver meta class.

    Register automatically ExprResolver classes."""

    def __new__(mcs, *args, **kwargs):

        result = super(mcs, *args, **kwargs)

        register(exprresolver=result)

        return result


class ExprResolver(object):
    """Expression resolver class.

    All sub classes are automatically registered."""

    __metaclass__ = _MetaExprResolver

    __registry__ = 'py'  #: regitration name.

    def __call__(self, expr, safe=True, tostr=False, scope=None):
        """Resolve input expression.

        :param str expr: configuration expression to resolve in this language.
        :param bool safe: safe run execution context (True by default).
        :param bool tostr: format the result.
        :param dict scope: execution scope (contains references to expression
            objects).
        """

        raise NotImplementedError()
