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

from ..core import Configurable, applyconfiguration
from ...model.conf import configuration
from ...model.cat import category
from ...model.param import Parameter

from ...driver.test.base import TestConfDriver

from tempfile import NamedTemporaryFile

from six import add_metaclass


class ConfigurableTest(UTCase):

    def setUp(self):

        self.paths = (
            NamedTemporaryFile().name,
            NamedTemporaryFile().name
        )

        self.configurable = Configurable()

        self.conf = configuration(
            category(
                'A',
                Parameter('a', value='a', ptype=str),
                Parameter('_', value=2, ptype=int),
                Parameter('error', ptype=float, svalue='error')
            ),
            category(
                'B',
                Parameter('a', value='b', ptype=str),
                Parameter('b', value='b', ptype=str)
            )
        )

    def test_oldstyle(self):

        @Configurable()
        class TestA:
            pass

        TestA()

        @Configurable()
        class TestB:
            def __init__(self):
                pass

        TestB()

        @Configurable()
        class TestC(TestA):
            def __init__(self):
                TestA.__init__(self)

        TestC()

    def test_configuration_files(self):

        configurable = Configurable(paths=self.paths)

        self.assertEqual(configurable.paths, self.paths)

        configurable = Configurable()
        configurable.paths = self.paths

        self.assertEqual(configurable.paths, self.paths)

    def test_configure_to_reconfigure_param(self):
        """Test to reconfigure an object with targets parameter."""

        class ToConfigure(object):
            """Class to configure."""

            def __init__(self):
                super(ToConfigure, self).__init__()
                self.test = None

        target = ToConfigure()

        param = 'test'

        conf = configuration(category('TEST', Parameter(param, value=True)))

        self.configurable.configure(conf=conf, targets=[target])
        self.assertTrue(target.test)

    def test_configure_without_inheritance(self):
        """Test to configure an object without inheritance."""

        @Configurable(conf=category('TEST', Parameter('test', value=True)))
        class BaseTest(object):
            """base Class to configure."""

        class Test(BaseTest):
            """Class to configure."""

        targets = Test()

        self.assertTrue(targets.test)

    def test_parser_inheritance(self):

        @Configurable()
        class BaseTest(object):
            pass

        @Configurable()
        @Configurable()
        class SubTest(BaseTest):
            pass

        class Test(SubTest):
            pass

        configurables = Configurable.get_annotations(BaseTest)

        self.assertEqual(len(configurables), 1)

        configurables = Configurable.get_annotations(SubTest)

        self.assertEqual(len(configurables), 3)

        configurables = Configurable.get_annotations(Test)

        self.assertEqual(len(configurables), 3)

    def test_class_callparams(self):
        """Test to call params on a class."""

        @Configurable(
            conf=[
                Parameter('test0', value=True),
                Parameter('test1', value=False)
            ]
        )
        class Test(object):

            def __init__(self, test0=None):

                super(Test, self).__init__()

                self.test0 = test0

        test = Test()

        self.assertTrue(test.test0)
        self.assertFalse(test.test1)

    def test_metaclass(self):
        """Test to configurate a metaclass."""

        @Configurable(conf=Parameter('test', value=True))
        class MetaTest(type):
            pass

        @add_metaclass(MetaTest)
        class Test(object):
            pass

        test = Test()

        self.assertTrue(test.test)

    def test_function_callparams(self):
        """Test to call params on a function."""

        @Configurable(conf=category('', Parameter('test', value=True)))
        def twist(test=None):
            return test

        value = twist()

        self.assertTrue(value)

        value = twist(False)

        self.assertFalse(value)

        Configurable.get_annotations(twist)[0].conf['']['test'].value = 1

        value = twist()

        self.assertEqual(value, 1)

    def test_inheritance(self):
        """Test with inheritance between targets objects."""

        conf0 = configuration(
            category(
                'test0',
                Parameter('test0', value=0)
            ),
            category(
                'test1',
                Parameter('test1', value=1)
            )
        )

        conf1 = configuration(
            category(
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

    def test_applyconfiguration(self):
        """Test the function applyconfiguration."""

        conf = configuration(category('', Parameter('test', value=True)))

        @Configurable(conf=conf)
        class Test(object):
            pass

        test = Test()

        self.assertTrue(test.test)

        test.test = False

        applyconfiguration(targets=[test])

        self.assertTrue(test.test)

        class Test(object):
            pass

        test = Test()

        self.assertFalse(hasattr(test, 'test'))

        applyconfiguration(targets=[test], conf=conf)

        self.assertTrue(test.test)

    def test_annotation(self):
        """Test to use a configurable instancec such as a decodator."""

        configurable = Configurable(
            conf=configuration(category('', Parameter('test', value=True)))
        )

        @configurable
        class Test(object):
            pass

        test = Test()

        self.assertTrue(test.test)

        test.test = False

        applyconfiguration(targets=[test])

        self.assertTrue(test.test)

    def test_object(self):
        """Test to configure objects."""

        configurable = Configurable(
            conf=configuration(category('', Parameter('test', value=True)))
        )

        class Test(object):
            pass

        test = Test()

        configurable(test)
        configurable.applyconfiguration(targets=[test])

        self.assertTrue(test.test)

        test.test = False

        applyconfiguration(targets=[test])

        self.assertTrue(test.test)

    def test_multiconf(self):
        """Test to get configuration from multi resources."""

        tcd0, tcd1 = TestConfDriver(), TestConfDriver()

        tcd0.confbypath['test0'] = configuration(
            category(
                'test',
                Parameter('test0', value='0')
            )
        )
        tcd0.confbypath['test1'] = configuration(
            category(
                'test',
                Parameter('test1', value='1')
            )
        )
        tcd1.confbypath['test1'] = configuration(
            category(
                'test',
                Parameter('test2', svalue='=@test0/test.test0 + @test1/test.test1'),
                Parameter('test3', value=3)
            )
        )

        configurable = Configurable(drivers=[tcd0, tcd1])

        configurable.applyconfiguration(
            targets=[configurable], paths=['test0', 'test1']
        )

        self.assertEqual(configurable.test0, '0')
        self.assertEqual(configurable.test1, '1')
        self.assertEqual(configurable.test2, '01')
        self.assertEqual(configurable.test3, 3)

    def test_safe(self):
        """Test to configurate a configurable in a safe context."""

        conf = configuration(
            category(
                'test',
                Parameter('test', svalue='=open')
            )
        )

        configurable = Configurable(conf=conf, autoconf=False)

        self.assertRaises(
            Parameter.Error,
            configurable.applyconfiguration,
            targets=configurable, paths='test'
        )

    def test_unsafe(self):
        """Test to configurate a configurable in an unsafe context."""

        conf = configuration(
            category(
                'test',
                Parameter('test', svalue='=int')
            )
        )

        configurable = Configurable(conf=conf, safe=False)

        configurable.applyconfiguration(targets=[configurable], paths='test')

        self.assertIs(configurable.test, int)

    def test_subconf(self):
        """Test sub configuration."""

        class Test(object):
            pass

        class Test2(object):
            def __init__(self, param=None):
                self.param = param

        conf = configuration(
            category(
                'test',
                Parameter('subtest', value=Test),
                Parameter('subtest2', value=Test2)
            ),
            category(
                ':subtest',
                Parameter('param', svalue='=@subtest'),
                Parameter('attr', value=True)
            ),
            category(
                ':subtest:param',
                Parameter('param', svalue='=@subtest'),
                Parameter('attr', value=True)
            )
        )

        test = Test()

        applyconfiguration(conf=conf, targets=[test])

        self.assertIs(test.subtest2, Test2)
        self.assertIsInstance(test.subtest, Test)
        self.assertTrue(test.subtest.attr)
        self.assertIsInstance(test.subtest.param, Test)
        self.assertIs(test.subtest.param.param, Test)
        self.assertTrue(test.subtest.param.attr)

        oldsubtestparam = test.subtest.param

        conf[':subtest:param']['attr'].value = False

        applyconfiguration(conf=conf, targets=[test], keepstate=True)

        self.assertIs(test.subtest2, Test2)
        self.assertIsInstance(test.subtest, Test)
        self.assertTrue(test.subtest.attr)
        self.assertIsInstance(test.subtest.param, Test)
        self.assertIs(test.subtest.param.param, Test)
        self.assertFalse(test.subtest.param.attr)

        self.assertIs(test.subtest.param, oldsubtestparam)

        applyconfiguration(conf=conf, targets=[test], keepstate=False)

        self.assertIs(test.subtest2, Test2)
        self.assertIsInstance(test.subtest, Test)
        self.assertTrue(test.subtest.attr)
        self.assertIsInstance(test.subtest.param, Test)
        self.assertIs(test.subtest.param.param, Test)
        self.assertFalse(test.subtest.param.attr)

        self.assertIsNot(test.subtest.param, oldsubtestparam)

    def test_ptype(self):
        """Test application of ptype."""

        @Configurable(
            conf=[
                Parameter('test', ptype=int, svalue='1'),
                Parameter('ex', svalue='2', ptype=int)
            ]
        )
        class Test(object):

            def __init__(self, test=None, *args, **kwargs):

                super(Test, self).__init__(*args, **kwargs)

                self.testy = test

        test = Test()

        self.assertEqual(test.testy, 1)
        self.assertFalse(hasattr(test, 'test'))
        self.assertEqual(test.ex, 2)

        applyconfiguration(
            targets=[test], conf=[
                Parameter('test', svalue='2'),
                Parameter('ex', svalue='3')
            ]
        )

        self.assertEqual(test.testy, 1)
        self.assertEqual(test.test, 2)
        self.assertEqual(test.ex, 3)

        Configurable.get_annotations(test)[0].applyconfiguration(
            targets=[test], conf=[
                Parameter('test', svalue='3'),
                Parameter('ex', svalue='4', ptype=bool)
            ]
        )

        self.assertEqual(test.testy, 1)
        self.assertEqual(test.test, 3)
        self.assertTrue(test.ex)

if __name__ == '__main__':
    main()
