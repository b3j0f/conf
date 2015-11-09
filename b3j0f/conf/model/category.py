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


from six import string_types

from .base import CompositeModelElement
from .parameter import Parameter


class Category(CompositeModelElement):
    """Parameter category which contains a dictionary of params.
    """

    __contenttype__ = Parameter  #: content type.

    __slots__ = ('name', ) + CompositeModelElement.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Category, self).__init__(*args, **kwargs)

        self.name = name

    def getparams(self, pname):
        """Get parameters which match with input pname.

        :param pname: parameter name.
        :type pname: str or regex
        :rtype: list
        """

        result = []

        if isinstance(pname, string_types):

            if pname in self._content:
                result = [self._content[pname]]

        else:
            result = list(
                param for param in self._content.values()
                if pname.match(param.name)
            )

        return result
