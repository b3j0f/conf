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

"""Configuration definition objects."""

__all__ = ['Configuration']

from .base import CompositeModelElement
from .cat import Category

from ..parser.resolver.core import (
    DEFAULT_SAFE, DEFAULT_BESTEFFORT, DEFAULT_SCOPE
)


class Configuration(CompositeModelElement):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    __contenttype__ = Category  #: content type.

    __slots__ = (
        'safe', 'besteffort', 'scope'
    ) + CompositeModelElement.__slots__

    def __init__(
            self, safe=DEFAULT_SAFE, besteffort=DEFAULT_BESTEFFORT,
            scope=DEFAULT_SCOPE, *args, **kwargs
    ):

        super(Configuration, self).__init__(*args, **kwargs)

        self.safe = safe
        self.besteffort = besteffort
        self.scope = scope

    def resolve(
            self, configurable=None, scope=None, safe=None, besteffort=None
    ):
        """Resolve all parameters.

        :param Configurable configurable: configurable to use for foreign
            parameter resolution.
        :param dict scope: variables to use for parameter expression evaluation.
        :param bool safe: safe execution (remove builtins functions).
        :raises: Parameter.Error for any raised exception.
        """

        if scope is None:
            scope = self.scope

        if safe is None:
            safe = self.safe

        if besteffort is None:
            besteffort = self.besteffort

        for category in self.values():

            for param in category.values():

                param.resolve(
                    configurable=configurable, conf=self,
                    scope=scope, safe=safe, besteffort=besteffort
                )

    def param(self, pname, cname=None, history=0):
        """Get parameter from a category and history.

        :param str pname: parameter name.
        :param str cname: category name. Default is the last registered.
        :param int history: historical param value from specific category or
            final parameter value if cname is not given. For example, if history
            equals 1 and cname is None, result is the value defined just before
            the last parameter value if exist. If cname is given, the result
            is the parameter value defined before the category cname.
        :rtype: Parameter
        :raises: NameError if pname or cname do not exist."""

        result = None

        category = None

        categories = []  # list of categories containing input parameter name

        for cat in self.values():

            if pname in cat:

                categories.append(cat)

                if cname == cat.name:
                    break

        if cname is not None and (
                not categories or categories[-1].name != cname
        ):
            raise NameError('Category {0} does not exist.'.format(cname))

        categories = categories[:max(1, len(categories) - history)]

        for category in categories:
            if pname in category:
                if result is None:
                    result = category[pname].copy()

                else:
                    result.update(category[pname])

        return result


def configuration(*cats):
    """Quick instanciaton of Configuration with categories."""

    return Configuration(melts=cats)
