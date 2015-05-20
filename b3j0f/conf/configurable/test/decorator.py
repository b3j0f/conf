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


from unittest import main, TestCase

from b3j0f.conf.params import Parameter, Category
from b3j0f.conf.configurable.core import Configurable
from b3j0f.conf.configurable.decorator import conf_paths, add_category


class DecoratorTest(TestCase):
    """Configuration Manager unittest class.
    """

    def test_conf_paths(self):

        test_conf_paths = ["test1", "test2"]

        @conf_paths(*test_conf_paths)
        class TestConfigurable(Configurable):
            pass

        testConfigurable = TestConfigurable()

        configurable_conf_paths = testConfigurable.conf_paths

        for i in range(1, len(test_conf_paths)):
            self.assertEqual(test_conf_paths[-i], configurable_conf_paths[-i])

    def test_add_category(self):

        CATEGORY = 'TEST'

        @add_category(name=CATEGORY)
        class TestConfigurable(Configurable):
            pass

        tc = TestConfigurable()

        self.assertTrue(CATEGORY in tc.conf)
        self.assertTrue(len(tc.conf) > 0)
        self.assertTrue(len(tc.conf[CATEGORY]) > 0)

        category_len = len(tc.conf[CATEGORY])

        parameters = [Parameter('a'), Parameter('b')]

        @add_category(name=CATEGORY, content=parameters)
        class TestConfigurable(Configurable):
            pass

        tc = TestConfigurable()

        self.assertTrue(CATEGORY in tc.conf)
        self.assertTrue(len(tc.conf) > 0)
        self.assertEqual(
            len(tc.conf[CATEGORY]), category_len + len(parameters))

        @add_category(name=CATEGORY, unified=False)
        class TestConfigurable(Configurable):
            pass

        tc = TestConfigurable()

        self.assertTrue(CATEGORY in tc.conf)
        self.assertTrue(len(tc.conf) > 0)
        self.assertEqual(len(tc.conf[CATEGORY]), 0)

        @add_category(name=CATEGORY, unified=False, content=parameters)
        class TestConfigurable(Configurable):
            pass

        tc = TestConfigurable()

        self.assertTrue(CATEGORY in tc.conf)
        self.assertTrue(len(tc.conf) > 0)
        self.assertEqual(len(tc.conf[CATEGORY]), len(parameters))

        category = Category(CATEGORY, *parameters)

        @add_category(name=CATEGORY, unified=False, content=category)
        class TestConfigurable(Configurable):
            pass

        tc = TestConfigurable()

        self.assertTrue(CATEGORY in tc.conf)
        self.assertTrue(len(tc.conf) > 0)
        self.assertEqual(len(tc.conf[CATEGORY]), len(category))

if __name__ == '__main__':
    main()
