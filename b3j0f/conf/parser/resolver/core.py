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

"""core resolver module.

Contains signature of the resolver function and and default parameter values."""

__all__ = [
    'DEFAULT_BESTEFFORT', 'DEFAULT_SAFE', 'DEFAULT_TOSTR', 'DEFAULT_SCOPE',
    'resolver'
]

DEFAULT_BESTEFFORT = True  #: default best effort execution context flag.
DEFAULT_SAFE = True  #: default safe execuction context flag.
DEFAULT_TOSTR = False  #: default conversion to str flag.
DEFAULT_SCOPE = None  #: default scope execution context.

def resolver(
        expr, safe=DEFAULT_SAFE, tostr=DEFAULT_TOSTR, scope=DEFAULT_SCOPE,
        besteffort=DEFAULT_BESTEFFORT
):
    """Resolve input expression.

    This function is given such as template resolution function. For wrapping
    test for example.

    :param str expr: configuration expression to resolve.
    :param bool safe: if True (default), run safely execution context.
    :param bool tostr: format the result.
    :param dict scope: execution scope (contains references to expression
        objects).
    :param bool besteffort: if True (default), try to resolve unknown variable
        name with execution runtime.
    :return: resolved expression."""


    raise NotImplementedError()
