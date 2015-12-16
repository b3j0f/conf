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

from ..core import Configurable
from ...model.conf import Configuration
from ...model.cat import Category
from ...model.param import Parameter

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

        configurable = Configurable()
        configurable.paths = self.paths

        self.assertEqual(configurable.paths, self.paths)

        configurable = Configurable(paths=self.paths)

        self.assertEqual(configurable.paths, self.paths)

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
        configurable.paths = self.paths

        for path in self.paths:
            try:
                remove(path)
            except OSError:
                pass

        conf = configurable.get_conf()

        self.assertEqual(len(conf), len(self.conf))

        # get parameters from empty files
        for path in self.paths:
            with open(path, 'w') as _file:
                _file.write('\n')

        conf = configurable.get_conf()

        self.assertEqual(len(conf), len(self.conf))

        # get parameters from empty files and empty parsing_rules
        conf = Configuration()
        configurable.get_conf(conf=conf)

        self.assertEqual(len(conf), 0)

        # fill files
        configurable = Configurable(paths=self.paths)

        # add first category in conf file[0]
        configurable.set_conf(
            rscpath=self.paths[0],
            conf=Configuration(self.conf['A']),
            driver=configurable.drivers[0]
        )

        # add second category in conf file[1]
        configurable.set_conf(
            rscpath=self.paths[1],
            conf=Configuration(self.conf['B']),
            driver=configurable.drivers[1]
        )
        print('test')
        conf = configurable.get_conf(conf=self.conf)

        unified_configuration = conf.unify()
        parameters = unified_configuration[Configuration.VALUES]
        errors = unified_configuration[Configuration.ERRORS]

        self.assertIn('a', parameters)
        self.assertNotIn('a', errors)
        self.assertEqual(parameters['a'].value, 'b')
        self.assertIn('_', parameters)
        self.assertNotIn('_', errors)
        self.assertEqual(parameters['_'].value, 2)
        self.assertIn('b', parameters)
        self.assertNotIn('b', errors)
        self.assertEqual(parameters['b'].value, 'b')
        self.assertIn('error', errors)
        self.assertNotIn('error', parameters)

    def test_reconfigure(self):

        self.assertTrue(self.configurable.auto_conf)

        conf = Configuration(
            Category('TEST', Parameter('auto_conf', value=False))
        )

        self.configurable.configure(conf=conf)
        self.assertFalse(self.configurable.auto_conf)
        self.assertEqual(self.configurable.log_lvl, 'INFO')

        conf = Configuration(
            Category('TEST', Parameter('log_lvl', value='DEBUG'))
        )

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

        conf = Configuration(Category('TEST', Parameter(param, value=True)))

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

        conf = Configuration(Category('TEST', Parameter(param, value=True)))

        configurable.configure(conf=conf, to_configure=to_configure)
        self.assertTrue(to_configure.test)

    def test_parser_inheritance(self):

        class _Configurable(Configurable):

            def _clsconf(self, *args, **kwargs):

                result = super(_Configurable, self)._clsconf(*args, **kwargs)

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
