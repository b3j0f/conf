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
from .param import Parameter


class Configuration(CompositeModelElement):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    __contenttype__ = Category  #: content type.

    __slots__ = CompositeModelElement.__slots__

    ERRORS = ':ERRORS'  #: category name which contains errors.
    VALUES = ':VALUES'  #: category name which contains local param values.
    FOREIGNS = ':FOREIGN'  #: category name which contains foreign params vals.

    def resolve(
        self, configurable=None, _locals=None, _globals=None, safe=True
    ):
        """Resolve all parameters.

        :param Configurable configurable: configurable to use for foreign
            parameter resolution.
        :param dict _locals: local variable to use for local python expression
            resolution.
        :param dict _globals: global variable to use for local python
            expression resolution.
        :param bool safe: safe execution (remove builtins functions).
        :raises: Parameter.Error for any raised exception.
        """

        for category in self._content.values():

            for param in category:

                param.resolve(
                    configurable=configurable, conf=self,
                    _locals=_locals, _globals=_globals, safe=safe
                )

    def unify(self):
        """Get a conf which contains only two categories:

        - VALUES where params are all self params where values are not
            exceptions.contains all values.
        - ERRORS where params are all self params where values are
            exceptions.

        :return: two categories named respectivelly VALUES and ERRORS and
            contain respectivelly self param values and parsing errors.
        :rtype: Configuration
        """

        result = Configuration()

        values = Category(Configuration.VALUES)
        errors = Category(Configuration.ERRORS)
        foreigns = Category(Configuration.FOREIGNS)

        for category in self:

            for param in category:

                pvalue = None

                try:  # get value
                    pvalue = param.value

                except Parameter.Error:
                    pass

                if (pvalue, param.error) != (None, None):
                    final_values = values if param.local else foreigns

                    if param.error is not None:  # if param is in error
                        to_update = errors
                        to_delete = final_values

                    else:
                        to_update = final_values
                        to_delete = errors

                    to_update += param

                    if param.name in to_delete:
                        del to_delete[param.name]

        result += values
        result += foreigns
        result += errors

        return result

    def get_unified_category(self, name):
        """Add a category with input name which takes all this parameters.

        :param str name: new category name.
        """

        result = Category(name)

        for cat in self._content.values():
            for param in cat:
                result.put(param)

        return result

    def pvalue(self, pname, cname=None):
        """Get final parameter value, from the category "VALUES" or
        from a calculated.

        :param str pname: parameter name.
        :param str cname: category name.
        :raises: NameError if pname or cname do not exist."""

        result = None

        if cname is None:
            if Configuration.VALUES in self._content:
                category = self._content[Configuration.VALUES]

            else:
                unified = self.unify()
                if pname in unified[Configuration.VALUES]:
                    category = unified[Configuration.VALUES]

                else:
                    category = unified[Configuration.FOREIGNS]

        else:
            category = self._content[cname]

        if category is None:
            raise NameError('Category {0} does not exist.'.format(cname))

        param = category[pname]

        result = param.value

        return result

    def update(self, conf):
        """Update this configuration with other configuration parameter values
        and svalues.

        :param Configuration conf: configuration from where get parameter values
            and svalues."""

        for cat in conf:

            if cat.name in self:

                selfcat = self._content[cat.name]

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
