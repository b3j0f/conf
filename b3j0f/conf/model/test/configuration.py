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


from ..parser import ParserError


class ConfigurationTest(UTCase):
    """Test exprparser."""

    def setUp(self):

        self.configuration = Configuration(
            Category(
                'ctest',
                Parameter('ptest')
            )
        )

        self.configurable = Configurable()

    def _assertValue(
        self, svalue, _type=object, _globals=None, _locals=None, exp=False
    ):
        """Assert value with input _type."""

        exprparser = getexprparser()

        if exp:

            self.assertRaises(
                ParserError, exprparser,
                svalue=svalue, _type=_type, _globals=_globals, _locals=_locals
            )

        value = exprparser(
            svalue=svalue, _type=_type, _globals=_globals, _locals=_locals
        )

        self.assertIsInstance(value, _type)

    def test_int(self):
        """Test exprparser with int _type."""

        exprparser = getexprparser()

        value = exprparser(svalue="1", _type=int)

        self.assertIsInstance(value, int)

    def test_default(self):
        """Test getexprparser with default parameters."""

        exprparser = getexprparser()

        self.assertIsNotNone(exprparser)

if __name__ == '__main__':
    main()
