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
from .category import Category
from .parameter import Parameter


class Configuration(CompositeModelElement):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    __contenttype__ = Category  #: content type.

    __slots__ = CompositeModelElement.__slots__

    ERRORS = '_ERRORS'  #: category name which contains errors.
    VALUES = '_VALUES'  #: category name which contains local param values.
    FOREIGNS = '_FOREIGN'  #: category name which contains foreign params vals.

    def resolve(self, configurable=None, _locals=None, _globals=None):
        """Resolve all category parameters.

        :param Configurable configurable: configurable to use for foreign
            parameter resolution.
        :param Configuration configuration: configuration to use for
            cross-value resolution.
        :param dict _locals: local variable to use for local python expression
            resolution.
        :param dict _globals: global variable to use for local python
            expression resolution.
        :raises: Parameter.Error for any raised exception.
        """

        for category in self._content.values():

            for param in category:

                param.resolve(
                    configurable=configurable, configuration=self,
                    _locals=_locals, _globals=_globals
                )

    def unify(self, copy=False):
        """Get a conf which contains only two categories:

        - VALUES where params are all self params where values are not
            exceptions.contains all values
        - ERRORS where params are all self params where values are
            exceptions

        :param bool copy: copy self params (default False).
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

                    to_update.put(param.copy() if copy else param)

                    if param.name in to_delete:
                        del to_delete[param.name]

        result += values
        result += foreigns
        result += errors

        return result

    def get_unified_category(self, name, copy=False):
        """Add a category with input name which takes all params provided
        by other categories.

        :param str name: new category name.

        :param bool copy: copy self params (default False).
        """

        result = Category(name)

        for category in self._content.values():
            for param in category:
                result.put(param.copy() if copy else param)

        return result

    def add_unified_category(self, name=VALUES, copy=False, new_content=None):
        """Add a unified category to self and add new_content if not None."""

        category = self.get_unified_category(name=name, copy=copy)

        if new_content is not None:
            category += new_content

        self += category

    def get_vparam(self, pname):
        """Get final parameter value, from the category "VALUES" or
        from a calculated."""

        result = None

        if Configuration.VALUES in self.content:

            categories = [self._content[Configuration.VALUES]]

        else:

            categories = self._content.values()

        for category in categories:

            param = category.get(pname)

            if param is not None:

                result = param.value

        return result

    def fill(
            self,
            conf, categories=True, parameters=True, override=False,
            svalueonly=True
    ):
        """Fill this parameters from input configuration.

        :param Configuration conf: input configuration from where get
            parameters.
        :param bool categories: if True (default), add not existing categories.
        :param bool parameters: if True (default), add not existing parameters.
        :param bool override: if False (default), do not override existing
            parameter values.
        :param bool svalueonly: if True (default), fill only svalue. Otherwise,
            fill value as well.
        :return: self
        :rtype: Configuration
        """

        cats2fill = None

        if categories:
            cats2fill = conf._content.values()

        else:
            cats2fill = tuple(
                category for category in conf._content.values()
                if category.name in self._content
            )

        for cat2fill in cats2fill:

            self.setdefault(cat2fill.name, Category(name=cats2fill.name))

            params2fill = None

            if parameters:
                params2fill = cat2fill.parameters()

            else:
                params2fill = tuple(
                    param for param in cat2fill.content
                )

            for param2fill in params2fill:

                param = cat2fill.setdefault(param2fill.name, param2fill.copy())

                if override or (
                    param.svalue not in (None, '')
                    and param.value not in (None, '')
                ):

                    param.svalue = param2fill.svalue

                    if not svalueonly:
                        param.value = param2fill.value
