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

from ..core import Configurable, getconfigurables, applyconfiguration
from ...model.conf import Configuration
from ...model.cat import Category
from ...model.param import Parameter

from ...driver.test.base import TestConfDriver

from tempfile import NamedTemporaryFile

from os import remove


class ConfigurableTest(UTCase):

    def setUp(self):

        self.paths = (
            NamedTemporaryFile().name,
            NamedTemporaryFile().name
        )

        self.configurable = Configurable()

        self.conf = Configuration(
            Category(
                'A',
                Parameter('a', value='a', vtype=str),
                Parameter('_', value=2, vtype=int),
                Parameter('error', vtype=float, svalue='error')
            ),
            Category(
                'B',
                Parameter('a', value='b', vtype=str),
                Parameter('b', value='b', vtype=str)
            )
        )

    def test_configuration_files(self):

        configurable = Configurable(inheritedconf=False)
        configurable.paths = self.paths

        self.assertEqual(configurable.paths, self.paths)

        configurable = Configurable(paths=self.paths, inheritedconf=False)

        self.assertEqual(configurable.paths, self.paths)

    def test_store(self):

        configurable = Configurable()

        self.assertEqual(configurable.store, Configurable.DEFAULT_STORE)

        configurable = Configurable(store=not Configurable.DEFAULT_STORE)

        self.assertEqual(configurable.store, not Configurable.DEFAULT_STORE)

        configurable.store = Configurable.DEFAULT_STORE

        self.assertEqual(configurable.store, Configurable.DEFAULT_STORE)

    def test_configure_to_reconfigure_param(self):
        """Test to reconfigure an object with toconfigure parameter."""

        class ToConfigure(object):
            """Class to configure.
            """
            def __init__(self):
                super(ToConfigure, self).__init__()
                self.test = None

        toconfigure = ToConfigure()

        param = 'test'

        conf = Configuration(Category('TEST', Parameter(param, value=True)))

        self.configurable.configure(conf=conf, toconfigure=toconfigure)
        self.assertTrue(toconfigure.test)

    def test_configure_without_inheritance(self):
        """Test to configure an object without inheritance."""

        @Configurable(
            conf=Category('TEST', Parameter('test', value=True))
        )
        class ToConfigure(object):
            """Class to configure."""

            def __init__(self):

                super(ToConfigure, self).__init__()

                self.test = None

        toconfigure = ToConfigure()

        self.assertTrue(toconfigure.test)

    def test_parser_inheritance(self):

        class _Configurable(Configurable):

            def clsconf(self, *args, **kwargs):

                result = super(_Configurable, self).clsconf(*args, **kwargs)

                result += Category('PLOP')

                return result

        configurable = Configurable()

        _configurable = _Configurable()

        self.assertEqual(
            len(configurable.conf) + 1,
            len(_configurable.conf)
        )

    def test_inheritance(self):
        """Test with inheritance between toconfigure objects."""

        conf0 = Configuration(
            Category(
                'test0',
                Parameter('test0', value=0)
            ),
            Category(
                'test1',
                Parameter('test1', value=1)
            )
        )

        conf1 = Configuration(
            Category(
                'test1',
                Parameter('test1', value=2)
            )
        )

        @Configurable(conf=conf0)
        class Parent(object):
            pass

        self.assertEqual(Parent().test0, 0)
        self.assertEqual(Parent().test1, 1)

        @Configurable(conf=conf1)
        class Child(Parent):
            pass

        self.assertEqual(Child().test0, 0)
        self.assertEqual(Child().test1, 2)

    def test_getconfigurables(self):
        """Test the getconfigurables function."""

        configurable = Configurable()

        configurables = getconfigurables(configurable)

        self.assertFalse(configurables)

        configurable.toconfigure += [configurable]

        configurables = getconfigurables(configurable)

        self.assertEqual(configurables, [configurable])

    def test_applyconfiguration(self):
        """Test the function applyconfiguration."""

        configurable = Configurable()
        configurable.toconfigure += [configurable]

        store = configurable.store

        self.assertEqual(store, Configurable.DEFAULT_STORE)

        configurable.store = not store

        self.assertEqual(configurable.store, not Configurable.DEFAULT_STORE)

        applyconfiguration(toconfigure=configurable)

        self.assertEqual(configurable.store, Configurable.DEFAULT_STORE)

    def test_multiconf(self):
        """Test to get configuration from multi resources."""

        tcd0, tcd1 = TestConfDriver(), TestConfDriver()

        tcd0.confbypath['test0'] = Configuration(
            Category(
                'test',
                Parameter('test0', value='0')
            )
        )
        tcd0.confbypath['test1'] = Configuration(
            Category(
                'test',
                Parameter('test1', value='1')
            )
        )
        tcd1.confbypath['test1'] = Configuration(
            Category(
                'test',
                Parameter('test2', value='=@://test0/test.test0 + @://test1/test.test1'),
                Parameter('test3', value=3)
            )
        )

        configurable = Configurable(drivers=[tcd0, tcd1])

        configurable.applyconfiguration(
            toconfigure=configurable, paths=['test0', 'test1']
        )

        self.assertEqual(configurable.test0, '0')
        self.assertEqual(configurable.test1, '1')
        self.assertEqual(configurable.test2, '01')
        self.assertEqual(configurable.test3, 3)

    def test_safe(self):
        """Test to configurate a configurable in a safe context."""

        conf = Configuration(
            Category(
                'test',
                Parameter('test', svalue='=open')
            )
        )

        configurable = Configurable(conf=conf)

        self.assertRaises(
            Parameter.Error,
            configurable.applyconfiguration,
            toconfigure=configurable, paths='test'
        )

    def test_unsafe(self):
        """Test to configurate a configurable in an unsafe context."""

        conf = Configuration(
            Category(
                'test',
                Parameter('test', svalue='=int')
            )
        )

        configurable = Configurable(conf=conf, safe=False)

        configurable.applyconfiguration(
            toconfigure=configurable, paths='test'
        )

        self.assertIs(configurable.test, int)


if __name__ == '__main__':
    main()
