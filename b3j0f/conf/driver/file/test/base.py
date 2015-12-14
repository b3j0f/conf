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

"""conf file driver UTs."""

from logging import getLogger

from b3j0f.utils.ut import UTCase

from unittest import main

from ....model.conf import Configuration
from ....model.cat import Category
from ....model.param import Parameter

from ..base import FileConfDriver

from pickle import load, dump

from os import remove


class TestConfDriver(FileConfDriver):
    """Configuration file driver for test."""

    def resource(self):

        return {}

    def _cnames(self, resource, *args, **kwargs):

        return resource.keys()

    def _params(
            self, resource, cname, *args, **kwargs
    ):

        result = [
            (pname, resource[cname][pname]) for pname in resource[cname]
        ]

        return result

    def _pathresource(self, rscpath):

        result = None

        with open(rscpath, 'r') as handle:

            result = load(handle)

        return result

    def _set_conf(self, resource, rscpath, conf):

        for cat in conf:
            for param in cat:
                resource.setdefault(cat.name, {})[param.name] = param.svalue

        with open(rscpath, 'w') as handle:

            try:
                dump(resource, handle)

            except TypeError:
                pass


class FileConfDriverTest(UTCase):
    """Configuration Manager unittest class."""

    ERROR_PARAMETER = 'foo4'

    def setUp(self):

        self.logger = getLogger()

        self.manager = self._get_conf_manager()

        self.conf = Configuration(
            Category(
                'A',
                Parameter('a', value=0, vtype=int),  # a is 0
                Parameter('b', value=True, vtype=bool)
            ),  # b is overriden
            Category(
                'B',
                Parameter('b', value=1, vtype=int),  # b is 1
                Parameter('c', vtype=int, svalue='er')   # error
            )
        )

        self.path = self.get_conf_file()

    def get_conf_file(self):

        return '/tmp/b3j0f{0}.conf'.format(type(self).__name__)

    def _remove(self):
        try:
            remove(self.path)
        except OSError:
            pass

    def _open(self):

        try:
            open(self.path, 'wb').close()
        except OSError:
            pass

    def test_configuration(self):

        # try to get conf from not existing file
        self._remove()

        conf = self.manager.get_conf(
            path=self.path,
            logger=self.logger
        )

        self.assertIsNone(conf)

        # get conf from an empty media
        self._open()

        conf = self.manager.get_conf(
            path=self.path,
            logger=self.logger
        )

        self.assertIsNone(conf)

        conf = self.manager.get_conf(
            path=self.path,
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
        self.assertIn('c', errors)
        self.assertNotIn('c', parameters)

        # get some conf
        conf = Configuration(self.conf['B'])

        conf = self.manager.get_conf(
            path=self.path,
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
        """Only one method to override by sub tests."""

        return self._get_manager()()

    def _get_manager(self):

        return TestConfDriver

if __name__ == '__main__':
    main()