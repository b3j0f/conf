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

from re import compile as re_compile

from copy import deepcopy

from ..registry import register

MISSING_NAME = r'\'(?P<name>.+)\''
MISSING_NAME_REGEX = re_compile(MISSING_NAME)


@register('py')
def resolvepy(expr, safe=True, tostr=False, scope=None, besteffort=True):
    """Resolve input expression.

    :param str expr: configuration expression to resolve in this language.
    :param bool safe: safe run execution context (True by default).
    :param bool tostr: format the result.
    :param dict scope: execution scope (contains references to expression
        objects).
    :param bool besteffort: try to resolve unknown variable name with execution
        runtime.
    """

    _eval = safe_eval if safe else eval

    _scope = deepcopy(scope)

    while besteffort:

        try:

            result = _eval(expr, _scope)

        except NameError as nex:

            arg = nex.args
            match = MISSING_NAME_REGEX.search(arg)
            missing = match.group('name')
            try:
                missing_value = lookup(missing)

            except ImportError:
                break

            else:
                _scope[missing] = missing_value

        else:
            break

    if tostr:
        result = str(result)

    return result
