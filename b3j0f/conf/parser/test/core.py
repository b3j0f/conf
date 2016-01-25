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

"""parser UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.path import getpath

from ..conf import Configuration
from ..cat import Category
from ..param import Parameter
from ...configurable.core import Configurable
from ...driver.test.base import TestConfDriver
from ..parser import (
    _simpleparser, _exprparser, _resolve, serialize, EXPR_PREFIX
)


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

    def test_bool_ptrue(self):
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


class ConfigurationTest(UTCase):
    """Base class of test which uses a local configuration."""

    def setUp(self):

        self.count = 5

        self.cnames = [None] * self.count
        self.pname = 'param'
        self.pvalues = [None] * self.count

        self.conf = Configuration()

        for i in range(self.count):
            self.cnames[i] = 'c{0}'.format(i)
            self.pvalues[i] = i + 1
            category = Category(
                self.cnames[i],
                Parameter('param', value=self.pvalues[i])
            )
            self.conf += category


class Resolve(ConfigurationTest):

    def test_default(self):
        """Test default params."""

        value = _resolve(conf=self.conf, pname=self.pname)

        self.assertEqual(value, self.pvalues[-1])

    def test_cname(self):
        """Test with cname."""

        for i in range(self.count):

            value = _resolve(
                conf=self.conf, cname=self.cnames[i], pname=self.pname
            )

            self.assertEqual(value, self.pvalues[i])

    def test_nocname(self):
        """Test when category name does not exist."""

        self.assertRaises(
            KeyError, _resolve, cname='test', pname=self.pname, conf=self.conf
        )

    def test_nopname(self):
        """Test when parameter name does not exist."""

        self.assertRaises(KeyError, _resolve, pname='test', conf=self.conf)


class Serialiazer(ConfigurationTest):
    """Test the function serializer."""

    def test_str(self):
        """Test to serialize a string."""

        value = 'test'
        serialized = serialize(value)

        self.assertEqual(value, serialized)

    def test_none(self):
        """Test to serialize None."""

        serialized = serialize(None)

        self.assertIsNone(serialized)

    def test_other(self):
        """Test to serialize other."""

        types = [int, float, complex, dict, list, set]

        for _type in types:

            value = _type()

            serialized = serialize(value)

            self.assertEqual(serialized, '{0}{1}'.format(EXPR_PREFIX, value))


class ExprParser(ConfigurationTest):
    """Test the function _exprparser."""

    def setUp(self):

        super(ExprParser, self).setUp()

        self.configurable = Configurable(
            drivers=[TestConfDriver()]
        )

    def test_empty(self):
        """Test default value."""

        value = _exprparser(svalue='')

        self.assertIsNone(value, '')

    def test_pname(self):
        """Test parameter value."""

        value = _exprparser(svalue='@{0}'.format(self.pname), conf=self.conf)

        self.assertEqual(value, self.pvalues[-1])

    def test_cname(self):
        """Test with a resolve argument."""

        svalue = ''
        for i in range(self.count):
            svalue += '@{0}.{1} +'.format(self.cnames[i], self.pname)

        svalue = svalue[:-2]  # remove the last '+'
        value = _exprparser(svalue=svalue, conf=self.conf)

        self.assertEqual(value, sum(self.pvalues))

    def test_confpath(self):
        """Test with a conf path."""

        svalue = '@://test/param'

        value = _exprparser(
            svalue=svalue, conf=self.conf, configurable=self.configurable
        )

    def test_confpath_cname(self):
        """Test with a conf path and a cname."""

    def test_lookup(self):
        """Test lookup parameter."""

        svalue = '#{0}'.format(getpath(getpath))

        value = _exprparser(svalue=svalue, _globals={'getpath': getpath})

        self.assertIs(value, getpath)

    def test_error_lookup(self):
        """Test a lookup parameter without referencing the python object."""

        svalue = '#{0}'.format(getpath(getpath))

        self.assertRaises(ImportError, _exprparser, svalue=svalue)


if __name__ == '__main__':
    main()
