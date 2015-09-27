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

"""Configuration definition objects.
"""

__all__ = ['Configuration', 'Category', 'Parameter']


from collections import Iterable

from b3j0f.utils.version import basestring, OrderedDict
from b3j0f.utils.path import lookup

from json import loads as jsonloads


class Configuration(object):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    ERRORS = 'ERRORS'  #: category name which contains errors.
    VALUES = 'VALUES'  #: category name which contains local parameter values.
    FOREIGNS = 'FOREIGN'  #: category name which contains not local parameters.

    def __init__(self, *categories):
        """
        :param list categories: categories to configure.
        """

        super(Configuration, self).__init__()

        self.categories = OrderedDict()

        # set categories
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
            category = self.categories.get(other.name)

            if category is None:
                self.put(other)

            else:
                for param in other:
                    category.put(param)

        return self

    def __repr__(self):

        return 'Configuration({0})'.format(self)

    def get(self, category_name, default=None):
        """Get a category by its name.

        :param str category_name: category name.
        :param default: default value if category_name is not registered.
        :return: related Category.
        :rtype: Category
        """

        return self.categories.get(category_name, default)

    def setdefault(self, category_name, category):
        """Register a category with specific name if name not already used.

        :param str category_name: category name.
        :param Category category: to register.
        :return: existing category or input category if no category have been
            registered with this name.
        :rtype: Category
        """

        return self.categories.setdefault(category_name, category)

    def put(self, category):
        """Put a category and return the previous one if exist.
        """

        result = self.categories.get(category.name)
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

        for category in self.categories.values():
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

        for category in self.categories.values():
            if not isinstance(category, ParamList):
                for param in category.values():
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

        for category in self.categories:

            category.clean()

    def copy(self, cleaned=False):
        """Copy this Configuration.

        :param bool cleaned: copy this element without parameter values.
        """

        result = Configuration()

        for category in self.categories.values():
            result.put(category.copy(cleaned=cleaned))

        return result

    def update(self, conf):
        """Update this content with input conf.
        """

        for category in conf:
            category = self.categories.setdefault(
                category.name, category.copy()
            )

            for param in category:
                param = category.setdefault(
                    param.name, param.copy()
                )


class Category(dict):
    """Parameter category which contains a dictionary of params.
    """

    def __init__(self, name, *params):
        """
        :param str name: unique in a conf.
        :param list params: Parameters
        """

        super(Category, self).__init__()

        self.name = name

        for param in params:
            self[param.name] = param

    def __iter__(self):

        return iter(self.values())

    def __eq__(self, other):

        return isinstance(other, Category) and other.name == self.name

    def __hash__(self):

        return hash(self.name)

    def __repr__(self):

        return 'Category({0}, {1})'.format(self.name, self.values())

    def __iadd__(self, value):

        if isinstance(value, Category):
            self += value.values()

        elif isinstance(value, Iterable):
            for content in value:
                self += content

        elif isinstance(value, Parameter):
            self.put(value)

        else:
            raise Exception(
                'Wrong value {0} to add. (Param | Category)+ expected.'
                .format(value)
            )

        return self

    def put(self, param):
        """Put a param and return the previous one if exist
        """

        result = self.get(param.name)
        self[param.name] = param

        return result

    def clean(self):
        """Clean this params in setting value to None.
        """

        for param in self.values():

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

    class Error(Exception):
        """Handle Parameter errors.
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
        """Get parameter value.

        :return: parameter value.
        """
        return self._value

    @value.setter
    def value(self, value):
        """Change of parameter value.

        :param value: new value to use. If value is a str and not parable by
            this parameter, the value becomes the parsing exception.
        """

        if isinstance(value, basestring) and self.parser is not None:
            # parse value if str and if parser exists
            try:
                self._value = self.parser(value)

            except Exception as ex:
                self._value = ex

        else:
            self._value = value

    def copy(self, name=None, cleaned=False):
        """Get a copy of the parameter with specified name and new value if
        cleaned.

        :param str name: new parameter name.
        :param bool cleaned: clean the value.
        :return: new parameter.
        """
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
    def bool(value):
        """Boolean value parser.

        :param str value: value to parse.
        :return: True if value in [True, true, 1]. False Otherwise.
        :rtype: bool
        """

        return value == 'True' or value == 'true' or value == '1'

    @staticmethod
    def path(value):
        """Python class path value parser.

        :param str value: python class path to parse.
        :return: lookup(value).
        """

        return lookup(value)

    @staticmethod
    def json(value):
        """Get a data from a json data format.

        :param str value: json format to parse.
        :return: data.
        :rtype: str, list, dict, int, float or bool
        """

        return jsonloads(value)

    @staticmethod
    def _typedjson(value, cls):
        """Private static method which uses the json method and check if result
        inherits from the cls. Otherwise, raise an error.

        :param str value: value to parse in a json format.
        :param type cls: expected result class.
        :return: parsed value.
        :rtype: cls
        """

        result = Parameter.json(value)

        if not isinstance(result, cls):
            raise Parameter.Error(
                'Wrong type: {0}. {1} expected.'.format(value, cls)
            )

        return result

    @staticmethod
    def dict(value):
        """Get a dict from a dict json format.

        :param str value: dictionary json format to parse.
        :return: parsed dictionary.
        :rtype: dict
        :raises: Parameter.Error if value is not a dict json format.
        """

        return Parameter._typedjson(value, dict)

    @staticmethod
    def array(value):
        """Get an array from:

        - an array json format.
        - a list of item name separated by commas.

        :param str value: list of items to parse. The format must be of

            - array json type.
            - named item separated by commas.

        :return: parsed array.
        :rtype: list
        :raises: Parameter.Error if value is not a list json format.
        """

        if value[0] == '[':
            result = Parameter._typedjson(value, list)

        else:
            result = list(item for item in value.split(','))

        return result


class ParamList(object):
    """Identify the list of parameters in a category.
    """
