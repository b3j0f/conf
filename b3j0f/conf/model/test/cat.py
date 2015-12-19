#!/usr/bin/env python
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

"""model.cat UTs."""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..cat import Category
from ..param import Parameter


class CategoryTest(UTCase):
    """Test exprparser."""

    def setUp(self):

        self.name = 'test'
        self.cat = Category(name=self.name)

        for i in range(1, len(self.name)):
            param = Parameter(self.name[:i])
            rparam = Parameter('^{0}.*'.format(self.name[:i]))
            self.cat += param, rparam

    def test_name(self):
        """Test name."""

        self.assertEqual(self.cat.name, self.name)

    def test_getparams(self):
        """Test the method getparams."""

        param = Parameter(self.name)

        params = self.cat.getparams(param=param)

        self.assertEqual(len(self.name) - 1, len(params))


if __name__ == '__main__':
    main()
