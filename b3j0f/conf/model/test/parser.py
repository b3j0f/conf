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


from unittest import main

from b3j0f.utils.ut import UTCase

from ..configuration import Configuration
from ..category import Category
from ..parameter import Parameter

from ...configurable.core import Configurable


from ..parser import ParserError, _simpleparser, _exprparser


class SimpleParserTest(UTCase):
    """Test the function _simpleparser."""

    def test_bool_empty(self):
        """Test bool type with an empty string."""

        value = _simpleparser(svalue='', _type=bool)

        self.assertFalse(value)

    def test_bool_1(self):
        """Test bool type with 1."""

        value = _simpleparser(svalue='1', _type=bool)

        self.assertTrue(value)

    def test_bool_true(self):
        """Test bool type with true."""

        value = _simpleparser(svalue='true', _type=bool)

        self.assertTrue(value)

    def test_bool_True(self):
        """Test bool type with True value."""

        value = _simpleparser(svalue='True', _type=bool)

        self.assertTrue(value)

    def test_bool_wrong(self):
        """Test bool type with false value."""

        value = _simpleparser(svalue='TrUe', _type=bool)

        self.assertFalse(value)

    def test_string(self):
        """Test default with string type."""

        value = _simpleparser(svalue='test')

        self.assertEqual(value, 'test')


class ExprParser(UTCase):
    """Test the function _exprparser."""

    def test(self):
        """Test default value."""

        value = _exprparser(svalue='')

        self.assertFalse(value, '')


if __name__ == '__main__':
    main()
