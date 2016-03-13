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

"""expr resolver cls UTs."""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..base import ExprResolver
from ..registry import resolve


class TestExprResolver(ExprResolver):

    __resolver__ = 'test'

    def __call__(self, *args, **kwargs):

        return '{0}{0}'.format(TestExprResolver.__resolver__)


class ExprResolverTest(UTCase):
    """Test ExprResolver."""

    def setUp(self):

        self.test = 'test'

    def test__resolver__(self):

        class Test(ExprResolver):

            __register__ = True

            __resolver__ = self.test

            def __call__(*args, **kwargs):

                return self.test.upper()

        result = resolve(expr='', name=self.test)

        self.assertEqual(result, self.test.upper())

    def test__name__(self):

        class Test(ExprResolver):

            __register__ = True

            def __call__(*args, **kwargs):

                return self.test.upper()

        result = resolve(expr='', name=Test.__name__)

        self.assertEqual(result, self.test.upper())


if __name__ == '__main__':
    main()
