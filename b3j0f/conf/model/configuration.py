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


from b3j0f.utils.version import OrderedDict

from .category import Category


class Configuration(object):
    """Manage conf such as a list of Categories.

    The order of categories permit to ensure param overriding.
    """

    ERRORS = '_ERRORS'  #: category name which contains errors.
    VALUES = '_VALUES'  #: category name which contains local param values.
    FOREIGNS = '_FOREIGN'  #: category name which contains foreign params vals.

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
        """Add categories or conf categories in self."""

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
        """Put a category and return the previous one if exist."""

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

        for category in self:

            for param in category:

                pvalue = None

                try:  # get value
                    pvalue = param.value

                except:
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

        for category in self.categories.values():
            for param in category.values():
                result.put(param.copy() if copy else param)

        return result

    def add_unified_category(self, name=VALUES, copy=False, new_content=None):
        """Add a unified category to self and add new_content if not None."""

        category = self.get_unified_category(name=name, copy=copy)

        if new_content is not None:
            category += new_content

        self += category

    def add_param_list(self, name, content):
        """Add a list of parameters to self."""

        self.categories[name] = content

    def clean(self):
        """Clean this params in setting value to None."""

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
        """Update this content with input conf."""

        for category in conf:
            category = self.categories.setdefault(
                category.name, category.copy()
            )

            for param in category:
                param = category.setdefault(
                    param.name, param.copy()
                )
