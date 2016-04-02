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

        __slots__ = ModelElement.__slots__ + ('name', 'cleaned', 'local')

        def __init__(
                self, name=None, local=False, cleaned=False, *args, **kwargs
        ):

            super(ModelElementTest.TestME, self).__init__(
                *args, **kwargs
            )

            self.cleaned = cleaned
            self.name = name
            self.local = local

    def setUp(self):

        self.me = ModelElementTest.TestME()

    def test_copy(self):
        """Test to copy a model element."""

        me = self.me.copy()

        self.assertFalse(me.cleaned)

    def test_cleaned_copy(self):
        """Test to a copied model element."""

        me = self.me.copy(cleaned=True)

        self.assertTrue(me.cleaned)

    def test_update(self):
        """Test the method update."""

        self.assertIsNone(self.me.name)

        copiedme = self.me.copy()

        self.assertIsNone(copiedme.name)

        copiedme.name = 'test'

        self.me.update(copiedme)

        self.assertEqual(self.me.name, 'test')

        self.assertFalse(self.me.cleaned)

        self.me.update(copiedme, copy=True, cleaned=True)

        self.assertTrue(self.me.cleaned)

        copiedme.name = None

        self.me.update(copiedme)

        self.assertIsNone(copiedme.name)
        self.assertIsNotNone(self.me.name)

    def test_update_inheritance(self):
        """Test the method update with inheritance of properties."""

        name = ModelElementTest.TestME(name=1, local=None)
        local = ModelElementTest.TestME(local=2)

        name.update(local)

        self.assertEqual(name.name, 1)
        self.assertEqual(name.local, 2)


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

        self.cme = CompositeModelElementTest.TestCME(melts=content)

    def test___iter__(self):
        """Test the __iter__ method."""

        iterator = iter(self.cme.values())

        counts = list(range(self.count))

        for i in range(self.count):

            item = next(iterator)
            counts.remove(int(item.name))

        self.assertEqual(len(counts), 0)

    def test___getitem__(self):
        """Test the __getitem__ method."""

        mes = list(self.cme.values())

        for i in range(self.count):

            me = self.cme[str(i)]
            me = self.cme[me.name]
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
            self.cme[me.name] = me

        names = set(me.name for me in self.cme.values())

        self.assertEqual(len(names), self.count)

    def test___delitem__(self):
        """Test the __delitem__ method."""

        for i in range(self.count):

            del self.cme[str(i)]

        self.assertEqual(len(self.cme), 0)

        for i in range(self.count):

            me = ModelElementTest.TestME(name=str(i))
            self.cme[str(i)] = me
            del self.cme[me.name]

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
            self.assertIn(me.name, self.cme)

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

        ccme += self.cme.values()

        self.assertEqual(len(ccme), len(self.cme))

    def test___iadd__iterable(self):
        """Test the method __iadd__ with an iterable."""

        ccme = self.cme.copy()

        ccme.clear()

        self.assertFalse(ccme)

        ccme += list(self.cme.values())

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

        self.cme -= list(self.cme.values())

        self.assertFalse(self.cme)

    def test___isub__cme(self):
        """Test the method __isub__ with a CompositeModelElement."""

        self.cme -= self.cme.values()

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

        ccme ^= self.cme.values()

        self.assertEqual(len(ccme), len(self.cme))

    def test___ixor__iterable(self):
        """Test the method __ixor__ with an iterable."""

        ccme = self.cme.copy()

        ccme.clear()

        self.assertFalse(ccme)

        ccme ^= list(self.cme.values())

        self.assertEqual(len(ccme), len(self.cme))

    def test___ixor__error(self):
        """Test the method __ixor__ without ModelElement."""

        self.assertRaises(TypeError, self.cme.__ixor__, None)

    def test_keys(self):
        """Test the method keys."""

        keys = tuple(self.cme.keys())
        names = tuple(str(i) for i in range(self.count))

        self.assertEqual(names, keys)

    def test_copy(self):
        """Test the method copy."""

        ccme = self.cme.copy()

        for melt in ccme.values():

            selfmelt = self.cme[melt.name]

            self.assertIsNot(selfmelt, melt)
            self.assertFalse(melt.cleaned)

    def test_pop(self):
        """Test to pop elements."""

        name = str(0)

        self.assertIn(name, self.cme)

        me = self.cme.pop(name)

        self.assertNotIn(name, self.cme)

        me.name == name

    def test_get(self):
        """Test the method get."""

        for elt in list(self.cme.values()):

            melt = self.cme.get(elt.name)

            self.assertIs(elt, melt)

            melt = self.cme.get('')
            self.assertIsNone(melt)

            melt = self.cme.get('', 2)
            self.assertIs(melt, 2)

    def test_setdefault(self):
        """Test the method setdefault."""

        for elt in list(self.cme.values()):

            melt = elt.copy(cleaned=True)
            self.cme.setdefault(melt.name, melt)

            elt = self.cme[melt.name]

            self.assertFalse(elt.cleaned)

    def test_clear(self):
        """Test the method clear."""

        self.assertEqual(len(self.cme), self.count)

        self.cme.clear()

        self.assertFalse(self.cme)

    def test_update(self):
        """Test the method update."""

        me = ModelElementTest.TestME(name='test')
        cme = CompositeModelElementTest.TestCME(melts=[me])

        self.cme.update(cme, copy=True)

        for selfme in self.cme.values():

            if me.name == 'test':
                self.assertFalse(me.local)

            else:
                self.assertTrue(me.local)

    def test_update_inheritance(self):
        """Test the method update with inheritance of properties."""

        name = ModelElementTest.TestME(
            name='test', local=None, cleaned='cleaned'
        )
        local = ModelElementTest.TestME(
            name='test', local='local', cleaned=None
        )

        cname = CompositeModelElementTest.TestCME(melts=[name])
        clocal = CompositeModelElementTest.TestCME(melts=[local])

        lcme = cname.copy()

        lcme.update(clocal)

        self.assertEqual(lcme['test'].local, 'local')
        self.assertEqual(lcme['test'].cleaned, 'cleaned')

        params = lcme.params

        self.assertEqual(params['test'].local, 'local')
        self.assertEqual(params['test'].cleaned, 'cleaned')

if __name__ == '__main__':
    main()
