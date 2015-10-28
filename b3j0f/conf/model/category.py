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

__all__ = ['Category']


from collections import Iterable

from .parameter import Parameter


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
        """Clean this params in setting value to None."""

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
