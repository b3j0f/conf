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

from __future__ import absolute_import

from unittest import main

from six import string_types

from b3j0f.utils.ut import UTCase

from ..param import Parameter, PType, BOOL, ARRAY, Array
from parser import ParserError


class PTypeTest(UTCase):
    """Test PType."""

    def setUp(self):

        self.ptype = PType(ptype=Parameter)

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

        self.assertFalse(issubclass(type(None), self.ptype))

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

    def test_instanciate_object(self):
        """Test to instanciate a parameter with an object such as name."""

        svalue = 1

        value = PType(str)(svalue)

        self.assertIsInstance(value, str)
        self.assertEqual(value, str(1))

    def test_instanciateerror(self):
        """Test to instanciate with an error."""

        self.assertRaises(ParserError, self.ptype, {'': None})


class BoolTest(UTCase):
    """Test the bool class."""

    def test(self):
        """Test to auto convert a value from BOOL."""

        param = Parameter(svalue='false', ptype=BOOL)

        self.assertFalse(param.value)

        param.svalue = 'true'

        self.assertTrue(param.value)


class ArrayTest(UTCase):
    """Test the array class"""

    def test_ARRAY(self):
        """Test to auto convert a value from ARRAY."""

        ptype = ARRAY

        param = Parameter(svalue='', ptype=ptype)

        self.assertEqual(param.value, [])
        self.assertIsInstance(param.value, ptype)

        param = Parameter(svalue='a', ptype=ptype)

        self.assertEqual(param.value, ['a'])
        self.assertIsInstance(param.value, ptype)

        param = Parameter(svalue='a,b', ptype=ptype)

        self.assertEqual(param.value, ['a', 'b'])
        self.assertIsInstance(param.value, ptype)

    def test_ptype(self):
        """Test to auto convert a value from an Array with a specific type."""

        ptype = Array(ptype=int)

        param = Parameter(svalue='', ptype=ptype)

        self.assertEqual(param.value, [])
        self.assertIsInstance(param.value, ptype)

        param = Parameter(svalue='1', ptype=ptype)

        self.assertEqual(param.value, [1])
        self.assertIsInstance(param.value, ptype)

        param = Parameter(svalue='1,2', ptype=ptype)

        self.assertEqual(param.value, [1, 2])
        self.assertIsInstance(param.value, ptype)

        param = Parameter(svalue='1,type', ptype=ptype)

        self.assertRaises(TypeError, getattr(param, 'value'))

        ptype = Array(ptype=Parameter)

        param = Parameter(
            svalue='b3j0f.conf.model.param.Parameter', ptype=ptype
        )
        self.assertIsInstance(param.value, ptype)


