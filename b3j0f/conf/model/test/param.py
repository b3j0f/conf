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

"""model.param UTs."""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..param import Parameter, PType
from ..parser import ParserError


class PTypeTest(UTCase):
    """Test PType."""

    def setUp(self):

        self.ptype = PType(_type=Parameter)

    def test_isinstance(self):
        """Test if isinstance."""

        self.assertIsInstance(Parameter(''), self.ptype)

    def test_PTypeisinstance(self):
        """Test isinstance of PTYpe."""

        self.assertIsInstance(self.ptype, self.ptype)

    def test_isnotinstance(self):
        """Test is not instance."""

        self.assertNotIsInstance(None, self.ptype)

    def test_issubclass(self):
        """Test is subclass."""

        self.assertTrue(issubclass(Parameter, self.ptype))

    def test_PTypeissubclass(self):
        """Test is subclass of PType."""

        self.assertTrue(issubclass(PType, self.ptype))

    def test_notissubclass(self):
        """Test is not subclass."""

        self.assertFalse(issubclass(None.__class__, self.ptype))

    def test_instanciate(self):
        """Test to instanciate a parameter."""

        value = 'test'

        param = self.ptype(value)

        self.assertIsInstance(param, Parameter)
        self.assertEqual(value, param.name)

    def test_instanciate_kwargs(self):
        """Test to instanciate a parameter with kwargs."""

        value = {'name': 'test'}

        param = self.ptype(value)

        self.assertIsInstance(param, Parameter)
        self.assertEqual(value['name'], param.name)

    def test_instanciate_args(self):
        """Test to instanciate a parameter with args."""

        value = ['test']

        param = self.ptype(value)

        self.assertIsInstance(param, Parameter)
        self.assertEqual(value[0], param.name)

    def test_instanciateerror(self):
        """Test to instanciate with an error."""

        self.assertRaises(ParserError, self.ptype, 2)


if __name__ == '__main__':
    main()
