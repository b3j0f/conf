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

"""Javascript expression resolver."""

from __future__ import print_function

__all__ = ['resolvejs']

from ..registry import register

from ..core import DEFAULT_TOSTR, DEFAULT_SCOPE

try:
    from PyV8 import JSContext

except ImportError:

    from sys import stderr
    print(
        'Impossible to load the javascript resolver. Install the PyV8 before.',
        file=stderr
    )
    def resolvejs(**_):
        """Default resolvejs if PyV8 is not installed."""
        pass

else:
    CTXT = JSContext()

    @register('js')
    @register('javascript')
    @register('pyv8')
    def resolvejs(
            expr, tostr=DEFAULT_TOSTR, scope=DEFAULT_SCOPE, *args, **kwargs
    ):
        """Javascript resolver."""

        _ctxt = CTXT if scope is None else JSContext(scope)

        if tostr:
            expr = '({0}).string'.format(expr)

        result = _ctxt.eval(expr)

        return result

