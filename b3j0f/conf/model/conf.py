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


class Configuration(CompositeModelElement):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    __contenttype__ = Category  #: content type.

    __slots__ = CompositeModelElement.__slots__

    def resolve(
            self, configurable=None, scope=None, safe=True
    ):
        """Resolve all parameters.

        :param Configurable configurable: configurable to use for foreign
            parameter resolution.
        :param dict scope: variables to use for parameter expression evaluation.
        :param bool safe: safe execution (remove builtins functions).
        :raises: Parameter.Error for any raised exception.
        """

        for category in self.values():

            for param in category:

                param.resolve(
                    configurable=configurable, conf=self,
                    scope=scope, safe=safe
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
        :raises: NameError if pname or cname do not exist."""

        result = None

        category = None

        categories = []  # list of categories containing input parameter name

        for cat in self.values():

            if pname in cat:

                categories.append(cat)

                if cname in (None, cat.name):
                    category = cat

                    if cname is not None:
                        break

        if category is None:
            raise NameError('Category {0} does not exist.'.format(cname))

        category = categories[- (history + 1)]

        result = category[pname]

        return result

    def update(self, conf):
        """Update this configuration with other configuration parameter values
        and svalues.

        :param Configuration conf: configuration from where get parameter values
            and svalues."""

        for cat in conf:

            if cat.name in self:

                selfcat = self[cat.name]

                for param in cat:

                    paramstoupdate = selfcat.getparams(param=param)

                    if paramstoupdate:

                        for paramtoupdate in paramstoupdate:

                            paramtoupdate.svalue = param.svalue

                            try:
                                paramtoupdate.value = param.value

                            except TypeError:
                                pass

                    else:
                        # mark the param such as foreign
                        selfcat += param.copy(local=False)

            else:
                self += cat
