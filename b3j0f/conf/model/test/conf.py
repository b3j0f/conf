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

"""Configuration UTs."""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..conf import Configuration
from ..cat import Category
from ..param import Parameter


class ConfigurationTest(UTCase):
    """Test exprparser."""

    def setUp(self):

        self.count = 5

        self.conf = Configuration()

        for count in range(self.count):

            cat = Category('{0}'.format(count))
            self.conf += cat

            for index in range(count):

                param = Parameter(
                    name='p{0}{1}'.format(count, index),
                    value=count + index
                )

                if (index + count) % 2 == 0:  # add errors
                    param._error = True
                    param.value = None

                cat += param

    def test_resolve(self):
        """Test the method resolve."""

        for cat in self.conf:
            for param in cat:
                param.svalue = '=1'

        self.conf.resolve()

        for cat in self.conf:
            for param in cat:
                self.assertEqual(param.value, 1)

    def test_unify(self):
        """Test the function unify."""

        unifiedconf = self.conf.unify()

        self.assertNotIn(Configuration.ERRORS, self.conf)
        self.assertIn(Configuration.ERRORS, unifiedconf)

        errors = unifiedconf[Configuration.ERRORS]
        self.assertEqual(len(errors), (self.count * (self.count + 1) // 8) + 1)

        self.assertNotIn(Configuration.VALUES, self.conf)
        self.assertIn(Configuration.VALUES, unifiedconf)

        self.assertNotIn(Configuration.FOREIGNS, self.conf)
        self.assertIn(Configuration.FOREIGNS, unifiedconf)

    def test_get_unified_category(self):
        """Test the method get_unified_category."""

        cat = self.conf.get_unified_category(name='test')

        self.assertEqual(len(cat), self.count * 2)

    def test_pvalue(self):
        """Test the method pvalue."""

        for cat in self.conf:

            for param in cat:

                value = param.value

                if value is None:
                    continue

                pvalue = self.conf.pvalue(pname=param.name)

                self.assertEqual(value, pvalue)

                pvalue = self.conf.pvalue(pname=param.name, cname=cat.name)

                self.assertEqual(value, pvalue)

    def test_update(self):
        """Test the method update."""

        copiedcat = self.conf['0'].copy()
        copiedcat += Parameter('test', value=-1)

        for param in copiedcat:
            param.value = -1

        conf = Configuration(
            Category('test', Parameter('test')),
            copiedcat
        )

        self.conf.update(conf)

        self.assertIs(self.conf['test'], conf['test'])

        for cat in conf:
            if cat.name == 'test':
                self.assertIs(self.conf['test'], cat)

            else:
                for param in cat:

                    if cat.name == '0':
                        self.assertIn('test', cat)

                        self.assertEqual(param.value, -1)

                    elif param._error is None:

                        self.assertEqual(
                            param.value, int(cat.name) + int(param.name)
                        )


if __name__ == '__main__':
    main()
