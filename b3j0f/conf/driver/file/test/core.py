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


from logging import getLogger

from b3j0f.utils.ut import UTCase

from unittest import main

from b3j0f.conf.params import Configuration, Category, Parameter
from b3j0f.conf.driver.file.core import FileConfDriver

from pickle import loads, dump

from os import remove


class TestConfDriver(FileConfDriver):
    """Configuration Manager for test.
    """

    __register__ = True

    def _has_category(
        self, conf_resource, category, logger, *args, **kwargs
    ):

        return category in conf_resource

    def _has_parameter(
        self, conf_resource, category, param, logger,
        *args, **kwargs
    ):

        return param.name in conf_resource[category.name]

    def _get_categories(self, conf_resource, logger, *args, **kwargs):
        return conf_resource.keys()

    def _get_parameters(
        self, conf_resource, category, logger, *args, **kwargs
    ):
        return conf_resource[category.name].keys()

    def _get_conf_resource(
        self, logger, conf_path=None, *args, **kwargs
    ):

        result = dict()

        if conf_path is not None:

            with open(conf_path, 'rb') as handle:

                try:
                    result = loads(handle.read())

                except Exception:
                    pass

        return result

    def _get_value(
        self, conf_resource, category, param, logger,
        *args, **kwargs
    ):

        return conf_resource[category.name][param.name]

    def _set_category(
        self, conf_resource, category, logger, *args, **kwargs
    ):

        conf_resource.setdefault(category.name, dict())

    def _set_parameter(
        self, conf_resource, category, param, logger,
        *args, **kwargs
    ):
        conf_resource[category.name][param.name] = param.value

    def _update_conf_resource(
        self, conf_resource, conf_path, *args, **kwargs
    ):

        with open(conf_path, 'wb') as handle:

            try:
                dump(conf_resource, handle)

            except Exception:
                pass


class FileConfDriverTest(UTCase):
    """Configuration Manager unittest class.
    """

    ERROR_PARAMETER = 'foo4'

    def setUp(self):
        self.logger = getLogger()

        self.manager = self._get_conf_manager()

        self.conf = Configuration(
            Category(
                'A',
                Parameter('a', value=0, parser=int),  # a is 0
                Parameter('b', value=True, parser=Parameter.bool)
            ),  # b is overriden
            Category(
                'B',
                Parameter('b', value=1, parser=int),  # b is 1
                Parameter('c', value='er', parser=int)   # error
            )
        )

        self.conf_path = self.get_conf_file()

    def get_conf_file(self):

        return '/tmp/b3j0f.conf'

    def _remove(self):
        try:
            remove(self.conf_path)
        except OSError:
            pass

    def _open(self):

        try:
            open(self.conf_path, 'wb').close()
        except OSError:
            pass

    def test_configuration(self):

        # try to get conf from not existing file
        self._remove()

        conf = self.manager.get_conf(
            conf_path=self.conf_path,
            logger=self.logger
        )

        self.assertIsNone(conf)

        # get conf from an empty media
        self._open()

        conf = self.manager.get_conf(
            conf_path=self.conf_path,
            logger=self.logger
        )

        self.assertIsNone(conf)

        # get full conf
        self.manager.set_conf(
            conf_path=self.conf_path,
            conf=self.conf,
            logger=self.logger
        )

        conf = self.manager.get_conf(
            conf_path=self.conf_path,
            conf=self.conf,
            logger=self.logger
        )

        self.assertIsNotNone(conf)
        self.assertEqual(len(conf), 2)

        unified_conf = conf.unify()

        parameters = unified_conf[Configuration.VALUES]
        errors = unified_conf[Configuration.ERRORS]

        self.assertIn('a', parameters)
        self.assertNotIn('a', errors)
        self.assertEqual(parameters['a'].value, 0)
        self.assertIn('b', parameters)
        self.assertNotIn('b', errors)
        self.assertEqual(parameters['b'].value, 1)
        #print(parameters['c'])
        self.assertIn('c', errors)
        self.assertNotIn('c', parameters)

        # get some conf
        conf = Configuration(self.conf['B'])

        conf = self.manager.get_conf(
            conf_path=self.conf_path,
            conf=conf,
            logger=self.logger
        )

        unified_conf = conf.unify()

        parameters = unified_conf[Configuration.VALUES]
        errors = unified_conf[Configuration.ERRORS]

        self.assertNotIn('a', parameters)
        self.assertNotIn('a', errors)
        self.assertIn('b', parameters)
        self.assertNotIn('b', errors)
        self.assertEqual(parameters['b'].value, 1)
        self.assertNotIn('c', parameters)
        self.assertIn('c', errors)

    def _get_conf_manager(self):
        """Only one method to override by sub tests
        """
        return TestConfDriver()

    def _get_manager_path(self):

        return 'b3j0f.conf.driver.file.test.TestConfDriver'

    def _get_manager(self):

        return TestConfDriver

if __name__ == '__main__':
    main()
