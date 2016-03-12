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

"""model.cat module."""

__all__ = ['Category']

from .base import CompositeModelElement
from .param import Parameter


class Category(CompositeModelElement):
    """Parameter category which contains a dictionary of params."""

    __contenttype__ = Parameter  #: content type.

    __slots__ = ('name', 'local') + CompositeModelElement.__slots__

    def __init__(self, name, local=True, *args, **kwargs):
        """
        :param str name: category name to use.
        """

        super(Category, self).__init__(*args, **kwargs)

        self.name = name
        self.local = local

    def getparams(self, param):
        """Get parameters which match with input param.

        :param Parameter param: parameter to compare with this parameters.
        :rtype: list
        """

        return list(cparam for cparam in self.values() if cparam == param)

    def copy(self, cleaned=False, name=None, *args, **kwargs):

        if name is None:
            name = self.name

        return super(Category, self).copy(name=name, *args, **kwargs)


def category(name, *params):
    """Quick instanciation of category with parameteres."""

    return Category(name=name, melts=params)
