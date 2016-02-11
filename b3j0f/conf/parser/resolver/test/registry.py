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

from ..registry import (
    ResolverRegistry, names, resolve, register, loadresolvers, defaultname,
    getname
)


class GetNameTest(UTCase):

    def test_routine(self):

        name = getname(lambda **kwargs: None)

        self.assertEqual(name, (lambda: None).__name__)

    def test_class(self):

        name = getname(GetNameTest)

        self.assertEqual(name, GetNameTest.__name__)

    def test_registeredclass(self):

        class Test(object):

            __resolver__ = 'test'

        name = getname(Test)

        self.assertEqual(name, Test.__resolver__)

    def test_callable(self):

        class Test(object):

            def __call__(self):
                pass

        name = getname(Test())

        self.assertEqual(name, Test.__name__)

    def test_registeredcallable(self):

        class Test(object):

            __resolver__ = 'test'

            def __call__(self):
                pass

        name = getname(Test())

        self.assertEqual(name, Test.__resolver__)

    def test_notcallable(self):

        self.assertRaises(TypeError, getname, 2)


class ResolverRegistryTest(UTCase):

    def test_defaultregistry(self):

        reg = ResolverRegistry()

        self.assertIsNone(reg.default)

        self.assertFalse(reg.resolvers)

    def test_defaultwithregistry(self):

        name = 'test'

        reg = ResolverRegistry(**{name: lambda **_: None})

        self.assertIs(reg.default, name)

        self.assertTrue(reg.resolvers)

    def test_nodefaultwithoutregistry(self):

        func = lambda **_: None

        reg = ResolverRegistry(default=func)

        self.assertIs(reg.default, func.__name__)

        self.assertTrue(reg.resolvers)

    def test_defaultandregistry(self):

        reg = ResolverRegistry('test', test=lambda **_: None)

        self.assertEqual(reg.default, 'test')
        self.assertIn('test', reg.resolvers)

    def test_defaultnotinregistry(self):

        self.assertRaises(
            NameError, ResolverRegistry, 'test2', test=lambda **_: None
        )

    def test_nonames(self):

        reg = ResolverRegistry()

        self.assertFalse(reg.names)

    def test_names(self):

        reg = ResolverRegistry(test=lambda **_: None, example=lambda **_: None)

        self.assertEqual(set(reg.names), set(['test', 'example']))


if __name__ == '__main__':
    main()
