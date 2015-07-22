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


from unittest import TestCase, main

from b3j0f.conf.configurable.core import Configurable
from b3j0f.conf.params import Configuration, Category, Parameter

from tempfile import NamedTemporaryFile

from os import remove


class ConfigurableTest(TestCase):

    def setUp(self):

        self.conf_paths = (
            NamedTemporaryFile().name,
            NamedTemporaryFile().name
        )

        self.configurable = Configurable()

        self.conf = Configuration(
            Category(
                'A',
                Parameter('a', value='a'),
                Parameter('2', value=2, parser=int),
                Parameter('error', value='error', parser=float)),
            Category(
                'B',
                Parameter('a', value='b'),
                Parameter('b', value='b')))

    def test_configuration_files(self):

        configurable = Configurable()
        configurable.conf_paths = self.conf_paths

        self.assertEqual(
            configurable.conf_paths,
            self.conf_paths)

        configurable = Configurable(
            conf_paths=self.conf_paths)

        self.assertEqual(
            configurable.conf_paths,
            self.conf_paths)

    def test_auto_conf(self):

        configurable = Configurable()

        self.assertTrue(configurable.auto_conf)

        configurable.auto_conf = False

        self.assertFalse(configurable.auto_conf)

    def test_logging_level(self):

        configurable = Configurable()

        self.assertTrue(configurable.log_lvl, 'INFO')

        configurable = Configurable(log_lvl='DEBUG')

        self.assertTrue(configurable.log_lvl, 'DEBUG')

        configurable.log_lvl = 'INFO'

        self.assertTrue(configurable.log_lvl, 'INFO')

    def test_configuration(self):

        # test to get from no file
        configurable = Configurable()

        conf = configurable.get_conf()

        self.assertEqual(len(conf), len(self.conf))

        # test to get from files which do not exist
        configurable.conf_paths = self.conf_paths

        for conf_path in self.conf_paths:
            try:
                remove(conf_path)
            except OSError:
                pass

        conf = configurable.get_conf()

        self.assertEqual(len(conf), len(self.conf))

        # get parameters from empty files
        for conf_path in self.conf_paths:
            with open(conf_path, 'w') as _file:
                _file.write('\n')

        conf = configurable.get_conf()

        self.assertEqual(len(conf), len(self.conf))

        # get parameters from empty files and empty parsing_rules
        conf = Configuration()
        configurable.get_conf(conf=conf)

        self.assertEqual(len(conf), 0)

        # fill files
        configurable = Configurable(
            conf_paths=self.conf_paths)

        # add first category in conf file[0]
        configurable.set_conf(
            conf_path=self.conf_paths[0],
            conf=Configuration(self.conf['A']),
            driver=configurable._drivers.split(',')[0])

        # add second category in conf file[1]
        configurable.set_conf(
            conf_path=self.conf_paths[1],
            conf=Configuration(self.conf['B']),
            driver=configurable._drivers.split(',')[1])

        conf = configurable.get_conf(conf=self.conf)

        unified_configuration = conf.unify()
        parameters = unified_configuration[Configuration.VALUES]
        errors = unified_configuration[Configuration.ERRORS]

        self.assertTrue('a' in parameters and 'a' not in errors)
        self.assertEqual(parameters['a'].value, 'b')
        self.assertTrue('2' in parameters and '2' not in errors)
        self.assertEqual(parameters['2'].value, 2)
        self.assertTrue('b' in parameters and 'b' not in errors)
        self.assertEqual(parameters['b'].value, 'b')
        self.assertTrue('error' in errors and 'error' not in parameters)

    def test_reconfigure(self):

        self.assertTrue(self.configurable.auto_conf)

        conf = Configuration(
            Category(
                'TEST',
                Parameter('auto_conf', value=False)))

        self.configurable.configure(conf=conf)
        self.assertFalse(self.configurable.auto_conf)
        self.assertEqual(self.configurable.log_lvl, 'INFO')

        conf = Configuration(
            Category(
                'TEST',
                Parameter('log_lvl', value='DEBUG')))

        self.configurable.configure(conf=conf)
        self.assertEqual(self.configurable.log_lvl, 'INFO')

        self.configurable.reconf_once = True
        self.configurable.configure(conf=conf)
        self.assertEqual(self.configurable.log_lvl, 'DEBUG')
        self.assertFalse(self.configurable.reconf_once)

        self.configurable.log_lvl = 'INFO'
        self.configurable.auto_conf = True
        self.configurable.configure(conf=conf)
        self.assertEqual(self.configurable.log_lvl, 'DEBUG')

    def test_configure_to_reconfigure_param(self):
        """Test to reconfigure an object with to_configure parameter.
        """

        self.assertTrue(self.configurable.auto_conf)

        class ToConfigure(object):
            """Class to configure.
            """
            def __init__(self):
                super(ToConfigure, self).__init__()
                self.test = None

        to_configure = ToConfigure()

        param = 'test'

        conf = Configuration(
            Category(
                'TEST',
                Parameter(param, value=True)
            )
        )

        self.configurable.configure(conf=conf, to_configure=to_configure)
        self.assertTrue(to_configure.test)

    def test_configure_without_inheritance(self):
        """Test to configure an object without inheritance.
        """

        class ToConfigure(object):
            """Class to configure.
            """
            def __init__(self):

                super(ToConfigure, self).__init__()

                self.test = None

        to_configure = ToConfigure()

        configurable = Configurable(to_configure=to_configure)

        param = 'test'

        conf = Configuration(
            Category(
                'TEST',
                Parameter(param, value=True)
            )
        )

        configurable.configure(conf=conf, to_configure=to_configure)
        self.assertTrue(to_configure.test)

    def test_parser_inheritance(self):

        class _Configurable(Configurable):

            def _conf(self, *args, **kwargs):

                result = super(_Configurable, self)._conf(
                    *args, **kwargs)

                result += Category('PLOP')

                return result

        configurable = Configurable()

        _configurable = _Configurable()

        self.assertEqual(
            len(configurable.conf) + 1,
            len(_configurable.conf)
        )

if __name__ == '__main__':
    main()
