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

__all__ = ['Configuration', 'Category', 'Parameter']


from collections import Iterable

from b3j0f.utils.version import basestring, OrderedDict
from b3j0f.utils.path import lookup


class Configuration(object):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    ERRORS = 'ERRORS'  #: category name which contains errors
    VALUES = 'VALUES'  #: category name which contains local parameter values
    FOREIGNS = 'FOREIGN'  #: category name which contains not local parameters

    def __init__(self, *categories):
        """
        :param list categories: categories to configure.
        """

        super(Configuration, self).__init__()

        # set categories
        self.categories = OrderedDict()
        for category in categories:
            self.categories[category.name] = category

    def __iter__(self):

        return iter(self.categories.values())

    def __delitem__(self, category_name):

        del self.categories[category_name]

    def __getitem__(self, category_name):

        return self.categories[category_name]

    def __contains__(self, category_name):

        return category_name in self.categories

    def __len__(self):

        return len(self.categories)

    def __iadd__(self, other):
        """Add categories or conf categories in self.
        """

        # if other is a conf add a copy of all other categories
        if isinstance(other, Configuration):
            for category in other:
                self += category

        else:  # in case of category
            category = self.get(other.name)

            if category is None:
                self.put(other)

            else:
                for param in other:
                    category.put(param)

        return self

    def __repr__(self):

        return 'Configuration({0})'.format(self.categories)

    def get(self, category_name, default=None):

        return self.categories.get(category_name, default)

    def setdefault(self, category_name, category):

        return self.categories.setdefault(category_name, category)

    def put(self, category):
        """Put a category and return the previous one if exist.
        """

        result = self.get(category.name)
        self.categories[category.name] = category
        return result

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
                if param.value is not None:
                    final_values = values if param.local else foreigns

                    if isinstance(param.value, Exception):
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

        for category in self:
            if not isinstance(category, ParamList):
                for param in category:
                    result.put(param.copy() if copy else param)

        return result

    def add_unified_category(self, name, copy=False, new_content=None):
        """Add a unified category to self and add new_content if not None.
        """

        category = self.get_unified_category(name=name, copy=copy)

        if new_content is not None:
            category += new_content

        self += category

    def add_param_list(self, name, content):
        """Add a list of parameters to self.
        """

        self.categories[name] = content

    def clean(self):
        """Clean this params in setting value to None.
        """

        for category in self:

            category.clean()

    def copy(self, cleaned=False):
        """Copy this Configuration.

        :param bool cleaned: copy this element without parameter values.
        """

        result = Configuration()

        for category in self:
            result.put(category.copy(cleaned=cleaned))

        return result

    def update(self, conf):
        """Update this content with input conf.
        """

        for category in conf:
            category = self.setdefault(
                category.name, category.copy())

            for param in category:
                param = category.setdefault(
                    param.name, param.copy())


class Category(object):
    """Parameter category which contains a dictionary of params.
    """

    def __init__(self, name, *params):
        """
        :param str name: unique in a conf.
        :param list params: Parameters
        """

        super(Category, self).__init__()

        self.name = name
        # set param by names.
        self.params = {}

        for param in params:
            self.params[param.name] = param

    def __iter__(self):

        return iter(self.params.values())

    def __delitem__(self, param_name):

        del self.params[param_name]

    def __getitem__(self, param_name):

        return self.params[param_name]

    def __contains__(self, param_name):

        return param_name in self.params

    def __len__(self):

        return len(self.params)

    def __eq__(self, other):

        return isinstance(other, Category) and other.name == self.name

    def __hash__(self):

        return hash(self.name)

    def __repr__(self):

        return 'Category({0}, {1})'.format(self.name, self.params)

    def __iadd__(self, value):

        if isinstance(value, Category):
            self += value.params.values()

        elif isinstance(value, Iterable):
            for content in value:
                self += content

        elif isinstance(value, Parameter):
            self.put(value)

        else:
            raise Exception('Wrong type to add {0} to {1}. \
Must be a Category, a Parameter or a list of {Parameter, Category}'.format(
                value, self))

        return self

    def setdefault(self, param_name, param):

        return self.params.setdefault(param_name, param)

    def get(self, param_name, default=None):

        return self.params.get(param_name, default)

    def put(self, param):
        """Put a param and return the previous one if exist
        """

        result = self.get(param.name)
        self.params[param.name] = param
        return result

    def clean(self):
        """Clean this params in setting value to None.
        """

        for param in self.params.values():

            param.clean()

    def copy(self, name=None, cleaned=False):
        """Copy this Category.

        :param bool cleaned: copy this element without parameter values.
        """

        if name is None:
            name = self.name

        result = Category(name)

        for param in self:
            _param = param.copy(cleaned=cleaned)
            result.put(_param)

        return result


class Parameter(object):
    """Parameter identified among a category by its name.

    Provide a value (None by default) and a parser (str by default).
    """

    def __init__(
        self, name, parser=None, value=None, critical=False,
        local=True, asitem=None
    ):
        """
        :param str name: unique by category.
        :param value: param value. None if not given.
        :param callable parser: param test deserializer which takes in param
            a str.
        :param bool critical: True if this parameter is critical. A critical
            parameter can require to restart a component for example.
        :param bool local: distinguish local parameters from those found in
            configuration resources.
        :param Category asitem: distinguish parameters from those in a
            ParamList.
        """

        super(Parameter, self).__init__()

        self.name = name
        self._value = value
        self.parser = parser
        self.critical = critical
        self.local = local
        self.asitem = asitem

    def __eq__(self, other):

        return isinstance(other, Parameter) and other.name == self.name

    def __hash__(self):

        return hash(self.name)

    def __repr__(self):

        return 'Parameter({0}, {1}, {2})'.format(
            self.name, self.value, self.parser)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, basestring) and self.parser is not None:
            # parse value if str and if parser exists
            try:
                self._value = self.parser(value)

            except Exception as e:
                self._value = e

        else:
            self._value = value

    def copy(self, name=None, cleaned=False):

        if name is None:
            name = self.name

        kwargs = {
            "name": name,
            "parser": self.parser
        }
        if not cleaned:
            kwargs["value"] = self.value

        result = Parameter(**kwargs)

        return result

    def clean(self):
        """Clean this param in removing values
        """

        self._value = None

    @staticmethod
    def array(item_type=str):
        """Get an array from an input value where items are separated by ','.
        """

        def split(value):
            return [item_type(v) for v in value.split(',')]

        return split

    @staticmethod
    def bool(value):
        return value == 'True' or value == 'true' or value == '1'

    @staticmethod
    def path(value):
        return lookup(value)


class ParamList(object):
    """Identify the list of parameters in a category.
    """

    def __init__(self, parser=None, *args, **kwargs):
        super(ParamList, self).__init__(*args, **kwargs)

        self.parser = parser