class ParameterTest(UTCase):
    """Test a parameter."""

    def setUp(self):

        self.param = Parameter('test')

    def test___eq__strstr(self):
        """Test parameter comparison between str."""

        param = self.param.copy()

        self.assertIsInstance(param.name, string_types)
        self.assertEqual(param, self.param)

        param.name = param.name.upper()

        self.assertIsInstance(param.name, string_types)
        self.assertNotEqual(param, self.param)

    def test___eq__restr(self):
        """Test parameter comparison between regex and string."""

        param = Parameter('tes.')

        self.assertNotIsInstance(param.name, string_types)

        self.assertEqual(self.param, param)
        self.assertEqual(param, self.param)

        param.name = self.param.name + '.'

        self.assertNotIsInstance(param.name, string_types)
        self.assertNotEqual(self.param, param)
        self.assertNotEqual(param, self.param)

    def test___eq__rere(self):
        """Test parameter comparison between two regex."""

        self.param.name = '.*'
        param = self.param.copy()

        self.assertNotIsInstance(param.name, string_types)
        self.assertEqual(self.param, param)

        param.name = '.'
        self.assertNotIsInstance(param.name, string_types)
        self.assertNotEqual(self.param, param)

    def test_hash(self):
        """Test the method hash."""

        param = Parameter('test', )

        self.assertEqual(hash(param), hash(self.param))

        paramset = set((self.param, self.param.copy(), param))

        self.assertEqual(len(paramset), 1)

    def test_repr(self):
        """Test the method repr."""

        paramrepr = repr(self.param)
        cparamrepr = repr(self.param.copy())

        self.assertEqual(cparamrepr, paramrepr)

    def test_conf_name(self):
        """Test the method conf_name."""

        conf_name = self.param.conf_name

        self.assertEqual(
            conf_name, '{0}{1}'.format(self.param.name, Parameter.CONF_SUFFIX)
        )

    def test_svalue(self):
        """Test the property svalue."""

        self.assertIsNone(self.param.svalue)

        # check if parameter clean its protected attributes
        self.param._value = 1
        self.param._error = 1
        self.param.svalue = ''

        self.param.value = None

        self.assertIsNone(self.param._error)
        self.assertIsNone(self.param._value)
        self.assertEqual(self.param.svalue, '')

    def test_svalue_from_value(self):
        """Test to set svalue from value."""

        self.assertIsNone(self.param.svalue)

        # check if parameter clean it protected attributes
        self.param.value = '1'

        self.assertEqual(self.param.svalue, self.param.value)

    def test_svalue_nonify(self):
        """Test to nonify svalue."""

        self.param.value = 1
        self.param._error = 1
        self.param.svalue = None

        self.assertIsNotNone(self.param._value)
        self.assertIsNotNone(self.param._error)

        # nonify only if svalue exist
        self.param.svalue = '=1'
        self.assertIsNone(self.param._value)
        self.assertIsNone(self.param._error)

    def test_value(self):
        """Test the property value."""

        self.assertIsNone(self.param.value)

        self.param.value = 1

        self.assertEqual(self.param.value, 1)

    def test_value_from_svalue(self):
        """Test to set value from svalue."""

        self.param.svalue = '=1'

        value = self.param.value

        self.assertEqual(value, 1)

    def test_value_error_ptype(self):
        """Test to set value with wrong type."""

        self.param.ptype = int

        self.assertRaises(
            TypeError, lambda x: setattr(self.param, 'value', x), '3'
        )

        self.assertIsInstance(self.param.error, TypeError)

        self.param.svalue = ''

        self.assertRaises(Parameter.Error, lambda: getattr(self.param, 'value'))

    def test_copy(self):
        """Test the method copy."""

        param = Parameter(
            name='test',
            local=not Parameter.DEFAULT_LOCAL,
            ptype=int,
            conf=1,
            value=1,
            svalue='=1'
        )

        cparam = param.copy()

        self.assertEqual(param.name, cparam.name)
        self.assertEqual(param.local, cparam.local)
        self.assertEqual(param.ptype, cparam.ptype)
        self.assertEqual(param.conf, cparam.conf)
        self.assertEqual(param.value, cparam.value)
        self.assertEqual(param.svalue, cparam.svalue)

    def test_copy_cleaned(self):
        """Test the method copy with cleaned as True."""

        param = Parameter(
            name='test',
            local=not Parameter.DEFAULT_LOCAL,
            ptype=int,
            conf=1,
            value=1,
            svalue='=1'
        )

        cparam = param.copy(value=None, svalue=None)

        self.assertEqual(param.name, cparam.name)
        self.assertEqual(param.local, cparam.local)
        self.assertEqual(param.ptype, cparam.ptype)
        self.assertEqual(param.conf, cparam.conf)
        self.assertIsNone(cparam.value)
        self.assertIsNone(cparam.svalue)

    def test_simple_conversion(self):
        """Test simple conversion of parameter."""

        param = Parameter('', svalue='=1.0', ptype=int)

        self.assertIsInstance(param.value, int)

        param = Parameter('', svalue='=1.0')

        self.assertIsInstance(param.value, float)

if __name__ == '__main__':
    main()
