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

from ..base import ModelElement, CompositeModelElement


class ModelElementTest(UTCase):
    """Test ModelElement."""

    class TestME(ModelElement):
        """ModelElement test."""

        def __init__(self, name=None, *args, **kwargs):

            super(ModelElementTest.TestME, self).__init__(
                *args, **kwargs
            )

            self.cleaned = False
            self.name = name

        def clean(self, *args, **kwargs):

            self.cleaned = True

    def setUp(self):

        self.me = ModelElementTest.TestME()

    def test_clean(self):
        """Test to clean a model element."""

        self.assertFalse(self.me.cleaned)

        self.me.clean()

        self.assertTrue(self.me.cleaned)

    def test_copy(self):
        """Test to copy a model element."""

        me = self.me.copy()

        self.assertFalse(me.cleaned)

        me = self.me.copy(cleaned=True)

        self.assertTrue(me.cleaned)


class CompositeModelElementTest(UTCase):
    """Test the CompositeModelElement."""

    class TestCME(CompositeModelElement):
        """CompositeModelElement test."""

    def setUp(self):

        self.count = 50

        content = [
            ModelElementTest.TestME(name=str(i)) for i in range(self.count)
        ]

        self.cme = CompositeModelElementTest.TestCME(*content)

    def test___iter__(self):
        """Test the __iter__ method."""

        iterator = iter(self.cme)

        counts = list(range(self.count))

        for i in range(self.count):

            item = next(iterator)
            counts.remove(int(item.name))

        self.assertEqual(len(counts), 0)

    def test___getitem__(self):
        """Test the __getitem__ method."""

        mes = list(self.cme.content)

        for i in range(self.count):

            me = self.cme[str(i)]
            me = self.cme[me]
            mes.remove(me)

        self.assertEqual(0, len(mes))

    def test___setitem__(self):
        """Test the __setitem__ method."""

        for i in range(self.count):

            me = ModelElement()
            self.cme[str(i)] = me

        for me in self.cme:

            self.assertFalse(hasattr(me, 'name'))

        for i in range(self.count):

            me = ModelElementTest.TestME(name=str(i))
            self.cme[me] = me

        names = set(me.name for me in self.cme)

        self.assertEqual(len(names), self.count)

    def test___delitem__(self):
        """Test the __delitem__ method."""

        for i in range(self.count):

            del self.cme[str(i)]

        self.assertEqual(len(self.cme), 0)

        for i in range(self.count):

            me = ModelElementTest.TestME(name=str(i))
            self.cme[str(i)] = me
            del self.cme[me]

        self.assertEqual(len(self.cme), 0)

    def test___getattr__(self):
        """Test the method __getattr__."""

        for i in range(self.count):

            me = getattr(self.cme, str(i))
            self.assertEqual(me.name, str(i))

    def test___contains__(self):
        """Test the method __contains__."""

        for i in range(self.count):

            me = self.cme[str(i)]

            self.assertIn(str(i), self.cme)
            self.assertIn(me, self.cme)

        self.assertNotIn(str(i + 1), self.cme)

    def test___len__(self):
        """Test the method __len__."""

        self.assertEqual(len(self.cme), self.count)

        self.cme.clear()

        self.assertEqual(len(self.cme), 0)

    def test___iadd__(self):
        """Test the method __iadd__."""

if __name__ == '__main__':
    main()
