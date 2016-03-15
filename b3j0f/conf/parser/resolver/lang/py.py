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

"""python expression resolver."""

__all__ = ['resolvepy']

from b3j0f.utils.runtime import safe_eval
from b3j0f.utils.path import lookup

from re import compile as re_compile, sub

from ..registry import register
from ..core import (
    DEFAULT_BESTEFFORT, DEFAULT_SAFE, DEFAULT_TOSTR, DEFAULT_SCOPE
)


MISSING_NAME = r'\'(?P<name>\w+)\''
MISSING_NAME_REGEX = re_compile(MISSING_NAME)

MISSING_VARIABLE = r'(?P<name>(\w+\.)*{0}(\.\w+)*)'


def genrepl(scope):
    """Replacement function with specific scope."""

    def repl(match):
        """Internal replacement function."""

        name = match.group('name')

        value = lookup(name, scope=scope)

        result = name.replace('.', '_')
        scope[result] = value

        return result

    return repl


@register('py')
@register('python')
def resolvepy(
        expr,
        safe=DEFAULT_SAFE, tostr=DEFAULT_TOSTR, scope=DEFAULT_SCOPE,
        besteffort=DEFAULT_BESTEFFORT
    ):
    """Resolve input expression.

    :param str expr: configuration expression to resolve in this language.
    :param bool safe: safe run execution context (True by default).
    :param bool tostr: format the result.
    :param dict scope: execution scope (contains references to expression
        objects).
    :param bool besteffort: try to resolve unknown variable name with execution
        runtime."""

    result = None

    _eval = safe_eval if safe else eval

    _expr = expr

    scope = {} if scope is None else scope.copy()

    while True:

        try:
            result = _eval(_expr, scope)

        except (AttributeError, NameError) as nex:

            if not besteffort:
                raise

            arg = nex.args[0]
            missing = MISSING_NAME_REGEX.findall(arg)[-1]

            try:
                _expr = sub(
                    MISSING_VARIABLE.format(missing),
                    genrepl(scope=scope),
                    _expr
                )

            except ImportError:
                raise nex

        else:
            break

    if tostr:
        result = str(result)

    return result
