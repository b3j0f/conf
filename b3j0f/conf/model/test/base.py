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

"""model.base UTs."""

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

        def copy(self, *args, **kwargs):

            result = super(ModelElementTest.TestME, self).copy(*args, **kwargs)

            result.name = self.name

            return result

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

    def test_cleaned_copy(self):
        """Test to a copied model element."""

        me = self.me.copy(cleaned=True)

        self.assertTrue(me.cleaned)


class CompositeModelElementTest(UTCase):
    """Test the CompositeModelElement."""

    class TestCME(CompositeModelElement):
        """CompositeModelElement test."""

        __contenttype__ = ModelElementTest.TestME

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

        cmelen = len(self.cme)

        for i in range(self.count):

            me = self.cme.pop(str(i))

            _cmelen = len(self.cme)
            self.assertEqual(_cmelen, cmelen - 1)

            self.cme += me

            _cmelen = len(self.cme)
            self.assertEqual(_cmelen, cmelen)
            self.assertFalse(self.cme[str(i)].cleaned)

            me = me.copy()
            me.cleaned = True

            self.cme += me

            self.assertEqual(_cmelen, len(self.cme))
            self.assertTrue(self.cme[str(i)].cleaned)

    def test___iadd__me(self):
        """Test the method __iadd__ with a CompositeModelElement."""

        ccme = self.cme.copy()

        ccme.clear()

        self.assertFalse(ccme)

        ccme += self.cme

        self.assertEqual(len(ccme), len(self.cme))

    def test___iadd__iterable(self):
        """Test the method __iadd__ with an iterable."""

        ccme = self.cme.copy()

        ccme.clear()

        self.assertFalse(ccme)

        ccme += list(self.cme.content)

        self.assertEqual(len(ccme), len(self.cme))

    def test___iadd__error(self):
        """Test the method __iadd__ without ModelElement."""

        self.assertRaises(TypeError, self.cme.__iadd__, None)

    def test___isub__me(self):
        """Test the method __isub__ with a model element."""

        for i in range(self.count):

            self.cme -= self.cme[str(i)]

        self.assertFalse(self.cme)

    def test___isub__mes(self):
        """Test the method __isub__ with model elements."""

        self.cme -= list(self.cme.content)

        self.assertFalse(self.cme)

    def test___isub__cme(self):
        """Test the method __isub__ with a CompositeModelElement."""

        self.cme -= self.cme

        self.assertFalse(self.cme)

    def test___isub__error(self):
        """Test the method __isub__ without ModelElement."""

        self.assertRaises(TypeError, self.cme.__isub__, None)

    def test___ixor__(self):
        """Test the method __ixor__."""

        cmelen = len(self.cme)

        for i in range(self.count):

            me = self.cme.pop(str(i))

            _cmelen = len(self.cme)
            self.assertEqual(_cmelen, cmelen - 1)

            self.cme ^= me

            _cmelen = len(self.cme)
            self.assertEqual(_cmelen, cmelen)
            self.assertFalse(self.cme[str(i)].cleaned)

            me = me.copy()
            me.cleaned = True

            self.cme ^= me

            self.assertEqual(_cmelen, len(self.cme))
            self.assertFalse(self.cme[str(i)].cleaned)

    def test___ixor__me(self):
        """Test the method __ixor__ with a CompositeModelElement."""

        ccme = self.cme.copy()

        ccme.clear()

        self.assertFalse(ccme)

        ccme ^= self.cme

        self.assertEqual(len(ccme), len(self.cme))

    def test___ixor__iterable(self):
        """Test the method __ixor__ with an iterable."""

        ccme = self.cme.copy()

        ccme.clear()

        self.assertFalse(ccme)

        ccme ^= list(self.cme.content)

        self.assertEqual(len(ccme), len(self.cme))

    def test___ixor__error(self):
        """Test the method __ixor__ without ModelElement."""

        self.assertRaises(TypeError, self.cme.__ixor__, None)

    def test___repr__(self):
        """Test the method __repr__."""

        assertrepr = repr(self.cme)

        self.assertEqual(
            assertrepr,
            '{0}({1})'.format(self.cme.__class__.__name__, self.cme._content)
        )

    def test_keys(self):
        """Test the method keys."""

        keys = self.cme.names()
        names = tuple(str(i) for i in range(self.count))

        self.assertEqual(names, keys)

    def test_setcontent(self):
        """Test to set content."""

        content = self.cme.content

        self.cme.content = []
        self.assertFalse(self.cme)

        self.cme.content = content
        self.assertEqual(len(self.cme), self.count)

    def test_put(self):
        """Test to put element."""

        for elt in self.cme.content:

            oldelt = self.cme.put(elt.copy())

            self.assertIs(elt, oldelt)
            self.assertIsNot(elt, self.cme[elt.name])

    def test_clean(self):
        """Test the method clean."""

        for elt in self.cme:

            elt.cleaned = False

        self.cme.clean()

        for elt in self.cme:

            self.assertTrue(elt.cleaned)

    def test_copy(self):
        """Test the method copy."""

        ccme = self.cme.copy()

        for melt in ccme:

            selfmelt = self.cme[melt]

            self.assertIsNot(selfmelt, melt)
            self.assertFalse(melt.cleaned)

        ccme = self.cme.copy(cleaned=True)

        for melt in ccme:

            selfmelt = self.cme[melt]

            self.assertIsNot(selfmelt, melt)
            self.assertTrue(melt.cleaned)

    def test_pop(self):
        """Test to pop elements."""

        name = str(0)

        self.assertIn(name, self.cme)

        me = self.cme.pop(name)

        self.assertNotIn(name, self.cme)

        me.name == name

    def test_get(self):
        """Test the method get."""

        for elt in self.cme:

            melt = self.cme.get(elt.name)

            self.assertIs(elt, melt)

            melt = self.cme.get('')
            self.assertIsNone(melt)

            melt = self.cme.get('', 2)
            self.assertIs(melt, 2)

    def test_setdefault(self):
        """Test the method setdefault."""

        for elt in self.cme.content:

            melt = elt.copy(cleaned=True)
            self.cme.setdefault(melt.name, melt)

            elt = self.cme[melt.name]

            self.assertFalse(elt.cleaned)

            del self.cme[elt.name]

            self.cme.setdefault(melt.name, melt)

            elt = self.cme[melt.name]

            self.assertTrue(elt.cleaned)

    def test_clear(self):
        """Test the method clear."""

        self.assertEqual(len(self.cme), self.count)

        self.cme.clear()

        self.assertFalse(self.cme)

    def test_update(self):
        """Test the method update."""

        ccme = self.cme.copy(cleaned=True)

        for i in range(self.count):

            name = str(i)
            mod = i % 3

            if mod == 0:

                del self.cme[name]

            elif mod == 1:

                del ccme[name]

        self.cme.update(ccme)

        for i in range(self.count):

            name = str(i)
            elt = self.cme[name]
            mod = i % 3

            if mod in (0, 2):
                self.assertTrue(elt.cleaned)

            elif mod == 1:
                self.assertFalse(elt.cleaned)


if __name__ == '__main__':
    main()
